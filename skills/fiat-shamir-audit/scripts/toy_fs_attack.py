#!/usr/bin/env python3
# TOY: not secure. Small field, truncated hash; for demonstrating Fiat-Shamir pitfalls only.
"""toy_fs_attack.py -- what goes wrong when the statement is not hashed (weak Fiat-Shamir).

    python3 toy_fs_attack.py              # run the demo and print the numbers
    python3 toy_fs_attack.py --selftest   # assertions only, exit 0 on success

Toy protocol (public-coin, one verifier message, no prover message):
    statement x = (A, B), two polynomials over F_p of degree <= d, claimed equal;
    the verifier samples r in F_p and accepts iff A(r) = B(r).
Its soundness error is d/p (Schwartz-Zippel, [Thaler §3.4, Schwartz-Zippel Lemma]).

Compiled with Fiat-Shamir the challenge becomes r = H(...):
  * weak FS,   r = H(domain)            -- the statement is not hashed;
  * strong FS, r = H(domain, A, B, salt) -- the statement is the first thing absorbed.

Weak FS: the prover computes r first and then picks a false statement that passes at r, e.g.
B = A + (X - r). It wins with probability 1 using one query: the construction is only non-adaptively sound
(the instance cannot depend on the oracle), exactly the failure described in
[CY24 §Lack of adaptive security, section:fs-lack-of-adaptive-soundness].
Strong FS: the best the prover can do is grind over statements/salts; with t queries its success is at most
(t+1) d/p ([CY24 §Adaptive soundness, theorem:narg-from-sp-adaptive-soundness]) and a simple grinding prover
gets close to t d/p - C(t,2)(d/p)^2 ([CY24 §Lower bound on the non-adaptive soundness error,
lemma:attack-against-warmup-narg-from-sp]). The demo measures both.

Also included: a transcript lint that compares the items a transcript absorbs (in order) with the items the
paper says must be absorbed, and a domain-separation check for several hash roles derived from one function.
"""
from __future__ import annotations

import argparse
import hashlib
import random
import sys
from math import comb

P = 101          # toy field F_101
D = 1            # degree bound of A and B


def H(*parts: object, p: int = P) -> int:
    """Toy random oracle onto F_p: SHA-256 of a canonical, length-prefixed encoding, reduced mod p (tiny bias,
    irrelevant for a demo; real code must sample uniformly, see the skill's checklist)."""
    h = hashlib.sha256()
    for part in parts:
        b = repr(part).encode()
        h.update(len(b).to_bytes(8, "big") + b)
    return int.from_bytes(h.digest(), "big") % p


def ev(poly: tuple[int, ...], r: int, p: int = P) -> int:
    acc = 0
    for c in reversed(poly):
        acc = (acc * r + c) % p
    return acc


def verify(A, B, r, p: int = P) -> bool:
    return ev(A, r, p) == ev(B, r, p)


def is_true_statement(A, B, p: int = P) -> bool:
    n = max(len(A), len(B))
    a = list(A) + [0] * (n - len(A)); b = list(B) + [0] * (n - len(B))
    return all((x - y) % p == 0 for x, y in zip(a, b))


# ----------------------------------------------------------------------------- weak FS: adaptive attack ---

def weak_fs_challenge(A, B, salt: int, p: int = P) -> int:
    return H("toy-id-check/challenge", salt, p=p)          # BUG under test: statement not absorbed


def strong_fs_challenge(A, B, salt: int, p: int = P) -> int:
    return H("toy-id-check/challenge", A, B, salt, p=p)    # statement absorbed first


def weak_fs_attack(seed: int = 0, p: int = P):
    """One oracle query: learn r, then choose a FALSE statement that passes at r."""
    rnd = random.Random(seed)
    salt = rnd.randrange(2 ** 32)
    r = weak_fs_challenge(None, None, salt, p)
    A = (rnd.randrange(p), rnd.randrange(p))
    B = ((A[0] - r) % p, (A[1] + 1) % p)                    # B = A + (X - r): differs from A, agrees at r
    proof = salt
    return A, B, proof


def check_weak(A, B, proof, p: int = P) -> bool:
    return verify(A, B, weak_fs_challenge(A, B, proof, p), p)


def check_strong(A, B, proof, p: int = P) -> bool:
    return verify(A, B, strong_fs_challenge(A, B, proof, p), p)


