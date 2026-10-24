---
name: sage-check
description: Numeric sanity check of every ZK lemma, polynomial identity, PIOP completeness/soundness claim and parameter claim on small fields, with exhaustive search where feasible. Use it before writing a proof, before Lean formalisation, and whenever a falsifier needs a counterexample search. Works with SageMath if installed and falls back to pure Python/sympy otherwise.
---
# sage-check: test every lemma on small cases first

## Why

Proving a false lemma wastes days, and formalising one in Lean wastes weeks. Most
wrong statements fail on a toy instance: a small field such as F₁₇ or F₉₇, one or two
sum-check variables, a circuit with four rows. Run a finite check **before** proving and **before** formalising.

## Protocol

1. **Transcribe the statement exactly** as in THEORY.md. Include every quantifier and
   side condition (degree bounds, domain sizes, which values are public). Each checked statement gets an ID matching THEORY.md / CLAIMS.md.
2. **Choose a parameter grid.**
   - Include every smallest case: fields p ∈ {17, 97} (and p = 2, 3 where the statement
     allows it), number of variables μ ∈ {1, 2, 3}, degree d ∈ {1, 2, 3}, trace or
     table length n ∈ {1, 2, 4, 8}.
   - Cover the field structures the statement distinguishes: a prime field with a
     large 2-adic subgroup (p = 17, 97 both have 2^k | p − 1) and one without; an
     extension field if the protocol samples challenges there.
   - Include the boundary of any inequality hypothesis, on both sides.
   - Include at least one parameter as large as the experiments use, if it is feasible.
3. **Test the hypotheses too.** Check that the hypotheses are satisfiable on the grid,
   because a vacuous theorem "passes" every check. Then check the conclusion.
   For soundness claims, write down an explicit **cheating strategy** (e.g. lie in
   round 1, then play honestly) and measure its acceptance frequency; a bound that the
   best strategy you can think of meets with equality is a good sign, one it exceeds
   is a refutation.
4. **Search exhaustively** wherever the space is finite and small (≤ 10⁷ cases).
   Otherwise use random sampling with a fixed seed, and report the seed and the sample
   size.
5. **Also test the converse.** If a condition is claimed to be necessary *and*
   sufficient, test both directions separately.
6. **Use exact arithmetic**: `GF(p)`/`Zmod`, `Integer`, `QQ`, `sympy.Rational`, or
   plain `int` with `% p`. Use no floats unless the statement is about floats; compare
   frequencies as `count * p <= bound_numerator * total`, not as floats. For asymptotic claims, check the exact
   finite formula on a range and fit the trend; do not trust a plotted curve.
7. **Output one JSON line per check**:
   `{"check": ID, "params": {...}, "cases": N, "passed": bool, "counterexample": {...} | null}`.
   Save the script under `checks/` and the output under `results/checks/`, then add an
   EVIDENCE row if any number from it reaches the paper.
8. If a check fails, give the **minimal** counterexample (smallest parameters) to
   `falsifier` and `theorist`. Do not patch the statement silently.

## Script template

`scripts/sanity_check_template.py` is a runnable skeleton with a guarded Sage import,
a `check(...)` helper that stops at the first counterexample, and toy statements over
F₁₇ and F₉₇: sum-check completeness for every challenge vector, the Schwartz–Zippel
bound as an exhaustive zero count (tight on an extremal polynomial), sum-check soundness
against a "lie in round 1" prover, the grand-product multiset check behind
permutation/lookup arguments, and one deliberately false statement (degree-1 round
polynomials for an individual-degree-2 polynomial) that shows counterexample output.
Runs in a few seconds; exit code 0 means every statement behaved as expected. Copy it,
then replace the `STATEMENTS` list.

```bash
python3 skills/sage-check/scripts/sanity_check_template.py          # pure Python
sage -python skills/sage-check/scripts/sanity_check_template.py     # uses Sage if present
```

## Typical checks by area

| area | what to check on toy parameters |
|---|---|
| PIOP completeness | run the honest prover and verifier on **every** instance and challenge over F₁₇ / F₉₇ (small μ, d, n); one rejected honest transcript is a completeness bug, usually a degree bound, an off-by-one in the domain, or a missing boundary constraint |
| Schwartz–Zippel / soundness error | count zeros exhaustively and compare the frequency with d/|F| (or μd/|F| for sum-check); compare a concrete cheating prover's acceptance frequency with the claimed soundness error; check which field the challenges come from (base vs extension) |
| sum-check | round-by-round: g_i(0) + g_i(1) equals the previous claim, deg g_i ≤ the stated bound, final oracle query consistent; try individual degree d + 1 to see the check fail |
| permutation / lookup arguments | grand-product or log-derivative identities on toy circuits: true permutations and table-contained witnesses pass for every challenge; non-permutations and out-of-table values pass for at most the claimed number of challenges; empty table and repeated entries handled |
| polynomial identities | quotient divisibility by the vanishing polynomial, multilinear-extension identities, batching (random linear combination) checked coefficient by coefficient over a small field |
| knowledge soundness | on a toy instance, actually run the extractor: rewind with fresh challenges (special soundness) or interpolate from accepting transcripts, and check that the output **is** a valid witness for R |
| zero knowledge | on tiny instances, compare the distribution of real transcripts with simulator outputs by exhaustive enumeration (exact equality for perfect ZK; total-variation distance for statistical ZK) |
| cost formulas | operation counts (field multiplications, hashes, MSM/NTT sizes) from an instrumented toy prover vs the closed form in THEORY.md |

## Tooling notes

- In Sage, `GF(p)`, `GF(p^k)`, `PolynomialRing(GF(p), names)` and
  `R.lagrange_polynomial(...)` cover most checks. Run with `sage -python script.py` so the same file stays
  importable as plain Python.
- In pure Python, `int` arithmetic with `% p`, `pow(a, -1, p)`, a dict-of-monomials
  polynomial and Lagrange interpolation on {0, …, d} (all in the template) are enough
  for most toy checks; `sympy` (`Poly(..., modulus=p)`, `primitive_root`) helps for
  roots of unity and evaluation domains.
- Small fields hide nothing about the *algebra* but everything about the *security
  level*: a check over F₉₇ validates the identity and the shape of the bound, not the
  128-bit claim. The bits come from soundness-budget <!-- TODO: link once skill exists -->.
- Mathematica, if connected, is useful for closed forms and series. Treat its output
  as a hint, then recheck with exact finite computation.
