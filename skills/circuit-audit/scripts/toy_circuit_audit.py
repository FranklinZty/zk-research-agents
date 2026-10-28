#!/usr/bin/env python3
# TOY: not secure. Tiny fields, toy gadgets; for demonstrating circuit-audit checks only.
"""toy_circuit_audit.py -- find an under-constrained gadget by exhaustive search on a small field.

    python3 toy_circuit_audit.py              # run the demo and print the audit lines
    python3 toy_circuit_audit.py --selftest   # assertions only, exit 0 on success

The gadget is a k-bit range check written as R1CS over F_p (Thaler's bit-decomposition approach,
[Thaler §6.5, Turning Computer Programs Into Circuit Satisfiability Instances]): the witness holds bits
b_0..b_{k-1}, one constraint per bit enforces b_i * (b_i - 1) = 0, and one constraint enforces
x = sum_i 2^i b_i. Its specification: for public x in F_p, a witness exists iff x < 2^k, and then it is unique.

Four variants are audited by brute force over the whole public-input x witness space F_p x F_p^k:
  * buggy   : the booleanity constraint of one bit is missing (a typical refactoring slip);
  * fixed   : all k booleanity constraints present;
  * wrap    : all constraints present, but 2^k > p, so x and x + p can both be decomposed (field wrap-around);
  * overcon : a spurious extra constraint b_0 = 0 (rejects honest odd inputs).
For each, the audit reports: completeness (every in-spec input has a witness, and the witness generator's
output satisfies the constraints), soundness (no out-of-spec input has a witness), and witness uniqueness.
A small is-zero gadget with a non-deterministic inverse hint is audited the same way.

The audit line printed for each variant is meant for the "falsifier evidence" column of CLAIMS.md.
Pure Python 3.10+, no dependencies.
"""
from __future__ import annotations

import argparse
import itertools
import random
import sys
from dataclasses import dataclass, field

# ------------------------------------------------------------------ R1CS ---

LC = dict  # linear combination: variable name -> coefficient ("one" is the constant-1 variable)


@dataclass
class R1CS:
    """Constraints <a,z> * <b,z> = <c,z> over F_p; z maps names to field elements, z["one"] = 1."""
    p: int
    public: list[str]
    witness: list[str]
    constraints: list[tuple[LC, LC, LC, str]] = field(default_factory=list)

    def add(self, a: LC, b: LC, c: LC, tag: str) -> None:
        self.constraints.append((a, b, c, tag))

    def _lc(self, lc: LC, z: dict) -> int:
        return sum(coef * z[v] for v, coef in lc.items()) % self.p

    def failing(self, z: dict) -> list[str]:
        """Tags of the constraints that z violates (empty list = satisfied)."""
        return [tag for a, b, c, tag in self.constraints
                if (self._lc(a, z) * self._lc(b, z) - self._lc(c, z)) % self.p]

    def satisfied(self, z: dict) -> bool:
        return not self.failing(z)


def range_check(p: int, k: int, drop_bool: int | None = None, extra_b0_zero: bool = False) -> R1CS:
    """k-bit range check of public x. drop_bool=i omits bit i's booleanity constraint (the planted bug)."""
    bits = [f"b{i}" for i in range(k)]
    cs = R1CS(p, ["x"], bits)
    for i, b in enumerate(bits):
        if i != drop_bool:
            cs.add({b: 1}, {b: 1, "one": -1}, {}, f"bool[{b}]")            # b * (b - 1) = 0
    cs.add({"one": 1}, {**{b: pow(2, i, p) for i, b in enumerate(bits)}}, {"x": 1}, "recompose")
    if extra_b0_zero:
        cs.add({"one": 1}, {"b0": 1}, {}, "spurious[b0=0]")
    return cs


def range_check_witness(x: int, k: int) -> dict:
    """The witness generator: what the prover's code computes (integer bits of x)."""
    return {f"b{i}": (x >> i) & 1 for i in range(k)}


def range_check_spec(x: int, k: int) -> bool:
    return x < 2 ** k


