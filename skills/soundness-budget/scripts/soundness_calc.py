#!/usr/bin/env python3
"""soundness_calc.py -- itemised concrete-soundness budget for a ZK argument.

    python3 soundness_calc.py --example toy-bcs                 # worked toy budget, worst-case level
    python3 soundness_calc.py --example toy-bcs --level average-case --evidence
    python3 soundness_calc.py --config budget.json [--evidence]
    python3 soundness_calc.py --selftest

Every term is an upper bound eps_i(t) on the probability that an adversary making at most t oracle queries
breaks one ingredient; the budget is the union bound eps(t) = sum_i eps_i(t). From eps(t) we read off a security
level with one of the two definitions of [CY24 §Security levels, section:security-levels]:

    worst-case   s bits  iff  eps(t) <= 2^-s        for every t in [1, 2^s]
    average-case s bits  iff  t / eps(t) >= 2^s     for every t in [1, 2^s]

The output always names the definition used and whether every term is proven or some term is conjectured.

Sources. Hash-based terms follow the error bounds of CY24 (pure random oracle model, oracle output size lam,
query bound t); each function's docstring names the label. Algebraic terms (Schwartz-Zippel, sum-check,
batching) follow Thaler. Reed-Solomon proximity (FRI and successors) is "source: other": the formulas here are
the ones stated in [Thaler §10.4.4, Details of FRI: Better Reed-Solomon Proximity Proofs via Interaction] for
the proven (Johnson) regime, and a clearly labelled conjectured regime. Computational assumptions (curve
discrete log, pairings) are not functions of t; they enter as a cap in bits, by convention, not by theorem.

All arithmetic is exact (fractions.Fraction over Python integers); bits are -log2 of the exact value.
Pure Python 3.10+, no dependencies.
"""
from __future__ import annotations

import argparse
import datetime
import json
import math
import os
import subprocess
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from math import comb
from typing import Callable

F = Fraction


def bits(eps: Fraction) -> float:
    """-log2(eps) for an exact positive rational (inf for 0)."""
    if eps <= 0:
        return math.inf
    return math.log2(eps.denominator) - math.log2(eps.numerator)


def _depth(ell: int) -> int:
    """Merkle tree depth for ell leaves (ell rounded up to a power of two)."""
    return max(0, (ell - 1).bit_length())


# ------------------------------------------------------------- CY24: random oracle and Merkle trees ---

def rom_collision(lam: int, t: int) -> Fraction:
    """Probability that t queries to a lam-bit random oracle contain a collision: (t-1)t / 2^(lam+1).

    [CY24 §Collision resistance, lemma:rom-cr]
    """
    return F((t - 1) * t, 2 ** (lam + 1))


def merkle_binding(lam: int, t: int, ell: int) -> Fraction:
    """Merkle binding error t^2 / 2^(lam+1), stated for t >= 2(d+1)^2 with d = log2(ell).

    For smaller t we return the value at the threshold (the error is non-decreasing in t), which is conservative.
    [CY24 §Binding, lemma:mt-binding]
    """
    t = max(t, 2 * (_depth(ell) + 1) ** 2)
    return F(t * t, 2 ** (lam + 1))


def merkle_extraction(lam: int, t: int, ell: int) -> Fraction:
    """Single-commitment Merkle extraction error (t-1)t / 2^(lam+1) + 2(d+1)ell / 2^lam.

    It is at most t^2 / 2^(lam+1) once t >= 4(d+1)ell.  [CY24 §Extractability, lemma:mt-extractability]
    """
    d = _depth(ell)
    return F((t - 1) * t, 2 ** (lam + 1)) + F(2 * (d + 1) * ell, 2 ** lam)


def merkle_multi_extraction(lam: int, t: int, ell: int, commitments: int) -> Fraction:
    """Extraction error for `commitments` adaptively produced Merkle commitments of ell leaves:
    3/2 (t-1)t / 2^lam + 2(d+1)ell / 2^lam + (K-1)t / 2^lam  with K = commitments.

    [CY24 §Extractability, lemma:mt-multi-extractability]
    """
    d = _depth(ell)
    return F(3 * (t - 1) * t, 2 ** (lam + 1)) + F(2 * (d + 1) * ell, 2 ** lam) + F((commitments - 1) * t, 2 ** lam)


