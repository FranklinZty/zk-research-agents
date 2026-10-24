#!/usr/bin/env python3
# TOY: not secure
"""sage-check template: exhaustive small-field checks of ZK lemma statements.

Copy this file, replace STATEMENTS, and run:
    python3 sanity_check_template.py        (pure Python)
    sage -python sanity_check_template.py   (Sage available -> used for cross-checks)

Each statement is (ID, parameter iterator, hypothesis(params) -> bool,
conclusion(params) -> bool).  Output: one JSON line per statement.
Exit code 1 if any statement has a counterexample (so CI / agents notice).

Toy statements below are about sum-check, Schwartz-Zippel and a grand-product
multiset check over F_17 / F_97 -- replace them.
"""
from __future__ import annotations

import itertools
import json
import random
import sys

try:  # guarded Sage import (SPEC: sage optional)
    from sage.all import GF, PolynomialRing  # type: ignore
    HAVE_SAGE = True
except Exception:  # pragma: no cover
    HAVE_SAGE = False

SEED = 20261024
FIELDS = (17, 97)


def check(sid, params_iter, hypothesis, conclusion, max_cases=10 ** 7):
    cases = vacuous = 0
    for params in params_iter:
        if cases >= max_cases:
            break
        if not hypothesis(params):
            vacuous += 1
            continue
        cases += 1
        if not conclusion(params):
            return {"check": sid, "cases": cases, "passed": False, "counterexample": params}
    return {"check": sid, "cases": cases, "passed": cases > 0, "counterexample": None,
            "note": "VACUOUS: hypothesis never satisfied" if cases == 0 else f"{vacuous} param points excluded by hypothesis"}


# ---------------------------------------------------------------------------- field helpers
def poly_eval(coeffs: dict, point, p: int) -> int:
    """Evaluate a multivariate polynomial {exponent tuple: coeff} at point mod p."""
    acc = 0
    for exps, c in coeffs.items():
        term = c
        for x, e in zip(point, exps):
            term = term * pow(x, e, p) % p
        acc = (acc + term) % p
    return acc


def lagrange_eval(ys, r: int, p: int) -> int:
    """Evaluate the unique poly of degree < len(ys) with values ys at 0..len(ys)-1, at r."""
    n, acc = len(ys), 0
    for i, y in enumerate(ys):
        num = den = 1
        for j in range(n):
            if j != i:
                num = num * (r - j) % p
                den = den * (i - j) % p
        acc = (acc + y * num * pow(den, -1, p)) % p
    return acc


def random_poly(mu: int, deg: int, p: int, rng: random.Random) -> dict:
    """Random polynomial in mu variables with individual degree <= deg."""
    return {e: rng.randrange(p) for e in itertools.product(range(deg + 1), repeat=mu)}


def sumcheck_run(g, mu, deg, p, challenges, sent_deg=None, cheat=None):
    """Honest sum-check prover + verifier; returns True iff the verifier accepts.

    sent_deg: degree of the round polynomials the prover sends (default deg).
    cheat: optional (alpha, ts).  The prover claims H + delta(0) + delta(1) with
    delta(X) = alpha * prod(X - t), sends g_1 + delta, and plays honestly afterwards
    (the standard 'lie in round 1' strategy; it survives iff r_1 is a root of delta).
    """
    sent_deg = deg if sent_deg is None else sent_deg
    H = sum(poly_eval(g, b, p) for b in itertools.product((0, 1), repeat=mu)) % p
    def delta(x):
        alpha, ts = cheat
        out = alpha
        for t in ts:
            out = out * (x - t) % p
        return out

    claim = (H + delta(0) + delta(1)) % p if cheat else H
    prefix = []
    for i in range(mu):
        rest = mu - i - 1
        ys = [sum(poly_eval(g, prefix + [x] + list(b), p)
                  for b in itertools.product((0, 1), repeat=rest)) % p
              for x in range(sent_deg + 1)]
        if i == 0 and cheat:
            ys = [(y + delta(x)) % p for x, y in enumerate(ys)]
        if (ys[0] + ys[1]) % p != claim:
            return False
        r = challenges[i]
        claim = lagrange_eval(ys, r, p)
        prefix.append(r)
    return claim == poly_eval(g, prefix, p)


