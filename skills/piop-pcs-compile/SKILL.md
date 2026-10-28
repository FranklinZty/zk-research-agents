---
name: piop-pcs-compile
description: Build a SNARK the standard way and check every compilation precondition — write the protocol as a PIOP (oracles, degree bounds, queries, checks, round-by-round error), choose a PCS, verify binding / extractability / evaluation binding / hiding / batch-opening soundness / degree enforcement against the PIOP's needs, then derive prover time, verifier time and proof size. Hash-based route (BCS, COS) checked against CY24; algebraic PCS route (KZG, IPA, Dory) against Thaler and the original papers. Use at P2 to cost an idea and at P3 before writing the main theorem.
---
# piop-pcs-compile: PIOP + PCS + Fiat–Shamir, with the preconditions written down

## Why

Most modern ZK constructions are "a polynomial IOP compiled with a polynomial commitment scheme, then made
non-interactive". Each step has a theorem with preconditions, and a missing one is a standard proof gap: a PCS
that is binding but not extractable under a knowledge-soundness claim; a degree bound the PIOP relies on but the
PCS does not enforce; batched openings with an unaccounted Schwartz–Zippel term; a ZK claim with non-hiding
openings; a PIOP proven sound but not round-by-round sound. This skill makes the pipeline explicit and produces
the cost formulas that `idea-mining-loop` and `bench-protocol` compare against.

Sources: hash route (IOP + Merkle trees) from CY24, which proves BCS and COS for IOPs in general, not for PIOPs
specifically; PIOPs and algebraic PCS from Thaler; compiler theorems for "PIOP + algebraic PCS" from the papers
that state them (source: other). Terms: [GLOSSARY](../../references/books/GLOSSARY.md).

## 1. Write the protocol as a PIOP

Fill this table before anything else ([Thaler §10.2, Polynomial IOPs and Associated Succinct Arguments];
[Thaler §10.6, Unifying IPs, MIPs, and IOPs via Polynomial IOPs]):

```markdown
| round | prover sends (oracle / plain) | polynomial: uni/multilinear, #vars, degree bound | verifier samples (set, bits) | queries (points, chosen when) | verifier check (identity) | RBR error this round |
|---|---|---|---|---|---|---|
| 1 | [f] oracle | univariate, deg < n | α ∈ F_{p^2} | — | — | — |
| 2 | [q] oracle | univariate, deg < 2n | z ∈ F_{p^2} | f(z), q(z) | f(z)·α − … = q(z)·Z_H(z) | 2n/|F_{p^2}| |
```

(Toy layout.) Then state: completeness; soundness **as round-by-round soundness** (or special soundness for
knowledge), because Fiat–Shamir needs it ([CY24 §Strong soundness properties, section:strong-soundness-properties]);
knowledge soundness if claimed; HVZK if ZK is claimed, including which evaluations are revealed
([Thaler §13.3, Zero-Knowledge via Masking Polynomials]). Run the completeness and soundness of the PIOP on toy
fields first (`skills/sage-check`). If the circuit's own polynomials are fixed per circuit, mark them as
**index** oracles (holographic PIOP; see §4).

## 2. Choose the PCS

| family | setup / model / assumption | fits | read |
|---|---|---|---|
| FRI (and STIR, WHIR) + Merkle | transparent; ROM; proximity theorem (proven vs conjectured regime) | univariate (multilinear via reductions), plausibly post-quantum | [Thaler §10.4, FRI and Associated Polynomial Commitments]; STIR/WHIR: source: other, ePrint 2024/390, 2024/1586 |
| Ligero / Brakedown (tensor codes) + Merkle | transparent; ROM | multilinear, fast prover, larger proofs | [Thaler §10.5, Ligero and Brakedown Polynomial Commitments] |
| KZG | trusted (universal) SRS; pairings; binding from SDH, extraction from a knowledge assumption or GGM/AGM | univariate, constant-size openings | [Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup]; multilinear: [Thaler §15.3, Extension of KZG to Multilinear Polynomials] |
| IPA / Bulletproofs, Hyrax | transparent; discrete log | logarithmic proofs, linear (IPA) or √n (Hyrax-style) verifier | [Thaler §14.4, Bulletproofs]; [Thaler §14.3, Trading Off Commitment Size and Verification Costs] |
| Dory | transparent; asymmetric pairings, SXDH | logarithmic verifier, multilinear | [Thaler §15.4, Dory: Transparent Scheme with Logarithmic Verification Costs]; source: other, ePrint 2020/1274 |

