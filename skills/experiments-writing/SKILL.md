---
name: experiments-writing
description: Use when turning benchmark results into the evaluation section. Enforces that every printed number traces to an EVIDENCE.md row, prescribes table designs (parameters, main results, ablation, comparison), fair-comparison statements, and boundary/limitation statements.
---

# Experiments writing

## Iron rule

**Every number printed in the paper (text, table, figure, caption, footnote,
abstract) has an `EVIDENCE.md` row**: `ID | number as printed | command | log path |
commit | machine | date | runs/median`. Tables are generated from the data files
behind those rows (e.g. with the `crbench` table generator), not typed. Put
`% EV:<ID>` comments next to hand-placed numbers so a script can cross-check.

## Procedure

1. **Freeze the data.** Ask `experimenter` for the final json/csv and the EVIDENCE
   rows. Anything measured after the freeze requires a new row and a note in
   `DECISIONS.md`.
2. **Decide the scope sentence** for every range ("on the 9 circuits at 128-bit proven
   soundness"). Scope comes from the parameter/soundness table, generated.
   State the **timing scope** once and keep it everywhere: whether prover time includes
   witness generation, preprocessing (key generation, circuit compilation) and setup.
3. **Write the section** following `paper-playbook/sections/10_experiments.md`.
4. **Generate tables** (below). Mark the best cell per column (bold, optional light
   colour); two-level headers with `\multicolumn`; captions define every abbreviation
   and symbol.
5. **Write the fairness statements** (below) that apply.
6. **Write boundary/limitation remarks** (below).
7. **Cross-check script**: `crbench audit-tex paper/main.tex EVIDENCE.md` (lib/bench),
   or extract every number from the PDF text (`pdftotext -layout`) and match it to
   EVIDENCE rows; unmatched numbers are errors unless they are parameters or
   citations. Record the result in `SUBMISSION.md`.

## Table set

| table | contents | notes |
|---|---|---|
| Parameters | one row per configuration: field/curve, PCS parameters (rate, queries, folding factor), grinding bits, soundness per term and total, proven/conjectured | `\resizebox{\linewidth}{!}` if wide; soundness column mandatory |
| Main results | **one row per circuit or workload**: constraints (or rows × columns), P time, V time, proof size, peak memory, ratio | ratio column states "vs <baseline>" in the header; header says whether P time includes witness generation |
| Preprocessing / setup | per circuit: setup or SRS generation, key generation / circuit compilation, proving- and verification-key sizes | **separate from P time**, never folded into it silently |
| Prover breakdown | per phase: witness, commit, sum-check / quotient, open (and recursion/wrapping if used) | shows where the gain comes from |
| Ablation | each component alone vs composed; failure counts/timeouts for variants that do not work | strongest evidence that the combination is necessary |
| Mechanism check | model-predicted vs measured operation counts (MSM size, NTT size, hashes) | supports a cost model claim |
| Comparison with published work | System, Ref, same statement, constraints, P/V time, proof size, setup, soundness (bits, p/c); "measured by us" vs "as reported" marker; threads/GPU | incomparable rows (different statement or soundness level): symbol + "—" in ratio column + caption explanation |
| On-chain verification | verifier gas, calldata bytes, proof wrapping cost (e.g. to a pairing-based SNARK) | only when on-chain verification is part of the claim |

Constraint counts from different arithmetizations are not comparable; compare the same computation and report
each system's own count, with the compiler version in EVIDENCE.

Layout: `\scriptsize`, `\arraystretch` ≈ 0.92, `\tabcolsep` ≈ 2.6pt; tables at `[t]`;
table captions above tables, figure captions below figures.

## Fair-comparison statements (use the ones that apply)

- **Same pipeline:** "All ratios are against <baseline> run in our pipeline with the
  same <radix/parameters/library commit>; only <stage> differs."
- **Measured vs claimed:** "Rerunning the artifact of [X] on our machine reproduces
  their claimed a–b× as c–d×; we report both."
- **General caution before cross-paper tables:** "Such comparisons must be read with
  care because of differences in libraries, hardware and failure probabilities; we
  mark numbers taken from the original papers with ◇."
- **Metric orientation remark:** "Our goal is throughput; for latency-critical
  applications <other scheme> remains preferable."
- **Parallelism remark:** "All our numbers are single-threaded. Evaluating
  independent instances in parallel helps every scheme equally, so single-thread
  numbers compare designs, not hardware."
- **Security-level parity:** "Both our parameters and the baseline's give λ bits of
  soundness under the same regime (proven / conjectured), computed with
  <soundness calculator commit>; where the baseline's default parameters target a
  different level, we re-parameterise it and report both."
- **Timing scope:** "Prover times include witness generation and exclude
  preprocessing and setup, for every system in the table; preprocessing is reported in
  Table <n>." State it even if it seems obvious.
- **Baseline strength:** "We use the fastest configuration of <library> for the
  baseline (<flags>), not the default one." (Reviewers and shepherds check this.)

## Boundary / limitation statements

- Exclusions: "The k configurations below the claimed soundness level (or relying on a
  conjecture where we claim proven soundness) are excluded from the headline ranges and
  flagged in Table <n>."
- Overheads: "Our prover uses 1.2–1.5× [ill.] the baseline's peak memory, and proofs
  are 0.4 kB [ill.] larger."
- Regime where we lose: "For t ≥ 7 [ill.], [X] is faster because ...; the regimes do
  not overlap." Say it before a reviewer does.
- Not applicable: "Our method requires <condition>; for instances violating it the
  implementation falls back to the baseline (log shows '<message>')."
- Measurement noise: "Absolute times vary with machine load across sessions; all
  ratios come from interleaved back-to-back runs in one session."

## Measurement hygiene to report (and to follow)

- Interleave A/B runs (ABAB...) in the same session; report median and IQR/CI.
- No concurrent heavy jobs; use a bench lock; pin threads.
- Never mix numbers from different sessions in one ratio; if an earlier number is not
  reproducible, retract it explicitly (and say so in the rebuttal if already quoted).
- Proof verification for every timed run (the verifier must accept; a run whose proof
  fails is reported, not dropped).

## Output

`paper/sections/experiments.tex`, generated tables in `paper/tables/`, the
cross-check report in `SUBMISSION.md`.
