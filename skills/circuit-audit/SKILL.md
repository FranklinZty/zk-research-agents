---
name: circuit-audit
description: Check that OUR OWN circuit encodes exactly the intended relation — under- and over-constraint, witness uniqueness by exhaustive search on a small field, differential tests of the witness generator against the constraint system, range constraints, field wrap-around (mod p), non-deterministic hints, public-input binding, lookup tables. Says what halo2 MockProver, Circomspect and Picus can and cannot show. The circuit-engineer runs it on their own circuits; the falsifier re-runs it independently at P6. Not for auditing other people's circuits.
---
# circuit-audit: does the circuit prove the statement the paper claims?

## Scope

Only circuits we wrote (gadgets, application circuits, the in-circuit verifier of our recursion). This skill is
not for finding, exploiting or disclosing bugs in third-party circuits or deployed systems. Published bug
studies (source: other, ePrint 2023/512, 2023/190) are cited for the *kinds* of mistakes, not as targets.

The builder (`circuit-engineer`) audits their own circuit; `falsifier` repeats the audit independently, from the
specification rather than from the builder's report (the proposer does not judge their own claim).

## Why

An argument system proves that the prover knows a witness satisfying the **circuit**. With knowledge soundness,
the extractor outputs *some* witness for the relation the circuit defines
([CY24 §Knowledge soundness, definition:adaptive-straightline-knowledge-soundness]; [Thaler §7.4, Knowledge-Soundness]).
That is a guarantee about the intended statement only if the circuit's relation equals the intended one:
- **under-constrained**: the circuit accepts witnesses (or public inputs) the specification rejects. The
  soundness theorem still holds, about the wrong relation, and the application claim is false;
- **over-constrained**: the circuit rejects honest inputs. Completeness fails, usually on edge cases (zero,
  the maximum value, an odd length) that benchmarks never hit.

An application paper's core claim is "this circuit implements F". The audit is the evidence for that claim.
Front ends that turn programs into circuits rely on non-deterministic witness values (whole execution
transcripts, sorted copies, bit decompositions) that only constraints keep honest
([Thaler §6.5.4, Details of the Transformation]); each such value is a place where a missing constraint hides.

## Inputs

- The specification of each gadget as a function or relation on integers / field elements, written before
  looking at the constraints: for which public inputs must a witness exist, and is it unique.
- The constraint system as compiled (R1CS matrices, Plonkish gates + selectors + copy constraints + lookups,
  AIR transitions), at a pinned commit; the witness generator (the code that fills in the witness).
- The field (p, extension), and every value range the specification assumes.

## Checklist

Mark each item PASS / FAIL / N.A. per gadget, with evidence (test name, script output, counterexample).

1. **Specification written down.** "x is a k-bit integer", "out = 1 iff x = 0", "y = SHA-256(m) for |m| ≤ L".
   A gadget without a written specification cannot be audited; that is the first finding.
2. **Witness uniqueness (determinism).** For every public input, the outputs, and every intermediate value the
   specification defines, are uniquely determined. Hints that are legitimately free (an inverse of 0, a
   blinding value) are listed explicitly; everything else must be forced. Check it exhaustively on a small field
   (procedure step 2), with a solver (Picus, below), or by a written argument per constraint.
3. **No out-of-spec acceptance (under-constraint).** For every public input that the specification rejects, no
   witness satisfies the circuit. The classic case: the bit decomposition without the booleanity constraint
   b·(b−1) = 0 on some bit, so x = Σ 2^i b_i holds for values of x outside [0, 2^k) (the booleanity check is the
   standard one in [Thaler §6.5.4, Details of the Transformation]).
4. **No honest rejection (over-constraint).** Every in-spec input has a witness, and the witness generator's
   output satisfies every constraint. Test edge cases deliberately: 0, 1, p−1, 2^k−1, empty and maximal inputs.
5. **Range constraints.** Every value later interpreted as an integer (compared, used as an index, shifted,
   concatenated into bytes) is range-checked where it is created, not only where it is used. Lookup-based range
   checks: the table really contains exactly [0, 2^c), it is a *fixed* (preprocessed) column and not
   prover-chosen, the top limb is range-checked to its smaller width when c does not divide k, and the limb
   recomposition is constrained ([Thaler §6.6.3, Efficiently Representing Non-Arithmetic Operations Over Large Prime-Order Fields]).