def merkle_multi_config_extraction(lam: int, t: int, ells: list[int], commitments: int) -> Fraction:
    """Same, for trees of several sizes ell_1..ell_k (one per IOP round): the single-size bound with ell replaced
    by sum(ells) and d by the largest depth.  [CY24 §Extractability, lemma:mt-multi-configuration-multi-extractability]
    """
    d = max(_depth(e) for e in ells)
    return F(3 * (t - 1) * t, 2 ** (lam + 1)) + F(2 * (d + 1) * sum(ells), 2 ** lam) + F((commitments - 1) * t, 2 ** lam)


def hash_chain_term(lam: int, t: int) -> Fraction:
    """Extra error of the hash-chain variant of multi-round Fiat-Shamir: t^2 / 2^lam.
    The variant also needs every verifier challenge to carry at least lam bits.

    [CY24 §Soundness, theorem:hashchain-fs-for-public-coin-ip]
    """
    return F(t * t, 2 ** lam)


# ------------------------------------------------------------- CY24: from interactive to non-interactive ---

def fs_sigma(t: int, eps_sp: Fraction) -> Fraction:
    """Fiat-Shamir for a Sigma protocol with soundness error eps_sp: (t+1) eps_sp.

    [CY24 §Adaptive soundness, theorem:narg-from-sp-adaptive-soundness]
    """
    return (t + 1) * F(eps_sp)


def sr_from_standard(t: int, k: int, eps_ip: Fraction) -> Fraction:
    """Generic upper bound on state-restoration soundness of a k-round public-coin IP from its soundness error:
    C(t+k, k) eps_ip. Exponential in k: use RBR or special soundness instead whenever possible.

    [CY24 §State restoration, lemma:ip-sr-vs-standard]
    """
    return comb(t + k, k) * F(eps_ip)


def sr_lower_bound(t: int, k: int, eps_ip: Fraction) -> Fraction:
    """Matching lower bound: a universal state-restoration attack achieves floor(t/k) eps - C(floor(t/k), 2) eps^2.

    [CY24 §State restoration, lemma:ip-sr-vs-standard]
    """
    m = t // k
    return m * F(eps_ip) - comb(m, 2) * F(eps_ip) ** 2


def sr_from_rbr(t: int, k: int, eps_rbr: Fraction) -> Fraction:
    """State-restoration soundness from round-by-round soundness error eps_rbr: (t + k) eps_rbr.

    [CY24 §RBR soundness implies SR soundness, theorem:rbr-soundness-to-sr-soundness]
    """
    return (t + k) * F(eps_rbr)


def sr_knowledge_from_special_soundness(t: int, arities: list[int], challenge_sizes: list[int]) -> Fraction:
    """State-restoration knowledge error of a public-coin IP with special soundness of arities a_i over challenge
    sets of sizes |C_i|: (t+1) (1 - prod_i (1 - (a_i - 1)/|C_i|)).

    [CY24 §State-restoration knowledge soundness for IPs, theorem:ss-to-sr-knowledge-soundness-for-ip]
    """
    keep = F(1)
    for a, c in zip(arities, challenge_sizes, strict=True):
        keep *= 1 - F(a - 1, c)
    return (t + 1) * (1 - keep)


def kilian(lam: int, t: int, eps_pcp: Fraction, ell: int) -> Fraction:
    """Kilian interactive argument: eps_pcp + Merkle extraction error.

    [CY24 §Adaptive soundness, theorem:kilian-adaptive-soundness]
    """
    return F(eps_pcp) + merkle_extraction(lam, t, ell)


def micali(lam: int, t: int, eps_pcp: Fraction, ell: int) -> Fraction:
    """Micali: (t+1) eps_pcp + Merkle multi-extraction error with K = t+1 commitments
    (at most (t+1) eps_pcp + 2.5 t^2 / 2^lam once t >= 2(log ell + 1) ell).

    [CY24 §Soundness, theorem:micali-soundness]
    """
    return (t + 1) * F(eps_pcp) + merkle_multi_extraction(lam, t, ell, t + 1)


