# Building Cryptographic Proofs from Hash Functions (v1.2)

- **Author(s):** Alessandro Chiesa, Eylon Yogev
- **Format:** LaTeX source + PDF in the authors' repository (CC BY-SA 4.0); not in this repository. Fetch with
  `references/books/fetch.sh cy24`.
- **Pinned copy:** <https://github.com/hash-based-snargs-book/hash-based-snargs-book>, commit
  `305fa3d9d19ee6dba135de64b3156d1760df8426` ("Version 1.2")
- **TOC source:** generated 2026-10-27 from `snargs-book.tex` at the pinned commit
  (`python3 scripts/check_book_refs.py --dump-cy24-toc`). Parts, chapters and sections with their LaTeX labels;
  no numbers, because citations use labels (`[CY24 §<section name>, <label>]`, see `references/books/README.md`).
  Chapter-by-chapter navigation: [`references/books/hash-snargs/MAP.md`](../../books/hash-snargs/MAP.md).

## Table of contents
- Foreword — `section:foreword`
- Preface — `section:preface`
  - Motivation
  - Scope
  - Structure of the book
  - How to use this book
  - Acknowledgements
- Mathematical background — `chapter:mathematical-background`
  - Notation — `section:notation`
  - Probability — `section:probability`
  - Probabilistic experiments — `section:probabilistic-experiments`
  - Auxiliary (in)equalities — `section:equalities-and-inequalities`

**Part: What are Cryptographic Proofs?** (`part:what-are-crypto-proofs`)

- The random oracle model — `chapter:what-is-rom`
  - Definition — `section:rom-definition`
  - Simulation by lazy sampling — `section:rom-lazy-sampling`
  - Pseudorandom functions vs. random oracles — `section:prf-vs-ro`
  - Realizations — `section:rom-realizations`
  - Benefits and drawbacks — `section:rom-benefits-and-drawbacks`
- Basic cryptographic properties — `chapter:rom-basic-properties`
  - Unpredictability — `section:unpredictability`
  - Inversion resistance — `section:inversion-resistance`
  - Collision resistance — `section:collision-resistance`
  - Regularity — `section:regularity`
- Arguments in the ROM — `chapter:argument-definitions`
  - Non-interactive arguments — `section:narg-basics`
  - Interactive arguments — `section:iarg-basics`
  - Efficiency measures — `section:arg-efficiency-measures`
  - Succinct arguments — `section:arg-succinctness`
- Additional security definitions — `chapter:narg-advanced`
  - Knowledge soundness — `section:narg-knowledge-soundness`
  - Zero knowledge — `section:narg-zero-knowledge`
- Basic observations about arguments — `chapter:narg-warmup`
  - Error reduction — `section:soundness-error-reduction`
  - Non-adaptive vs. adaptive security — `section:non-adaptive-security`
  - Construction with an inefficient prover — `section:inefficient-prover-construction`
  - Lower bound on argument size — `section:lower-bound-on-argument-size`
  - Limitation on public randomness — `section:ursm-limitation`
  - Limitation on zero knowledge — `section:zero-knowledge-limitation`
  - Simulation on instances not in the language — `section:simulators-not-in-language`
- Arguments in general oracle settings — `chapter:narg-in-general-oracle-settings`
  - Definitions — `section:narg-definitions-with-oracle-distribution`
  - Indifferentiability — `section:indifferentiability`
  - Replacing the oracle setting — `section:narg-from-one-oracle-to-another-oracle`
  - The setting of multiple random oracles — `section:rom-derive-multiple-from-single`

**Part: NARGs Based on SPs** (`part:narg-from-sp`)

- Sigma protocols — `chapter:sp`
  - Definition — `section:definition-of-sp`
- Warmup: non-adaptive security — `chapter:warmup-narg-from-sp-nonadaptive-security`
  - Construction — `section:warmup-narg-from-sp-construction`
  - Lower bound on the non-adaptive soundness error — `section:warmup-narg-from-sp-lower-bound`
  - Non-adaptive soundness — `section:warmup-narg-from-sp-nonadaptive-soundness`
  - Non-adaptive knowledge soundness — `section:warmup-narg-from-sp-nonadaptive-knowledge-soundness`
  - Non-adaptive zero knowledge — `section:warmup-narg-from-sp-nonadaptive-zk`
  - Lack of adaptive security — `section:warmup-narg-from-sp-no-adaptive-security`
- The Fiat–Shamir transformation for SPs — `chapter:fiat-shamir-transformation-for-sp`
  - Construction — `section:narg-from-sp-construction`
  - Adaptive soundness — `section:narg-from-sp-adaptive-soundness`
- Additional security definitions — `chapter:fs-for-sp-additional`
  - Knowledge soundness — `section:fs-sigma-protocol-adaptive-knowledge-soundness`
  - Zero knowledge — `section:narg-from-sp-zero-knowledge`
- State restoration — `chapter:fs-for-sp-sr`
  - Definition — `section:sp-sr-definition`
  - Security from state restoration — `section:sp-fs-via-sr`
  - Comparison with standard soundness notions — `section:sp-sr-comparison`

**Part: NARGs Based on IPs** (`part:narg-from-ip`)

- Interactive proofs — `chapter:ip`
  - Definition — `section:ip-definitions`
  - State restoration — `section:fs-sr-attacks`
- The Fiat–Shamir transformation for IPs — `chapter:basic-fs-for-ip`
  - Construction — `section:basic-fs-for-ip`
  - Lower bound on the soundness error — `section:basic-fs-attack-sr`
  - Soundness — `section:basic-fs-reduction`
  - Knowledge soundness — `section:basic-fs-knowledge-soundness`
