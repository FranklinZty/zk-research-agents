---
name: abstract-craft
description: Use when writing or tightening a paper abstract (and its plain-text submission-form twin). Applies the three-part paradigm (state of the art, our technique, results and artifact) with a sentence-level function table and an overclaim filter.
---

# Abstract craft

## Inputs

`CLAIMS.md` (survived/weakened claims), `EVIDENCE.md` (numbers), the contribution
list (`paper/sections/intro.tex`), target venue (for length norms, see
[venue-calibration](../venue-calibration/SKILL.md)).

## Procedure

1. **Write a one-line viewpoint** of the paper: "We view X as Y." If this sentence
   cannot be written, the abstract is not ready; go back to the overview.
2. **Fill the sentence-function table** below in `paper/ABSTRACT_PLAN.md` (Chinese or
   English bullet map is fine; discuss it with the human author before prose).
3. **Draft three paragraphs** (see `paper-playbook/sections/02_abstract.md`).
4. **Overclaim filter** (automatic pass, then manual):
   - forbidden: novel, groundbreaking, rigorous guarantee, optimal (unless proven),
     significantly (without a number), first (unless a literature search in
     `LITERATURE.md` supports it, and even then prefer "to our knowledge, the first").
   - every number → EVIDENCE row id noted in a LaTeX comment `% EV:E12`.
   - every scope noun ("12 circuits", "all fields of characteristic p > 2^{60}") →
     matches the parameter/soundness tables.
   - soundness status stated: every security level says whether it is **proven** or
     rests on a **conjecture** (e.g. a proximity-gap conjecture beyond the Johnson
     bound); and the **setup** is named as transparent, universal (updatable SRS) or
     trusted (circuit-specific).
   - "post-quantum" / "plausibly post-quantum" only with the assumption it rests on
     (e.g. "collision-resistant hashing in the ROM"); never for schemes whose
     soundness or binding uses pairings or discrete log.
5. **Consistency pass**: abstract ↔ contributions ↔ conclusion use the same numbers,
   the same order and the same framework name.
6. **Length**: follow the venue norms in
   [venue-calibration](../venue-calibration/SKILL.md) and the CFP; the submission-form
   limit can be shorter than the PDF abstract.
7. **Plain-text twin** `paper/abstract_plain.txt` for the submission form.

## Sentence-function table (7–10 sentences)

| # | function | notes |
|---|---|---|
| S1 | field consensus + bottleneck | no citation needed |
| S2 | existing routes, grouped, venue'year | 1–2 representatives per route |
| S3 | open question | "However, ... has remained open." |
| S4 | our object and viewpoint | "We present/propose X, which views ... as ..." |
| S5–S6 | technical points, one each | "First, ... At the same time, ..." or structure → bound → construction |
| S7 | what we *prove* (property, not activity) | not "we analyse security" but "we prove knowledge soundness in the ROM with error ≤ 2^{-λ} for ..." |
| S8 | scope → range → concrete points vs named baseline | same soundness level, same machine; if true, say so |
| S9 | artifact / formalisation / invitation for analysis | exact scope of formal verification |

## Upgrading weak sentences

| weak | strong |
|---|---|
| "Our SNARK is efficient." | "At 128-bit provable soundness, proofs are X kB and the prover is 2.1–3.4× faster than Y on the same machine." |
| "Our scheme is secure." | "We prove knowledge soundness in the ROM; at the default parameters soundness is λ₁ bits proven, or λ₂ bits under the proximity-gap conjecture of [A]." |
| "Our protocol needs no trusted setup and is post-quantum." | "The setup is transparent, and soundness relies only on collision-resistant hashing in the ROM, which makes it plausibly post-quantum." |
| "We formally verify our results in Lean." | "Completeness and soundness of the sum-check core (Lemmas 2–5) are machine-checked in Lean 4; the Fiat–Shamir compilation is not." |
| "We unify prior work." | "The lookup arguments of [A] and [B] are the cases k=1 and t=1 of our construction." |

## Headline-range hygiene

- Lower end = the most conservative **measured** number; if the upper end is an
  estimate, label it as an estimate in the table and say "up to ... (estimated)".
- Never mix instances below the claimed security level into the range, and never mix
  proven and conjectured soundness levels in one range.
- If a baseline number is reproduced rather than taken from the paper, the abstract
  compares against the reproduced number and the paper reports both.

## Output

`paper/sections/abstract.tex`, `paper/abstract_plain.txt`, and a short diff note in
`paper/CHANGELOG.md`.

See toy examples: `skills/paper-playbook/examples/toy_abstracts.md`.