def micali_simplified(lam: int, t: int, eps_pcp: Fraction) -> Fraction:
    """(t+1) eps_pcp + 2.5 t^2 / 2^lam.  [CY24 §Soundness, theorem:micali-soundness]"""
    return (t + 1) * F(eps_pcp) + F(5 * t * t, 2 ** (lam + 1))


def bcs(lam: int, t: int, eps_sr: Fraction, ells: list[int]) -> Fraction:
    """BCS: IOP state-restoration error + Merkle multi-configuration extraction (K = t+1) + hash-chain term
    (at most eps_sr + 3.5 t^2 / 2^lam once t >= 2(log ell + 1) ell). eps_sr is the IOP's SR soundness error
    evaluated at budget t (use sr_from_rbr for an RBR-sound IOP).

    [CY24 §Soundness, theorem:bcs-soundness]
    """
    return F(eps_sr) + merkle_multi_config_extraction(lam, t, ells, t + 1) + hash_chain_term(lam, t)


def bcs_simplified(lam: int, t: int, eps_sr: Fraction) -> Fraction:
    """eps_sr + 3.5 t^2 / 2^lam.  [CY24 §Soundness, theorem:bcs-soundness]"""
    return F(eps_sr) + F(7 * t * t, 2 ** (lam + 1))


def basic_commitment_binding(lam: int, t: int) -> Fraction:
    """Hash commitment binding (and extraction) error t^2 / 2^(lam+1).  [CY24 §Binding, lemma:cm-binding]"""
    return F(t * t, 2 ** (lam + 1))


def basic_commitment_hiding(salt: int, t: int) -> Fraction:
    """Hash commitment hiding error t / 2^salt (finite t).  [CY24 §Hiding, lemma:cm-hiding]"""
    return F(t, 2 ** salt)


def fs_zk_salt_term(salt: int, t: int) -> Fraction:
    """Salt term of the ZK error of (hash-chain) Fiat-Shamir: t / 2^salt, added to the IP's HVZK error.

    [CY24 §Zero knowledge, theorem:hashchain-fs-zero-knowledge]
    """
    return F(t, 2 ** salt)


def merkle_hiding(lam: int, salt: int, t: int, ell: int, opened: int) -> Fraction:
    """Merkle hiding error for `opened` revealed leaves of ell: opened*ell*t/2^salt + opened*ell*t/2^(2 lam).

    [CY24 §Hiding, lemma:mt-privacy]
    """
    return F(opened * ell * t, 2 ** salt) + F(opened * ell * t, 2 ** (2 * lam))


# ------------------------------------------------------------- Thaler: algebraic (statistical) terms ---

def schwartz_zippel(degree: int, set_size: int) -> Fraction:
    """A nonzero polynomial of total degree <= degree vanishes at a uniform point of S^m w.p. <= degree/|S|.
    Use |S| = size of the field the challenge is *sampled* from (extension field if challenges live there).

    [Thaler §3.4, Schwartz-Zippel Lemma]
    """
    return F(degree, set_size)


def sumcheck(variables: int, degree: int, field_size: int) -> Fraction:
    """Interactive soundness error of sum-check for a v-variate polynomial of individual degree d: v d / |F|.
    Its round-by-round error is d / |F| per round (feed that to sr_from_rbr for the FS-compiled version).

    [Thaler §4.1, The Sum-Check Protocol]
    """
    return F(variables * degree, field_size)


def batching(claims: int, field_size: int) -> Fraction:
    """Random linear combination of m claims with powers of one challenge: (m-1)/|F| (Schwartz-Zippel on a
    univariate polynomial of degree m-1). With m independent challenges it is 1/|F|.

    [Thaler §3.4, Schwartz-Zippel Lemma]
    """
    return F(claims - 1, field_size)


# ------------------------------------------------------------- source: other -- Reed-Solomon proximity ---

