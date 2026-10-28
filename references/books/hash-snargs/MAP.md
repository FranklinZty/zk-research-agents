# CY24 navigation map

Chiesa–Yogev, *Building Cryptographic Proofs from Hash Functions*, v1.2, commit `305fa3d`
(pinning, licence and citation rules: [../README.md](../README.md); terms: [../GLOSSARY.md](../GLOSSARY.md)).
This file is a **map**, not a summary: for each chapter it says what you find there and when to open it, and
lists the labels worth jumping to. Read the statement itself in the cached source
(`references/books/.cache/hash-snargs/snargs-book.tex`, search for the label) before relying on it.

Everything in CY24 is proved in the pure random oracle model, unconditionally, with explicit error terms in the
query bound t, the oracle output size λ and the instance size. Probabilistic-proof design (PIOPs, Reed–Solomon
proximity, FRI internals) and algebraic commitments are out of scope: see [../thaler/MAP.md](../thaler/MAP.md).

## Chapters

### Front matter

- **Mathematical background.** Notation, probability tools and the "experiment" notation used in every
  statement. Open it when a probability bound in a proof needs a named inequality.
  [CY24 §Probability, lemma:inclusion-exclusion-2, lemma:law-of-total-probability, definition:statistical-distance]

### Part: What are Cryptographic Proofs?

- **The random oracle model.** The model itself, lazy sampling, and how hash functions realise it. Open it to
  state the model in a THEORY.md assumption ledger. [CY24 §Definition, definition:the-rom]
- **Basic cryptographic properties.** Query-bounded one-wayness, collision resistance and pseudorandomness of a
  random oracle; every later Merkle and Fiat–Shamir error term is built from these.
  [CY24 §Inversion resistance, lemma:rom-ow] [CY24 §Collision resistance, lemma:rom-cr]
- **Arguments in the ROM.** Completeness, non-adaptive and adaptive soundness for non-interactive and
  interactive arguments, and the efficiency measures. The reference definitions for any soundness claim.
  [CY24 §Non-interactive arguments, definition:narg-completeness, definition:narg-nonadaptive-soundness, definition:narg-adaptive-soundness]
  [CY24 §Interactive arguments, definition:iarg-adaptive-soundness]
- **Additional security definitions** (first one). Straightline and rewinding knowledge soundness,
  witness-extended emulation, non-adaptive and adaptive zero knowledge (simulator programs the oracle).
  [CY24 §Knowledge soundness, definition:adaptive-straightline-knowledge-soundness, definition:adaptive-rewinding-knowledge-soundness, definition:narg-witness-extended-emulation]
  [CY24 §Zero knowledge, definition:once-nonadaptive-zk-narg, definition:once-adaptive-zk-narg]
- **Basic observations about arguments.** Error reduction by repetition; the generic non-adaptive → adaptive
  compiler and why it costs a factor t; size lower bounds; why ZK needs a programmable oracle. Open it when
  someone claims adaptive security "for free" or a proof shorter than the soundness level allows.
  [CY24 §Non-adaptive vs. adaptive security, lemma:non-adaptive-to-adaptive-soundness, remark:separate-adaptive-vs-nonadaptive-soundness]
  [CY24 §Lower bound on argument size, lemma:lower-bound-on-argument-size]
- **Arguments in general oracle settings.** The same definitions when several oracles with different output
  sets are used, indifferentiability, and deriving many oracles from one by domain separation. Open it for any
  protocol with more than one hash role. [CY24 §Definitions, definition:narg-adaptive-soundness-with-general-oracle, definition:once-adaptive-zk-narg-with-general-oracle]
  [CY24 §The setting of multiple random oracles, section:rom-derive-multiple-from-single, lemma:multiple-from-single-construction]

### Part: NARGs Based on SPs

- **Sigma protocols.** Definitions (soundness, knowledge soundness, HVZK) for three-move public-coin protocols.
  [CY24 §Definition, definition:sp-soundness, definition:sp-knowledge-soundness, definition:sp-hvzk]
