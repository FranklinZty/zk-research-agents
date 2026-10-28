# Topic map: "which book / chapter proves X?"

Used via `skills/textbook-index`. Columns: **topic → first place to look → second opinion → typical
ZK use**. Chapter numbers come from the TOC files in [`toc/`](toc/) (see [CATALOG.md](CATALOG.md) for
bibliographic data). Chapter numbers taken from public-source TOCs are marked (pub) — confirm them before
putting them in a paper. Short slugs: DF = Dummit–Foote, IR = Ireland–Rosen, LN = Lidl–Niederreiter,
T = Thaler (*Proofs, Arguments, and Zero-Knowledge*; section numbers verified against the pinned PDF),
CY = Chiesa–Yogev (*Building Cryptographic Proofs from Hash Functions*; cited by chapter name, see
[`references/books/hash-snargs/MAP.md`](../books/hash-snargs/MAP.md) for the labels), BS = Boneh–Shoup,
KL = Katz–Lindell, GRS = Guruswami–Rudra–Sudan (*Essential Coding Theory*). In skills and THEORY.md, cite the two
pinned books in the checked format of [`references/books/README.md`](../books/README.md).

Lookup protocol (also in `skills/textbook-index`): (1) find the topic row; (2) open the TOC file and pick the
section; (3) read the section in your own copy; (4) record in `MATH-REFS.md` the exact statement you rely on,
book + section + (printed) page, and whether you checked its hypotheses against your setting. A citation
without a checked hypothesis is a hazard, not a reference.

## Finite fields and polynomials (all ZK constructions)

| topic | first look | second opinion | ZK use |
|---|---|---|---|
| Finite fields F_{p^n}: existence, uniqueness, subfields | DF §14.3 | LN ch.2 (pub); IR ch.7 | base / extension fields (Goldilocks, BabyBear, M31, binary towers) |
| Multiplicative group cyclic; primitive roots; element orders | IR ch.4 | DF §9.5, §14.3; LN ch.2 (pub) | NTT-friendly primes (2^k \| p−1), roots of unity, multiplicative subgroups as evaluation domains |
| Extension fields, towers, degree | DF §13.1–13.2 | Howie ch.3; Artin ch.15 | soundness via extension-field challenges, tower fields |
| Frobenius automorphism x ↦ x^p, trace and norm | DF §14.3 | LN ch.2 (pub) | binary-field arithmetic, trace-based packing |
| Polynomials over a field: division, roots, degree bound | DF §9.4–9.5 | LN ch.3 (pub); Howie ch.2 | "a nonzero degree-d polynomial has ≤ d roots" behind Schwartz–Zippel and quotient checks |
| Factorisation of polynomials over F_q | LN ch.4 (pub) | DF §9.4–9.6 | vanishing polynomials of subgroups / cosets |
| Lagrange interpolation, Vandermonde matrices | Meyer ch.4–5 (see its index) | Artin ch.1 | Lagrange bases in PLONK-style PIOPs, RS encoding |
| CRT for polynomial rings | DF §7.6 | Artin ch.11 | batching over cosets, quotienting by Z_H(X) |
| Equations over finite fields, point counts | IR ch.10 | LN ch.6 (pub) | counting bad challenges |
| Elliptic curves over finite fields (intro) | IR ch.18 | BS ch.15 (pub) | curve choice, pairing-friendly curves (use papers for concrete security) |

## Probability and counting arguments (soundness)

| topic | first look | second opinion | ZK use |
|---|---|---|---|
| Schwartz–Zippel lemma, polynomial identity testing | T §3.4 | T §2.1 (RS fingerprinting) | soundness error of random evaluation checks |
| Union bound, inclusion–exclusion | Merris §2.3 | CY "Mathematical background"; KL appendix (pub) | combining per-round soundness errors into a budget |
| Binomial / multinomial counting | Merris §1.7 | — | query-count and grinding bounds |
| Permutations and disjoint cycles | Merris §2.4 | Artin ch.2; DF §1.3 | copy-constraint permutation arguments (PLONK σ) |
| Paths, cycles, connectivity in graphs | West ch.1–2 | — | wiring graphs, equivalence classes of copy constraints |

## Interactive proofs, arguments, zero-knowledge