def fri_johnson(rate: Fraction, eta: Fraction, delta: Fraction, degree: int, field_size: int,
                queries: int) -> Fraction:
    """PROVEN regime. FRI soundness eps1 + eps2 with eps1 = (d0+1)^2 / ((2 eta)^7 |F|) and eps2 = (1-delta)^l,
    valid for 0 < eta < sqrt(rho)/20 and 0 < delta < 1 - sqrt(rho) - eta.
    This is the interactive IOPP error; for Fiat-Shamir use its round-by-round analysis.

    [Thaler §10.4.4, Details of FRI: Better Reed-Solomon Proximity Proofs via Interaction];
    source: other, Ben-Sasson-Carmon-Ishai-Kopparty-Saraf, ePrint 2020/654 (theorem quoted in Thaler);
    FS/RBR treatment: source: other, Block et al., ePrint 2023/1071.
    """
    rate, eta, delta = F(rate), F(eta), F(delta)
    if not (0 < eta and eta * eta * 400 < rate):
        raise ValueError("eta must satisfy 0 < eta < sqrt(rho)/20")
    # delta < 1 - sqrt(rho) - eta  <=>  (1 - eta - delta)^2 > rho  with 1 - eta - delta > 0
    if not (0 < delta and 1 - eta - delta > 0 and (1 - eta - delta) ** 2 > rate):
        raise ValueError("delta must lie in (0, 1 - sqrt(rho) - eta): outside the proven Johnson regime")
    eps1 = F((degree + 1) ** 2) / ((2 * eta) ** 7 * field_size)
    eps2 = (1 - delta) ** queries
    return eps1 + eps2


def fri_query_conjectured(rate: Fraction, eta: Fraction, queries: int) -> Fraction:
    """CONJECTURED regime (up to list-decoding capacity): query-phase term (rho + eta)^l only. The commit-phase
    term under the conjecture must be added separately with its source. Several 2025 papers question these
    conjectures in some parameter ranges: source: other, ePrint 2025/2046 and 2025/2197 (needs verification of
    their exact scope before using this regime at all).
    """
    return (F(rate) + F(eta)) ** queries


def grinding(eps_round: Fraction, pow_bits: int) -> Fraction:
    """Heuristic: a proof-of-work of b bits checked by the verifier before a challenge divides the per-attempt
    success of grinding that challenge by 2^b. Only valid if the nonce is absorbed into the transcript before the
    challenge is derived. source: other, ethSTARK documentation, ePrint 2021/582 -- needs verification for the
    protocol at hand; mark the term `heuristic` in the budget.
    """
    return F(eps_round) / 2 ** pow_bits


# ------------------------------------------------------------- budget ---

REGIMES = ("proven", "conjectured", "heuristic")


@dataclass
class Term:
    name: str
    eps: Callable[[int], Fraction]          # t -> error bound
    regime: str = "proven"
    source: str = ""

    def __post_init__(self):
        if self.regime not in REGIMES:
            raise ValueError(f"regime must be one of {REGIMES}")


