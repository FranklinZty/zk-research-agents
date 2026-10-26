# Toy introduction and contribution list — good vs bad

Invented paper T1 ("ToyLookup", a lookup argument with table-independent prover
cost). Numbers are **illustrative** `[ill.]`; citations like [A23] are placeholders.

## Contribution list

### Bad

```latex
\subsection{Our Contributions}
\begin{itemize}
\item We study lookup arguments and prove Lemma 3 and Theorem 5.
\item Our argument is 3.4x faster, although proofs are larger than in [A23].
\item We investigate how to make lookups secure and zero-knowledge.
\item We implement everything.
\end{itemize}
```

Problems: lemma numbers; concession inside contributions; "study/investigate";
"secure" names no notion or model; numbers in the wrong bullet and without security
level or timing scope; no section pointers; no deliverable in the last bullet.

### Good

```latex
\subsection{Our Contributions}
Inspired by the observation that only the support of the multiplicity vector enters
the prover's work, we determine when a lookup argument can avoid committing to
anything of table size. Building on it, we propose ToyLookup, a lookup argument in
which the logarithmic-derivative lookup of [A23] is the special case $k=1$. Our main
contributions are:

\begin{itemize}
\item \textbf{From the multiplicity support to table-independent provers.} We show
  that the prover only needs to commit to the restriction of the multiplicities to
  their support, of size at most $m$, and that the table enters solely through one
  multilinear evaluation. This covers every table with a succinctly evaluable
  multilinear extension, including the range and XOR tables used by 90\% [ill.] of
  the lookups in the benchmark circuits of \Cref{tab:coverage}.
\item \textbf{A unified view of logarithmic-derivative lookups.} The lookup of [A23]
  is the case $k=1$ and the preprocessed variant of [B24] the case of an unstructured
  table; interior points, reachable by neither, are optimal for large structured
  tables. For any table the best $k$ is selected by a closed-form rule
  (\Cref{sec:select}).
\item \textbf{A knowledge-sound, zero-knowledge argument.} We compile the PIOP with
  any extractable, hiding multilinear PCS and prove knowledge soundness and
  (full) zero knowledge in the ROM, with a universal setup (\Cref{sec:security}).
\item \textbf{Faster provers for large tables.} For $m=2^{20}$ [ill.] lookups into a
  $2^{32}$-entry [ill.] table at 128-bit proven soundness, proving is 2.1--3.4$\times$
  [ill.] faster than the strongest baseline on the same machine, every proof verified
  (\Cref{tab:main}).
\end{itemize}
```

## Opening funnel

### Bad

> ZK is a hot topic. Many papers have been written about lookups. Lookups are slow.
> In this paper we make them faster.

### Good (structure only; wording illustrative)

> Succinct arguments let a prover convince a verifier that a computation is correct,
> with verification far cheaper than the computation [..]. Among arithmetizations,
> Plonkish constraint systems with lookups are the ones of choice for circuits with
> many range checks and non-native operations, because a lookup replaces a bit
> decomposition by a single table membership [..]. This line of work [.., .., .., ..]
> has steadily reduced the cost per lookup, yet provers still pay for the table.
> Concretely, a logarithmic-derivative lookup factors into three stages:
> (i) multiplicity computation ..., cost O(m + N); (ii) commitments to the inverse
> vectors ..., an MSM of size m + N; (iii) a sum-check over the two sums ..., O(m + N)
> field operations. Every previous construction can be cast as
> \[ \min_{\Pi}\ \mathrm{cost}_{\mathcal{P}}(\Pi) \quad \text{s.t. } \Pi \text{ is a knowledge-sound argument for } \mathcal{R}_{\mathrm{lkp}}. \tag{1}\]
> Whether a lookup argument can make cost_𝒫 independent of N without per-table
> preprocessing has remained open.