Trade-off overview: [Thaler §16.3, Polynomial Commitment Schemes: Pros and Cons]. Record the choice and the
alternatives rejected in DECISIONS.md, and the model/assumption in the assumption ledger (`skills/zk-definitions`).

## 3. Compilation preconditions (check every row)

| # | precondition | why the compiled argument needs it | hash route (CY24) | algebraic route |
|---|---|---|---|---|
| C1 | **binding / evaluation binding** | a cheating prover must not answer one query two ways | Merkle binding [CY24 §Binding, lemma:mt-binding] | [Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup] (SDH); [Thaler §14.4, Bulletproofs] (DL) |
| C2 | **extractability** | knowledge soundness of the argument extracts the PIOP oracles from the commitments, then runs the PIOP extractor | Merkle (multi-)extraction from the query trace, straightline [CY24 §Extractability, lemma:mt-multi-configuration-multi-extractability] | knowledge assumption or GGM/AGM for KZG [Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup]; rewinding for IPA [Thaler §14.4, Bulletproofs]; binding without extraction is not enough [Thaler §7.4, Knowledge-Soundness] |
| C3 | **degree enforcement** | the PIOP's soundness uses the degree bounds; the PCS must guarantee them | FRI proves proximity to the RS code of the stated degree [Thaler §10.4.4, Details of FRI: Better Reed-Solomon Proximity Proofs via Interaction] | SRS length bounds the degree; separate degree checks when the PIOP needs a tighter bound (source: other, e.g. Marlin ePrint 2019/1047) |
| C4 | **queries outside the commitment domain** | PIOP queries random points of the field, not of the evaluation domain | quotient / out-of-domain sampling [Thaler §10.4.2, Polynomial commitments and queries to points outside]; DEEP: source: other, ePrint 2019/336 | native |
| C5 | **batch-opening soundness** | many evaluation claims are merged by random linear combinations | a batching term (m−1)/|F| per combination with one challenge; budget it | [Thaler §16.1, Batch Evaluation of Homomorphically Committed Polynomials]; term from [Thaler §3.4, Schwartz-Zippel Lemma] |
| C6 | **hiding / ZK openings** (only if ZK is claimed) | revealed evaluations and commitments must be simulatable | HVZK IOP + salted Merkle leaves + salted FS [CY24 §Zero knowledge, theorem:bcs-zero-knowledge] [CY24 §Hiding, lemma:mt-privacy] | hiding commitments and ZK evaluation proofs, or masking polynomials [Thaler §14.1, A Zero-Knowledge Scheme with Linear Size Commitments] [Thaler §13.3, Zero-Knowledge via Masking Polynomials] |
| C7 | **round-by-round / state-restoration soundness of the whole interactive argument** | the FS step needs it, including the PCS's own rounds (FRI folding, IPA rounds) | [CY24 §RBR soundness implies SR soundness, theorem:rbr-soundness-to-sr-soundness]; FRI rounds: source: other, ePrint 2023/1071 | special soundness of IPA rounds [CY24 §State-restoration knowledge soundness for IPs, theorem:ss-to-sr-knowledge-soundness-for-ip] (ROM part) |
| C8 | **transcript** | commitments absorbed before the challenges they bind; points chosen after commitments | `skills/fiat-shamir-audit` | `skills/fiat-shamir-audit` |
| C9 | **public coin** | FS applies only to public-coin protocols | [CY24 §Definition, definition:iop-public-coin] | same |

## 4. Hash-based route: BCS and COS (CY24)

- **BCS** turns a public-coin IOP into a non-interactive argument: each oracle message is Merkle-committed, each
  challenge is derived by hash-chain FS, and the verifier's queries are answered with authentication paths
  ([CY24 §Construction, construction:bcs-transformation]). A PIOP whose PCS is FRI is, as a whole, an IOP (PIOP
  rounds plus FRI rounds); BCS is applied to that whole IOP. Non-oracle prover messages are supported
  ([CY24 §Construction, remark:bcs-non-oracle-messages]); basic instead of hash-chain FS removes the λ-bit
  challenge condition ([CY24 §Construction, remark:bcs-with-basic-fs]).
