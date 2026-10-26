#!/usr/bin/env python3
# TOY: not secure -- didactic walk-through of the idea-mining loop on a toy FRI cost model.
"""toy_mining_demo.py -- the 8-step idea-mining loop, end to end, on a toy ZK problem.

Problem (Step 0, probe-able bottleneck): a FRI-style low-degree test for a polynomial of
degree < d = 2^D, committed on a domain of size N = d / rho (rate rho = 2^-b), folded by a
factor k = 2^a per round.  Proxy metric: proof size (KiB) x verifier work (hash-compression
units), at a fixed toy target of LAMBDA bits.  Lower is better.  Baseline: binary folding
(k = 2) at rate 1/2.

Toy cost model (NOT a soundness analysis -- real numbers come from soundness-budget):
  * queries q = ceil(LAMBDA / beta(rho)); beta is a toy per-query bit count, either
    'proven'      beta = -log2((1 + rho) / 2)   (unique-decoding-style toy)
    'conjectured' beta = -log2(rho)             (list-decoding-style toy)
  * each round opens one coset of k field elements per query (one Merkle leaf per coset)
    and a Merkle path of depth log2(#cosets);
  * the habit-fixed implementation uses the SAME k in every round, so when a does not divide
    D it pads the degree up to k^ceil(D/a) (domain grows accordingly).

The loop finds an outlier along the k axis, kills a naive explanation ('that k is just too
wide') with two control experiments, validates the closed-form model against a direct simulation
of the Merkle openings (with path de-duplication across queries), and ends with the
mixed-arity generalisation and a continuous-relaxation lower bound.  The procedure is the
point; the numbers are synthetic.

Run:  python3 toy_mining_demo.py              (D = 20, a few seconds)
      python3 toy_mining_demo.py --D 22       (honest Gate-B failure: no outlier)
      python3 toy_mining_demo.py --selftest
"""
from __future__ import annotations

import argparse
import math
import random
import sys

LAMBDA = 100          # toy target bits
FELT, HASH = 8, 32    # bytes per field element / digest
BLOCK = 64            # bytes per hash-compression call
MUL = 0.02            # one field multiplication, in hash-compression units
A_RANGE = range(1, 8)  # folding factor k = 2^a, k in 2..128
B_RANGE = range(1, 6)  # rate rho = 2^-b, rho in 1/2..1/32
TAU = 0.10            # anomaly threshold: log-excess over the convex trend along k


def beta(b: int, regime: str) -> float:
    rho = 2.0 ** -b
    return -math.log2((1 + rho) / 2) if regime == "proven" else float(b)


def queries(b: int, regime: str) -> int:
    return math.ceil(LAMBDA / beta(b, regime))