6. **Field wrap-around (mod p).** A prime field simulates integer arithmetic only while values stay in
   [0, p) or [−p/2, p/2] ([Thaler §6.5.4, Details of the Transformation]). Check, per gadget:
   - a decomposition into k bits with 2^k ≥ p is **not unique**: x and x + p may both decompose (the toy script
     shows it over F_7 with k = 3); either keep 2^k < p or add a canonicity check against p − 1;
   - sums and products of range-checked values must stay below p (e.g. a 64×64-bit product does not fit a 64-bit
     field), otherwise "a + b = c" holds modulo p only;
   - signed values, subtraction-based comparisons (a − b ≥ 0 encoded as a range check on a − b) and "x < p/2"
     sign tests need their own bound on both operands.
7. **Non-deterministic hints.** Every value computed outside the constraints (inverse, square root, division
   quotient and remainder, sorted order, Merkle path direction bits, memory read values) is constrained to be
   the right one, not just *a* consistent one: q·d + r = n needs r < d; an is-zero gadget needs both
   x·inv = 1 − out and x·out = 0; a sort needs a permutation argument *and* the order check.
8. **Public-input binding.** Every public input is constrained to the cell the circuit uses (copy constraint to
   the instance column, or the R1CS public variables), and the verifier key fixes the circuit, selectors and
   fixed columns. A public value that is merely "present" in the instance column and never copied is unused.
9. **Selectors, copy constraints, lookups (Plonkish).** Each gate is enabled on exactly the intended rows;
   copy constraints link the cells the specification links; lookup inputs are the cells intended (and are
   gated by a selector when only some rows look up). Rows added for padding or blinding satisfy no gate by
   accident. A satisfied gate on a row where its selector is off proves nothing.
10. **Witness generator vs reference implementation.** On random and edge-case inputs, the circuit's public
    output equals a native reference implementation of F (differential test). This finds wrong circuits that
    are perfectly determined, which items 2–3 cannot.
11. **Recursion and in-circuit verification** (if any): the in-circuit verifier checks *all* of the native
    verifier's conditions, recomputes the Fiat–Shamir transcript in-circuit (`skills/fiat-shamir-audit`), and
    binds the inner proof's public inputs to the outer statement.

## Tools and what each can show

| tool / method | use it for | what it cannot show |
|---|---|---|
| exhaustive search on a small field (this skill's script) | uniqueness and under-/over-constraint of a gadget parametric in p and k, exactly | anything about the real field: thresholds such as 2^k vs p change. Run several p, including one with 2^k ≥ p; only small gadgets fit |
| differential testing (generator vs constraints, circuit vs reference) | over-constraint, generator bugs, wrong-but-deterministic circuits, regressions | a missing constraint: the honest witness still satisfies the weaker system (the script demonstrates this) |
| negative tests (mutate one witness cell, expect rejection) | that a specific constraint is live | constraints you did not think of mutating |
| halo2 `MockProver` (`halo2_proofs::dev`) | runs synthesis on a concrete witness and reports each failing gate, lookup and copy constraint with its cell; the standard harness for items 4, 9 and negative tests | it only judges the witness it is given: it cannot prove that no other witness exists; `needs verification`: the exact failure categories reported by the halo2 version we pin |
| Circomspect (Trail of Bits, static analyser for Circom; source: other, github.com/trailofbits/circomspect) | lints Circom code for signals assigned with `<--` and never constrained, unused or unconstrained signals and similar patterns | Circom only; heuristic, with false positives and false negatives; no semantic guarantee. `needs verification`: its current list of checks |
| Picus (Veridise; source: other, ePrint 2023/512, github.com/Veridise/Picus) | decides whether a circuit's outputs are uniquely determined by its inputs, with an SMT solver; returns safe, unsafe with two witnesses, or unknown | scales to gadgets, not whole large circuits (timeouts → "unknown", which is not "safe"); uniqueness is not correctness (item 10); `needs verification`: supported front ends beyond Circom/R1CS |
| static analysis of Circom circuits (source: other, ePrint 2023/190) | the class of "unconstrained signal" bugs at scale | same limits as other heuristics; Circom only |
| a written proof per gadget | the only route for large gadgets: one lemma "constraints ⇔ specification" per gadget, composed | errors in the proof; pair it with the small-field check of the same gadget |

None of these replaces item 1: every tool checks against *some* notion of intended behaviour, and uniqueness
tools check determinism, not that the determined value is the right one.

## Procedure

1. **Inventory.** List gadgets with their specification, constraint count and the hint values they introduce
   (`CIRCUITS.md`: one row per gadget; counts come from `skills/constraint-cost`).
2. **Small-field model.** Re-instantiate each gadget generically in p and k (the same constraint-building
   code, not a hand copy). Enumerate all public inputs × witnesses for small p, compare with the specification,
   and report counterexamples. Start from the toy:
   ```bash
   python3 skills/circuit-audit/scripts/toy_circuit_audit.py            # audit lines for six toy variants
   python3 skills/circuit-audit/scripts/toy_circuit_audit.py --selftest
   ```
   It plants a missing booleanity constraint in a 3-bit range check over F_11 and finds that 8, 9 and 10 are
   accepted (and every x has 4 witnesses); after the fix every x < 8 has exactly one witness and every x ≥ 8 has
   none. It also shows the 2^k ≥ p wrap-around (over F_7, 0 decomposes as 000 and as 111), an over-constrained
   variant that the differential test catches, a random differential test that **misses** the planted bug, and
   an is-zero gadget whose hint is unconstrained without x·out = 0.
3. **Real field.** Run the circuit's own test harness (MockProver or the framework's equivalent) with honest
   witnesses on edge cases (item 4), one negative test per constraint family (item 9), and the differential test
   against the reference (item 10). Run Picus / Circomspect where the front end is supported, and record
   "unknown" results as open, not as passes.
