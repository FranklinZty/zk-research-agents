#!/usr/bin/env python3
# TOY: not secure. Operation-count model with toy unit costs; for predicting before implementing only.
"""prover_cost_model.py -- predict per-phase prover/verifier operation counts, then compare with a measured log.

    python3 prover_cost_model.py --n 1048576 --field bn254 --piop plonk --pcs kzg
    python3 prover_cost_model.py --n 1048576 --field goldilocks --piop plonk --pcs fri --queries 80
    python3 prover_cost_model.py --n 1048576 --field bn254 --piop sumcheck --pcs kzg --demo-log > m.log
    python3 prover_cost_model.py --n 1048576 --field bn254 --piop sumcheck --pcs kzg --compare m.log
    python3 prover_cost_model.py --selftest

Model. The statement has n constraints (rows), padded to N = 2^ceil(log2 n). The PIOP is either
  plonk     univariate quotient over a blow-up domain (3 wire columns, 1 permutation column, quotient in 3 pieces);
  sumcheck  multilinear, Spartan-style: one committed witness MLE, two sum-checks over v = log2 N variables.
The PCS is either
  kzg       MSMs over the scalar field of a pairing group (the field must be that group's order, [Thaler §19.3.1, Field choice]);
  fri       low-degree extension by NTT at rate rho, Merkle trees over the extension, folding and q queries.
Each phase reports: MSM count and points, NTT count and butterflies, field multiplications, hashes, sum-check
rounds and term evaluations, pairings, and an estimate of memory traffic. Formulas used:
  * MSM of size N with b-bit scalars, Pippenger window c ~ log2 N - 2: about (b/c)(N + 2^(c+1)) group additions,
    i.e. O(N b / log N) ([Thaler §19.3.2, Relative Efficiency of Different Operations]);
  * radix-2 NTT of size N: (N/2) log2 N butterflies (checked against a real NTT in --selftest);
  * sum-check over v variables, degree d: sum_j (d+1) 2^(v-j) term evaluations ([Thaler §4.1, The Sum-Check Protocol],
    checked against a real sum-check prover in --selftest);
  * FRI: an LDE of size N/rho dominates the prover ([Thaler §10.4.3, Costs of FRI]); Merkle opening proofs counted
    without and with path pruning, the pruned size being |copath(I) minus path(I)| hash values
    ([CY24 §Path pruning, lemma:path-pruning-is-copaths-minus-paths, lemma:path-pruning-lower-and-upper]).
Predicted time = sum of ops x unit cost; the unit costs below are TOY placeholders -- replace them with
microbenchmarks of the target machine (one EVIDENCE row each) before comparing with real measurements.

Comparison. A measured log has one "phase: value ms" line per phase (the convention of skills/bench-protocol).
Phases whose measured/predicted ratio is outside [1/t, t] (default t = 1.5) are flagged: by bench-protocol rule 10
they must be explained before any number is published.

Op counting reuses lib/cryptomath/cryptomath/costmodel (Counter / count; nested counters per phase).
Pure Python 3.10+; no third-party dependencies.
"""
from __future__ import annotations

