---
name: related-work-writing
description: Use when writing or auditing the Related Work section. Organises prior work by axis rather than chronology, builds the asymptotic comparison table with an "Ours" row, writes the bridge and "Our work" paragraphs, and checks every characterisation of prior work against its source.
---

# Related-work writing

## Inputs

`LITERATURE.md` (related-work matrix from `lit-scout`), `refs.bib` (verified), the
objective equation and framework from the introduction/overview.

## Procedure

1. **Choose axes.** From the literature matrix pick one or two axes along which all
   relevant works improve (what they reduce, what structure they exploit). Write them
   as a pair of contrasting verbs if possible ("restricts where" / "restricts how";
   "smaller proofs" / "faster provers"). For ZK, the default axes are the
   **arithmetization** (R1CS / Plonkish / AIR / CCS) and the **PCS** family (pairing-based
   KZG; discrete-log IPA; hash-based FRI / STIR / WHIR / Brakedown / Binius); see
   "Organising ZK related work" below.
2. **Place each work.** For each work record: axis, method in one line, cost formula
   in its own notation translated to ours, scope restrictions (†/‡), venue'year.
   Verify each cost formula against the original (page/section noted in
   `LITERATURE.md`). Where later papers paraphrase an earlier paper's bottleneck,
   compare with the earlier paper's own experiments section.
3. **Build the table** (`templates/paper/sections/related_table.tex` style): grouped
   rows, last row `\textbf{Ours}`, caption defines all symbols. For SNARK papers use the
   standard comparison table below.
4. **Write the paragraphs**: lead-in (3 sentences) → classic works on axis 1 (one
   sentence each, shared limitation last) → recent works (two contrasting bullets) →
   bridge (`\textbf{Insight from ...}`) → `\textbf{Our work.}` (five sentences) →
   complementary approaches → concurrent work.
5. **Tone filter**: remove "unfortunately", "fail", "naive", "suffer", "only";
   replace with factual scope statements ("... assumes ... rather than showing ...",
   "... instantiates a single case, leaving open ...").
6. **Self-citation check**: own prior work in third person, critiqued like others.
7. **Coverage check** with `lit-scout`: the last 12–18 months of ePrint plus the
   grey-literature pass for the topic keywords; any close concurrent work gets a
   labelled paragraph.
8. **Bib hygiene**: published versions over preprints when they exist; ePrint entries
   with the exact author list of the ePrint page; braces around acronyms in titles for
   `splncs04`. (Bib verification itself is owned by `lit-scout`.)

## SNARK comparison table (standard)

Reviewers expect this table; leaving it out is a common revision request. One row per system, grouped by PCS or
arithmetization, `\textbf{Ours}` last. All columns are filled from the related-work matrix (`LITERATURE.md`).

```latex
\begin{table}[t]\centering\scriptsize
\caption{Comparison of SNARKs for <relation>. $n$: number of constraints/gates; $|\mathbb{G}|$, $|\mathbb{F}|$:
group/field elements; $H$: hash evaluations. Setup: T = trusted (circuit-specific), U = universal, Tr = transparent.
PQ: plausibly post-quantum under the stated assumption. Concrete numbers at $n=2^{k}$ and $\lambda$-bit soundness
(p = proven, c = conjectured); \diamond{} = as reported in the cited paper, otherwise measured by us (same machine).}
\begin{tabular}{l c l c c c c c}
\toprule
System & Setup & Assumptions & PQ & $|\pi|$ & $P$ time & $V$ time & Concrete ($|\pi|$ / $P$ / $V$) \\
\midrule
\multicolumn{8}{l}{\emph{pairing-based PCS}} \\
<A>   & U  & AGM, ROM, q-type & no  & $O(1)\,|\mathbb{G}|$ & $O(n\log n)$ & $O(1)$ & \ldots \\
\multicolumn{8}{l}{\emph{hash-based PCS}} \\
<B>   & Tr & ROM, CR hash     & yes & $O(\log^2 n)\,H$ & $O(n\log n)$ & $O(\log^2 n)$ & \ldots \\
\midrule
\textbf{Ours} & & & & & & & \\
\bottomrule
\end{tabular}
\end{table}
```

Column rules: **Setup** and **Assumptions** match the matrix exactly (no upgrading "universal" to "transparent");
**PQ** is "yes" only with the assumption shown; **P/V/π** use the same cost measure for every row; **concrete
numbers** state security level and proven/conjectured status, and rows at a different level are marked, not
silently mixed. Incomparable rows get "—" and a caption note.

## Organising ZK related work

- **By arithmetization**: one paragraph per family (R1CS-based, Plonkish, AIR/STARK, CCS-based folding), each ending
  with the limitation our work addresses in that family.
- **By PCS**: pairing-based, discrete-log, hash-based (and lattice-based only if relevant to the claim); state what
  the PCS choice implies for setup, proof size and post-quantum status.
- **Compiler layer**: folding, recursion and proof composition as a separate paragraph when the contribution
  touches it.
- **Orthogonal / complementary**: hardware acceleration, zkVMs and circuit DSLs, when they compose with ours.
- **Grey literature**: results known only from project docs or blogs are cited as `@misc` with access date and
  archive link (see `eprint-search`, `bib-verify`); say "described in" rather than "proved in".

## Placement in the paper

- IACR LNCS: usually §1.1 inside the introduction.
- Design papers: a "State of the art" subsection in the constraints/design section,
  one paragraph per competitor: who → technical core → its trade-off; last sentence
  points to the performance comparison section.
- Security conferences: often a separate section near the end; keep a short
  positioning paragraph in the introduction anyway.

## Anti-patterns

- A chronological list of summaries without a thesis.
- Characterising a prior work by a number from a secondary source.
- Calling a system "transparent", "post-quantum" or "128-bit secure" when its paper says "universal",
  "plausibly post-quantum" or "128-bit conjectured".
- A table whose "Ours" row differs from the abstract formula.
- Omitting the strongest baseline because it is inconvenient (reviewers will name it).

## Output

`paper/sections/related.tex`, table in the same file or `related_table.tex`,
verification notes appended to `LITERATURE.md`.