def is_zero(p: int, drop_out_constraint: bool = False) -> R1CS:
    """out = 1 if x == 0 else 0, with a hint inv = x^{-1} (any value when x = 0).
    Constraints: x * inv = 1 - out; x * out = 0. Without the second, for x != 0 every out is reachable with the
    hint inv = (1 - out) / x: the hint is unconstrained enough to choose the output."""
    cs = R1CS(p, ["x", "out"], ["inv"])
    cs.add({"x": 1}, {"inv": 1}, {"one": 1, "out": -1}, "x*inv=1-out")
    if not drop_out_constraint:
        cs.add({"x": 1}, {"out": 1}, {}, "x*out=0")
    return cs


def is_zero_spec(x: int, out: int) -> bool:
    return out == (1 if x == 0 else 0)


# --------------------------------------------------------------- the audit ---

@dataclass
class Audit:
    name: str
    p: int
    space: int                      # number of (public, witness) assignments enumerated
    incomplete: list = field(default_factory=list)       # in-spec public input with no witness
    generator_fails: list = field(default_factory=list)  # generator output violates constraints
    unsound: list = field(default_factory=list)          # out-of-spec public input with a witness
    non_unique: list = field(default_factory=list)       # (public input, number of witnesses)

    @property
    def verdict(self) -> str:
        bad = []
        if self.unsound:
            bad.append("UNDER-CONSTRAINED (accepts out-of-spec inputs)")
        if self.non_unique:
            bad.append("NON-UNIQUE WITNESS")
        if self.incomplete or self.generator_fails:
            bad.append("OVER-CONSTRAINED (rejects honest inputs)")
        return "PASS" if not bad else "FAIL: " + "; ".join(bad)

    def evidence_line(self, script: str = "skills/circuit-audit/scripts/toy_circuit_audit.py") -> str:
        """One line for the 'falsifier evidence' column of CLAIMS.md."""
        ex = []
        if self.unsound:
            ex.append(f"accepts out-of-spec {self.unsound[:3]}")
        if self.non_unique:
            ex.append(f"#witnesses {self.non_unique[:3]}")
        if self.incomplete:
            ex.append(f"rejects in-spec {self.incomplete[:3]}")
        if self.generator_fails:
            ex.append(f"generator output fails {self.generator_fails[:2]}")
        return (f"circuit-audit[{self.name}] exhaustive over F_{self.p}, {self.space} assignments: {self.verdict}"
                + (f" — {'; '.join(ex)}" if ex else "") + f" ({script})")


def audit_range_check(name: str, cs: R1CS, k: int) -> Audit:
    p = cs.p
    au = Audit(name, p, p ** (1 + len(cs.witness)))
    for x in range(p):
        sols = []
        for bits in itertools.product(range(p), repeat=len(cs.witness)):
            z = {"one": 1, "x": x, **dict(zip(cs.witness, bits))}
            if cs.satisfied(z):
                sols.append(bits)
        in_spec = range_check_spec(x, k)
        if in_spec and not sols:
            au.incomplete.append(x)
        if not in_spec and sols:
            au.unsound.append(x)
        if len(sols) > 1:
            au.non_unique.append((x, len(sols)))
        if in_spec:   # differential test: the generator's witness must satisfy the constraints
            z = {"one": 1, "x": x, **range_check_witness(x, k)}
            if not cs.satisfied(z):
                au.generator_fails.append((x, cs.failing(z)))
    return au


def audit_is_zero(name: str, cs: R1CS) -> Audit:
    p = cs.p
    au = Audit(name, p, p ** 3)
    for x in range(p):
        for out in range(p):
            n = sum(cs.satisfied({"one": 1, "x": x, "out": out, "inv": inv}) for inv in range(p))
            ok = is_zero_spec(x, out)
            if ok and n == 0:
                au.incomplete.append((x, out))
            if not ok and n:
                au.unsound.append((x, out))
            # inv is a hint: when x = 0 any inv works, which is harmless (out is still forced), so uniqueness
            # is checked on the output, not on the hint
        outs = [out for out in range(p)
                if any(cs.satisfied({"one": 1, "x": x, "out": out, "inv": i}) for i in range(p))]
        if len(outs) > 1:
            au.non_unique.append((x, len(outs)))
    return au