- **Warmup: non-adaptive security.** Fiat–Shamir without the instance in the hash: a lower bound showing the
  t-fold loss is real, and the explicit attacks that break adaptive soundness and adaptive ZK. The worked
  example behind every "hash the statement" check.
  [CY24 §Lower bound on the non-adaptive soundness error, lemma:attack-against-warmup-narg-from-sp]
  [CY24 §Lack of adaptive security, section:fs-lack-of-adaptive-soundness, section:fs-lack-of-adaptive-zk]
- **The Fiat–Shamir transformation for SPs.** The corrected construction (instance and salt hashed) and its
  adaptive soundness. [CY24 §The Fiat--Shamir transformation for SPs, construction:fs-for-sp, theorem:narg-from-sp-adaptive-soundness]
- **Additional security definitions** (SP chapter). Knowledge soundness and ZK of the compiled SP.
  [CY24 §Knowledge soundness, theorem:narg-from-sp-adaptive-knowledge-soundness] [CY24 §Zero knowledge, theorem:narg-from-sp-zero-knowledge]
- **State restoration.** The state-restoration game for SPs and why it is the right target notion.
  [CY24 §Definition, definition:sp-state-restoration-soundness] [CY24 §Comparison with standard soundness notions, lemma:sp-srs-to-soundness]

### Part: NARGs Based on IPs

- **Interactive proofs.** Multi-round public-coin IPs, their state-restoration game, and the gap between
  standard and state-restoration soundness (it can be exponential in the number of rounds). Open it for any
  many-round protocol that will be made non-interactive.
  [CY24 §State restoration, definition:ip-state-restoration-game, definition:ip-state-restoration-soundness, lemma:ip-sr-vs-standard]
- **The Fiat–Shamir transformation for IPs.** Basic multi-round FS (instance and all previous messages in every
  query), the matching lower bound (an SR attack is an attack on FS) and the upper bound.
  [CY24 §Construction, construction:basic-fs-for-public-coin-ip] [CY24 §Lower bound on the soundness error, lemma:attack-against-narg-from-ip]
  [CY24 §Soundness, theorem:basic-fs-for-public-coin-ip, remark:adaptivity-in-basic-fs]
- **Optimization: the hash-chain variant.** FS where each query carries only the previous challenge; costs an
  extra t²/2^λ term and needs every challenge to have at least λ bits.
  [CY24 §Construction, construction:hashchain-fs-for-public-coin-ip] [CY24 §Soundness, theorem:hashchain-fs-for-public-coin-ip]
- **Additional security definitions** (IP chapter). Knowledge soundness and ZK of the hash-chain variant (the ZK
  term depends on the salt size); reduction from state restoration.
  [CY24 §Knowledge soundness, theorem:hashchain-fs-knowledge-soundness] [CY24 §Zero knowledge, theorem:hashchain-fs-zero-knowledge]

### Part: Commitment Schemes

- **Basic commitment scheme.** Hash-based commitment: binding, extractability, hiding with explicit terms; the
  simplest worked example of security levels. [CY24 §Binding, lemma:cm-binding] [CY24 §Extractability, lemma:cm-extractability, lemma:cm-multi-extractability] [CY24 §Hiding, lemma:cm-hiding]
- **Merkle commitment scheme.** Definition with salts, collision lemma, binding, (multi-)extractability,
  hiding, equivocation. Every hash-based SNARK's Merkle error term comes from here.
  [CY24 §Collision lemma, lemma:mt-colliding-paths] [CY24 §Binding, lemma:mt-binding]
  [CY24 §Extractability, lemma:mt-extractability, lemma:mt-multi-extractability, lemma:mt-multi-configuration-multi-extractability]
  [CY24 §Hiding, lemma:mt-root-hiding, lemma:mt-privacy] [CY24 §Equivocation, lemma:mt-equivocation]

### Part: SNARGs Based on PCPs

