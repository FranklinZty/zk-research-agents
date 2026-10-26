# Toy technique overview and related-work table

Invented papers; all numbers and citations illustrative.

## Related-work table (T1, lookup arguments)

```latex
\begin{table}[t]
\centering\scriptsize
\caption{Asymptotic comparison of lookup arguments for $m$ lookups into a table of
size $N$. Prover: field operations and MSM size (group-based PCS); Proof: group and
field elements. $\dagger$: table must be preprocessed per circuit.
$\ddagger$: table must have a succinctly evaluable multilinear extension.
KS: knowledge soundness; all rows in the ROM.}
\label{tab:related}
\renewcommand{\arraystretch}{0.92}
\begin{tabular}{llcccc}
\toprule
Technique & Method & Prover & Proof & Setup & Notion \\
\midrule
\multirow{2}{*}{Grand product} & [C20]          & $O(m+N)$, MSM $m+N$ & $O(1)$     & universal & KS \\
                               & [D22]$^\dagger$ & $O(m)$, MSM $m$     & $O(1)$     & universal & KS \\
\midrule
Log. derivative & [A23] & $O(m+N)$, MSM $m+N$ & $O(\log(m+N))$ & universal & KS \\
\midrule
\textbf{Ours}$^\ddagger$ & & $O(m)$, MSM $m$ & $O(\log m)$ & universal & KS, ZK \\
\bottomrule
\end{tabular}
\end{table}
```

Rules shown: caption defines every symbol and the model; daggers mark scope; the
"Notion" column keeps knowledge soundness and ZK visible; the last row "Ours" matches
the formula in the abstract.

## Contrasting-verb bullets (T1)

> Recently, two independent lines of work exploit the structure of the multiplicity
> vector rather than the table size alone:
> - **Preprocessed lookups** restrict *when* the table is paid for: the table is
>   committed once per circuit and reused [D22]; however, each new table needs a new
>   preprocessing, leaving dynamic tables open.
> - **Logarithmic-derivative lookups** restrict *how* membership is checked: a
>   rational identity replaces the grand product [A23]; the prover still commits to
>   a vector of length N.

## Bad vs good overview headings

| bad | good |
|---|---|
| "Why lookups are needed" | "The support of the multiplicities, not the table, bounds the prover's commitments." |
| "Where the cost goes" | "For structured tables the table side is an evaluation the verifier computes itself." |
| "The streaming schedule" (T2) | "Interleaving extension and hashing makes memory independent of the trace length." |
| "Our circuit" (T3) | "A 16-bit lookup table replaces every bit decomposition without new witnesses." |

## Tiny worked example (T1)

> Over 𝔽₁₇ take the table t = (0, 1, 2, 3), the looked-up vector a = (1, 1, 3) and
> multiplicities c = (0, 2, 0, 1). At γ = 5 the left side is
> 1/6 + 1/6 + 1/8 = 3 + 3 + 15 = 4 and the right side is 2·(1/6) + 1·(1/8) = 4, so the
> identity holds. For a' = (1, 1, 4), which leaves the table, the left side at γ = 5
> is 3 + 3 + 2 = 8 ≠ 4; exhaustively, the identity with c fails for all 12 admissible
> γ (the 5 values making a denominator zero are excluded), well below the bound of
> m + N − 1 = 6 bad challenges.

Every number in such an example must be recomputable by a script (e.g. a copy of
`skills/sage-check/scripts/sanity_check_template.py`) listed in `EVIDENCE.md`.
