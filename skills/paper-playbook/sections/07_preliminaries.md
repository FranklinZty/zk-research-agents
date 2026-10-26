# 07 Preliminaries

## Job

Fix notation and recall exactly the background the later sections use. Nothing more:
standard material that is not referenced later goes to an appendix or is cited.
For a ZK paper the preliminaries fix four things that the security section quantifies
over: the **relation**, the **interactive model** (IOP/PIOP), the **commitment
scheme**, and the **Fiat–Shamir** compilation.

## Structure

```
2.1 Notation              compact table (symbol | meaning), 8–15 rows, 2 columns or a
                          4-column (symbol | meaning | symbol | meaning) layout
2.2 Relations and arguments   indexed relation, interactive argument, security notions
2.3 (Polynomial) IOPs     the oracle model the construction is stated in
2.4 Polynomial commitments    the PCS interface and the properties the compiler needs
2.5 Fiat–Shamir           the transform and the soundness notion it preserves
2.6 <prior technique>     one subsection per prior PIOP/gadget the construction builds
                          on (sum-check, grand product, log-derivative lookup, FRI ...),
                          stated as definitions/lemmas with citations
```

## Standard notation (adapt, but declare deviations)

| object | notation | remarks |
|---|---|---|
| security parameter | λ | concrete bits are a separate quantity; never write "λ = 128" for a soundness level without saying which term |
| field, extension | 𝔽 (or 𝔽_p), 𝕂 ⊇ 𝔽 for challenges | say explicitly when challenges are drawn from 𝕂 |
| indexed relation | ℛ = {(𝕚, 𝕩; 𝕨)}: index 𝕚 (circuit/constraint system), instance 𝕩 (public input), witness 𝕨 | drop 𝕚 if there is no preprocessing; ℒ(ℛ) for the language |
| argument | Π = (Setup, 𝒫, 𝒱) or (𝒢, 𝒫, 𝒱) with preprocessing ℐ | ⟨𝒫(𝕩, 𝕨), 𝒱(𝕩)⟩ = b for the interaction output |
| polynomials | 𝔽[X]_{<d} (univariate, degree < d); 𝔽[X₁,…,X_μ]^{≤1} (multilinear); \tilde{f} for the multilinear extension | domain H ⊂ 𝔽, vanishing polynomial Z_H, boolean hypercube {0,1}^μ |
| PIOP | rounds k, oracles [[f]], queries, degree bound d, soundness error ε | state the query complexity and the proof length per round |
| PCS | PCS = (Setup, Commit, Open, Eval) or (Setup, Com, Open, Verify); commitment C = Com(f) | name the properties used: binding, evaluation binding, knowledge soundness / extractability, hiding |
| random oracle | ℋ (one per domain-separated use) | write the transcript explicitly: ρ_i = ℋ(𝕚, 𝕩, C_1, …, C_i) |
| adversary | 𝒜, extractor ℰ, simulator 𝒮 | expected vs strict polynomial time stated in the definitions |
| negligible | negl(λ) | concrete bounds are expressions, not "negl" |

## Rules

- The notation table stays inside the Notation subsection, is short, and lists only
  symbols reused at least twice.
- **Write the relation out** with its public and private parts before any protocol.
  An ambiguous split between instance and witness is the most common source of a
  wrong soundness statement (the "statement" the verifier binds to must include every
  public value).
- **Define the security notions you prove, not the ones you wish you had.** Give the
  precise definitions of completeness, (knowledge) soundness or witness-extended
  emulation, and zero knowledge (honest-verifier or full; statistical, perfect or
  computational), and say whether the adversary chooses the instance adaptively. If
  simulation-extractability is claimed, define it here.
- **State the model once.** ROM, AGM, GGM or standard model; trusted, universal /
  updatable, or transparent setup. Every later theorem refers back to this paragraph.
- **PCS properties as a checklist.** The compilation theorem (§3 or §4) needs
  specific properties; list them in a definition so the theorem can cite them by name.
  For a hiding PCS, say whether hiding is perfect, statistical or computational.
- **Fiat–Shamir:** state which interactive notion is preserved (e.g. round-by-round
  soundness or state-restoration soundness) and that the transcript includes the
  index, the instance and all prior prover messages. Do not write "apply Fiat–Shamir"
  without saying what is hashed.
- Distinguish fields precisely (𝔽_p vs 𝔽_{p^e} vs a binary tower field); define the
  domain (multiplicative subgroup, coset, hypercube, circle domain) used for each
  oracle.
- Prior techniques (sum-check, grand-product, lookup, FRI) are recalled at the level
  needed to state your theorems, in your notation, with the original soundness error
  and cost formula, verified against the source paper.
- Short proofs of recalled facts may be given in place if a reviewer asked for them
  or if they fix a gap in the literature; otherwise cite.
- If a reviewer is likely to be unfamiliar with the area (general IACR audience),
  keep one paragraph of intuition per subsection; newcomers flag "background too
  brief" as a weakness.

## Toy fragment (T1, illustrative)

> **Definition 1 (Lookup relation).** For a field 𝔽 and sizes m, N, let
> ℛ_lkp = {(𝕚 = t ∈ 𝔽^N, 𝕩 = C_a; 𝕨 = a ∈ 𝔽^m) : C_a = Com(a) ∧ ∀ i, a_i ∈ {t_1,…,t_N}}.
> **Definition 2 (Knowledge soundness).** Π has knowledge error κ if there is an
> expected-polynomial-time extractor ℰ such that for every 𝒫* that makes 𝒱 accept on
> 𝕩 with probability ε > κ, ℰ^{𝒫*}(𝕩) outputs 𝕨 with (𝕚, 𝕩; 𝕨) ∈ ℛ with probability
> at least ε − κ.

## Checklist

- [ ] Every symbol in the notation table is used in ≥ 2 sections.
- [ ] The relation is written out with index, instance and witness.
- [ ] Definitions match exactly the notions the theorems claim (soundness vs knowledge
      soundness; HVZK vs ZK; adaptive or not).
- [ ] Model and setup stated once and referenced by every theorem.
- [ ] PCS properties the compiler needs are defined by name.
- [ ] Fiat–Shamir transcript contents stated.
- [ ] No material here that no later section uses.