- Optimization: the hash-chain variant — `chapter:hashchain-fs-for-ip`
  - Construction — `section:hashchain-fs-for-ip`
  - Soundness — `section:hashchain-fs-reduction`
- Additional security definitions — `chapter:fs-additional`
  - Knowledge soundness — `section:fs-knowledge-soundness`
  - Zero knowledge — `section:fs-zero-knowledge`
  - A security reduction from state-restoration — `section:fs-direct-reduction-to-sr`

**Part: Commitment Schemes** (`part:commitment-schemes`)

- Basic commitment scheme — `chapter:basic-commitment`
  - Binding — `section:basic-commitment-binding`
  - Extractability — `section:basic-commitment-extractability`
  - Hiding — `section:basic-commitment-hiding`
- Merkle commitment scheme — `chapter:merkle-commitment`
  - Definition — `section:merkle-commitment-definition`
  - Completeness — `section:merkle-commitment-completeness`
  - Collision lemma — `section:merkle-commitment-collision-lemma`
  - Binding — `section:merkle-commitment-binding`
  - Extractability — `section:merkle-commitment-extractability`
  - Hiding — `section:merkle-commitment-hiding`
  - Equivocation — `section:merkle-commitment-equivocation`

**Part: SNARGs Based on PCPs** (`part:snarg-from-pcp`)

- Probabilistically checkable proofs — `chapter:pcp`
  - Definition — `section:pcp-definition`
  - State restoration — `section:pcp-state-restoration`
- Warmup: succinct interactive arguments from PCPs — `chapter:kilian-transformation`
  - Construction — `section:kilian-construction`
  - Non-adaptive soundness — `section:kilian-nonadaptive-soundness`
  - Adaptive soundness — `section:kilian-adaptive-soundness`
  - Additional security definitions — `section:kilian-additional-security-definitions`
- The Micali transformation — `chapter:micali-transformation`
  - Construction — `section:micali-construction`
  - Soundness — `section:micali-soundness`
- Additional security definitions — `chapter:micali-additional`
  - Knowledge soundness — `section:micali-knowledge-soundness`
  - Zero knowledge — `section:micali-zero-knowledge`

**Part: SNARGs Based on IOPs** (`part:snarg-from-iop`)

- Interactive oracle proofs — `chapter:iop`
  - Definition — `section:iop-definition`
  - State restoration — `section:iop-state-restoration`
- Warmup: succinct interactive arguments from IOPs — `chapter:ibcs-transformation`
  - Construction — `section:ibcs-construction`
  - Non-adaptive soundness — `section:ibcs-nonadaptive-soundness`
  - Adaptive soundness — `section:ibcs-adaptive-soundness`
- The BCS transformation — `chapter:bcs-transformation`
  - Construction — `section:bcs-construction`
  - Soundness — `section:bcs-soundness`
- Additional security definitions — `chapter:bcs-additional`
  - Knowledge soundness — `section:bcs-knowledge-soundness`
  - Zero knowledge — `section:bcs-zero-knowledge`

**Part: Practical Considerations** (`part:practical-considerations`)

- Constructions of probabilistic proofs — `chapter:constructions-of-probabilistic-proofs`
  - Interactive proofs — `section:known-ips`
  - Probabilistically checkable proofs — `section:known-pcps`
  - Interactive oracle proofs — `section:known-iops`
  - Strong soundness properties — `section:strong-soundness-properties`
- Setting parameters — `chapter:setting-parameters`
  - Asymptotic vs. concrete security — `section:asymptotic-vs-concrete-security`
  - Security levels — `section:security-levels`
  - Concrete security for argument systems — `section:concrete-security-for-argument-systems`
- Merkle commitment scheme optimizations — `chapter:mt-optimizations`
  - Any message length — `section:any-message-length`
  - Path pruning — `section:compressing-opening-proof`
- Special soundness — `chapter:special-soundness`
  - Extraction from forks and trees — `section:definitions-for-special-soundness`
  - Knowledge soundness for SPs — `section:ss-sigma-protocols-knowledge`
  - State-restoration knowledge soundness for SPs — `section:ss-sigma-protocols-sr-knowledge`
  - Knowledge soundness for IPs — `section:ss-to-knowledge-soundness`
  - State-restoration knowledge soundness for IPs — `section:ss-to-sr-knowledge-soundness`
- Round-by-round soundness — `chapter:rbr-soundness`
  - Definition — `section:rbr-definition`
  - RBR soundness implies SR soundness — `section:rbr-soundness-to-sr-soundness`
  - RBR knowledge soundness implies SR knowledge soundness — `section:rbr-knowledge-soundness-to-sr-knowledge-soundness`
- Argument systems with preprocessing — `chapter:preprocessing-snargs`
  - The preprocessing setting — `section:motivate-preprocessing`
  - The holographic setting — `section:motivate-holography`
  - From holography to preprocessing — `section:from-holography-to-preprocessing`
  - Non-interactive arguments with preprocessing — `section:preprocessing-narg`
  - Holographic IOPs — `section:holographic-iop`
  - State restoration for holographic IOPs — `section:hiop-state-restoration`
  - The COS transformation — `section:cos-transformation`
  - Security of the COS transformation — `section:cos-security`
- Witness indistinguishability — `chapter:witness-indistinguishability`
  - Definition for non-interactive arguments — `section:wi-for-nargs`
  - Definitions for probabilistic proofs — `section:wi-for-probabilistic-proofs`
  - Statements for constructions — `section:wi-for-constructions`
- Error bounds — `section:error-bounds`
- Glossary — `section:glossary`
  - Acronyms
  - Symbols
- Bibliographic notes — `section:bibliographic-notes`