# ---------------------------------------------------------------------------- statements
def s1_params():
    """Completeness: every challenge vector, a few random polys, per field."""
    rng = random.Random(SEED)
    for p in FIELDS:
        for mu, deg in ((1, 1), (2, 1), (2, 2)):
            for _ in range(6 if p == 17 else 2):
                g = random_poly(mu, deg, p, rng)
                for ch in itertools.product(range(p), repeat=mu):
                    yield {"p": p, "mu": mu, "deg": deg, "g": g, "r": ch}


# S1 (true): the honest sum-check prover is always accepted.
S1 = ("S1: sum-check completeness (honest prover accepted for every challenge)", s1_params(),
      lambda P: True,
      lambda P: sumcheck_run(P["g"], P["mu"], P["deg"], P["p"], P["r"]))


def s2_params():
    rng = random.Random(SEED + 1)
    for p in FIELDS:
        for d in (1, 2, 3, 5):
            # extremal polynomial prod (x - a_i): exactly d*p zeros on F_p^2 (bound is tight)
            yield {"p": p, "d": d, "f": "extremal", "roots": rng.sample(range(p), d)}
            for _ in range(20 if p == 17 else 4):
                yield {"p": p, "d": d, "f": "random", "seed": rng.randrange(10 ** 9)}


def sz_zero_count(P) -> int:
    p, d = P["p"], P["d"]
    if P["f"] == "extremal":
        coeffs = {(0, 0): 1}
        for a in P["roots"]:  # multiply by (x - a)
            nxt: dict = {}
            for (i, j), c in coeffs.items():
                nxt[(i + 1, j)] = (nxt.get((i + 1, j), 0) + c) % p
                nxt[(i, j)] = (nxt.get((i, j), 0) - a * c) % p
            coeffs = nxt
        return sum(1 for x in range(p) for y in range(p) if poly_eval(coeffs, (x, y), p) == 0)
    rng = random.Random(P["seed"])
    coeffs = {(i, j): rng.randrange(p) for i in range(d + 1) for j in range(d + 1 - i)}
    coeffs[(d, 0)] = rng.randrange(1, p)  # nonzero, total degree exactly d
    return sum(1 for x in range(p) for y in range(p) if poly_eval(coeffs, (x, y), p) == 0)


# S2 (true): Schwartz-Zippel -- a nonzero bivariate poly of total degree d vanishes
# on at most a d/p fraction of F_p^2.  Empirical frequency is checked exhaustively.
S2 = ("S2: Schwartz-Zippel, zero frequency on F_p^2 <= d/p", s2_params(),
      lambda P: True,
      lambda P: sz_zero_count(P) * P["p"] <= P["d"] * P["p"] ** 2)


def s3_params():
    rng = random.Random(SEED + 2)
    for p in FIELDS:
        for mu, deg in ((2, 1), (2, 2), (3, 2)):
            for _ in range(3):
                yield {"p": p, "mu": mu, "deg": deg, "g": random_poly(mu, deg, p, rng),
                       "shift": rng.randrange(1, p), "seed": rng.randrange(10 ** 9)}


def cheat_rate_ok(P) -> bool:
    """Lie in round 1; over all r_1 (exhaustive) with fixed later challenges, the
    acceptance frequency must be <= mu*deg/p (the sum-check soundness bound)."""
    p, mu, deg = P["p"], P["mu"], P["deg"]
    rng = random.Random(P["seed"])
    tail = [rng.randrange(p) for _ in range(mu - 1)]
    while True:  # delta of degree deg with deg distinct roots and delta(0)+delta(1) != 0
        ts = rng.sample(range(p), deg)
        d0 = d1 = 1
        for t in ts:
            d0, d1 = d0 * (-t) % p, d1 * (1 - t) % p
        if (d0 + d1) % p:
            break
    alpha = P["shift"] * pow(d0 + d1, -1, p) % p
    acc = sum(sumcheck_run(P["g"], mu, deg, p, [r1] + tail, cheat=(alpha, ts))
              for r1 in range(p))
    return acc * p <= mu * deg * p


