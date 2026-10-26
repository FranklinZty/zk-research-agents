# Toy security statements and evaluation tables — good vs bad

Invented papers T1–T3 (see `toy_abstracts.md`). Every number is **illustrative**
`[ill.]`; citations like [A23] are placeholders.

## Theorem statements (T1)

### Bad

> **Theorem 1.** ToyLookup is secure.

Problems: no notion (soundness? knowledge soundness? ZK?), no model, no setup, no
error bound, no hypothesis on the field or the table.

### Good

> **Theorem 1 (Completeness).** For every (t, C_a; a) ∈ ℛ_lkp and every γ ∈ 𝕂 with
> γ ≠ −t_j for all j, the honest prover of Protocol 1 makes the verifier accept with
> probability 1.
>
> **Theorem 2 (Knowledge soundness of the PIOP).** If char 𝔽 > m, Protocol 1 is knowledge sound with
> knowledge error ε_PIOP ≤ (m + N)/|𝕂| + μ·2/|𝕂|, where μ = log m is the number of
> sum-check rounds.
>
> **Theorem 3 (Compiled argument).** Let PCS be an extractable multilinear PCS with
> extraction error ε_PCS, and let ℋ be a random oracle. The Fiat–Shamir compilation of
> Protocol 1 with PCS is a non-interactive argument of knowledge in the ROM with
> knowledge error at most Q·ε_PIOP + ε_PCS for adversaries making at most Q queries to
> ℋ, with the setup of PCS. If PCS is hiding, it is (statistical) zero knowledge.

## Extractor sketch (T1, body version)

> The extractor ℰ runs 𝒫* and the PCS extractor on the commitments to a, c, h and g,
> obtaining multilinear polynomials ã, c̃, h̃, g̃ except with probability ε_PCS. If
> the verifier accepts, the sum-check soundness and Schwartz–Zippel imply, except
> with probability ε_PIOP, that h_i = 1/(γ + a_i), g_j = c_j/(γ + t_j) and
> Σ_i h_i = Σ_j g_j as rational functions in γ, hence that every a_i is a pole of the
> right side, i.e. a_i ∈ {t_j}. ℰ outputs a. The full proof (Appendix A.2) bounds the
> number of rewinds by the forking lemma for the Fiat–Shamir version.

## Simulator sketch (T1, body version)

> The simulator 𝒮 samples γ and the sum-check challenges first and programs ℋ
> accordingly. It commits to random multilinear polynomials of the right sizes
> (hiding), runs the sum-check on masked polynomials whose sum is zero by
> construction, and answers the PCS evaluation queries with uniform values. Because
> each committed polynomial is masked with enough random coefficients to cover the
> 2 + μ evaluations revealed [ill.], the transcript is identically distributed.

Bad version: "zero knowledge follows from the hiding of the PCS". It ignores the
evaluations revealed by the openings and the sum-check messages.

## Comparison table (T2), good shape

```latex
\begin{table}[t]\centering\scriptsize
\caption{Proving a $2^{24}$-row [ill.] zkVM trace. All systems at 100-bit proven
soundness [ill.] (\Cref{tab:soundness}); prover time includes trace commitment and
FRI, excludes witness generation (\Cref{tab:witness}); same GPU, median of 7 runs,
every proof verified. $\diamond$: as reported by the authors, different GPU.}
\begin{tabular}{lrrrrr}
\toprule
System & P time (s) & V time (ms) & proof (KiB) & peak mem. (GiB) & ratio \\
\midrule
{[D23]}          & 41.2 [ill.] & 3.1 [ill.] & 182 [ill.] & 38.0 [ill.] & 1.00 \\
{[E24]}$^\diamond$ & 30.5 [ill.] & 2.9 [ill.] & 176 [ill.] & 44.1 [ill.] & — \\
\textbf{ToyProver} & \textbf{24.8} [ill.] & 3.1 [ill.] & 182 [ill.] & \textbf{7.3} [ill.] & 1.66 \\
\bottomrule
\end{tabular}\end{table}
```

What it shows: equal soundness and regime stated in the caption; timing scope
stated; P, V, proof size and memory together; a reported-only row gets "—" in the
ratio column; the proof size is identical because the proof is unchanged.

## Circuit-correctness paragraph (T3)

> **Circuit correctness.** Each gadget (range check, limb decomposition, non-native
> multiplication, signature verification) was checked for under-constraint by
> enumerating all witnesses for every public input over a 17-element toy field and
> confirming uniqueness, and by differential testing of the witness generator against
> the constraints on 10^4 [ill.] random inputs at full size. Range checks bound every
> limb to 16 bits, so no limb product wraps around the field modulus (Lemma 4). The
> scripts are part of the artifact.