def arities(D: int, a: int, mixed: bool) -> list[int]:
    if mixed:  # last round folds by the remainder
        return [a] * (D // a) + ([D % a] if D % a else [])
    return [a] * math.ceil(D / a)  # uniform arity; degree padded to k^rounds


def cost(D: int, a: int, b: int, regime: str = "proven", mixed: bool = False) -> dict:
    ar = arities(D, a, mixed)
    log_n = sum(ar) + b                       # padded degree + blow-up
    q = queries(b, regime)
    depths, s = [], log_n
    for ai in ar:
        depths.append(s - ai)
        s -= ai
    felts = sum(1 << ai for ai in ar)
    hashes = sum(depths)
    proof = q * (felts * FELT + hashes * HASH) + len(ar) * HASH + FELT
    verifier = q * (hashes + sum(math.ceil((1 << ai) * FELT / BLOCK) for ai in ar)
                    + sum((1 << ai) * ai * MUL for ai in ar))
    return {"q": q, "rounds": len(ar), "log_n": log_n, "proof_kib": proof / 1024,
            "verifier": verifier, "metric": proof / 1024 * verifier}


def sweep(D: int, regime: str = "proven", mixed: bool = False) -> dict:
    return {(a, b): cost(D, a, b, regime, mixed) for a in A_RANGE for b in B_RANGE}


def hull_excess(ys: list[float]) -> list[float]:
    """Distance of each point above the lower convex envelope of (index, y)."""
    out = []
    for i, y in enumerate(ys):
        env = y
        for j in range(i):
            for k in range(i + 1, len(ys)):
                env = min(env, ys[j] + (ys[k] - ys[j]) * (i - j) / (k - j))
        out.append(y - env)
    return out


def anomalies(table: dict) -> dict:
    """Points out of proportion along the k axis: log(metric) more than TAU above the lower
    convex envelope of the other folding factors at the same rate.  A cost built from smooth
    terms is (close to) convex in log k, so the envelope is the trend.
    Returns {a: number of rates at which a is an outlier}."""
    out: dict = {}
    for b in B_RANGE:
        ex = hull_excess([math.log(table[(a, b)]["metric"]) for a in A_RANGE])
        for a, e in zip(A_RANGE, ex):
            if e > TAU:
                out[a] = out.get(a, 0) + 1
    return out


def padding(D: int, a: int) -> int:
    return 2 ** (a * math.ceil(D / a) - D)


def simulate_proof(D: int, a: int, b: int, regime: str = "proven", mixed: bool = False,
                   seed: int = 1) -> dict:
    """Direct simulation: draw q query positions, walk them through the folds, and count the
    distinct Merkle leaves and the authentication nodes a multiproof must contain."""
    ar = arities(D, a, mixed)
    q = queries(b, regime)
    rng = random.Random(seed)
    log_n = sum(ar) + b
    xs = [rng.randrange(1 << log_n) for _ in range(q)]
    felts = hashes = 0
    s = log_n
    for ai in ar:
        n_cosets_log = s - ai
        leaves = {x % (1 << n_cosets_log) for x in xs}
        felts += len(leaves) * (1 << ai)
        anc = leaves
        for _ in range(n_cosets_log):
            hashes += len({c ^ 1 for c in anc} - anc)
            anc = {c >> 1 for c in anc}
        xs = [x % (1 << n_cosets_log) for x in xs]
        s = n_cosets_log
    proof = felts * FELT + hashes * HASH + len(ar) * HASH + FELT
    return {"proof_kib": proof / 1024}


def lower_bound(D: int, b: int, regime: str = "proven") -> float:
    """Continuous relaxation: k = 2^t with real t > 0 and fractional rounds D/t."""
    best = float("inf")
    for i in range(1, 801):
        t = i / 100
        r = D / t
        q = queries(b, regime)
        hashes = sum(D + b - t * (j + 1) for j in range(int(r))) + (r - int(r)) * b
        felts = r * 2 ** t
        proof = q * (felts * FELT + hashes * HASH)
        ver = q * (hashes + r * max(1.0, 2 ** t * FELT / BLOCK) + r * 2 ** t * t * MUL)
        best = min(best, proof / 1024 * ver)
    return best


def loop(D: int, verbose: bool = True) -> dict:
    say = print if verbose else (lambda *a, **k: None)
    res: dict = {"D": D}
    base = cost(D, 1, 1)
    say(f"Step 0  target: proof KiB x verifier work for degree 2^{D}, {LAMBDA} toy bits (proven regime)")
    say(f"Step 1  probe: baseline k=2, rate 1/2 -> q={base['q']}, proof {base['proof_kib']:.0f} KiB,"
        f" verifier {base['verifier']:.0f}, metric {base['metric']:.3g}")
    # Pre-gate 0: folding factor and rate are prover/verifier substrate; the soundness budget is
    # the security-bearing part and is held fixed (same LAMBDA, same regime) across the sweep.
    # Gate A: the habit-fixed parameter is 'one folding factor k for every round'.
    tab = sweep(D)
    best = min(tab, key=lambda ab: tab[ab]["metric"])
    res["best"] = best
    say(f"Step 3  swept k in {[1 << a for a in A_RANGE]} x rate in "
        f"{['1/%d' % (1 << b) for b in B_RANGE]}: best k={1 << best[0]}, rate 1/{1 << best[1]},"
        f" metric {tab[best]['metric']:.3g} ({base['metric'] / tab[best]['metric']:.1f}x vs baseline)")
    conj = sweep(D, "conjectured")
    cb = min(conj, key=lambda ab: conj[ab]["metric"])
    res["best_conj"] = cb
    say(f"        same sweep in the toy conjectured regime: best rate 1/{1 << cb[1]} (proven: 1/{1 << best[1]})"
        " -> the regime changes the optimum; never mix them in one comparison")
    # Step 4 (exact synthesis) is exhaustive here: the grid is the whole space.
    dips = anomalies(tab)
    res["outliers"] = sorted(dips)
    if not dips:
        say("Gate B  FAILED honestly: log(metric) is convex along k at every rate; no outlier ->"
            " record the negative result, go back to Step 2 (free another parameter)")
        res["gate_b"] = False
        return res
    res["gate_b"] = True
    say(f"Gate B  outliers (> {TAU:.2f} in log above the convex trend along k) at k ="
        f" {[1 << a for a in sorted(dips)]}, at {sorted(set(dips.values()))} of {len(B_RANGE)} rates"
        " -- worse out of proportion to their neighbours")
    # Step 5: hypotheses.  H0 is about the leaf itself (width k, independent of D and of the
    # folding schedule); H1 is about the schedule (uniform arity pads the degree when a does not divide D).
    padded = {a for a in A_RANGE if D % a}
    res["h1_ok"] = set(dips) <= padded
    say(f"Step 5  H0 'k={[1 << a for a in sorted(dips)]} is intrinsically too wide (k-element leaves dominate)';"
        f"  H1 'uniform arity pads d up to k^ceil(D/a)' -> padded k = {[1 << a for a in sorted(padded)]}"
        f" (factors { {1 << a: padding(D, a) for a in sorted(padded)} }): outliers within padded set:"
        f" {res['h1_ok']}")
    # Step 6: control experiments -- keep the surface feature of H0 (same k, same leaf width, same
    # rate), remove the property of H1 (padding).  The outlier must vanish iff H1 is the cause.
    mixed_tab = sweep(D, mixed=True)
    still = sorted(set(dips) & set(anomalies(mixed_tab)))
    Dc = next(x for x in range(D + 1, D + 30) if all(x % a == 0 for a in dips))
    ctrl2 = sorted(set(dips) & set(anomalies(sweep(Dc))))
    res["control_vanishes"] = not still and not ctrl2
    say(f"Step 6  control (i) same k, mixed arity (last round folds by the remainder): outliers left {still or 'none'};"
        f" control (ii) D={Dc}, where log2 k | D: outliers left {ctrl2 or 'none'}"
        f" -> {'H0 killed, H1 survives' if res['control_vanishes'] else 'H1 incomplete, back to Step 5'}")
    # Step 7: validate the closed-form model by direct simulation (multiproof de-duplication):
    # baseline vs candidate vs the outlier vs the outlier's control.
    a, b = best
    ao = max(dips, key=lambda x: dips[x])
    rows = [("baseline", 1, 1, False), ("candidate", a, b, False),
            ("outlier", ao, b, False), ("control", ao, b, True)]
    res["sim"] = {}
    for name, a_, b_, mx in rows:
        c = cost(D, a_, b_, mixed=mx)
        sm = simulate_proof(D, a_, b_, mixed=mx)["proof_kib"]
        res["sim"][name] = (c["proof_kib"], sm)
        say(f"Step 7  {name:9s} k={1 << a_:3d} rate 1/{1 << b_:2d} {'mixed  ' if mx else 'uniform'}:"
            f" closed form {c['proof_kib']:7.1f} KiB, simulated multiproof {sm:7.1f} KiB"
            f" ({(1 - sm / c['proof_kib']):.0%} saved by de-duplication); prover domain 2^{c['log_n']}")
    say("        the closed form over-counts shared Merkle nodes; the ranking must survive the simulation."
        " Price: lower rate cuts queries but multiplies the prover's domain -- report P, V, proof size together")
    # Step 8: generalise over the family of degrees + lower bound
    fam = {x: sorted(anomalies(sweep(x, mixed=True))) for x in range(16, 25)}
    res["mixed_family_outliers"] = {x: v for x, v in fam.items() if v}
    mb = min(mixed_tab, key=lambda ab: mixed_tab[ab]["metric"])
    lb = lower_bound(D, mb[1])
    res["gap"] = mixed_tab[mb]["metric"] / lb
    say(f"Step 8  mixed arity for D=16..24: outliers {res['mixed_family_outliers'] or 'none'};"
        f" best k={1 << mb[0]}, rate 1/{1 << mb[1]}, within {res['gap']:.2f}x of the continuous-relaxation bound")
    return res


def selftest() -> int:
    r = loop(20, verbose=False)
    assert r["gate_b"] and r["outliers"] == [6], r                    # k = 64, padded 16x
    assert r["h1_ok"] and r["control_vanishes"], r                    # controls kill H0
    for cf, sm in r["sim"].values():                                   # de-dup never increases size
        assert sm <= cf + 1e-9, r["sim"]
    assert r["sim"]["candidate"][1] < r["sim"]["baseline"][1]          # ranking survives simulation
    assert r["sim"]["control"][0] < r["sim"]["outlier"][0]
    assert r["mixed_family_outliers"] == {}, r["mixed_family_outliers"]
    assert 1.0 <= r["gap"] < 1.5, r["gap"]                             # bound is a bound, and close
    assert r["best_conj"][1] > r["best"][1]                            # regime moves the optimal rate
    assert loop(22, verbose=False)["gate_b"] is False                  # honest Gate-B failure
    # independent re-check of the closed form on one point by hand
    c = cost(4, 2, 1)                                                  # 2 rounds of k=4, log_n = 5
    assert c["rounds"] == 2 and c["log_n"] == 5
    assert c["proof_kib"] * 1024 == c["q"] * (8 * FELT + (3 + 1) * HASH) + 2 * HASH + FELT
    print("selftest: OK")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--D", type=int, default=20, help="log2 of the degree bound (8..24)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if not 8 <= args.D <= 24:
        ap.error("D must be within 8..24")
    loop(args.D)
