---
name: falsify
description: Red-team protocol for trying to refute a ZK research claim (soundness or zero-knowledge theorem, concrete security level, prover/verifier speed-up, proof size, circuit correctness, novelty) before anyone else does. Use at the P6 falsification gate, before any number or theorem goes into the paper, and whenever a sub-agent reports a surprisingly good result. Produces a verdict of survived, weakened or refuted, with evidence, in CLAIMS.md.
---
# falsify: try to break the claim before a reviewer does

## Principle

The job is to **refute** the claim, not to confirm it. An agent handed a framework
tends to collect supporting evidence and amplify a wrong premise. In
practice, most refuted claims in multi-agent rounds turn out to be the
*orchestrator's own* hypotheses. So:

- The proposer first writes the claim as a **falsifiable statement**. It names exact
  quantifiers and parameters (field, degree bounds, rate, number of queries, soundness
  regime, timing scope), gives a *kill switch* (the observation that would refute it),
  and describes the smallest experiment that could refute it.
- The falsifier's prompt says: "Your primary task is to verify this, not to redo it.
  If it is wrong, say exactly where; that is worth more than a confirmation."
- Every attempt must **actually run** something: a computation, a script or a search.
  Report real outputs. Never invent them.
- If no counterexample is found, say "could not refute" and list what was tried. Do not
  hide behind vague wording.

Scope: we falsify **our own** claims, protocols, implementations and circuits. This
skill is not for auditing or disclosing flaws in other people's systems.

## Input

A row in `CLAIMS.md` (`ID | claim | proposer | status | falsifier evidence | EVIDENCE refs`)
with status `open`, plus the sources it cites (THEORY.md section, soundness table,
EVIDENCE rows, logs, code, circuits).

## Attack order (cheap and decisive first)

Work through all seven. Stop early only on a clean refutation.

1. **Definitions.** Which notion is actually claimed, and which one does the proof
   establish? Check each layer separately:
   - soundness vs **knowledge soundness** vs **witness-extended emulation** (a
     soundness proof does not give an argument *of knowledge*; a rewinding extractor
     that runs in expected polynomial time is not the same as one with a strict bound);
   - **honest-verifier ZK** vs full (malicious-verifier) ZK; statistical vs perfect vs
     computational; whether ZK survives the PCS openings (hiding commitments, masking
     polynomials, the number of evaluations leaked);
   - whether the application needs **simulation-extractability** (e.g. proofs that can
     be observed and re-randomised by an adversary) and whether it is proven;
   - adaptive vs non-adaptive choice of statement; the relation R = {(x; w)} written
     out, including which values are public.
   Also: does a symbol mean the same thing in the abstract, the theorem and the
   experiment (e.g. "n" as number of constraints in one place and trace length after
   padding in another)? Cross-check against [zk-definitions](../zk-definitions/SKILL.md).
2. **Model and assumptions.** In which model is the theorem proven: ROM, AGM, GGM, or
   the standard model? Does it need a **trusted setup** (and is that stated in the
   abstract), a universal/updatable SRS, or none? Is a **conjecture** used, such as a
   proximity-gap or list-decoding conjecture for Reed–Solomon codes beyond the proven
   range (unique decoding / Johnson bound)? Is a hash function modelled as a random
   oracle while the implementation uses an algebraic hash with a different analysis?
   Every assumption the proof uses must appear in the theorem statement; an unstated
   one is a `weakened` verdict at least.
3. **Fiat–Shamir compilation.** For every non-interactive claim: does the transcript
   absorb the statement, public inputs, all commitments and the parameters, in the
   order they are produced? Is the multi-round soundness loss (round-by-round
   soundness, not just the interactive bound) accounted for? Do paper and code agree?
   Hand this to [fiat-shamir-audit](../fiat-shamir-audit/SKILL.md) and record its
   report path here.
4. **Small-parameter exhaustion.** Try the smallest fields (F₁₇, F₉₇), smallest degrees
   and number of variables (d = 1, μ = 1, 2), the smallest folding factor and the
   boundary rate, degenerate statements (all-zero witness, empty lookup table, a single
   row) and the *largest* configuration used in the experiments. Check completeness
   exhaustively and soundness empirically (cheating-prover success frequency vs the
   claimed bound) with `skills/sage-check`. One finite counterexample settles the
   question.
5. **Numeric recomputation.** Recompute every number in the claim from the raw logs.
   Do not use the paper's table or a previous summary. Check:
   - that the rows of a table come from the *same* configuration. Mixing the
     fastest prover time from one rate with the smallest proof from another is a
     classic failure;
   - that "best vs best" is really best vs best, and the ratio uses the stated protocol;
   - arithmetic inside tables (sums of phase times, proof-size components, soundness
     terms, rounding: `round` vs `ceil` on bits can differ by exactly 1);
   - that the same number is identical everywhere it appears: abstract, introduction,
     evaluation, appendix;
   - that every timed run actually **verified** (a fast prover producing a rejected
     proof is not a result), and that failures are attributed correctly — an
     out-of-memory kill is not a "timeout" until the log says so.