def random_differential(cs: R1CS, k: int, trials: int, seed: int = 0) -> int:
    """Differential test on random in-spec inputs (what one runs when the field is too big to enumerate):
    returns the number of inputs whose generated witness violates the constraints. It finds over-constraints
    and generator bugs, never a missing constraint -- that needs the exhaustive or solver-based search."""
    rng = random.Random(seed)
    bad = 0
    for _ in range(trials):
        x = rng.randrange(min(cs.p, 2 ** k))
        bad += not cs.satisfied({"one": 1, "x": x, **range_check_witness(x, k)})
    return bad


# ------------------------------------------------------------------- demo ---

P, K = 11, 3          # 2^3 = 8 < 11: the decomposition is unique when every bit is boolean
P_WRAP, K_WRAP = 7, 3  # 2^3 = 8 > 7: x and x + 7 both fit in 3 bits


def run(verbose: bool = True) -> dict:
    res = {
        "buggy": audit_range_check("range3 buggy: no bool[b2]", range_check(P, K, drop_bool=2), K),
        "fixed": audit_range_check("range3 fixed", range_check(P, K), K),
        "wrap": audit_range_check("range3 over F_7 (2^k > p)", range_check(P_WRAP, K_WRAP), K_WRAP),
        "overcon": audit_range_check("range3 + spurious b0=0", range_check(P, K, extra_b0_zero=True), K),
        "iszero_buggy": audit_is_zero("is-zero without x*out=0", is_zero(P, drop_out_constraint=True)),
        "iszero_fixed": audit_is_zero("is-zero", is_zero(P)),
    }
    res["random_diff_buggy"] = random_differential(range_check(P, K, drop_bool=2), K, 200)
    res["random_diff_overcon"] = random_differential(range_check(P, K, extra_b0_zero=True), K, 200)
    if verbose:
        for key in ("buggy", "fixed", "wrap", "overcon", "iszero_buggy", "iszero_fixed"):
            print(res[key].evidence_line())
        print(f"random differential test, 200 inputs: buggy variant -> {res['random_diff_buggy']} failures "
              f"(misses the missing constraint), over-constrained variant -> {res['random_diff_overcon']} failures")
    return res


def selftest() -> int:
    r = run(verbose=False)
    b, f, w, o = r["buggy"], r["fixed"], r["wrap"], r["overcon"]
    # planted bug: b2 unconstrained -> x = b0 + 2 b1 + 4 b2 with any b2 in F_11 -> every x has a witness
    assert b.unsound == list(range(8, 11)), b.unsound
    assert b.verdict.startswith("FAIL") and "UNDER-CONSTRAINED" in b.verdict
    # in F_11 with b2 free, x is reached once per (b0, b1) pair: 4 witnesses for every x
    assert all(n == 4 for _, n in b.non_unique) and len(b.non_unique) == 11, b.non_unique
    # after the fix: unique witness for x < 8, none for x >= 8, generator agrees
    assert f.verdict == "PASS", f.evidence_line()
    assert not (f.unsound or f.non_unique or f.incomplete or f.generator_fails)
    # field wrap-around: over F_7 the 3-bit decomposition of 0 has a second witness, 111 (7 = 0 mod 7)
    assert w.non_unique == [(0, 2)], w.non_unique
    assert "NON-UNIQUE" in w.verdict and not w.unsound
    # over-constraint: odd honest inputs rejected; the differential test catches it, also on random inputs
    assert o.incomplete == [1, 3, 5, 7] and o.generator_fails and "OVER-CONSTRAINED" in o.verdict
    assert r["random_diff_overcon"] > 0
    # ... but random differential testing alone does not find the missing constraint
    assert r["random_diff_buggy"] == 0
    # is-zero: for x = 0 the remaining constraint still forces out = 1; the hole is x != 0, where
    # x * inv = 1 - out has a solution inv for every out
    iz, izf = r["iszero_buggy"], r["iszero_fixed"]
    assert iz.unsound and all(x != 0 for x, _ in iz.unsound), iz.unsound
    assert izf.verdict == "PASS", izf.evidence_line()
    # the evidence line is a single line that names the verdict
    line = b.evidence_line()
    assert "\n" not in line and "FAIL" in line and "F_11" in line
    print("selftest: OK")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    run(verbose=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