@dataclass
class Budget:
    title: str
    level: str                               # worst-case | average-case
    terms: list[Term]
    caps: list[tuple[str, float, str]] = field(default_factory=list)   # (name, bits, source)
    max_bits: int = 400

    def total(self, t: int) -> Fraction:
        return sum((term.eps(t) for term in self.terms), F(0))

    def _holds(self, s: int) -> bool:
        if self.level == "worst-case":
            return self.total(2 ** s) <= F(1, 2 ** s)
        if self.level == "average-case":
            # t / eps(t) is minimised at an endpoint of [1, 2^s] when eps is a polynomial in t with non-negative
            # coefficients (1/t + const + t + ... is convex); the grid of powers of two is a safety net.
            for j in range(s + 1):
                t = 2 ** j
                if F(t) < self.total(t) * 2 ** s:
                    return False
            return True
        raise ValueError("level must be worst-case or average-case")

    def statistical_level(self) -> int:
        """Largest integer s for which the chosen definition holds (the predicate is monotone in s)."""
        lo, hi = 0, self.max_bits
        if not self._holds(0):
            return 0
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self._holds(mid):
                lo = mid
            else:
                hi = mid - 1
        return lo

    def level_bits(self) -> tuple[float, str]:
        s = float(self.statistical_level())
        limiter = "union bound over the terms"
        for name, b, _src in self.caps:
            if b < s:
                s, limiter = b, name
        return s, limiter

    def regime(self) -> str:
        regs = {t.regime for t in self.terms}
        return "conjectured" if "conjectured" in regs else "heuristic" if "heuristic" in regs else "proven"

    def table(self) -> str:
        s, limiter = self.level_bits()
        si = self.statistical_level()
        t = 2 ** si
        rows = [f"### {self.title}", "",
                f"Security-level definition: **{self.level}** [CY24 §Security levels, section:security-levels]. "
                f"Regime: **{self.regime()}**. Terms evaluated at t = 2^{si}.", "",
                "| term | eps(t) | bits | regime | source |", "|---|---|---|---|---|"]
        for term in self.terms:
            e = term.eps(t)
            rows.append(f"| {term.name} | 2^-{bits(e):.2f} | {bits(e):.2f} | {term.regime} | {term.source} |")
        tot = self.total(t)
        rows.append(f"| **union bound** | 2^-{bits(tot):.2f} | {bits(tot):.2f} | {self.regime()} | sum of the rows |")
        for name, b, src in self.caps:
            rows.append(f"| cap: {name} | — | {b:g} | assumption | {src} |")
        rows += ["", f"**Security level: {s:g} bits ({self.level}, {self.regime()})**; limited by: {limiter}."]
        return "\n".join(rows)

    def evidence_rows(self, command: str) -> str:
        s, _ = self.level_bits()
        commit = _git_head()
        today = datetime.date.today().isoformat()
        row = (f"| E? | {s:g} bits ({self.level}, {self.regime()}) | {command} | results/soundness/<name>.txt | "
               f"{commit} | - | {today} | 1 / exact |")
        return "\n".join([
            "EVIDENCE rows (fill the ID, save this output under the log path, see skills/log-to-evidence):",
            "| ID | number/fact as printed in paper | command | log path | commit | machine | date | runs/median |",
            "|---|---|---|---|---|---|---|---|", row])


def _git_head() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], capture_output=True, text=True, timeout=5)
        return r.stdout.strip() or "-"
    except Exception:
        return "-"


# ------------------------------------------------------------- examples and JSON configs ---

def toy_bcs(level: str = "worst-case") -> Budget:
    """TOY: a hash-based argument (sum-check PIOP + FRI, compiled with BCS) over a 64-bit field with a
    degree-2 extension for challenges. Parameters are illustrative, not from any real system."""
    p = 2 ** 64 - 2 ** 32 + 1
    ext = p ** 2
    lam, mu, d = 256, 20, 3
    k = mu + 12                                    # sum-check rounds + FRI folding rounds (toy)
    ells = [2 ** 24] * 13
    # Per-round RBR error of the FRI rounds: must come from the PCS's own RBR theorem (source: other,
    # ePrint 2023/1071). TOY placeholder value, not computed here.
    rbr_fri = F(1, 2 ** 132)
    rbr = max(F(d, ext), rbr_fri)
    return Budget(
        title="toy-bcs (TOY parameters)", level=level,
        terms=[
            Term("IOP state restoration via RBR, (t+k) eps_rbr", lambda t: sr_from_rbr(t, k, rbr), "proven",
                 "[CY24 §RBR soundness implies SR soundness, theorem:rbr-soundness-to-sr-soundness]; "
                 "sum-check rounds: [Thaler §4.1, The Sum-Check Protocol]; FRI rounds: TOY placeholder, take from "
                 "the PCS's RBR theorem (source: other, ePrint 2023/1071)"),
            Term("Merkle multi-extraction (13 trees, K = t+1)",
                 lambda t: merkle_multi_config_extraction(lam, t, ells, t + 1), "proven",
                 "[CY24 §Extractability, lemma:mt-multi-configuration-multi-extractability]"),
            Term("hash-chain FS", lambda t: hash_chain_term(lam, t), "proven",
                 "[CY24 §Soundness, theorem:hashchain-fs-for-public-coin-ip]"),
        ])


