# Thaler navigation map

Thaler, *Proofs, Arguments, and Zero-Knowledge*, author's PDF dated July 18, 2023, sha256 `ef4e0fdb…`
(pinning and citation rules: [../README.md](../README.md); full verified TOC:
[../../textbooks/toc/thaler-proofs-arguments-and-zero-knowledge.md](../../textbooks/toc/thaler-proofs-arguments-and-zero-knowledge.md);
terms: [../GLOSSARY.md](../GLOSSARY.md)). This file is a **map**: what each chapter is for and when to open it.
No text from the book is reproduced here, and none may be (no direct quotation at all for this book).

Thaler is the default source for *designing* probabilistic proofs and for the algebraic route (discrete-log and
pairing commitments, linear PCPs, AGM/GGM-based SNARKs). Its security definitions are mostly informal and
asymptotic; for a precise definition or a concrete hash-based error bound use CY24 ([../hash-snargs/MAP.md](../hash-snargs/MAP.md)).
Lookup arguments (beyond a short plookup overview in ch. 6), most folding schemes, STIR/WHIR, Binius and
small-field soundness are not covered: cite the original papers ("source: other").

## Chapters

- **1–2. Introduction; fingerprinting and Freivalds.** Motivation and the first randomised checks
  (Reed–Solomon fingerprinting). Open for intuition on why low-degree checks work.
  [Thaler §2.1, Reed-Solomon Fingerprinting] [Thaler §2.4, Univariate Lagrange Interpolation]
- **3. Definitions and technical preliminaries.** Informal IP and argument definitions, Schwartz–Zippel,
  low-degree and multilinear extensions. The standard place to cite the Schwartz–Zippel term of a budget.
  [Thaler §3.1, Interactive Proofs] [Thaler §3.2, Argument Systems] [Thaler §3.4, Schwartz-Zippel Lemma]
  [Thaler §3.5, Low Degree and Multilinear Extensions]
- **4. Interactive proofs.** The sum-check protocol with its soundness error, applications, and GKR with its
  costs and soundness. Open for any sum-check-based PIOP and its per-round error.
  [Thaler §4.1, The Sum-Check Protocol] [Thaler §4.5.2, A Useful Subroutine: Reducing Multiple Polynomial Evaluations to One]
  [Thaler §4.6, The GKR Protocol and Its Efficient Implementation] [Thaler §4.6.5, Discussion of Costs and Soundness]
- **5. Fiat–Shamir.** Random oracle model, the transformation (including why the statement must be hashed and
  the weak/strong FS naming), statistical vs computational bits of security, grinding, knowledge soundness
  under FS. Read with CY24's FS chapters, which give the precise bounds.
  [Thaler §5.1, The Random Oracle Model] [Thaler §5.2, The Fiat-Shamir Transformation]
  [Thaler §5.3.1, “Bits of Security”: Statistical vs. Computational] [Thaler §5.3.3, Fiat-Shamir Preserves Knowledge-Soundness in the Random Oracle Model]
- **6. Front ends.** From programs to circuit satisfiability, memory checking, non-arithmetic operations,
  CPU-like vs ASIC-like front ends. Open for constraint counting and circuit design.
  [Thaler §6.5, Turning Computer Programs Into Circuit Satisfiability Instances] [Thaler §6.6, Alternative Transformations and Optimizations]
- **7. A first succinct argument.** GKR + polynomial commitment; the informal knowledge-soundness and
  extractable-PCS notions. [Thaler §7.3, A First Succinct Argument for Circuit Satisfiability] [Thaler §7.4, Knowledge-Soundness]
- **8. MIPs.** Two-prover protocols, the Clover-style MIP for circuit SAT and its R1CS extension.
  [Thaler §8.4, Extension from Circuit-SAT to R1CS-SAT]
- **9. PCPs.** PCP definitions, Kilian/Micali from PCPs, knowledge soundness of those arguments.
  [Thaler §9.2, Compiling a PCP Into a Succinct Argument] [Thaler §9.2.1, Knowledge-Soundness of Kilian and Micali’s Arguments]
- **10. Interactive oracle proofs.** IOPs and polynomial IOPs, univariate sum-check PIOP for R1CS, FRI and its
  soundness regimes (proven vs conjectured), Ligero/Brakedown commitments. Open for any FRI-based PCS.
  [Thaler §10.2, Polynomial IOPs and Associated Succinct Arguments] [Thaler §10.3, A Polynomial IOP for R1CS-satisfiability]
  [Thaler §10.4, FRI and Associated Polynomial Commitments] [Thaler §10.4.4, Details of FRI: Better Reed-Solomon Proximity Proofs via Interaction]
  [Thaler §10.5, Ligero and Brakedown Polynomial Commitments] [Thaler §10.6, Unifying IPs, MIPs, and IOPs via Polynomial IOPs]
- **11. Zero-knowledge.** Informal ZK definitions and their variants (perfect / statistical / computational,
  honest-verifier vs malicious, plain vs auxiliary input), limits of SZK. [Thaler §11.1, What is Zero-Knowledge?]
