# Glossary: canonical ZK terms for this repository

Every skill, agent and paper draft uses these terms with these meanings. Each row is a one-line definition in our
own words plus the place to read the precise statement. Source order: **CY24** for definitions and hash-based
analysis, **Thaler** for algebraic constructions and protocol design, **other** (a checked ePrint id or DOI) for
anything neither book covers. Citation rules: [README.md](README.md). Notation used below: λ = random-oracle
output size (security parameter), t = adversary's query bound, k = number of rounds, s = target security level in
bits, n = instance size bound.

Terms in **bold** are on the ZK term-protection list of [`skills/polish-writing`](../../skills/polish-writing/SKILL.md):
never merge or swap them in an edit. The pairs on that list are: proof ↔ argument, zero-knowledge ↔ honest-verifier
ZK, soundness ↔ knowledge soundness, SNARK ↔ zkSNARK ↔ SNARG, succinct ↔ short, transparent ↔ universal setup,
proven ↔ conjectured, statistical ↔ computational ZK.

## Proof systems and models

| term | definition (repository usage) | source |
|---|---|---|
| **proof** | soundness holds against unbounded provers (statistical soundness) | [Thaler §3.1, Interactive Proofs] |
| **argument** | soundness holds only against bounded provers: query-bounded in the ROM, polynomial-time under an assumption otherwise | [CY24 §Non-interactive arguments, definition:narg-adaptive-soundness] · [Thaler §3.2, Argument Systems] |
| NARG / IARG | non-interactive / interactive argument | [CY24 §Arguments in the ROM, chapter:argument-definitions] |
| **succinct** | argument size (and, in this repository, verifier time) much smaller than the witness / the computation; "short" alone bounds size only | [CY24 §Succinct arguments, section:arg-succinctness] |
| **SNARG** | succinct non-interactive argument (no knowledge claim) | [CY24 §Succinct arguments, section:arg-succinctness] |
| **SNARK** | SNARG with knowledge soundness | [CY24 §Succinct arguments, section:arg-succinctness] |
| **zkSNARK** | SNARK that is also zero-knowledge | [CY24 §Succinct arguments, section:arg-succinctness] |
| ROM | every party gets oracle access to a uniformly random function; security is stated against t-query adversaries | [CY24 §Definition, definition:the-rom] · [Thaler §5.1, The Random Oracle Model] |
| programmable ROM (EPROM) | the ZK simulator may output a list of oracle positions and answers that override the random oracle; required for ZK in the ROM | [CY24 §Zero knowledge, definition:once-adaptive-zk-narg] · [CY24 §Limitation on zero knowledge, lemma:npro-limitation] |
| general oracle setting | several independent oracles with different output sets; derived from one oracle by domain separation | [CY24 §Definitions, definition:narg-adaptive-soundness-with-general-oracle] · [CY24 §The setting of multiple random oracles, section:rom-derive-multiple-from-single] |
| standard model | no idealised oracle or group; security from falsifiable assumptions on concrete objects | [CY24 §Succinct arguments, section:arg-succinctness] |
| GGM | generic group model: the adversary uses the group only through an oracle for the group operation | [Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup] — not covered by CY24 |
| AGM | algebraic group model: every group element the adversary outputs comes with its representation over the elements it received | [Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup]; source: other, Fuchsbauer–Kiltz–Loss, ePrint 2017/620 — not covered by CY24 |
| trusted setup / SRS | public parameters sampled with secret randomness ("toxic waste") that must be destroyed | [Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup] |
| **universal setup** | one trusted (possibly updatable) SRS reusable for every circuit up to a size bound | source: other, Marlin, ePrint 2019/1047; PLONK, ePrint 2019/953 |
| **transparent** | public parameters involve no secret randomness (e.g. only the choice of hash function) | [CY24 §Preface, section:preface] |
| preprocessing / indexer | a one-time, public, deterministic step that encodes the circuit (index) so the verifier can run in time sublinear in it | [CY24 §The preprocessing setting, definition:indexed-relation-and-language] |
| holographic IOP | IOP whose verifier reads the index only through oracle queries to an encoding produced by an indexer | [CY24 §Holographic IOPs, definition:hiop-soundness] |
| PIOP (polynomial IOP) | IOP whose prover messages are polynomials of bounded degree that the verifier queries at points of its choice | [Thaler §10.2, Polynomial IOPs and Associated Succinct Arguments] |
| IOP / PCP / IP / MIP | interactive oracle proof / probabilistically checkable proof / interactive proof / multi-prover IP | [CY24 §Definition, definition:iop-soundness] · [CY24 §Definition, definition:pcp-soundness] · [CY24 §Definition, definition:ip-soundness] · [Thaler §8.1, MIPs: Definitions and Basic Results] |
| Σ-protocol (SP) | three-move public-coin protocol: commitment, random challenge, response | [CY24 §Definition, definition:sp-soundness] · [Thaler §12.2.1, Σ-Protocols] |
| public-coin | every verifier message is fresh uniform randomness; required by every FS-style transformation | [CY24 §Interactive arguments, definition:arg-public-coin] |