4. **Write the audit report** (format below) and put the one-line result into the claim's CLAIMS.md row.
   Fixes go back to `circuit-engineer`; the audit is re-run at the fixed commit, and the old line stays,
   struck through, in the report.

## Report format

`falsify/<claim-id>/circuit-audit.md`:

```markdown
# Circuit audit — <circuit>, <repo>@<commit>, field <p>, auditor <builder | falsifier>
| gadget | spec | uniqueness | under | over | ranges | wrap | hints | public inputs | method | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| range_k | x < 2^k, bits unique | PASS | PASS | PASS | PASS | 2^k < p checked | n.a. | x copied from instance | exhaustive F_11, F_13 + MockProver edge cases | script log, test t_range_* |
| is_zero | out = [x = 0] | PASS | PASS | PASS | n.a. | n.a. | inv free only at x = 0 | out public | exhaustive F_11 + Picus (safe) | ... |
Open: Picus "unknown" on <gadget> (timeout 600 s). Verdict: PASS / FAIL (gadgets …).
```

CLAIMS.md "falsifier evidence" column, one line per audited gadget or circuit, as the script prints it:

```text
circuit-audit[range3 buggy: no bool[b2]] exhaustive over F_11, 14641 assignments: FAIL: UNDER-CONSTRAINED (accepts out-of-spec inputs); NON-UNIQUE WITNESS — accepts out-of-spec [8, 9, 10]; #witnesses [(0, 4), (1, 4), (2, 4)] (falsify/C7/circuit-audit.md)
circuit-audit[range3 fixed] exhaustive over F_11, 14641 assignments: PASS (falsify/C7/circuit-audit.md)
```

A claim "our circuit computes F" is `survived` only if every gadget it uses is PASS on the specification, with
the method named; "PASS (differential tests only)" supports `weakened` wording at most.

## Pitfalls

- Auditing the gadget against the witness generator instead of against the specification: both can share a bug.
- Treating random testing as an under-constraint check (the honest witness always satisfies a weaker system).
- A small-field check whose p is so small that the gadget behaves differently (2^k vs p, overflow of sums).
- Hand-copying constraints into the small-field model instead of re-running the real constraint builder.
- Range-checking a value where it is used but not where a hint created it; a lookup table that is an advice
  (prover-filled) column.
- A tool's "no warnings" or "unknown" reported as "verified".
- Counting the audit as done after a fix without re-running it at the fixed commit.
