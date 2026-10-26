---
name: mock-review
description: Use before submission (about 3 days and again 1 day before) or before a rebuttal to simulate venue-calibrated reviews. Runs falsify-first ZK reviewer personas (soundness reviewer for proofs and Fiat–Shamir, implementation-and-benchmark reviewer, application-and-industry-relevance reviewer, plus optional data-auditor and desk-reject auditor), verifies their findings, and outputs scored reviews plus an executable fix list.
---

# Mock review

## Principles

1. **Falsify first.** The writer first produces a list of falsifiable statements
   (from `CLAIMS.md` and the contribution list: "the argument is knowledge sound
   with error ≤ (m + N)/|𝕂|", "the prover is 2× faster at 100-bit proven soundness",
   "the circuit has a unique witness for every public input"). Reviewers are told to
   break them, not to praise.
2. **Personas are views of one analysis, not independent experts.** Say so in the
   output. Do not present simulated scores as a prediction of the real outcome.
3. **Only findings that can be located in the source, data or a script are accepted.**
   Reviewer agents produce false positives; the coordinating agent verifies each
   finding (reproduce the counterexample, open the log, recompute the cell).
4. **Read-only.** Mock reviewers never edit the paper; they write `REVIEWS.md`.
5. **Evidence-based and constructive.** Each weakness cites a page/section/equation
   and proposes a fix.

## Personas

| persona | stance | checks |
|---|---|---|
| **Soundness reviewer** (proofs and Fiat–Shamir) | senior theorist who assumes the proof is wrong | which notion is proven vs claimed (soundness vs knowledge soundness vs witness-extended emulation; HVZK vs ZK; simulation-extractability); the extractor actually extracts (rewinding bound, PCS extraction, decoding radius); the simulator covers every PCS opening and query; model, setup and every conjecture stated in the theorem; Fiat–Shamir transcript complete and the multi-round loss accounted for; concrete soundness table recomputed term by term, proven and conjectured separated; hypotheses vs the paper's own parameter table; small-field counterexamples; body vs appendix formula mismatches |
| **Implementation and benchmark reviewer** | builds provers for a living | baseline is the current release of the strongest system, pinned; same soundness level and regime on both arms; same statement (not the same constraint count across arithmetizations); timing scope (witness generation, preprocessing, setup) identical; same threads and hardware features (AVX-512/asm/GPU); P time, V time, proof size and memory all reported; recursion/wrapping listed separately; every timed proof verified; prover-phase breakdown explains the gain; scaling over sizes, not one point; artifact builds and runs |
| **Application and industry-relevance reviewer** | practitioner from a team deploying ZK | does the statement match a real use (credentials, rollups, zkVMs, ML)? trust model (who runs setup, who holds the witness, what is public); on-chain cost (gas, calldata) if claimed; circuit correctness (under-constraint, range checks, field wrap-around) argued, not assumed; novelty vs the closest prior work **including grey literature** (project docs, blog posts, production systems); can I restate the idea after the overview? is "first"/"optimal"/"practical" justified? |
| Data auditor (optional) | accountant | recomputes every ratio, sum, phase total, proof-size component and soundness term in every table from EVIDENCE rows and logs |
| Desk-reject auditor (optional) | PC chair | page limit, template, fonts, page numbers, anonymity (run `anonymize-check`, incl. repository and package-manifest identities), every URL resolves, references complete |

Pick 3 (default) to 5 personas; for a protocol/theory paper the soundness reviewer
is mandatory, for a system paper the implementation reviewer, for an application
paper the application reviewer (and the soundness reviewer reads the circuit
argument). Weights and venue anchors from
[venue-calibration](../venue-calibration/SKILL.md).

## Procedure