| topic | first look | second opinion | ZK use |
|---|---|---|---|
| Sum-check protocol, GKR | T §4.1, §4.6 | — | multilinear PIOPs, sum-check-based provers |
| Fiat–Shamir transform: construction, adaptive security, multi-round loss | CY "The Fiat–Shamir transformation for SPs / for IPs", "Optimization: the hash-chain variant" | T §5.2–5.3; BS ch.19 (pub) | non-interactive arguments, transcript design |
| State-restoration, round-by-round and special soundness | CY "State restoration", "Round-by-round soundness", "Special soundness" | T §5.3 | FS loss for many-round protocols, extractors |
| Security definitions: (knowledge) soundness, adaptive vs non-adaptive, ZK in the ROM | CY "Arguments in the ROM", "Additional security definitions" | T §3.1–3.2, §7.4, §11.1 | theorem statements, assumption ledger |
| Security levels, concrete security, parameter setting | CY "Setting parameters" | T §5.3.1 | worst-case vs average-case bits, budget tables |
| Merkle commitments: binding, extraction, hiding | CY "Merkle commitment scheme" | T §6.6.1 (memory checking), §9.2 | hash-based PCS, Merkle error terms |
| Front ends: programs → circuits | T §6.5–6.6 | T §8.4 (R1CS) | arithmetisation, constraint counting |
| IOPs and succinct arguments from hashes (BCS, Micali, COS) | CY "The BCS transformation", "Argument systems with preprocessing" | T §10.1–10.4, §9.2 | FRI-based SNARKs, Merkle commitments |
| Zero-knowledge definitions, simulators | CY "Additional security definitions" (ZK in the ROM) | T §11.1, §13.3 (masking); BS ch.20 (pub) | HVZK vs full ZK, masking |
| Sigma protocols | T §12.2 | CY "Sigma protocols"; BS ch.19 (pub) | knowledge-of-opening proofs |
| Polynomial commitments (DL, pairings) | T §14.4 (Bulletproofs), §15.2 (KZG), §15.4 (Dory), §16.3 | BS ch.15 (pub, pairings) | KZG, IPA, Bulletproofs-style PCS |
| Linear PCPs, Groth16-style SNARKs | T §17.4–17.5 | — | pairing-based SNARKs, public-input handling |
| Recursion, composition, folding | T §18.1–18.5 | — | recursive SNARKs, wrapping, Nova-style folding |
| Definitions and reductions, hash functions | KL ch.6, ch.9 (pub) | BS ch.8 (pub) | assumption statements, collision resistance of Merkle trees |

## Coding theory and Reed–Solomon proximity (FRI / STIR / WHIR)

| topic | first look | second opinion | ZK use |
|---|---|---|---|
| Linear codes, distance, Singleton bound, MDS | GRS (catalogued, no TOC) | MacWilliams–Sloane; Roth | rate / distance of RS codes in hash-based SNARKs |
| Reed–Solomon codes | GRS | Roth; Merris (codes and designs chapter) | low-degree testing, FRI codewords |
| Johnson bound, list decoding | GRS | Guruswami (list decoding survey); Guruswami–Sudan | proximity parameter regimes: unique decoding vs Johnson vs conjectured |
| Proximity testing of RS codes | T §10.4.4; FRI paper (catalogued) | DEEP-FRI, STIR, WHIR papers | query complexity and soundness of the PCS |
| Proximity gaps / correlated agreement | BCIKS (ePrint 2020/654, `needs verification`) | — | batching soundness, provable vs conjectured parameters |

## Gaps (topics the local corpus does not cover well)

- **Concrete soundness of FRI/STIR/WHIR**: textbooks do not give it; cite the paper and state whether the
  regime used is proven or conjectured.
- **Pairing-friendly curves and their concrete security** (BN254, BLS12-381): IR ch.18 is introductory only; use
  the curve literature directly.
- **Fast polynomial arithmetic (NTT variants, additive FFT over binary fields)**: use the algorithm literature;
  Meyer ch.5 only covers the DFT as a matrix factorisation.
- **Lookup arguments, folding beyond Nova, STIR/WHIR, Binius**: paper-only; see the reading lists. (Multilinear
  PCS: T §10.4.5, §15.3, §15.4; Nova: T §18.5.)