def toy_kzg(level: str = "worst-case") -> Budget:
    """TOY: a sum-check PIOP compiled with a pairing-based PCS over a 254-bit curve. Statistical terms from
    Thaler; the curve enters as a cap. Parameters are illustrative."""
    r = 2 ** 254
    mu, d, k = 22, 3, 22
    return Budget(
        title="toy-kzg (TOY parameters)", level=level,
        terms=[
            Term("sum-check PIOP, FS via RBR", lambda t: sr_from_rbr(t, k, F(d, r)), "proven",
                 "[Thaler §4.1, The Sum-Check Protocol]; [CY24 §RBR soundness implies SR soundness, theorem:rbr-soundness-to-sr-soundness] (ROM part only)"),
            Term("batched PCS openings (8 claims, powers of one challenge)", lambda t: (t + 1) * batching(8, r), "proven",
                 "[Thaler §3.4, Schwartz-Zippel Lemma]"),
        ],
        caps=[("discrete log / pairing assumption on the toy curve (stated, not proven)", 100.0,
               "source: other, ePrint 2017/334 -- needs verification for the actual curve")])


EXAMPLES = {"toy-bcs": toy_bcs, "toy-kzg": toy_kzg}


def from_config(cfg: dict) -> Budget:
    """JSON: {"title", "level", "lambda", "terms": [{"name", "kind", "regime", "source", ...params}], "caps": [...]}
    kinds: const (eps), rbr (k, eps_rbr), sr_standard (k, eps_ip), fs_sigma (eps_sp), merkle_multi (ells),
    hash_chain, micali (eps_pcp, ell), bcs (eps_sr, ells), special_soundness (arities, challenge_sizes).
    Rationals are strings such as "3/18446744073709551616" or "2^-100"."""
    lam = int(cfg.get("lambda", 256))

    def q(x) -> Fraction:
        if isinstance(x, str) and x.startswith("2^"):
            e = int(x[2:])
            return F(2) ** e
        return F(x)

    terms = []
    for spec in cfg["terms"]:
        kind = spec["kind"]
        if kind == "const":
            e = q(spec["eps"]); fn = lambda t, e=e: e
        elif kind == "rbr":
            k, e = int(spec["k"]), q(spec["eps_rbr"]); fn = lambda t, k=k, e=e: sr_from_rbr(t, k, e)
        elif kind == "sr_standard":
            k, e = int(spec["k"]), q(spec["eps_ip"]); fn = lambda t, k=k, e=e: sr_from_standard(t, k, e)
        elif kind == "fs_sigma":
            e = q(spec["eps_sp"]); fn = lambda t, e=e: fs_sigma(t, e)
        elif kind == "merkle_multi":
            ells = [int(x) for x in spec["ells"]]; fn = lambda t, ells=ells: merkle_multi_config_extraction(lam, t, ells, t + 1)
        elif kind == "hash_chain":
            fn = lambda t: hash_chain_term(lam, t)
        elif kind == "micali":
            e, ell = q(spec["eps_pcp"]), int(spec["ell"]); fn = lambda t, e=e, ell=ell: micali(lam, t, e, ell)
        elif kind == "bcs":
            e, ells = q(spec["eps_sr"]), [int(x) for x in spec["ells"]]; fn = lambda t, e=e, ells=ells: bcs(lam, t, e, ells)
        elif kind == "special_soundness":
            a, c = [int(x) for x in spec["arities"]], [int(x) for x in spec["challenge_sizes"]]
            fn = lambda t, a=a, c=c: sr_knowledge_from_special_soundness(t, a, c)
        else:
            raise ValueError(f"unknown term kind {kind!r}")
        terms.append(Term(spec.get("name", kind), fn, spec.get("regime", "proven"), spec.get("source", "")))
    caps = [(c["name"], float(c["bits"]), c.get("source", "")) for c in cfg.get("caps", [])]
    return Budget(cfg.get("title", "budget"), cfg.get("level", "worst-case"), terms, caps)


# ------------------------------------------------------------- self-test ---

