---
name: paper-playbook
description: Use when drafting or restructuring a ZK paper (protocol/theory, system/implementation, or application/circuit) in IACR LNCS, IACR journal or security-conference format. Gives the overall skeleton, page budget per paper type, and the rhetorical moves of every section from title to appendix (relation/PIOP/PCS/FS preliminaries, protocol boxes, completeness/knowledge soundness/ZK/concrete soundness), with good/bad toy examples.
---

# Paper Playbook — structure and rhetorical moves for ZK papers

The playbook fixes the **form** of a paper; the content is always rewritten for the
new paper. Templates here are structures, not wording to copy.

## Five principles (read first)

1. **Every number has one source.** Abstract, intro, body, tables and appendix quote
   the same value from the same row of `EVIDENCE.md`. No number enters the paper
   without an EVIDENCE row (SPEC §3). Numbers are generated or grep-checked, never
   retyped from memory.
2. **Write falsifiable claims first, then try to break them.** Each contribution is
   first written as one sentence in `CLAIMS.md`; the `falsifier` and `reviewer-sim`
   agents attack it before the prose is polished.
3. **Form is fixed, wording is new.** Reuse the skeleton and the moves, never the
   sentences of a previous paper.
4. **The body carries the weight; the appendix only supplements.** Reviewers are not
   obliged to read appendices. No claim in the body may depend solely on an appendix.
5. **Late edits are only necessary and verifiable ones.** In the last 24 hours before
   a deadline, fix errors only; no stylistic rewrites.

## Section files

| file | section |
|---|---|
| `sections/00_overall_structure.md` | skeleton, page budget per paper type, layout hard rules, notation freeze |
| `sections/01_title.md` | title patterns and anti-patterns |
| `sections/02_abstract.md` | three-part paradigm (state of the art → technique → results/artifact) |
| `sections/03_introduction.md` | funnel → pipeline → objective equation → open question |
| `sections/04_contributions.md` | lead-in + ordered bullets; wording rules |
| `sections/05_technique_overview.md` | recall routes → reduce to questions → insights answer them |
| `sections/06_related_work.md` | organise by axis not by time; comparison table; bridge paragraph |
| `sections/07_preliminaries.md` | notation; relation ℛ = {(𝕚, 𝕩; 𝕨)}, PIOP, PCS, Fiat–Shamir; only what is reused |
| `sections/08_main_construction.md` | relation → PIOP protocol box (cryptocode) → theorem → compilation → cost/selection rule |
| `sections/09_security_correctness.md` | completeness, knowledge soundness (extractor), zero knowledge (simulator), concrete soundness table (proven vs conjectured) |
| `sections/10_experiments.md` | nine-part evaluation section; timing scope; number discipline |
| `sections/11_conclusion.md` | two-to-three sentence conclusion |
| `sections/12_appendix.md` | appendix organisation; "not load-bearing" rule |
| `examples/toy_abstracts.md` | good/bad abstracts for three toy papers |
| `examples/toy_intro_and_contributions.md` | toy intro funnel + contribution list, good vs bad (T1) |
| `examples/toy_overview_and_related.md` | toy related-work table, contrasting-verb bullets, overview headings, worked example |
| `examples/toy_security_and_eval.md` | toy theorem statements, extractor/simulator sketches, soundness and comparison tables |

Toy papers used throughout (all numbers are **invented and illustrative**):

- **T1 (protocol / theory):** "ToyLookup", a lookup argument whose prover cost is
  independent of the table size, via a sum-check over the logarithmic derivative.
- **T2 (system / implementation):** "ToyProver", a memory-bounded FRI prover that
  streams the low-degree extension into the Merkle commitment.
- **T3 (application / circuit):** a range-checked anonymous-credential circuit that
  replaces bit decompositions by lookups and verifies a non-native signature.

Page budget by paper type (LNCS, ~25–30 pp. body; details in `00_overall_structure.md`):

| part | protocol / theory | system / implementation | application / circuit |
|---|---|---|---|
| intro (incl. related work, contributions, overview) | ~25% | ~25% | ~25% |
| preliminaries | ~12% | ~10% | ~10% |
| construction | ~30% | ~25% (system design) | ~20% (circuit specification) |
| security | ~20% (+ appendix proofs) | ~5% (concrete soundness, FS) | ~10% (circuit correctness, trust model) |
| evaluation | ~8% | ~30% | ~30% |

## Workflow (used by the `writer` agent)

1. Freeze notation and the framework's one-word name (`00_overall_structure.md`).
2. Write `CLAIMS.md` rows for each contribution; get falsifier verdicts.
3. Draft in this order: contributions → technique overview → main construction →
   experiments → related work → introduction → abstract → title → conclusion.
   (The abstract is written last because it summarises the other sections.)
4. After each section, run the section's checklist (end of each file).
5. Hand to `reviewer-sim`; iterate; hand to `submission-rebuttal`.

## Related skills

- [abstract-craft](../abstract-craft/SKILL.md), [technique-overview](../technique-overview/SKILL.md),
  [related-work-writing](../related-work-writing/SKILL.md),
  [experiments-writing](../experiments-writing/SKILL.md),
  [venue-calibration](../venue-calibration/SKILL.md), [polish-writing](../polish-writing/SKILL.md)
- ZK theory: [zk-definitions](../zk-definitions/SKILL.md), [piop-pcs-compile](../piop-pcs-compile/SKILL.md),
  [soundness-budget](../soundness-budget/SKILL.md), [fiat-shamir-audit](../fiat-shamir-audit/SKILL.md)
- Not yet available (later batch): circuit-audit <!-- TODO: link once skill exists -->.
- LaTeX skeleton: `templates/paper/`.