- **Preconditions and errors**: soundness from the IOP's state-restoration soundness plus Merkle and hash-chain
  terms ([CY24 §Soundness, theorem:bcs-soundness]); straightline knowledge soundness needs **straightline**
  state-restoration knowledge soundness of the IOP ([CY24 §Knowledge soundness, theorem:bcs-knowledge-soundness];
  [CY24 §State restoration, definition:iop-state-restoration-knowledge]); ZK needs an HVZK IOP and salts
  ([CY24 §Zero knowledge, theorem:bcs-zero-knowledge]). Put every term in `skills/soundness-budget`.
- **COS (preprocessing)**: for a holographic IOP, a deterministic indexer Merkle-commits to the index encoding
  once; the verifier then runs in time sublinear in the circuit. Extra error from the offline phase, on top of
  BCS ([CY24 §The COS transformation, construction:cos-transformation]; [CY24 §Security of the COS transformation, theorem:cos-soundness, theorem:cos-knowledge-soundness, theorem:cos-zero-knowledge]).
  A holographic IOP is first viewed as an ordinary IOP for the indexed relation
  ([CY24 §Security of the COS transformation, lemma:from-hiop-to-iop]).
- The proximity part (FRI/STIR/WHIR soundness, proven vs conjectured) is **not** in CY24: cite the papers and
  mark the regime.

## 5. Algebraic route: PIOP + KZG / IPA / Dory

- Replace every oracle by a PCS commitment and every query by an evaluation proof; the result is an interactive
  argument whose soundness is the PIOP's plus the PCS's binding/extraction terms; then apply FS
  ([Thaler §10.2, Polynomial IOPs and Associated Succinct Arguments]). A precise compiler theorem with its
  conditions is in the papers that introduced this paradigm (source: other: Marlin ePrint 2019/1047, PLONK ePrint
  2019/953, HyperPlonk ePrint 2022/1355; `needs verification`: cite the exact theorem number you use).
- The model is mixed (ROM for FS, plus AGM/GGM or knowledge assumptions for extraction, plus SDH/DL). Write all of
  them in the ledger; no CY24 bound covers the algebraic part.
- Preprocessing: commit to the index polynomials once with the same PCS (universal SRS) — state who computes the
  commitments and whether the SRS is updatable.

## 6. Derive the costs

Count from the PIOP table, per proof, before implementing:

| quantity | formula (fill in) | dominated by |
|---|---|---|
| prover time | PIOP prover field ops + Σ_oracles commit(deg) + Σ_queries open + batching | NTT/MSM size, hashes (Merkle), sum-check rounds |
| verifier time | PIOP checks + Σ PCS verifications (+ Merkle paths × queries) | pairings / MSMs / hashes |
| proof size | Σ commitments + Σ evaluation proofs + plain PIOP messages (+ authentication paths, with pruning [CY24 §Path pruning, lemma:path-pruning-lower-and-upper]) | FRI queries × path length; group elements |
| setup | transparent / universal SRS size / circuit-specific | — |

Express each entry in operation counts (field mults, hashes, MSM of size n, pairings) and as a function of the
parameters the soundness budget fixes (queries, rate, field). The detailed per-operation model belongs to
prover-cost-model <!-- TODO: link once skill exists -->; circuit sizes come from constraint-cost
<!-- TODO: link once skill exists -->.

## Output (THEORY.md, "Construction and compilation")

```markdown
### Compilation of <PIOP> with <PCS>
PIOP table: (§1 table) · soundness notion of the PIOP: RBR, eps_rbr per round = … (THEORY.md §…)
PCS: <name>, setup <…>, model/assumptions <…> (ledger A5–A7)
Preconditions: C1 ✓ (…) · C2 ✓ (…) · C3 ✓ (…) · C4 ✓ · C5 term (m−1)/|F| in budget row … · C6 n/a (no ZK claim) · C7 ✓ (…) · C8 FS audit link · C9 ✓
Compiler theorem used: CY24 label (hash route) / theorem number and ePrint id of the compiler paper (algebraic route)
Costs: P = …, V = …, |π| = … (operation counts; EVIDENCE rows once measured)
```

## Pitfalls

- Knowledge soundness claimed with a PCS that is only shown binding.
- PIOP soundness proven for the interactive protocol only; FRI rounds left out of the round-by-round analysis.
- Degree bounds assumed in the PIOP but not enforced by the PCS (or enforced for a larger degree).
- Batched openings at different points merged as if they were at one point.
- ZK claimed while the PCS opens evaluations of unmasked witness polynomials.
- A CY24 bound quoted for a KZG-based construction, or an AGM extraction argument presented as standard-model.
- Costs compared at different soundness levels (re-derive the parameters with `skills/soundness-budget` first).