- **Probabilistically checkable proofs.** PCP definitions; for PCPs, state-restoration soundness follows from
  standard soundness with a (t+1) factor. [CY24 §State restoration, theorem:pcp-srs-to-soundness, theorem:pcp-srk-to-knowledge]
- **Warmup: succinct interactive arguments from PCPs.** Kilian's interactive argument.
  [CY24 §Adaptive soundness, theorem:kilian-adaptive-soundness]
- **The Micali transformation.** Kilian + Fiat–Shamir analysed directly; the worked parameter example lives in
  the "Setting parameters" chapter. [CY24 §Construction, construction:micali-transformation] [CY24 §Soundness, theorem:micali-soundness, remark:micali-domain-separation]
- **Additional security definitions** (PCP chapter). [CY24 §Knowledge soundness, theorem:micali-knowledge-soundness] [CY24 §Zero knowledge, theorem:micali-zero-knowledge]

### Part: SNARGs Based on IOPs

- **Interactive oracle proofs.** IOP definitions and the IOP state-restoration game; the input notion for BCS.
  [CY24 §Definition, definition:iop-soundness, definition:iop-knowledge-straightline, definition:iop-hvzk] [CY24 §State restoration, definition:iop-state-restoration-soundness]
- **Warmup: succinct interactive arguments from IOPs.** Interactive BCS. [CY24 §Adaptive soundness, theorem:ibcs-adaptive-soundness]
- **The BCS transformation.** IOP + Merkle commitments + hash-chain FS; soundness in terms of the IOP's
  state-restoration error plus Merkle and hash-chain terms. The main theorem for STARK-style systems.
  [CY24 §Construction, construction:bcs-transformation] [CY24 §Soundness, theorem:bcs-soundness, lemma:ibcs-sr-soundness-reduction]
- **Additional security definitions** (IOP chapter). [CY24 §Knowledge soundness, theorem:bcs-knowledge-soundness] [CY24 §Zero knowledge, theorem:bcs-zero-knowledge]

### Part: Practical Considerations

- **Constructions of probabilistic proofs.** Short orientation on which IPs/PCPs/IOPs are used in practice and
  which known protocols have RBR or special soundness (with references out of the book).
  [CY24 §Strong soundness properties, section:strong-soundness-properties]
- **Setting parameters.** Asymptotic vs concrete security; the worst-case and average-case security-level
  definitions; worked parameter choices for Micali and BCS. Open it before writing any "λ-bit" claim.
  [CY24 §Security levels, section:security-levels] [CY24 §Concrete security for argument systems, section:concrete-security-for-micali, section:concrete-security-for-bcs]
- **Merkle commitment scheme optimizations.** Arbitrary message lengths and path pruning (proof-size
  accounting for multi-openings). [CY24 §Path pruning, lemma:path-pruning-lower-and-upper]
- **Special soundness.** Forks and trees of transcripts, and the extractors that turn special soundness into
  (state-restoration) knowledge soundness, with explicit errors.
  [CY24 §Extraction from forks and trees, definition:sp-special-soundness, definition:ip-special-soundness]
  [CY24 §Knowledge soundness for IPs, theorem:ss-to-knowledge-soundness-for-ip] [CY24 §State-restoration knowledge soundness for IPs, theorem:ss-to-sr-knowledge-soundness-for-ip]
- **Round-by-round soundness.** State functions and "doomed" transcripts; RBR (knowledge) soundness implies the
  state-restoration notions with a (t + k) factor. The usual route for FRI/STIR/WHIR-based protocols.
  [CY24 §Definition, def:iop-round-by-round-soundness, def:iop-round-by-round-knowledge]
  [CY24 §RBR soundness implies SR soundness, theorem:rbr-soundness-to-sr-soundness] [CY24 §RBR knowledge soundness implies SR knowledge soundness, theorem:rbr-knowledge-soundness-to-sr-knowledge-soundness]