6. **Fairness at equal security.** Are both arms at the **same number of bits** and in
   the **same regime** (provable vs conjectured)? Same statement (the same computation,
   not the same constraint count across different arithmetizations)? Same timing scope
   (witness generation, preprocessing, setup in or out)? Same threads, SIMD/asm, GPU,
   commit? Are P time, V time and proof size reported together, and recursion or
   wrapping costs listed separately? A cited number never reproduced locally, or a
   single-configuration win reported as general, weakens the claim. Cross-check with
   `skills/baseline-pin`, `skills/bench-protocol` and
   [soundness-budget](../soundness-budget/SKILL.md); recompute the soundness budget independently
   rather than re-reading the theorist's table.
7. **Literature pre-emption.** Search for the core identity, PIOP or optimisation under
   other names. Check: the target paper's own citations; ePrint from the last 24
   months; follow-ups citing the baseline; **grey literature** (project repositories,
   design notes, blog posts, talks, specifications of production systems), which is
   where many ZK engineering ideas first appear; the textbook treatment (ask
   `lit-scout`). A reformulation of known work ("this PIOP is exactly sum-check over
   a different basis") downgrades novelty even when everything is correct. Record the
   ePrint, DOI or URL with an access date. Never cite from memory; if a reference
   cannot be verified, write "needs verification".

### Circuit claims

A claim of the form "circuit C correctly implements function f" (or "is not
under-constrained") is a separate class. Run the seven steps where they apply, and in
addition hand it to [circuit-audit](../circuit-audit/SKILL.md): under- and
over-constraint checks, witness uniqueness by exhaustion on a small field, differential
tests between the witness generator and the constraints, range and wrap-around (mod p)
checks, non-deterministic hints. A single second witness for the same public input
refutes an "is sound" claim.

## Verdict taxonomy (write into the CLAIMS.md status column)

| verdict | meaning | required evidence |
|---|---|---|
| `survived` | every attack in the order above was attempted and none succeeded | list of attempts, with commands and outputs or the searches run |
| `weakened` | true only under an extra hypothesis or assumption, in a weaker model, at a lower or conjectured security level, over a smaller parameter range, with a smaller constant, or with less novelty than claimed | the precise restated claim, plus the counterexample or recomputation that forced it |
| `refuted` | a counterexample, a recomputation contradicting the number, or prior art containing the result | a minimal reproducible counterexample (script plus output) or the exact prior-art citation |

A `weakened` verdict must include the **replacement claim text**. The proposer either
adopts it or appeals to `pi-orchestrator`. Keep `refuted` rows in the table with
their reason, so no one repeats the dead end.

## Output format

```markdown
| C7 | The toy PIOP has knowledge soundness error ≤ 2d/|F| per round and the FS-compiled argument gives ≥ 100 bits over F_{p^2} for d ≤ 8 | theorist | weakened | sage-check over F_17, F_97 (checks/c7.py → results/c7.txt): completeness holds on all instances; cheating-prover frequency within the bound. Recomputation (soundness/c7.py): the 100-bit figure uses the conjectured list-decoding regime for the FRI term; in the proven (Johnson) regime the total is 91 bits. FS transcript audit: no finding. Replacement: "... ≥ 91 bits proven, ≥ 100 bits under the list-decoding conjecture" | E14, E15 |
```

(Toy row: the bounds and bit counts are illustrative, not from any real system.)

Also append to the shared errata section (`STATE.md` → "Errata and rolling updates")
when a verdict changes something other agents rely on. State which source now wins.

## Veto

`falsifier` holds a veto. No claim with status `open` or `refuted` may appear in
`paper/`. A `weakened` claim may appear only in its restated form. `writer` checks
CLAIMS.md before each section, and `submission-rebuttal` re-checks before submission.

## Review-brief pattern (for parallel falsifier sub-agents)

When fanning out, give each sub-agent:

- one group of claims (definitions and model; Fiat–Shamir and soundness budget;
  arithmetic and units; performance numbers and fairness; circuits; artifacts and
  links; novelty);
- the verdict labels required on the first line (`REFUTED` / `CONFIRMED` / `UNVERIFIABLE`);
- a "do NOT do" list naming what the other sub-agents cover;
- an instruction to read the other sub-agents' outputs and **explicitly adjudicate any
  conflicts**.

## Pitfalls (distilled)

- Checking soundness and calling it knowledge soundness: the extractor is the part
  that is usually missing.
- Proving HVZK and claiming ZK for the non-interactive argument without arguing about
  the PCS openings.
- A security level computed with a conjectured bound in one table and compared against
  a baseline's proven bound in another.
- A proof that is correct for the interactive protocol, with no account of the
  Fiat–Shamir loss for a many-round protocol.
- Re-reading the proposer's soundness table instead of recomputing it.
- Benchmarks that never call the verifier.