def strong_fs_grinding(t: int, trials: int, seed: int = 1, p: int = P) -> float:
    """Grinding prover against strong FS: fix one false statement, try t salts, win if any challenge is a root
    of A - B. Returns the empirical success frequency over `trials` independent oracles (fresh domain tags)."""
    rnd = random.Random(seed)
    wins = 0
    for trial in range(trials):
        A = (rnd.randrange(p), rnd.randrange(p))
        B = ((A[0] + rnd.randrange(1, p)) % p, (A[1] + rnd.randrange(1, p)) % p)   # degree-1 difference
        for salt in range(t):
            r = H("toy-id-check/challenge", trial, A, B, salt, p=p)                 # trial = fresh oracle
            if verify(A, B, r, p):
                wins += 1
                break
    return wins / trials


# ----------------------------------------------------------------------------- lint helpers ---

def transcript_lint(absorbed: list[str], required: list[str]) -> list[str]:
    """Findings for a transcript that absorbed `absorbed` (in order) where the paper requires `required` (in order,
    each item before the challenge that depends on it). Empty list = no finding."""
    out = [f"missing: {item}" for item in required if item not in absorbed]
    present = [item for item in required if item in absorbed]
    pos = [absorbed.index(item) for item in present]
    for (a, pa), (b, pb) in zip(zip(present, pos), zip(present[1:], pos[1:])):
        if pa > pb:
            out.append(f"order: {a} must be absorbed before {b}")
    return out


def domain_separated(roles: dict[str, bytes]) -> bool:
    """True iff no role's prefix is a prefix of another's (so no query of one role equals a query of another,
    given length-prefixed bodies). Roles are e.g. Merkle leaf, Merkle node, FS round i, proof of work."""
    tags = list(roles.values())
    return all(not (i != j and tags[j].startswith(tags[i])) for i in range(len(tags)) for j in range(len(tags)))


# ----------------------------------------------------------------------------- demo / selftest ---

def run(verbose: bool = True) -> bool:
    ok = True

    def expect(cond, msg):
        nonlocal ok
        if verbose or not cond:
            print(("ok   " if cond else "FAIL ") + msg)
        ok &= bool(cond)

    eps = D / P
    # weak FS: 1 query, probability 1, statement false.
    wins = 0
    for seed in range(200):
        A, B, proof = weak_fs_attack(seed)
        wins += check_weak(A, B, proof) and not is_true_statement(A, B)
    expect(wins == 200, f"weak FS: adaptive prover passes a FALSE statement in 200/200 runs with 1 query (eps = {eps:.4f})")
    # the same forged proofs fail once the statement is hashed
    rej = sum(not check_strong(*weak_fs_attack(seed)) for seed in range(200))
    expect(rej >= 190, f"strong FS: the same forgeries are rejected in {rej}/200 runs (accepts only when H(A,B,salt) hits the root)")
    # strong FS: grinding success tracks t*eps and stays below (t+1)*eps (statistical tolerance for 2000 trials)
    for t in (1, 5, 20):
        freq = strong_fs_grinding(t, 2000, seed=t)
        upper = (t + 1) * eps
        lower = t * eps - comb(t, 2) * eps ** 2
        expect(freq <= upper + 0.03, f"strong FS, t = {t:2d}: grinding success {freq:.3f} <= (t+1)eps = {upper:.3f} (+0.03 tolerance)")
        expect(freq >= lower - 0.03, f"strong FS, t = {t:2d}: grinding success {freq:.3f} >= t eps - C(t,2)eps^2 = {lower:.3f} (-0.03)")
    # lint
    req = ["domain-tag", "params", "statement", "public-input", "commit-1", "challenge-1", "commit-2", "challenge-2"]
    expect(transcript_lint(req, req) == [], "transcript lint: complete transcript has no finding")
    f = transcript_lint(["domain-tag", "commit-1", "challenge-1", "commit-2", "challenge-2"], req)
    expect("missing: statement" in f and "missing: params" in f, "transcript lint: missing statement and params reported")
    f = transcript_lint(["domain-tag", "params", "statement", "public-input", "challenge-1", "commit-1", "commit-2", "challenge-2"], req)
    expect(any(x.startswith("order: commit-1") for x in f), "transcript lint: commitment absorbed after its challenge reported")
    expect(domain_separated({"leaf": b"\x00", "node": b"\x01", "fs": b"\x02"}), "domain separation: distinct one-byte tags")
    expect(not domain_separated({"fs": b"fs", "fs-round-1": b"fs-round-1"}), "domain separation: a tag that prefixes another is flagged")
    return ok


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    ok = run(verbose=True)
    print(("selftest: " if a.selftest else "demo: ") + ("all checks passed" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