def min_lambda(eps_of: Callable[[int, int], Fraction], s: int, level: str, lo: int = 1, hi: int = 1200) -> int | None:
    """Smallest oracle output size lam for which eps_of(lam, t) gives s bits under `level` (None if none <= hi)."""
    def ok(lam):
        return Budget("", level, [Term("x", lambda t: eps_of(lam, t))])._holds(s)
    if not ok(hi):
        return None
    while lo < hi:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def selftest() -> int:
    ok = True

    def expect(cond, msg):
        nonlocal ok
        print(("ok   " if cond else "FAIL ") + msg)
        ok &= bool(cond)

    s = 128
    # Exact small values.
    expect(rom_collision(8, 3) == F(6, 512), "rom_collision(8, 3) = 6/512")
    expect(sr_from_standard(10, 1, F(1, 100)) == F(11, 100), "SR from standard soundness, k = 1: (t+1) eps")
    expect(sr_from_rbr(10, 3, F(1, 7)) == F(13, 7), "SR from RBR: (t+k) eps")
    expect(sr_lower_bound(10, 2, F(1, 10)) == F(5, 10) - comb(5, 2) * F(1, 100), "SR lower bound formula")
    expect(sr_knowledge_from_special_soundness(0, [2], [101]) == F(1, 101), "special soundness, one round, arity 2: 1/|C|")

    # Re-derivations (ours, written out in skills/soundness-budget/SKILL.md, "Worked re-derivations").
    # (1) basic commitment binding t^2/2^(lam+1): worst-case needs lam >= 3s-1, average-case lam >= 2s-1.
    expect(min_lambda(basic_commitment_binding, s, "worst-case") == 3 * s - 1, "commitment binding, worst-case: lam = 3s-1 = 383")
    expect(min_lambda(basic_commitment_binding, s, "average-case") == 2 * s - 1, "commitment binding, average-case: lam = 2s-1 = 255")
    # (2) hiding t/2^salt: worst-case salt = 2s, average-case salt = s.
    expect(min_lambda(lambda salt, t: basic_commitment_hiding(salt, t), s, "worst-case") == 2 * s, "commitment hiding, worst-case: salt = 2s")
    expect(min_lambda(lambda salt, t: basic_commitment_hiding(salt, t), s, "average-case") == s, "commitment hiding, average-case: salt = s")
    # (3) Micali, simplified, worst-case with eps_pcp = 2^(-2s-2): 2.5*2^(2s)/2^lam <= 0.75*2^-s - 2^(-2s-2)
    #     gives lam >= 3s + log2(10/3) + o(1), i.e. lam = 3s+2; 3s+3 also works.
    epw = F(1, 2 ** (2 * s + 2))
    expect(min_lambda(lambda lam, t: micali_simplified(lam, t, epw), s, "worst-case") == 3 * s + 2, "Micali worst-case: minimal lam = 3s+2 = 386")
    # (4) Micali, average-case. With eps_pcp = 2^(-s-1) the ratio at t = 1 is 1/(2^-s + 2.5/2^lam) < 2^s for
    #     every lam: s bits are never reached. With eps_pcp = 2^(-s-2): t = 1 needs lam >= s+3, t = 2^s needs
    #     lam >= 2s + log2(10/3), so lam = 2s+2.
    expect(min_lambda(lambda lam, t: micali_simplified(lam, t, F(1, 2 ** (s + 1))), s, "average-case") is None,
           "Micali average-case with eps_pcp = 2^(-s-1): s bits unreachable (fails at t = 1)")
    expect(min_lambda(lambda lam, t: micali_simplified(lam, t, F(1, 2 ** (s + 2))), s, "average-case") == 2 * s + 2,
           "Micali average-case with eps_pcp = 2^(-s-2): minimal lam = 2s+2 = 258")
    # (5) BCS, simplified, with eps_sr <= 2^(-s-1) for every t: worst-case lam >= 3s+1+log2(3.5) -> 3s+3;
    #     average-case: t = 2^s needs lam >= 2s + log2(3.5) + o(1) -> 2s+2; t = 1 needs s+3.
    esr = F(1, 2 ** (s + 1))
    expect(min_lambda(lambda lam, t: bcs_simplified(lam, t, esr), s, "worst-case") == 3 * s + 3, "BCS worst-case: minimal lam = 3s+3 = 387")
    expect(min_lambda(lambda lam, t: bcs_simplified(lam, t, esr), s, "average-case") == 2 * s + 2, "BCS average-case: minimal lam = 2s+2 = 258")
    # (6) exact Merkle forms are below the simplified ones when the stated condition holds.
    lam, ell = 256, 2 ** 20
    t = 2 * (_depth(ell) + 1) * ell
    expect(micali(lam, t, epw, ell) <= micali_simplified(lam, t, epw), "Micali exact <= 2.5 t^2/2^lam when t >= 2(log ell+1) ell")
    expect(bcs(lam, t, esr, [ell]) <= bcs_simplified(lam, t, esr), "BCS exact <= 3.5 t^2/2^lam when t >= 2(log ell+1) ell")
    t4 = 4 * (_depth(ell) + 1) * ell
    expect(merkle_extraction(lam, t4, ell) <= F(t4 * t4, 2 ** (lam + 1)), "Merkle extraction <= t^2/2^(lam+1) when t >= 4(d+1) ell")
    # (7) worst-case level never exceeds average-case level.
    for b in (toy_bcs, toy_kzg):
        w, a = b("worst-case").statistical_level(), b("average-case").statistical_level()
        expect(w <= a, f"{b.__name__}: worst-case level {w} <= average-case level {a}")
    # (8) FRI, proven regime: rho = 1/16, |F| = 2^256, eta = 2^-14, d0 = 2^16, 65 queries, and delta = 3/4 - 2 eta
    #     (strictly inside the open interval (0, 1 - sqrt(rho) - eta)).
    #     eps1 = (2^16+1)^2 / (2^-91 * 2^256) ~ 2^-133.0, eps2 = (1/4 + 2^-13)^65 ~ 2^-129.95; total ~ 2^-129.8.
    e = fri_johnson(F(1, 16), F(1, 2 ** 14), F(3, 4) - F(1, 2 ** 13), 2 ** 16, 2 ** 256, 65)
    expect(129.7 < bits(e) < 129.9 and e <= F(1, 2 ** 128), f"FRI Johnson-regime example: {bits(e):.2f} bits >= 128")
    try:
        fri_johnson(F(1, 16), F(1, 2 ** 14), F(4, 5), 2 ** 16, 2 ** 256, 65)
        expect(False, "FRI: delta beyond 1 - sqrt(rho) - eta is rejected")
    except ValueError:
        expect(True, "FRI: delta beyond 1 - sqrt(rho) - eta is rejected")
    # (9) algebraic terms.
    p = 2 ** 64 - 2 ** 32 + 1
    expect(abs(bits(sumcheck(20, 3, p)) - (math.log2(p) - math.log2(60))) < 1e-9, "sum-check v d/|F| over a 64-bit field")
    expect(bits(sumcheck(20, 3, p * p)) > 2 * 60, "extension-field challenges roughly double the sum-check bits")
    expect(batching(1, p) == 0 and batching(8, p) == F(7, p), "batching (m-1)/|F|")
    # (10) budget plumbing: union bound, caps, regime and the JSON path agree with direct construction.
    bud = toy_kzg()
    expect(bud.level_bits()[0] == 100.0 and bud.regime() == "proven", "cap limits the toy KZG budget to 100 bits")
    cfg = {"title": "json", "level": "worst-case", "lambda": 256,
           "terms": [{"kind": "rbr", "k": 32, "eps_rbr": "3/18446744073709551616"}, {"kind": "hash_chain"}]}
    jb = from_config(cfg)
    expect(jb.total(1024) == sr_from_rbr(1024, 32, F(3, 2 ** 64)) + hash_chain_term(256, 1024), "JSON budget = sum of its terms")
    expect("worst-case" in jb.table() and "E?" in jb.evidence_rows("cmd"), "table names the definition; EVIDENCE row emitted")
    print("selftest:", "all checks passed" if ok else "FAILED")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--example", choices=sorted(EXAMPLES))
    g.add_argument("--config")
    g.add_argument("--selftest", action="store_true")
    ap.add_argument("--level", choices=["worst-case", "average-case"])
    ap.add_argument("--evidence", action="store_true", help="also print an EVIDENCE.md row")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.example:
        bud = EXAMPLES[a.example](a.level or "worst-case")
    else:
        with open(a.config, encoding="utf-8") as fh:
            cfg = json.load(fh)
        if a.level:
            cfg["level"] = a.level
        bud = from_config(cfg)
    print(bud.table())
    if a.evidence:
        cmd = "python3 " + " ".join([os.path.relpath(__file__)] + (argv if argv is not None else sys.argv[1:]))
        print()
        print(bud.evidence_rows(cmd))
    return 0


if __name__ == "__main__":
    sys.exit(main())