- **Argument systems with preprocessing.** Indexed relations, holographic IOPs, and the COS transformation
  (BCS with an indexer committing to the circuit). [CY24 §The preprocessing setting, definition:indexed-relation-and-language]
  [CY24 §Holographic IOPs, definition:hiop-soundness] [CY24 §Security of the COS transformation, theorem:cos-soundness, theorem:cos-knowledge-soundness, theorem:cos-zero-knowledge]
- **Witness indistinguishability.** WI definitions and which constructions preserve it.
  [CY24 §Definition for non-interactive arguments, definition:wi-narg, lemma:narg-zk-implies-wi]
- **Error bounds** (back matter). One-page tables of every bound in the book; the fastest way to find the right
  theorem. [CY24 §Error bounds, table:commitment-error-bounds, table:narg-error-bounds, table:rbr-error-bounds, table:ss-error-bounds]

## By task: what to open

| task (skill) | open |
|---|---|
| state the security notion and model (zk-definitions) | [CY24 §Non-interactive arguments, definition:narg-adaptive-soundness] · [CY24 §Knowledge soundness, definition:adaptive-straightline-knowledge-soundness, definition:adaptive-rewinding-knowledge-soundness] · [CY24 §Zero knowledge, definition:once-adaptive-zk-narg] · [CY24 §Definition, definition:the-rom] |
| write an extractor or a simulator (zk-definitions) | [CY24 §Extraction from forks and trees, definition:ss-tree-of-transcripts] · [CY24 §Knowledge soundness for SPs, theorem:ss-to-knowledge-soundness-for-sp] · [CY24 §Zero knowledge, construction:fs-simulator] |
| turn a bound into a security level (soundness-budget) | [CY24 §Security levels, section:security-levels] · [CY24 §Concrete security for argument systems, section:concrete-security-for-bcs] |
| Merkle error terms (soundness-budget) | [CY24 §Binding, lemma:mt-binding] · [CY24 §Extractability, lemma:mt-multi-configuration-multi-extractability] |
| FS loss for many-round protocols (soundness-budget, fiat-shamir-audit) | [CY24 §State restoration, lemma:ip-sr-vs-standard] · [CY24 §RBR soundness implies SR soundness, theorem:rbr-soundness-to-sr-soundness] · [CY24 §Soundness, theorem:hashchain-fs-for-public-coin-ip] |
| what goes into each hash query (fiat-shamir-audit) | [CY24 §Lack of adaptive security, section:fs-lack-of-adaptive-soundness] · [CY24 §Construction, construction:basic-fs-for-public-coin-ip, construction:hashchain-fs-for-public-coin-ip] · [CY24 §The setting of multiple random oracles, section:rom-derive-multiple-from-single] |
| salts for ZK (fiat-shamir-audit) | [CY24 §Lack of adaptive security, section:fs-lack-of-adaptive-zk] · [CY24 §Zero knowledge, theorem:hashchain-fs-zero-knowledge] · [CY24 §Hiding, lemma:mt-privacy] |
| compile an IOP with Merkle trees (piop-pcs-compile) | [CY24 §Soundness, theorem:bcs-soundness] · [CY24 §Knowledge soundness, theorem:bcs-knowledge-soundness] · [CY24 §Zero knowledge, theorem:bcs-zero-knowledge] |
| preprocessing / holography (piop-pcs-compile) | [CY24 §The COS transformation, construction:cos-transformation] · [CY24 §Security of the COS transformation, theorem:cos-soundness] |
| Merkle opening and argument size (prover-cost-model) | [CY24 §Path pruning, lemma:path-pruning-is-copaths-minus-paths, lemma:path-pruning-lower-and-upper] · [CY24 §Construction, construction:bcs-transformation, equation:bcs-prover-to-verifier] |
| check an adaptive-vs-non-adaptive claim (falsify) | [CY24 §Non-adaptive vs. adaptive security, lemma:non-adaptive-to-adaptive-soundness] · [CY24 §Lack of adaptive security, section:fs-lack-of-adaptive-soundness] |