## Soundness notions

| term | definition (repository usage) | source |
|---|---|---|
| **soundness** | a cheating prover makes the verifier accept a false instance with probability at most ε | [CY24 §Non-interactive arguments, definition:narg-adaptive-soundness] |
| non-adaptive soundness | the bound holds for every instance fixed *before* the oracle is sampled | [CY24 §Non-interactive arguments, definition:narg-nonadaptive-soundness] |
| adaptive soundness | the adversary picks the instance after querying the oracle; the default in this repository | [CY24 §Non-interactive arguments, definition:narg-adaptive-soundness] · [CY24 §Non-adaptive vs. adaptive security, remark:separate-adaptive-vs-nonadaptive-soundness] |
| **knowledge soundness** | an efficient extractor outputs a valid witness whenever the verifier accepts, except with probability κ | [CY24 §Knowledge soundness, definition:adaptive-straightline-knowledge-soundness] · [Thaler §7.4, Knowledge-Soundness] |
| straightline knowledge soundness | the extractor sees only the prover's output and its oracle query/answer trace (no rewinding, no reprogramming) | [CY24 §Knowledge soundness, definition:adaptive-straightline-knowledge-soundness] |
| rewinding knowledge soundness | the extractor may re-run the prover with fixed randomness; error and expected running time may depend on the prover's success probability | [CY24 §Knowledge soundness, definition:adaptive-rewinding-knowledge-soundness] |
| witness-extended emulation (WEE) | an emulator outputs a transcript distributed like the real one together with a witness whenever that transcript accepts | [CY24 §Knowledge soundness, definition:narg-witness-extended-emulation]; origin: source: other, Lindell, ePrint 2001/107 |
| state-restoration (SR) soundness | soundness of an IP/IOP against a prover that may rewind the verifier to any earlier state and resample, within a move budget; what Fiat–Shamir actually needs | [CY24 §State restoration, definition:ip-state-restoration-soundness] · [CY24 §State restoration, definition:iop-state-restoration-soundness] |
| SR knowledge soundness | the knowledge analogue of SR soundness | [CY24 §State restoration, definition:ip-state-restoration-knowledge] |
| special soundness | a witness can be computed from a fork (SP) or a tree (IP) of accepting transcripts with distinct challenges; arity = number of branches per round | [CY24 §Extraction from forks and trees, definition:sp-special-soundness, definition:ip-special-soundness] · [Thaler §12.2.1, Σ-Protocols] |
| round-by-round (RBR) soundness | a state function marks partial transcripts "doomed"; each round escapes doom with probability at most ε_rbr; implies SR soundness with a (t + k) factor | [CY24 §Definition, def:iop-round-by-round-soundness] · [CY24 §RBR soundness implies SR soundness, theorem:rbr-soundness-to-sr-soundness] |
| RBR knowledge soundness | the knowledge analogue of RBR soundness, with a straightline extractor per round | [CY24 §Definition, def:iop-round-by-round-knowledge] |
| simulation-extractability | knowledge soundness that still holds after the adversary sees simulated proofs (needed against proof malleability) | source: other, Groth–Maller ePrint 2017/540; Ganesh et al. ePrint 2021/511 — not covered by CY24 or Thaler |

