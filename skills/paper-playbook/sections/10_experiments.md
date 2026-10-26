# 10 Implementation and evaluation

Full procedure, table set and fairness statements:
[experiments-writing](../../experiments-writing/SKILL.md). Measurement protocol:
[bench-protocol](../../bench-protocol/SKILL.md); baselines:
[baseline-pin](../../baseline-pin/SKILL.md).

## Nine-part structure

```
[opening]        "We implement <system/circuit> in <language/library>, changing only
                 <component>; everything else is that of <baseline>, so every gain below
                 is due to <component> alone." Artifact footnote. Signpost: §x.1 fixes the
                 setup, §x.2 reports results.
[baselines]      One bullet per baseline: name + citation + what it is + pinned commit +
                 where it runs (our pipeline vs their artifact) + repository link.
                 Paragraph on why some systems are "reported for context" only (different
                 statement, different setup model).
[platform]       CPU model and frequency, cores and threads, SIMD/asm features, GPU model
                 and driver if used, memory, compiler/toolchain and library commits,
                 repetitions and statistic, "every timed run verifies its proof".
[parameters]     Table: one row per parameter set: field/curve, PCS parameters (rate,
                 queries, folding factor), grinding, soundness per term and total,
                 proven/conjectured (the table from §9 D, or a pointer to it).
[timing scope]   One sentence fixed for the whole section: whether prover time includes
                 witness generation, preprocessing and setup; where the excluded parts
                 are reported.
[workloads]      The statements proved: circuits or programs, their size in each
                 system's own unit (constraints, rows × columns, cycles), compiler
                 versions; why these workloads.
[results]        Signpost sentence + figure (prover-phase breakdown, or scaling in the
                 statement size) + main table with P time, V time, proof size, peak
                 memory, ratio. Three bold-headed claims, e.g.
                 \textbf{Prover speed-up.} scope → range → two concrete points.
                 \textbf{The components compose, and neither suffices alone.} ablation.
                 \textbf{What it costs.} proof size, verifier time, memory, setup.
[comparison]     Table vs published systems on the same statement and soundness level;
                 incomparable rows (different statement or soundness level) marked with a
                 symbol and "—" in the ratio column; measured vs reported numbers both
                 given; recursion/wrapping costs in their own columns.
[limitations]    Remarks: where we lose (small statements, verifier time, proof size),
                 parallelism policy, GPU vs CPU, regime (proven vs conjectured).
```

Application/circuit papers add a **circuit correctness** paragraph before the
results: how each gadget was checked for under-constraint (circuit-audit
<!-- TODO: link once skill exists -->), the test vectors, and the witness-generation
cost.

## Number discipline (summary)

1. Single data source (EVIDENCE rows → json/csv → tables); no hand-typed numbers.
2. Scope sentence before every range (workloads, sizes, soundness level and regime).
3. Exclusions stated explicitly.
4. Reproduced vs reported baseline numbers both given.
5. Incomparable is not forced into a ratio; constraint counts from different
   arithmetizations are not compared as if they were one unit.
6. Attribute each gain to the right component (prover-phase breakdown).
7. Disclose costs: proof size, verifier time, memory, setup/SRS, preprocessing.
8. The ablation is the strongest evidence; include it in the body.
9. Keep measured ratios; normalised variants go to the appendix.
10. Baseline configuration details that favour or disfavour the baseline are
    disclosed (appendix is fine).

## Checklist

- [ ] Opening sentence isolates the changed component.
- [ ] Platform paragraph has the six elements (toolchain + commits, CPU/GPU, threads,
      hardware features, repetitions + statistic, proof verification in every run).
- [ ] Timing-scope sentence present and identical for every arm.
- [ ] Parameter table has proven and conjectured soundness; every arm at the same level.
- [ ] P time, V time, proof size and memory reported together.
- [ ] Ablation in the body.
- [ ] Every table cell traceable to an EVIDENCE row.