- **12. Σ-protocols and commitments from discrete log.** Schnorr, special soundness, FS for Σ-protocols,
  Pedersen commitments and proving relations between committed values.
  [Thaler §12.2.1, Σ-Protocols] [Thaler §12.2.3, Fiat-Shamir Applied to Σ-Protocols] [Thaler §12.3, A Homomorphic Commitment Scheme]
- **13. ZK via commit-and-prove and masking polynomials.** The two generic ways to add ZK to a sum-check or
  IP-based argument. Open when the PCS openings leak evaluations. [Thaler §13.1, Proof Length of Witness Size Plus Multiplicative Complexity]
  [Thaler §13.3, Zero-Knowledge via Masking Polynomials] [Thaler §13.4, Discussion and Comparison]
- **14. Polynomial commitments from discrete log.** Hyrax-style and Bulletproofs/IPA commitments.
  [Thaler §14.3, Trading Off Commitment Size and Verification Costs] [Thaler §14.4, Bulletproofs]
- **15. Polynomial commitments from pairings.** Pairing background, KZG (SDH binding, extractability via
  knowledge assumptions or the GGM/AGM, trusted setup), multilinear KZG, Dory.
  [Thaler §15.1, Cryptographic Background] [Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup]
  [Thaler §15.3, Extension of KZG to Multilinear Polynomials] [Thaler §15.4, Dory: Transparent Scheme with Logarithmic Verification Costs]
- **16. Wrap-up of polynomial commitments.** Batch evaluation, sparse polynomials, and a comparison table of
  PCS trade-offs. [Thaler §16.1, Batch Evaluation of Homomorphically Committed Polynomials] [Thaler §16.3, Polynomial Commitment Schemes: Pros and Cons]
- **17. Linear PCPs.** From linear PCPs to SNARKs (GGPR), public input handling, ZK for the SNARK; the
  Groth16 line of work. [Thaler §17.4, GGPR: A Linear PCP Of Size O(|F|S) for Circuit-SAT and R1CS]
  [Thaler §17.5, Non-Interactivity and Public Verifiability] [Thaler §17.5.5, Handling Public Input]
- **18. Composition and recursion.** SNARK composition, recursion for iterative computation, and folding (Nova).
  [Thaler §18.1, Composing Two Different SNARKs] [Thaler §18.4, SNARKs for Iterative Computation via Recursion]
  [Thaler §18.5, SNARKs for Iterative Computation via Homomorphic Commitments]
- **19. Bird's-eye view.** A taxonomy of SNARK designs and their trade-offs; field choice and cost of
  operations. Open when positioning a paper. [Thaler §19.1, A Taxonomy of SNARKs] [Thaler §19.3.1, Field choice]

## By task: what to open

| task (skill) | open |
|---|---|
| Schwartz–Zippel and sum-check error terms (soundness-budget) | [Thaler §3.4, Schwartz-Zippel Lemma] · [Thaler §4.1, The Sum-Check Protocol] · [Thaler §4.6.5, Discussion of Costs and Soundness] |
| FRI proven vs conjectured proximity regime (soundness-budget) | [Thaler §10.4.4, Details of FRI: Better Reed-Solomon Proximity Proofs via Interaction] — then the papers listed in soundness-budget |
| statistical vs computational bits, grinding (soundness-budget) | [Thaler §5.3.1, “Bits of Security”: Statistical vs. Computational] |
| ZK flavours, masking, commit-and-prove (zk-definitions) | [Thaler §11.1, What is Zero-Knowledge?] · [Thaler §13.3, Zero-Knowledge via Masking Polynomials] · [Thaler §13.1, Proof Length of Witness Size Plus Multiplicative Complexity] |
| knowledge soundness and extractable PCS (zk-definitions, piop-pcs-compile) | [Thaler §7.4, Knowledge-Soundness] · [Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup] |
| AGM / GGM / knowledge assumptions (zk-definitions) | [Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup] · [Thaler §17.5, Non-Interactivity and Public Verifiability] |
| hash the statement, weak vs strong FS (fiat-shamir-audit) | [Thaler §5.2, The Fiat-Shamir Transformation] · [Thaler §12.2.3, Fiat-Shamir Applied to Σ-Protocols] |
| write the protocol as a PIOP (piop-pcs-compile) | [Thaler §10.2, Polynomial IOPs and Associated Succinct Arguments] · [Thaler §10.6, Unifying IPs, MIPs, and IOPs via Polynomial IOPs] |
| pick and check a PCS (piop-pcs-compile) | [Thaler §14.4, Bulletproofs] · [Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup] · [Thaler §10.4, FRI and Associated Polynomial Commitments] · [Thaler §16.1, Batch Evaluation of Homomorphically Committed Polynomials] · [Thaler §16.3, Polynomial Commitment Schemes: Pros and Cons] |
| circuits and front ends (constraint-cost, later batch) | [Thaler §6.5, Turning Computer Programs Into Circuit Satisfiability Instances] · [Thaler §8.4.1, Relationship Between R1CS-SAT and Arithmetic Circuit-SAT] |
