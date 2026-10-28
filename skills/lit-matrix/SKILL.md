---
name: lit-matrix
description: Build and lint the ZK related-work matrix (work, venue/year, arithmetization, PCS, setup, assumptions/model, post-quantum?, field, P/V/π asymptotics, concrete numbers + source, code available?, our delta) and the novelty-check log in LITERATURE.md. Use in P1, whenever a new baseline appears, and before writing the related-work section.
---

# lit-matrix

The matrix is the single place where "who did what, under which parameters, with which numbers" lives.
Writers copy from it; the falsifier attacks it; baselines are chosen from it.

## Format (in `LITERATURE.md`)

```markdown
## Related-work matrix

| work | venue/year | arithmetization | pcs | setup | assumptions/model | pq? | field | p/v/π asymptotics | concrete numbers + source | code? | our delta |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [@Toy23] ToyPlonk | ePrint 2023 | Plonkish | KZG | universal | AGM + ROM, q-DLOG | no | BN254 scalar | O(n log n) / O(1) / O(1) | 4.2 s P, 0.8 kB @ 2^20 gates (Tab. 3) | yes https://... | we ... |
| [@Toy24] ToyFRI | CONF 2024 | AIR | FRI | transparent | ROM, CR hash; proximity conj. | plausible | Goldilocks | O(n log n) / O(log² n) / O(log² n) | 90 kB, 100-bit proven (Tab. 2) | no | we ... |
```

Column rules (enforced by `scripts/lit_matrix.py`):

- **work** — bib key (`[@key]` or `\cite{key}`) or ePrint id, plus a short human name.
- **venue/year** — venue of the version you cite (ePrint-only is fine, say so).
- **arithmetization** — R1CS / Plonkish / AIR / CCS (or `n/a` for a standalone PCS or PIOP); name custom gates
  and lookups if they matter.
- **pcs** — KZG / IPA / FRI / STIR / WHIR / Brakedown / Binius / … (`n/a` for an information-theoretic PIOP).
- **setup** — `trusted` (circuit-specific), `universal` (updatable SRS) or `transparent`.
- **assumptions/model** — AGM / ROM / GGM / standard model, q-type assumptions, hash assumptions, and every
  conjecture soundness relies on (e.g. a proximity-gap conjecture). Write "proven" vs "conjectured" here.
- **pq?** — `yes` / `no` / `plausible` / `n/a`; anything but `no`/`n/a` needs its assumption in the previous column.
- **field** — the field or curve (BN254, BLS12-381, Goldilocks, BabyBear, M31, binary tower, …) and any extension
  used for soundness.
- **p/v/π asymptotics** — prover / verifier / proof size, in the cost measure the community uses (field ops, MSM
  size, hashes, group elements).
- Security level, hardware and timing scope (witness generation in or out) go into the numbers cell, never
  "normalised" away.
- **concrete numbers + source** — numbers *with* a pointer (Tab./Fig./Sec./p.) or `measured E<n>` (an EVIDENCE
  row, if we re-ran it). Numbers from a paper and numbers we measured are never mixed in one cell without saying so.
- **code?** — `yes <url>` / `no` / `unknown`.
- **our delta** — what we do that this row does not. `none` is an honest answer and triggers a PI decision.

## Procedure

1. Seed from `references/reading-lists/<area>.md`, then expand with `eprint-search` (last 12 months first,
   including its grey-literature pass). To grow the reading list itself, the bibliographic notes of the reference books — [CY24 §Bibliographic notes, section:bibliographic-notes] for the hash-based line, and the references of the relevant Thaler chapter (navigation: [references/books/thaler/MAP.md](../../references/books/thaler/MAP.md)) for the algebraic one — are a good source of entries for `references/reading-lists/`. Take only the bibliographic entry (authors, title, venue/ePrint id), never the books' commentary, and add it only after [bib-verify](../bib-verify/SKILL.md) has confirmed it.
2. One row per *result* (a paper with two incomparable results gets two rows).
3. Fill numbers only from the paper's tables/figures; if the paper's parameters differ from ours, note it in
   the numbers cell (security level, hardware, timing scope) instead of "normalising" silently.
4. Mark the 2–4 rows that are the real competitors (**bold** the work cell); `baseline-engineer` pins those.
5. Lint: `python3 skills/lit-matrix/scripts/lit_matrix.py LITERATURE.md --bib refs.bib`.
6. `python3 skills/lit-matrix/scripts/lit_matrix.py --template` prints an empty skeleton.

## Reading the matrix for gaps

Sort by *arithmetization*, then by *pcs*, then look for (a) arithmetization × PCS × setup cells with no row
(application gap — weakest kind of novelty, must be argued), (b) a technique used with one PCS or field but not the
neighbouring one (transfer, e.g. a KZG-only trick on a hash-based PCS), (c) a parameter every row fixes to the same
value (field, FRI rate, folding factor; a "hidden fixed parameter" — hand to `idea-miner`), (d) P/V/π asymptotics
that nobody has a lower bound for, (e) rows whose soundness is only conjectured where a proven variant is missing.
