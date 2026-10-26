# 09 Security: completeness, knowledge soundness, zero knowledge, concrete soundness

Every ZK construction needs the same four blocks, in this order. Theory papers put the
full proofs here (or in the appendix with a body sketch); system and application
papers built on an existing proof system may cite its theorems, but still give block
D for **their** parameters. Before writing, freeze the definitions and the
assumption ledger with zk-definitions <!-- TODO: link once skill exists -->, so the
model and notions here match §2 exactly.

## A. Completeness

- Statement: for every (𝕚, 𝕩; 𝕨) ∈ ℛ, the honest prover makes the verifier accept
  with probability 1 (perfect) or 1 − δ (state δ and where it comes from, e.g. a
  division by zero when a challenge hits a root, aborts in rejection sampling).
- Proof: walk through the numbered verifier checks of the protocol box one by one;
  each check reduces to an identity that holds for honest messages. Name the identity
  (sum-check round equation, quotient divisibility by Z_H, grand-product telescoping).
- Edge cases to mention explicitly: a challenge that collides with a domain element
  or table entry (γ = −t_j), padding rows, empty tables, the last folding round.
- Completeness is cheap to check exhaustively over a small field (`skills/sage-check`);
  say so in a footnote and ship the script.

## B. Knowledge soundness (with the extractor)

- **Statement first, with the notion and the model.** "Π is knowledge sound with
  knowledge error κ(λ) = … in the ROM / AGM, for every expected polynomial-time 𝒫*."
  If only soundness is proven, say "soundness"; if witness-extended emulation is
  needed (e.g. for composition), prove that.
- **Split the error.** κ = ε_PIOP + ε_PCS + ε_FS: the information-theoretic PIOP error
  (Schwartz–Zippel terms, sum-check terms, proximity terms), the PCS extraction /
  binding failure, and the Fiat–Shamir loss (number of hash queries times the
  round-by-round or state-restoration error). Each term gets its own lemma.
- **Extractor construction, in words before formulas.** Say how ℰ obtains the
  witness:
  - *PCS extraction:* run the PCS extractor on every commitment the prover sends
    (in the AGM: read the polynomial from the algebraic representation; for a
    Merkle/FRI commitment: extract the codeword from the prover's random-oracle
    queries, then decode within the proven proximity radius).
  - *Rewinding:* for special-soundness-style arguments, rewind 𝒫* on fresh challenges
    until enough accepting transcripts are collected, and interpolate; bound the
    expected running time (forking lemma or a tree-of-transcripts argument).
  - *Consistency:* show that the extracted polynomials satisfy the relation except
    with probability ε_PIOP, by the PIOP soundness theorem.
- **Model-specific obligations.** In the ROM, account for programming vs observing
  the oracle; in the AGM, say which group elements the adversary outputs; with a
  trusted setup, say which trapdoor must be unknown.
- **Conjectures in the theorem, not in a footnote.** If the proximity term uses a
  conjectured bound beyond the proven range, the theorem says "under Conjecture k".

## C. Zero knowledge (the simulator)

- **Notion:** honest-verifier ZK (HVZK) for the PIOP, then ZK for the compiled
  argument; statistical, perfect or computational; with or without a trusted setup.
  For a non-interactive argument in the ROM, the simulator programs the random oracle;
  say so.
- **Simulator construction:** sample the verifier's challenges first, then produce
  the prover messages with the right distribution:
  - masking: show that the evaluations the verifier sees (including **all PCS
    openings and the points queried by FRI-style tests**) are uniformly distributed
    given the masking polynomials' degree; count the number of evaluations revealed
    and size the masks accordingly;
  - hiding commitments: replace commitments by commitments to 0 (perfect/statistical
    hiding) or invoke the hiding assumption (computational);
  - programmability: set ℋ at the transcript prefixes the simulator needs.
- **The leak you forgot:** the number of PCS openings, the queried positions in a
  Merkle tree, the degree bound of a committed polynomial, the size of a lookup table,
  timing of the prover. State which of these the simulator reproduces and which are
  public by definition.
- If the argument is only HVZK, write "honest-verifier zero knowledge" in the title,
  abstract and theorem; do not upgrade it silently.
- Simulation-extractability, if claimed, gets its own theorem and proof.

## D. Concrete soundness table

Every parameter set used anywhere in the paper appears as a row. Generate the table
from the soundness calculator output (soundness-budget
<!-- TODO: link once skill exists -->), with an EVIDENCE row per number.

```latex
\begin{table}[t]\centering\scriptsize
\caption{Concrete knowledge soundness (bits) per parameter set. ``Proven'': the
proximity term uses a proven bound (unique decoding / Johnson bound). ``Conj.'': it
uses Conjecture~1. Algebraic: Schwartz--Zippel, sum-check and lookup terms over
$\mathbb{K}$. Totals are computed by the soundness script after the Fiat--Shamir loss
for $2^{64}$ hash queries. All values illustrative.}
\begin{tabular}{lcccc|ccc|cc}
\toprule
 & & & & & & \multicolumn{2}{c|}{proximity} & \multicolumn{2}{c}{total} \\
Set & $|\mathbb{K}|$ & rate & queries & grinding & algebraic & proven & conj. & proven & conj. \\
\midrule
P1 & $2^{128}$ & $1/2$ & 120 & 16 & 118 & 96  & 136 & 96  & 118 \\
P2 & $2^{128}$ & $1/4$ & 100 & 16 & 117 & 104 & 216 & 104 & 117 \\
\bottomrule
\end{tabular}\end{table}
```

Rules:

- **Two columns, never one:** proven and conjectured totals side by side. The headline
  number in the abstract states which one it is.
- **Each term separately:** algebraic terms (Schwartz–Zippel, sum-check, lookup),
  proximity/query terms, grinding, hash output length, curve or group security (a
  pairing-friendly curve's real security can be below its label), Fiat–Shamir loss.
  The total is the union bound (or minimum in bits) of the terms, computed by the
  script, not by hand.
- **Same table for the baselines** when the paper compares performance: the
  comparison is only fair at the same row values.
- **Field size for challenges:** say whether challenges come from 𝔽 or an extension
  𝕂, and use |𝕂| in every algebraic term.

## Pre-emptive defence of a known weakness

Four layers, as for any known limitation: acknowledge ("our argument is only proven
sound under the list-decoding conjecture at rate 1/2") → relocate ("the conjecture
affects only the query count, not the PIOP") → quantify ("in the proven regime the
query count grows by 23% [ill.], proof size by 18% [ill.]") → price the fallback
(report performance in the proven regime too, in the main table or a dedicated one).

## Checklist

- [ ] Completeness proven check by check, with edge cases; small-field script shipped.
- [ ] Knowledge soundness (not just soundness) if "argument of knowledge" is claimed;
      error split into PIOP, PCS and Fiat–Shamir terms; extractor described.
- [ ] ZK notion stated precisely; simulator covers every PCS opening and query.
- [ ] Model, setup and every conjecture appear in the theorem statements.
- [ ] Concrete soundness table with proven and conjectured columns for every
      parameter set used, generated from a script with EVIDENCE rows.
