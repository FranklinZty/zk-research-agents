# 00 Overall structure, page budget, layout rules

## Default skeleton (IACR LNCS conference paper)

Page counts are for a body limit of roughly 25–30 LNCS pages; scale proportionally.
Always check the current CFP for the actual limit and for what counts toward it.

| § | title | share of body | job |
|---|---|---|---|
| — | Abstract + keywords | page 1 | state of the art → our technique → results + artifact |
| 1 | Introduction | ~5% | funnel from field to bottleneck; pipeline; objective equation; open question |
| 1.1 | Related Work | ~7% | comparison table + axis paragraphs + bridge + "Our work" |
| 1.2 | Our Contributions | ~4% | lead-in + 3–4 ordered bullets |
| 1.3 | Technique Overview | ~12–15% | recall prior routes → reduce to precise questions → insights → figure |
| 1.4 | Organisation (optional) | 2–3 lines | only if the paper is long |
| 2 | Preliminaries | ~10–15% | notation table; relation, IOP/PIOP, PCS, Fiat–Shamir; only what is reused later |
| 3–5 | Main construction(s) | ~30–35% | relation → PIOP (protocol box) → theorem → compilation → cost / selection rule |
| 6 | Security | ~10–20% | completeness, knowledge soundness (extractor), zero knowledge (simulator), concrete soundness table |
| 7 | Implementation and evaluation | ~12–15% | baselines, platform, parameters + soundness, timing scope, workloads, results, ablation, comparison |
| 8 | Conclusion | ≤ 0.5 page | two to three sentences |
| A– | Appendix | unlimited | proofs, extra tables, reproduction details |

Variants:

- **Protocol / theory papers (CRYPTO/EUROCRYPT/ASIACRYPT/TCC):** the security
  section (proofs of knowledge soundness and ZK) is the largest after the
  construction, often a quarter of the body plus the appendix; the evaluation, if
  any, is short (cost table or a prototype); at TCC there is often no experiments
  section and the technique overview becomes the main exposition.
- **System / implementation papers (TCHES, CCS/S&P/USENIX):** the construction is the
  system design (data flow, memory, kernels); security is mostly inherited and
  shrinks to block D (concrete soundness) plus whatever the system changes
  (Fiat–Shamir transcript, parameters); evaluation grows to ~25–30%.
- **Application / circuit papers (CCS/S&P/USENIX/NDSS/PoPETs, FC/AFT):** two-column
  formats; threat and trust model (who runs setup, who holds the witness, what is
  public) and a system overview are expected early; a circuit specification section
  (gadgets, arithmetization, constraint counts) and a circuit-correctness argument
  replace most of the security section; evaluation carries more weight.
- **SoK papers:** a methodology section and a systematisation table replace the
  construction; evaluation compares systems at equal security on common statements.

## Page discipline

Legal ways to save space, in order of preference:

1. Tighten floats: algorithms `\footnotesize`, tables `\scriptsize` with
   `\arraystretch` 0.88–0.92, `\tabcolsep` 2.5–3pt.
2. Reduce global float/display glue in the preamble (`\textfloatsep`, `\intextsep`,
   `\floatsep`, `\abovedisplayskip`): modest reductions only.
3. Scale TikZ figures by 5–15%.
4. Remove footnote URLs duplicated elsewhere.
5. Only then cut sentences — cut adjectives before content, never cut numbers'
   scoping sentences.

**Forbidden (desk-reject risk):** `geometry` or any margin change, font-size change,
line-spacing change, removing page numbers when the CFP requires them.

**Overprinting trap:** a negative `\vspace` immediately before a float
(`algorithm`/`table`/`figure`) can make text overprint the float in the PDF while the
editor preview looks fine. Put negative glue *inside* the float before `\end{...}`,
or delete it; scan the PDF with the camera-ready overlap checker.

After every edit near the limit, rebuild and confirm the conclusion still ends on the
last allowed page (see `skills/camera-ready`).

## Notation and naming freeze (before writing, grep after writing)

- One concept, one symbol. Keep a table in `paper/NOTATION.md` (symbol, meaning,
  first defined in §). Replace globally and grep for the old symbol afterwards —
  including glued macros like `\inS` produced by careless replacement.
- One name for the framework/object: pick one word (e.g. "unified" vs "general") and
  use it in the title, section headings, figure captions, contributions and overview.
- Write membership as `$x \in S$`, not `$S \ni x$`.
- Theorem numbers in the appendix refer back with `\Cref` to the body numbering; do
  not renumber restated theorems.
- Formulas in the overview are **copied** from the body statements, not retyped.

## Global style rules (distilled from author preferences)

- Avoid em/en dashes as sentence punctuation; use commas, colons or separate
  sentences. (Ranges like `2--3` are fine.)
- No "explanatory" mini-headings such as "Why X is needed" or "Where the cost goes";
  they read as padding. Use statement-style paragraph headings (see overview file).
- Keep the notation table compact and inside the Notation subsection.
- Make the paper standalone for a general cryptographic reader: the first pages
  (title, abstract, introduction) must summarise the contribution without the body.

## Checklist

- [ ] Section shares roughly match the budget; the conclusion is on the last body page.
- [ ] No layout-changing package; page numbers present; paper size as required.
- [ ] Notation table frozen; old symbols grep to zero.
- [ ] Framework name identical in title, headings, captions, contributions, overview.
