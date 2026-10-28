#!/usr/bin/env python3
# TOY: not secure. Truncated hash outputs (lam = 8..16 bits) so that attacks succeed often enough to measure.
"""merkle_collision_mc.py -- Monte Carlo check that a measured attack success stays inside a CY24 bound.

    python3 merkle_collision_mc.py              # table: lam, t, measured frequency, bound
    python3 merkle_collision_mc.py --selftest   # assertions only, exit 0 on success

Random oracle: SHA-256 with a fresh per-trial key, truncated to lam bits (a fresh oracle per trial).
Experiment 1 (collision resistance): a t-query adversary queries t distinct inputs and wins if two answers
collide. CY24 bounds every t-query adversary by t(t-1)/2^(lam+1)
([CY24 §Collision resistance, lemma:rom-cr]); this naive strategy should come close to it.
Experiment 2 (Merkle binding): a depth-1 Merkle tree (two leaves, root = H(1 || H(0||m0) || H(0||m1))).
The adversary spends its t queries on leaf hashes of distinct messages; any leaf collision H(0||m) = H(0||m')
gives two valid openings of the same position to different messages, which the script then *verifies*
with the Merkle checker. CY24 bounds binding breaks by t^2/2^(lam+1) for t >= 2(depth+1)^2
([CY24 §Binding, lemma:mt-binding]).
A measured frequency above bound + 3 standard errors is a counterexample to the bound as transcribed (or a bug
in the experiment); report it, do not tune it away. The Fiat-Shamir analogue (grinding against strong FS,
weak-FS forgery) lives in skills/fiat-shamir-audit/scripts/toy_fs_attack.py and is not duplicated here.
Pure Python 3.10+, no dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
import math
import sys


def oracle(key: int, lam: int):
    """A fresh lam-bit random oracle per key (keyed, domain-separated SHA-256, truncated)."""
    def H(data: bytes) -> int:
        d = hashlib.sha256(key.to_bytes(8, "big") + data).digest()
        return int.from_bytes(d, "big") >> (256 - lam)
    return H


def collision_trial(key: int, lam: int, t: int) -> bool:
    H = oracle(key, lam)
    seen = set()
    for i in range(t):
        y = H(b"q" + i.to_bytes(8, "big"))
        if y in seen:
            return True
        seen.add(y)
    return False


def merkle_root(H, m0: bytes, m1: bytes) -> int:
    l0, l1 = H(b"\x00" + m0), H(b"\x00" + m1)
    return H(b"\x01" + l0.to_bytes(4, "big") + l1.to_bytes(4, "big"))


def merkle_check(H, root: int, pos: int, msg: bytes, sibling_leaf: int) -> bool:
    leaf = H(b"\x00" + msg)
    pair = (leaf, sibling_leaf) if pos == 0 else (sibling_leaf, leaf)
    return H(b"\x01" + pair[0].to_bytes(4, "big") + pair[1].to_bytes(4, "big")) == root


def binding_trial(key: int, lam: int, t: int) -> bool:
    """Spend t - 2 queries on leaf hashes (2 are needed to build the root); win iff two distinct messages
    open position 0 of the same root."""
    H = oracle(key, lam)
    seen: dict[int, bytes] = {}
    for i in range(max(0, t - 2)):
        m = b"m" + i.to_bytes(8, "big")
        y = H(b"\x00" + m)
        if y in seen:
            m0, m0b, m1 = seen[y], m, b"sibling"
            root = merkle_root(H, m0, m1)
            sib = H(b"\x00" + m1)
            assert merkle_check(H, root, 0, m0, sib) and merkle_check(H, root, 0, m0b, sib) and m0 != m0b
            return True
        seen[y] = m
    return False


def measure(trial, lam: int, t: int, trials: int, seed: int = 0) -> float:
    return sum(trial(seed * 10 ** 6 + k, lam, t) for k in range(trials)) / trials


def cr_bound(lam: int, t: int) -> float:
    return t * (t - 1) / 2 ** (lam + 1)


def mt_binding_bound(lam: int, t: int) -> float:
    return t * t / 2 ** (lam + 1)


def within(freq: float, bound: float, trials: int) -> bool:
    b = min(bound, 1.0)
    return freq <= b + 3 * math.sqrt(max(b * (1 - b), 1e-12) / trials)


def run(trials: int = 4000, verbose: bool = True) -> list[dict]:
    rows = []
    for lam in (10, 12, 14):
        for t in (8, 16, 32, 64):
            f1 = measure(collision_trial, lam, t, trials, seed=lam * 100 + t)
            f2 = measure(binding_trial, lam, t, trials, seed=lam * 1000 + t)
            rows.append({"lam": lam, "t": t, "cr_freq": f1, "cr_bound": cr_bound(lam, t),
                         "mt_freq": f2, "mt_bound": mt_binding_bound(lam, t),
                         "cr_ok": within(f1, cr_bound(lam, t), trials),
                         "mt_ok": within(f2, mt_binding_bound(lam, t), trials)})
    if verbose:
        print(f"{trials} trials per cell; bounds from lemma:rom-cr and lemma:mt-binding")
        print("| lam | t | collision freq | t(t-1)/2^(lam+1) | Merkle binding-break freq | t^2/2^(lam+1) | within |")
        print("|---|---|---|---|---|---|---|")
        for r in rows:
            print(f"| {r['lam']} | {r['t']} | {r['cr_freq']:.4f} | {r['cr_bound']:.4f} | {r['mt_freq']:.4f} | "
                  f"{r['mt_bound']:.4f} | {'yes' if r['cr_ok'] and r['mt_ok'] else 'NO'} |")
    return rows


def selftest() -> int:
    rows = run(trials=2000, verbose=False)
    assert all(r["cr_ok"] and r["mt_ok"] for r in rows), [r for r in rows if not (r["cr_ok"] and r["mt_ok"])]
    # the naive collision search is close to the bound when the bound is small (birthday regime)
    r = next(r for r in rows if r["lam"] == 14 and r["t"] == 64)
    assert 0.5 * r["cr_bound"] <= r["cr_freq"] <= r["cr_bound"] * 1.3, r
    # a deliberately wrong "bound" (linear in t, the inversion-type t/2^lam) is exceeded: the check can fail
    r = next(r for r in rows if r["lam"] == 10 and r["t"] == 64)
    assert not within(r["cr_freq"], r["t"] / 2 ** r["lam"], 2000), r
    # every binding break the experiment reports is a real one (asserted inside binding_trial)
    assert measure(binding_trial, 8, 64, 200) > 0
    print("selftest: OK")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trials", type=int, default=4000)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    rows = run(a.trials)
    return 0 if all(r["cr_ok"] and r["mt_ok"] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