## Zero-knowledge notions

| term | definition (repository usage) | source |
|---|---|---|
| **zero-knowledge** | a simulator, without the witness, produces proofs indistinguishable from real ones; for non-interactive arguments the simulator may program the oracle | [CY24 §Zero knowledge, definition:once-adaptive-zk-narg] · [Thaler §11.1, What is Zero-Knowledge?] |
| **honest-verifier ZK** (HVZK) | simulation only of the honest verifier's view (uniform challenges); the input property for FS-compiled ZK | [CY24 §Definition, definition:ip-hvzk] · [CY24 §Definition, definition:iop-hvzk] · [Thaler §11.1, What is Zero-Knowledge?] |
| non-adaptive ZK | indistinguishability for an instance–witness pair fixed before the oracle is sampled | [CY24 §Zero knowledge, definition:once-nonadaptive-zk-narg] |
| once-adaptive ZK | the adversary queries the oracle, then picks (x, w), then sees **one** real or simulated proof; CY24's adaptive ZK and the default here | [CY24 §Zero knowledge, definition:once-adaptive-zk-narg] · [CY24 §Definitions, definition:once-adaptive-zk-narg-with-general-oracle] |
| multi-adaptive ZK | as once-adaptive, but for many proofs requested adaptively; claim it only with a proof that covers many proofs | not defined in CY24 or Thaler: source: other, `needs verification` |
| perfect / **statistical** / **computational ZK** | simulated and real distributions are identical / statistically close / computationally indistinguishable; CY24's ZK is statistical in the query bound t | [Thaler §11.1, What is Zero-Knowledge?] · [CY24 §Zero knowledge, definition:once-adaptive-zk-narg] |
| witness indistinguishability (WI) | proofs under two different witnesses for the same instance are indistinguishable; implied by ZK | [CY24 §Definition for non-interactive arguments, definition:wi-narg, lemma:narg-zk-implies-wi] |
| masking polynomial | a random polynomial added to the prover's message so that revealed evaluations are uniformly distributed | [Thaler §13.3, Zero-Knowledge via Masking Polynomials] |
| commit-and-prove | the prover commits to the witness and proves statements about committed values with Σ-protocols | [Thaler §13.1, Proof Length of Witness Size Plus Multiplicative Complexity] |

## Commitment properties

| term | definition (repository usage) | source |
|---|---|---|
| binding | no t-query adversary opens one commitment to two different values at the same position (Merkle: error ≈ t²/2^{λ+1}) | [CY24 §Binding, lemma:cm-binding, lemma:mt-binding] |
| extractability | from the adversary's query trace up to the commitment, an extractor recovers the committed message, and every later valid opening is consistent with it | [CY24 §Extractability, lemma:cm-extractability, lemma:mt-extractability] · [Thaler §7.4, Knowledge-Soundness] (extractable PCS) |
| multi-extractability | extractability for many commitments produced adaptively by one adversary | [CY24 §Extractability, lemma:mt-multi-extractability, lemma:mt-multi-configuration-multi-extractability] |
| hiding | the commitment (and, for Merkle trees, opened paths) reveals nothing about unopened values; needs salts | [CY24 §Hiding, lemma:cm-hiding, lemma:mt-root-hiding, lemma:mt-privacy] |
| equivocation | a simulator can produce a commitment first and open it to any value later; used in ZK proofs | [CY24 §Equivocation, lemma:mt-equivocation] |
| evaluation binding (PCS) | no adversary opens one polynomial commitment at one point to two different values | [Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup] |
| PCS | polynomial commitment scheme: commit to a polynomial of bounded degree, later prove evaluations | [Thaler §7.3, A First Succinct Argument for Circuit Satisfiability] · [Thaler §16.3, Polynomial Commitment Schemes: Pros and Cons] |
| KZG | pairing-based univariate PCS with constant-size commitments and openings; trusted setup; binding under SDH, extractability via knowledge assumptions or GGM/AGM | [Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup] |
| IPA / Bulletproofs | discrete-log inner-product-argument PCS; transparent, logarithmic proofs, linear verifier | [Thaler §14.4, Bulletproofs] |
| FRI | interactive Reed–Solomon proximity test; with Merkle trees it gives a transparent hash-based PCS | [Thaler §10.4, FRI and Associated Polynomial Commitments] |
| Merkle commitment | hash tree over (salted) leaves; opening = authentication paths | [CY24 §Definition, definition:mt-graph] |