1. **Brief** (`reviews/REVIEW-BRIEF.md`): venue, paper path + hash, falsifiable
   statement list, persona assignments, what is out of scope (e.g. "we do not rerun the
   full benchmark; historical logs are not presented as fresh reproduction").
2. **Dispatch** persona agents in parallel, each with the brief and instructions to
   try to refute first.
3. **Verify** each finding: reproduce counterexamples with a script, recompute numbers,
   open cited logs. Mark each finding `confirmed | false-positive | unverifiable`.
4. **Score** with the six-point scale + confidence 1–4 per persona, plus dimension
   scores (problem value, novelty, technical soundness, experimental persuasiveness,
   precision of statements, reproducibility). Dimension scores are not averaged into
   an acceptance probability.
5. **Fix list** (`reviews/SUBMIT-FIXES.md`): items graded **must-fix** (compliance,
   integrity, confirmed errors) / **should-fix** / **won't-fix (with reason)**, each
   with file:line, old text, new text, and why. Include "good news" items (what was
   checked and found correct) so authors do not second-guess sound parts.
6. **Rebuttal prep**: list the 3–6 questions most likely to be asked and the evidence
   that answers each (feeds the `rebuttal` skill).
7. Human author decides which fixes to apply; after fixes, rerun the
   implementation reviewer (data) and desk-reject personas.

## Output format (`REVIEWS.md`)

```
## Round <k> — <date> — venue profile: <venue> — paper hash <sha256[:12]>
| persona | score | confidence | top-3 weaknesses | action item → agent |
|---|---|---|---|---|
Scope and limits of this review: <what was read, what was not rerun>
Personas are views of one analysis, not independent experts.

## Reviewer A — <persona>
Summary: 2–3 sentences.
Strengths:  S1 ... S2 ... S3 ...
Weaknesses: W1 (severity high|med|low, location, evidence, suggested fix) ...
Questions:  Q1 ... Q2 ...
Scores: overall x/6, confidence y/4; dimensions: ...
Recommendation: ...

## Reviewer B ...
## Reviewer C ...

## Meta-review (simulated discussion)
Score table | consensus points | disagreements | decisive issues |
subjective band with conditions (not a statistic) | top preparation items for rebuttal

## Verified findings
| id | finding | status confirmed/false-positive | evidence (script/log) |
```

## Frequent catches

| category | catch | prevention |
|---|---|---|
| anonymity | footnote URL to a personal code host account, or an author name in `Cargo.toml` / `package.json` | anonymous mirror only; run `anonymize-check` |
| soundness | "argument of knowledge" claimed, only soundness proven (no extractor) | prove knowledge soundness or weaken the claim; zk-definitions <!-- TODO: link once skill exists --> |
| soundness | HVZK proven, ZK claimed; PCS openings or FRI queries leak evaluations the simulator does not produce | count revealed evaluations; size the masking; state the notion precisely |
| soundness | headline security uses a conjectured proximity bound without saying so | proven and conjectured columns in the soundness table; abstract names the regime |
| soundness | Fiat–Shamir transcript omits the statement, public inputs or a commitment; multi-round loss ignored | list the transcript explicitly; fiat-shamir-audit <!-- TODO: link once skill exists --> |
| soundness | challenge sampled from the base field where the bound needs the extension | use |𝕂| in every algebraic term; recompute with soundness-budget <!-- TODO: link once skill exists --> |
| theory | body formula differs from appendix formula | copy from the proof source, never retype |
| theory | theorem hypothesis (field size, rate, degree bound) excludes some of the paper's own parameter sets | run the parameter table through each theorem |
| theory | completeness fails at an edge case (challenge equal to a table entry, padding row, empty table) | exhaustive check over a small field (`skills/sage-check`) |
| benchmark | baseline at a different security level or regime | re-parameterise the baseline; soundness column in every comparison table |
| benchmark | timing scope differs between arms (witness generation or preprocessing in one, not the other) | one timing-scope sentence for all arms; excluded phases in their own table |
| benchmark | only prover time reported; proof size or verifier time worse and omitted | P, V, proof size, memory together |
| benchmark | comparison against an outdated release of a fast-moving library | pin the current release; date the comparison |
| benchmark | constraint counts compared across arithmetizations | compare the same computation end to end |
| circuits | under-constrained gadget (a second witness for the same public input), field wrap-around in a range check | circuit-audit <!-- TODO: link once skill exists -->; witness-uniqueness check on a toy field |
| data | two incommensurable counters in one column | state each column's counter source in the caption |
| writing | composite gain credited to one component | label each number with its configuration; prover-phase breakdown |
| writing | "post-quantum", "transparent", "succinct" without the assumption, setup or bound | name the assumption and the bound once, in the theorem and the abstract |
| citations | fabricated or wrong metadata, wrong author count; concurrent work missed | `lit-scout` verifies each entry against DOI/ePrint; grey-literature pass |
| layout | overprinting after negative vspace near floats; protocol box wider than the column | PDF overlap scan; box width checked in the target template |
| strategy | best evidence (an ablation, a scaling series) not in the paper | ask "which experiment would convince a skeptic?" and check it is in the body |