import argparse
import importlib.util
import math
import os
import random
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def _load_costmodel():
    """cryptomath.costmodel's Counter/count. The package __init__ also imports the sympy-based formulas; the
    counter module itself is stdlib-only, so without sympy it is loaded directly from its file."""
    lib = os.path.join(ROOT, "lib", "cryptomath")
    if lib not in sys.path:
        sys.path.insert(0, lib)
    try:
        from cryptomath.costmodel import Counter, count  # type: ignore
        return Counter, count
    except ImportError:
        path = os.path.join(lib, "cryptomath", "costmodel", "counter.py")
        spec = importlib.util.spec_from_file_location("_costmodel_counter", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.Counter, mod.count


Counter, count = _load_costmodel()

# op names (strings, as costmodel expects)
MSM, MSM_PTS, GADD = "msm", "msm_points", "group_add"
NTT, BFLY = "ntt", "ntt_butterfly"
FMUL, HASH, PAIR = "field_mult", "hash", "pairing"
SC_ROUND, SC_TERM = "sumcheck_round", "sumcheck_term"
MEM = "mem_bytes"

# field: bits of an element, extension degree used for challenges/FRI folding, 2-adicity, pairing group or None
FIELDS = {
    "bn254": {"bits": 254, "ext": 1, "two_adicity": 28, "group": "bn254", "base_bits": 254},
    "bls12-381": {"bits": 255, "ext": 1, "two_adicity": 32, "group": "bls12-381", "base_bits": 381},
    "goldilocks": {"bits": 64, "ext": 2, "two_adicity": 32, "group": None},
    "babybear": {"bits": 31, "ext": 4, "two_adicity": 27, "group": None},
}

# TOY unit costs in nanoseconds per op (placeholders; calibrate with microbenchmarks before comparing)
def unit_costs(field: str) -> dict:
    f = FIELDS[field]
    fm = {254: 30.0, 255: 30.0, 64: 3.0, 31: 1.5}[f["bits"]]
    base = {254: 30.0, 381: 70.0}.get(f.get("base_bits", 0), 0.0)
    return {FMUL: fm, BFLY: 1.3 * fm, GADD: 12 * base, PAIR: 1.0e6, HASH: 250.0, SC_TERM: 2 * fm,
            MEM: 0.05, MSM: 0.0, MSM_PTS: 0.0, NTT: 0.0, SC_ROUND: 0.0}


# ------------------------------------------------------------ primitives ---

def elem_bytes(field: str, ext: bool = False) -> int:
    f = FIELDS[field]
    return math.ceil(f["bits"] / 8) * (f["ext"] if ext else 1)


def msm(N: int, field: str) -> None:
    b = FIELDS[field]["bits"]
    c = max(1, int(math.log2(N)) - 2)
    count(MSM)
    count(MSM_PTS, N)
    count(GADD, math.ceil(b / c) * (N + 2 ** (c + 1)))
    count(MEM, N * (elem_bytes(field) + 2 * math.ceil(FIELDS[field]["base_bits"] / 8)))


def ntt(N: int, field: str) -> None:
    if N.bit_length() - 1 > FIELDS[field]["two_adicity"]:
        raise ValueError(f"NTT of size {N} exceeds the 2-adicity of {field}")
    lg = N.bit_length() - 1
    count(NTT)
    count(BFLY, (N // 2) * lg)
    count(MEM, 2 * N * lg * elem_bytes(field))      # one read + write per pass, no cache blocking


def merkle_commit(leaves: int, leaf_elems: int, field: str) -> None:
    count(HASH, leaves + (leaves - 1))              # leaf hashes + inner nodes
    count(MEM, leaves * leaf_elems * elem_bytes(field))


def sumcheck_prover(v: int, d: int, field: str, factor: int = 1) -> None:
    """Term evaluations of the sum-check prover with oracle access to g ([Thaler §4.1, The Sum-Check Protocol])."""
    count(SC_ROUND, v)
    count(SC_TERM, factor * sum((d + 1) * 2 ** (v - j) for j in range(1, v + 1)))
    count(MEM, factor * 2 ** v * elem_bytes(field, ext=True) * 2)


# ----------------------------------------------------------------- model ---

def check_combo(field: str, pcs: str) -> None:
    if pcs == "kzg" and FIELDS[field]["group"] is None:
        raise ValueError(f"KZG needs the scalar field of a pairing group; {field} is not one "
                         "([Thaler §19.3.1, Field choice])")


def predict(n: int, field: str, piop: str, pcs: str, rho: int = 4, queries: int = 80,
            hash_bytes: int = 32, seed: int = 0) -> dict:
    """Return {"prover": {phase: ops}, "verifier": ops, "proof_bytes": {...}, "N": N}."""
    check_combo(field, pcs)
    N = 1 << max(1, (n - 1).bit_length())
    v = N.bit_length() - 1
    phases: dict = {}

    def commit(cols: int, size: int):
        for _ in range(cols):
            if pcs == "kzg":
                msm(size, field)
            else:
                ntt(size, field)                    # interpolate (iNTT) ...
                ntt(size * rho, field)              # ... and extend to the rate-rho domain
        if pcs == "fri":
            merkle_commit(size * rho, cols, field)  # one tree per commit round, columns batched in leaves

    with Counter("total") as total:
        if piop == "plonk":
            with Counter("commit") as c:
                commit(3, N)
            phases["commit"] = c
            with Counter("permutation") as c:
                count(FMUL, 8 * N)                  # grand-product numerators/denominators + batch inversion
                commit(1, N)
            phases["permutation"] = c
            with Counter("quotient") as c:
                for _ in range(4 if pcs == "kzg" else 0):
                    ntt(N, field)                   # KZG commits in Lagrange basis: interpolate for the quotient
                for _ in range(8):
                    ntt(4 * N, field)               # wires, z, selectors on the 4N coset
                count(FMUL, 20 * 4 * N)             # constraint evaluation per coset point
                ntt(4 * N, field)                   # quotient back to coefficients
                commit(3, N)
            phases["quotient"] = c
            with Counter("open") as c:
                count(FMUL, 10 * N)                 # evaluations, linearisation
                if pcs == "kzg":
                    msm(N, field); msm(N, field)    # two opening quotients
                else:
                    count(FMUL, 2 * rho * N)        # DEEP quotients + folding, geometric sum
                    layer = N * rho // 2
                    while layer >= 2:
                        merkle_commit(layer, 2, field)
                        layer //= 2
            phases["open"] = c
        elif piop == "sumcheck":
            with Counter("commit") as c:
                commit(1, N)
            phases["commit"] = c
            with Counter("sumcheck") as c:
                count(FMUL, 3 * 3 * N)              # Az, Bz, Cz from ~3N nonzeros
                sumcheck_prover(v, 3, field)        # outer: eq * (Az*Bz - Cz), degree 3
                sumcheck_prover(v, 2, field, factor=3)  # inner: three matrix terms, degree 2
            phases["sumcheck"] = c
            with Counter("open") as c:
                if pcs == "kzg":
                    size = N // 2
                    while size >= 1:                # multilinear KZG: v quotients of halving size
                        msm(size, field)
                        size //= 2
                else:
                    count(FMUL, 2 * rho * N)
                    layer = N * rho // 2
                    while layer >= 2:
                        merkle_commit(layer, 2, field)
                        layer //= 2
            phases["open"] = c
        else:
            raise ValueError(piop)

    with Counter("verifier") as ver:
        count(HASH, 4 * (v + 6))                    # transcript
        if piop == "sumcheck":
            count(FMUL, 2 * v * 4)
        else:
            count(FMUL, 60 + 2 * v)
        if pcs == "kzg":
            count(PAIR, 2 if piop == "plonk" else v + 1)
            count(GADD, 18 * 256 * 2)               # ~18 scalar multiplications (double-and-add)
        else:
            depth = (N * rho).bit_length() - 1
            count(HASH, queries * sum(range(1, depth + 1)))
            count(FMUL, queries * depth * 4)

    proof = proof_size(N, piop, pcs, rho, queries, field, hash_bytes, seed)
    return {"N": N, "v": v, "prover": {k: c.as_dict() for k, c in phases.items()},
            "prover_total": total.as_dict(), "verifier": ver.as_dict(), "proof_bytes": proof}


# ---------------------------------------------------- Merkle path pruning ---

def pruned_nodes(depth: int, indices: set[int]) -> int:
    """|copath(I) \\ path(I)| over all layers: the hash values a pruned multi-opening must contain
    ([CY24 §Path pruning, lemma:path-pruning-is-copaths-minus-paths]). Leaves are 0-based in [0, 2^depth)."""
    level, total = set(indices), 0
    for _ in range(depth):
        siblings = {i ^ 1 for i in level}
        total += len(siblings - level)
        level = {i >> 1 for i in level}
    return total


def proof_size(N, piop, pcs, rho, queries, field, hash_bytes, seed) -> dict:
    eb, ebx = elem_bytes(field), elem_bytes(field, ext=True)
    if pcs == "kzg":
        g1 = 32 if field == "bn254" else 48     # compressed G1 point
        commits = 9 if piop == "plonk" else 1 + (N.bit_length() - 1)
        return {"unpruned": commits * g1 + 6 * eb, "pruned": commits * g1 + 6 * eb}
    rng = random.Random(seed)
    unpruned = pruned = 0
    size = N * rho
    while size >= 2:
        depth = size.bit_length() - 1
        idx = {rng.randrange(size) for _ in range(queries)}
        unpruned += len(idx) * depth * hash_bytes
        pruned += pruned_nodes(depth, idx) * hash_bytes
        size //= 2
    answers = queries * 2 * ebx * ((N * rho).bit_length() - 1)
    return {"unpruned": unpruned + answers, "pruned": pruned + answers}


# ------------------------------------------------------- time and compare ---

def predicted_ms(pred: dict, field: str, units: dict | None = None) -> dict:
    u = units or unit_costs(field)
    return {ph: sum(u.get(op, 0.0) * n for op, n in ops.items()) / 1e6 for ph, ops in pred["prover"].items()}


LINE_RE = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*:\s*([0-9.eE+\-]+)\s*ms\s*$")


def parse_log(text: str) -> dict:
    return {m.group(1): float(m.group(2)) for m in map(LINE_RE.match, text.splitlines()) if m}


def compare(pred_ms: dict, measured: dict, threshold: float = 1.5) -> list[dict]:
    rows = []
    for ph, p in pred_ms.items():
        m = measured.get(ph)
        ratio = (m / p) if (m is not None and p > 0) else None
        flag = m is None or ratio > threshold or ratio < 1 / threshold
        rows.append({"phase": ph, "predicted_ms": p, "measured_ms": m, "ratio": ratio,
                     "flag": "MISSING" if m is None else ("EXPLAIN" if flag else "ok")})
    for ph in measured.keys() - pred_ms.keys():
        rows.append({"phase": ph, "predicted_ms": None, "measured_ms": measured[ph], "ratio": None,
                     "flag": "UNMODELLED"})
    return rows


def synthetic_log(pred_ms: dict, skew: dict | None = None) -> str:
    """A made-up 'measured' log: prediction times a per-phase factor (default: one phase 3.2x off)."""
    skew = skew if skew is not None else {"commit": 1.1, "permutation": 0.95, "quotient": 3.2,
                                          "sumcheck": 3.2, "open": 0.9}
    return "\n".join(f"{ph}: {t * skew.get(ph, 1.0):.3f} ms" for ph, t in pred_ms.items())


def render(pred: dict, field: str, rows: list[dict] | None = None) -> str:
    out = [f"N = {pred['N']} (v = {pred['v']}), field {field}",
           "| phase | MSMs | MSM points | group adds | NTTs | butterflies | field mults | hashes | sum-check rounds | sum-check terms | memory traffic MB | predicted ms (toy units) |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    pm = predicted_ms(pred, field)
    for ph, ops in pred["prover"].items():
        out.append(f"| {ph} | {ops.get(MSM, 0)} | {ops.get(MSM_PTS, 0)} | {ops.get(GADD, 0):.3g} | {ops.get(NTT, 0)} | "
                   f"{ops.get(BFLY, 0):.3g} | {ops.get(FMUL, 0):.3g} | {ops.get(HASH, 0):.3g} | {ops.get(SC_ROUND, 0)} | "
                   f"{ops.get(SC_TERM, 0):.3g} | {ops.get(MEM, 0) / 2**20:.1f} | {pm[ph]:.1f} |")
    out.append(f"verifier: {pred['verifier']}")
    out.append(f"proof bytes: unpruned {pred['proof_bytes']['unpruned']}, with path pruning {pred['proof_bytes']['pruned']}")
    if rows:
        out += ["", "| phase | predicted ms | measured ms | measured/predicted | flag |", "|---|---|---|---|---|"]
        for r in rows:
            f = lambda x: "-" if x is None else f"{x:.2f}"
            out.append(f"| {r['phase']} | {f(r['predicted_ms'])} | {f(r['measured_ms'])} | {f(r['ratio'])} | {r['flag']} |")
        if any(r["flag"] != "ok" for r in rows):
            out.append("Flagged phases must be explained before publishing (skills/bench-protocol rule 10): "
                       "uncalibrated unit costs, a phase timed with extra work (witness generation, serialization), "
                       "memory-bound kernels, a different field / extension / rate / query count than modelled, "
                       "a missing or extra commitment round.")
    return "\n".join(out)


# -------------------------------------------------------------- selftest ---

P97 = 97   # 97 - 1 = 2^5 * 3: NTTs up to size 32


def _ntt97(a: list[int], root: int) -> list[int]:
    """Iterative radix-2 NTT over F_97 that records one butterfly per inner step via costmodel.count."""
    n = len(a)
    a = a[:]
    j = 0
    for i in range(1, n):                           # bit reversal
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j |= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    length = 2
    while length <= n:
        w = pow(root, n // length, P97)
        for s in range(0, n, length):
            wk = 1
            for k in range(length // 2):
                u, t = a[s + k], a[s + k + length // 2] * wk % P97
                a[s + k], a[s + k + length // 2] = (u + t) % P97, (u - t) % P97
                count(BFLY)
                wk = wk * w % P97
        length *= 2
    return a


def _sumcheck97(tables: list[list[int]], rng) -> bool:
    """Honest sum-check prover/verifier for g = prod of d multilinear tables over F_97 ([Thaler §4.1, The Sum-Check Protocol]);
    each evaluation of g at a partially bound point is one counted term."""
    d, v = len(tables), len(tables[0]).bit_length() - 1
    claim = sum(math.prod(t[i] for t in tables) for i in range(2 ** v)) % P97
    cur = [t[:] for t in tables]
    for j in range(1, v + 1):
        half = len(cur[0]) // 2
        evals = []
        for x in range(d + 1):                      # s_j(x) for x = 0..d
            s = 0
            for i in range(half):
                term = 1
                for t in cur:
                    term = term * ((t[i] * (1 - x) + t[i + half] * x) % P97) % P97
                count(SC_TERM)
                s += term
            evals.append(s % P97)
        if (evals[0] + evals[1]) % P97 != claim:
            return False
        r = rng.randrange(P97)
        # interpolate s_j at r from evals at 0..d (Lagrange)
        claim = 0
        for a_, ya in enumerate(evals):
            num = den = 1
            for b_ in range(d + 1):
                if b_ != a_:
                    num, den = num * (r - b_) % P97, den * (a_ - b_) % P97
            claim = (claim + ya * num * pow(den, P97 - 2, P97)) % P97
        cur = [[(t[i] * (1 - r) + t[i + half] * r) % P97 for i in range(half)] for t in cur]
    final = math.prod(t[0] for t in cur) % P97
    return final == claim


def selftest() -> int:
    rng = random.Random(7)
    # 1. NTT butterflies: real NTT over F_97 vs (N/2) log2 N, and correctness vs the naive DFT
    g = 5                                           # generator of F_97^*
    for N in (2, 4, 8, 16, 32):
        root = pow(g, (P97 - 1) // N, P97)
        a = [rng.randrange(P97) for _ in range(N)]
        with Counter("ntt") as c:
            out = _ntt97(a, root)
        naive = [sum(a[j] * pow(root, i * j, P97) for j in range(N)) % P97 for i in range(N)]
        assert out == naive and c[BFLY] == (N // 2) * (N.bit_length() - 1), (N, c[BFLY])
    # 2. sum-check terms: real prover vs sum_j (d+1) 2^(v-j)
    for v, d in ((3, 2), (4, 3), (5, 1)):
        tables = [[rng.randrange(P97) for _ in range(2 ** v)] for _ in range(d)]
        with Counter("sc") as c:
            ok = _sumcheck97(tables, rng)
        with Counter("model") as m:
            sumcheck_prover(v, d, "bn254")
        assert ok and c[SC_TERM] == m[SC_TERM], (v, d, c[SC_TERM], m[SC_TERM])
    # 3. path pruning within the CY24 bounds; exact lower bound for a full subtree
    for depth in (4, 6, 8):
        for logI in range(0, depth + 1):
            I = set(rng.sample(range(2 ** depth), 2 ** logI))
            s = pruned_nodes(depth, I)
            assert depth - logI <= s <= (2 ** logI) * (depth - logI), (depth, logI, s)
        sub = set(range(4))
        assert pruned_nodes(depth, sub) == depth - 2
    # 4. combinations: KZG needs a pairing field; NTT size limited by 2-adicity
    try:
        predict(2 ** 10, "goldilocks", "plonk", "kzg")
        raise AssertionError("KZG over goldilocks accepted")
    except ValueError:
        pass
    try:
        predict(2 ** 27, "babybear", "plonk", "fri")
        raise AssertionError("NTT beyond 2-adicity accepted")
    except ValueError:
        pass
    # 5. nesting: phase counters add up to the total; MSM count of plonk+kzg is 3 + 1 + 3 + 2 = 9
    p = predict(2 ** 12, "bn254", "plonk", "kzg")
    for op, tot in p["prover_total"].items():
        assert tot == sum(ph.get(op, 0) for ph in p["prover"].values()), op
    assert p["prover_total"][MSM] == 9 and p["prover_total"][MSM_PTS] == 9 * 2 ** 12
    s = predict(2 ** 12, "bn254", "sumcheck", "kzg")
    assert s["prover"]["open"][MSM_PTS] == 2 ** 12 - 1 and s["prover"]["sumcheck"][SC_ROUND] == 24
    f = predict(2 ** 12, "goldilocks", "plonk", "fri", queries=40)
    assert f["proof_bytes"]["pruned"] < f["proof_bytes"]["unpruned"] and MSM not in f["prover_total"]
    # 6. comparison: the skewed phase is flagged, the others are not
    pm = predicted_ms(p, "bn254")
    rows = compare(pm, parse_log(synthetic_log(pm)))
    flags = {r["phase"]: r["flag"] for r in rows}
    assert flags == {"commit": "ok", "permutation": "ok", "quotient": "EXPLAIN", "open": "ok"}, flags
    rows = compare(pm, {**parse_log(synthetic_log(pm)), "witness": 5.0})
    assert any(r["flag"] == "UNMODELLED" for r in rows)
    assert parse_log("commit: 1.5 ms\njunk\nopen : 2e3 ms") == {"commit": 1.5, "open": 2000.0}
    print("selftest: OK")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=2 ** 20, help="constraints / rows")
    ap.add_argument("--field", choices=sorted(FIELDS), default="bn254")
    ap.add_argument("--piop", choices=["plonk", "sumcheck"], default="plonk")
    ap.add_argument("--pcs", choices=["kzg", "fri"], default="kzg")
    ap.add_argument("--rho", type=int, default=4, help="inverse FRI rate")
    ap.add_argument("--queries", type=int, default=80, help="FRI queries (take it from skills/soundness-budget)")
    ap.add_argument("--compare", metavar="LOG", help="measured log, one 'phase: value ms' line per phase")
    ap.add_argument("--threshold", type=float, default=1.5)
    ap.add_argument("--demo-log", action="store_true", help="print a synthetic 'measured' log and exit")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    pred = predict(a.n, a.field, a.piop, a.pcs, a.rho, a.queries)
    if a.demo_log:
        print(synthetic_log(predicted_ms(pred, a.field)))
        return 0
    rows = None
    if a.compare:
        with open(a.compare, encoding="utf-8") as fh:
            rows = compare(predicted_ms(pred, a.field), parse_log(fh.read()), a.threshold)
    print(render(pred, a.field, rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