## Transformations

| term | definition (repository usage) | source |
|---|---|---|
| Fiat–Shamir (FS) | replace each verifier challenge of a public-coin protocol by a hash of the transcript so far, **including the instance** | [CY24 §The Fiat--Shamir transformation for SPs, construction:fs-for-sp] · [Thaler §5.2, The Fiat-Shamir Transformation] |
| weak FS | FS that omits the instance (or public input / parameters) from the hash: only non-adaptive security | [CY24 §Lack of adaptive security, section:fs-lack-of-adaptive-soundness] · [Thaler §5.2, The Fiat-Shamir Transformation] |
| multi-round FS (basic) | FS for a k-round IP: round i hashes the instance and all previous prover messages and salts; soundness = the IP's SR soundness | [CY24 §Construction, construction:basic-fs-for-public-coin-ip] · [CY24 §Soundness, theorem:basic-fs-for-public-coin-ip] |
| hash-chain FS | multi-round FS where round i hashes only the previous challenge, the new message and a salt (instance only in round 1); extra error t²/2^λ | [CY24 §Construction, construction:hashchain-fs-for-public-coin-ip] · [CY24 §Soundness, theorem:hashchain-fs-for-public-coin-ip] |
| Kilian | interactive argument: Merkle-commit to a PCP, verifier sends query randomness, prover opens | [CY24 §Warmup: succinct interactive arguments from PCPs, construction:kilian-transformation] · [Thaler §9.2, Compiling a PCP Into a Succinct Argument] |
| Micali | Kilian made non-interactive with FS (query randomness derived from the Merkle root) | [CY24 §Construction, construction:micali-transformation] |
| BCS | IOP → non-interactive argument: Merkle-commit to each oracle message, derive challenges by hash-chain FS | [CY24 §Construction, construction:bcs-transformation] · source: other, ePrint 2016/116 |
| COS | BCS for holographic IOPs: an indexer Merkle-commits to the index encoding once; gives preprocessing SNARGs | [CY24 §The COS transformation, construction:cos-transformation] |
| PIOP + PCS compilation | replace each polynomial oracle by a PCS commitment and each query by an evaluation proof, then apply FS | [Thaler §10.2, Polynomial IOPs and Associated Succinct Arguments] — the hash-based instance of this is BCS |
| grinding / proof of work | the prover must find a nonce whose hash has b leading zeros before a challenge; adds about b bits against attackers who must redo it | [Thaler §5.3.1, “Bits of Security”: Statistical vs. Computational] (grinding attacks); for the defence: source: other, ethSTARK, ePrint 2021/582 |

## Security levels

| term | definition (repository usage) | source |
|---|---|---|
| concrete security | an explicit error bound ε(λ, n, t) for every query bound t, as opposed to "negligible in λ" | [CY24 §Asymptotic vs. concrete security, section:asymptotic-vs-concrete-security] |
| worst-case security level s | ε(λ, n, t) ≤ 2^{−s} for every t ≤ 2^s | [CY24 §Security levels, section:security-levels] |
| average-case security level s | t / ε(λ, n, t) ≥ 2^s for every t ≤ 2^s (expected cost of a successful attack); weaker than worst-case, needs a smaller λ | [CY24 §Security levels, section:security-levels] |
| statistical vs computational security | bits against an unbounded prover in the interactive protocol vs bits against a bounded attacker after FS | [Thaler §5.3.1, “Bits of Security”: Statistical vs. Computational] |
| **proven** / **conjectured** | a soundness term comes from a theorem (e.g. FRI up to the Johnson bound) / from an unproven conjecture (e.g. proximity up to capacity); never mix in one comparison | [Thaler §10.4.4, Details of FRI: Better Reed-Solomon Proximity Proofs via Interaction]; source: other, ePrint 2020/654, 2025/2046 |