# S3 (true): empirical soundness of sum-check against the 'lie in round 1' prover.
S3 = ("S3: sum-check cheating frequency <= mu*deg/p", s3_params(),
      lambda P: True, cheat_rate_ok)


def s4_params():
    for p in FIELDS:
        for n in (2, 3, 4):
            for a in itertools.product(range(3), repeat=n):
                for b in itertools.product(range(3), repeat=n):
                    yield {"p": p, "a": a, "b": b}


def bad_gammas(P) -> int:
    p, a, b = P["p"], P["a"], P["b"]
    cnt = 0
    for g in range(p):
        lhs = rhs = 1
        for x, y in zip(a, b):
            lhs, rhs = lhs * (x + g) % p, rhs * (y + g) % p
        cnt += lhs == rhs
    return cnt


# S4 (true): grand-product multiset check (the core of permutation / lookup arguments):
# if b is NOT a permutation of a, at most n of the p challenges gamma pass.
S4 = ("S4: grand-product check, non-permutations pass for <= n gammas", s4_params(),
      lambda P: sorted(P["a"]) != sorted(P["b"]),
      lambda P: bad_gammas(P) <= len(P["a"]))


def s5_params():
    rng = random.Random(SEED + 3)
    for p in FIELDS:
        for _ in range(5):
            g = random_poly(2, 2, p, rng)
            for ch in itertools.product(range(p), repeat=2):
                yield {"p": p, "mu": 2, "deg": 2, "g": g, "r": ch}


# S5 (FALSE, deliberately): "for g of individual degree 2 it suffices to send each
# round polynomial as 2 evaluations (degree <= 1)".  Degree-bound bugs of this kind
# break completeness; demonstrates counterexample output.
S5 = ("S5 (expected to FAIL): degree-1 round polys suffice for individual degree 2", s5_params(),
      lambda P: True,
      lambda P: sumcheck_run(P["g"], P["mu"], P["deg"], P["p"], P["r"], sent_deg=1))

STATEMENTS = [S1, S2, S3, S4, S5]
EXPECTED_FAIL = {S5[0]}


def sage_crosscheck() -> dict | None:
    """Optional: cross-check lagrange_eval against Sage's interpolation over F_17, F_97."""
    if not HAVE_SAGE:
        return None
    rng = random.Random(SEED + 4)
    ok = True
    for p in FIELDS:
        R = PolynomialRing(GF(p), "x")
        for _ in range(20):
            ys = [rng.randrange(p) for _ in range(rng.randrange(2, 6))]
            f = R.lagrange_polynomial(list(zip(range(len(ys)), ys)))
            r = rng.randrange(p)
            ok &= int(f(r)) == lagrange_eval(ys, r, p)
    return {"check": "sage-crosscheck lagrange_eval", "passed": bool(ok)}


def main() -> int:
    bad = 0
    for sid, it, hyp, concl in STATEMENTS:
        res = check(sid, it, hyp, concl)
        if res.get("counterexample"):
            res["counterexample"] = {k: v for k, v in res["counterexample"].items() if k != "g"}
        print(json.dumps(res))
        if not res["passed"] and sid not in EXPECTED_FAIL:
            bad += 1
        if sid in EXPECTED_FAIL and res["passed"]:
            print(json.dumps({"check": sid, "error": "expected a counterexample but found none"}))
            bad += 1
    sc = sage_crosscheck()
    if sc:
        print(json.dumps(sc))
        bad += 0 if sc["passed"] else 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