Every security claim in this repository states **which** level (worst-case or average-case) it uses, and every
budget table states it in its header.

## Algebraic and design terms (Thaler)

| term | definition (repository usage) | source |
|---|---|---|
| Schwartz–Zippel | a nonzero polynomial of total degree d vanishes at a uniform point of S^m with probability ≤ d/|S| | [Thaler §3.4, Schwartz-Zippel Lemma] |
| multilinear extension (MLE) | the unique multilinear polynomial agreeing with a function on {0,1}^m | [Thaler §3.5, Low Degree and Multilinear Extensions] |
| sum-check | IP reducing a sum of a v-variate polynomial over the hypercube to one evaluation; soundness error ≤ v·d/|F| for individual degree d | [Thaler §4.1, The Sum-Check Protocol] |
| GKR | IP for layered arithmetic circuits built from one sum-check per layer | [Thaler §4.6, The GKR Protocol and Its Efficient Implementation] |
| front end | compiler from a program to a circuit / constraint system | [Thaler §6.5, Turning Computer Programs Into Circuit Satisfiability Instances] |
| R1CS | rank-1 constraint system (Az ∘ Bz = Cz) | [Thaler §8.4, Extension from Circuit-SAT to R1CS-SAT] |
| linear PCP | PCP whose proof is a linear function the verifier queries at chosen vectors; basis of GGPR/Groth16 | [Thaler §17.1, Overview: Interactive Arguments From “Long”, Structured PCPs] · [Thaler §17.4, GGPR: A Linear PCP Of Size O(|F|S) for Circuit-SAT and R1CS] |
| recursion / composition | proving the verifier of one SNARK inside another | [Thaler §18.1, Composing Two Different SNARKs] · [Thaler §18.4, SNARKs for Iterative Computation via Recursion] |
| folding | combining two instances of a relation into one with a random linear combination (Nova) | [Thaler §18.5, SNARKs for Iterative Computation via Homomorphic Commitments]; newer schemes: source: other |

## Where the two books differ, and what this repository uses

| notion | CY24 | Thaler | repository |
|---|---|---|---|
| knowledge soundness | concrete: Pr[accept ∧ extraction fails] ≤ κ(λ, n, t); two flavours (straightline; rewinding with error and expected time depending on the prover's failure probability) | informal and asymptotic: if the prover convinces with non-negligible probability, a poly-time extractor with rewinding access finds a witness with non-negligible probability ([Thaler §7.4, Knowledge-Soundness]) | **CY24**, and always say which flavour. Thaler's form is the asymptotic shadow of CY24's rewinding notion; it is not enough for a concrete budget. |
| zero-knowledge | statistical, single proof, adaptive choice of (x, w), explicitly programmable ROM | informal; perfect / statistical / computational, malicious vs honest verifier, plain vs auxiliary input | **CY24** for non-interactive hash-based arguments; Thaler's taxonomy to *name* the flavour of an interactive or algebraic protocol (e.g. "honest-verifier perfect ZK PIOP"). |
| "bits of security" | worst-case vs average-case security level of an error function | statistical security of the interactive protocol vs computational security after FS (grinding) | **CY24** levels; additionally state the statistical bits of the underlying IOP, as Thaler does. |
| multi-round FS hashing | basic FS hashes the instance in every query; the hash-chain variant hashes it only in the first query | describes a chaining variant that hashes the input and the round index with the previous challenge | Either is acceptable when its theorem is cited; implementations must match the variant whose bound is used (`skills/fiat-shamir-audit`). |
| algebraic models (AGM, GGM), pairings, SDH | out of scope (pure ROM) | covered for KZG and Groth16-style SNARKs | Thaler or the original paper; never transfer a CY24 bound to these settings. |
