---
name: venue-calibration
description: Use when choosing a target venue for a ZK paper (protocol/theory, system/implementation, or application/circuit), adapting a draft to a venue's format, or calibrating a mock review. Summarises per-venue formats, what reviewers of ZK papers weigh, typical ZK rejection reasons with their pre-emptive fixes, and scoring rubrics for IACR venues (CRYPTO, EUROCRYPT, ASIACRYPT, TCC, PKC, TCHES), security venues (CCS, S&P, USENIX Security, NDSS, PoPETs) and blockchain venues (FC, AFT).
---

# Venue calibration

> **Everything numeric in this file (page limits, word limits, cycles, dates) changes
> between years. Treat it as orientation only and CHECK THE CURRENT CFP.** Record the
> CFP URL, the date you read it, and the exact quoted rules in `SUBMISSION.md` before
> you rely on them. Desk rejection "without consideration of merits" is common for
> format violations.

## 1. Format and process at a glance

| venue | template | body length (check the current CFP) | what counts | review process notes |
|---|---|---|---|---|
| CRYPTO | Springer LNCS | ~25–30 pp. at submission; camera-ready limit may differ | usually excludes references; supplementary material allowed but reviewers need not read it | anonymous; rebuttal/interactive phase in recent years; possible early reject round |
| EUROCRYPT | Springer LNCS | ~25–30 pp. | as above; body must be self-contained | two-stage process with early rejects before rebuttal in recent years (so first impression must come from the body alone) |
| ASIACRYPT | Springer LNCS | ~30 pp. | read carefully: some years count *everything before the references* (incl. appendices) toward the camera-ready limit | rebuttal + interactive phase with the meta-reviewer in recent years |
| TCC | Springer LNCS | check CFP | usually excludes references | theory audience; no experiments expected |
| PKC | Springer LNCS | check CFP | usually excludes references | public-key focus; implementation welcome but not required |
| TCHES (CHES) | IACR journal class (`iacrj`; older `iacrtrans`) | check CFP (roughly 20–25 pp. excl. references in recent years) | appendices may or may not count | several submission deadlines per year; journal-style decisions incl. major revision; artifact evaluation encouraged |
| ACM CCS | ACM `sigconf` two-column | ~12 pp. excl. references and well-marked appendices (check) | appendices limited in some years | anonymous; multiple cycles; rebuttal and/or major revision in recent years |
| IEEE S&P | IEEE two-column | ~13 pp. excl. references and appendices (check) | total-length cap may apply | multiple cycles; major revision outcome common |
| USENIX Security | USENIX two-column | ~13 pp. excl. references and appendices (check) | ethics / open-science sections required in recent years | multiple cycles; major revision; artifact evaluation |
| NDSS | IEEE-like two-column | ~13 pp. excl. references and appendices (check) | | two cycles; rebuttal/revision |
| PoPETs | PETS template | check CFP (roughly 12–15 pp. excl. references/appendices recommended) | | four issues per year; major revision common; artifact badges |
| FC (Financial Cryptography) | check CFP (LNCS in recent years) | check CFP; regular and short papers | check CFP | one deadline per year; blockchain and payments audience; SoK track in some years |
| AFT (Advances in Financial Technologies) | check CFP (LIPIcs in recent years, needs verification) | check CFP | check CFP | one deadline per year; consensus, DeFi, rollups, on-chain verification |

Class files: never modify margins, fonts or spacing. LNCS: `llncs.cls` +
`splncs04.bst`. IACR journals: follow the current class instructions; the submission
option usually anonymises and adds line numbers (`$$...$$` can break line numbering;
use `\[...\]`). Protocol boxes (cryptocode or a hand-rolled `tabular`) must fit the
column width of the target template; a two-column venue needs a narrower box design
than LNCS.

## 2. What reviewers weigh (heuristic weights for mock review)

| venue group | dimension weights (sum 100) |
|---|---|
| CRYPTO / EUROCRYPT / ASIACRYPT | correctness and soundness proofs 30, novelty of technique 25, significance 20, presentation 15, fit 10 |
| TCC | conceptual contribution 35, technical depth 30, novelty of technique 25, presentation 10 |
| PKC | correctness 30, novelty 25, significance 20, presentation 15, fit 10 |
| TCHES | implementation quality 25, correctness and concrete security of the implemented parameters 20, performance data and fair comparison 25, novelty 15, presentation 15 |
| CCS / S&P / USENIX / NDSS | technical soundness 25, practical impact 25, threat model and trust assumptions 20, novelty 15, presentation/evaluation 15 |
| PoPETs | privacy contribution 30, soundness 25, evaluation 20, usability/deployability 15, presentation 10 |
| FC / AFT | relevance to deployed systems 25, soundness 25, evaluation (incl. on-chain cost) 20, novelty 20, presentation 10 |

What ZK reviewers look for, by paper type and venue:

- **Protocol/theory at CRYPTO/EUROCRYPT/ASIACRYPT/TCC:** the exact security notion
  (knowledge soundness, which flavour of ZK, simulation-extractability if claimed),
  the model (ROM, AGM, standard), the setup assumption, and whether every
  conjecture is stated in the theorem. A new PIOP, PCS, folding scheme or compiler is
  judged by its *technique*: an asymptotic improvement or a new paradigm beats a
  constant factor. Proofs are read; an extractor sketched in one sentence is a common
  weak-reject reason. Concrete soundness (bits, provable vs conjectured) is
  increasingly expected even at theory venues when the paper claims practicality.
- **TCC:** new definitions, impossibility results, connections to complexity (e.g.
  PCPs/IOPs, succinct arguments from minimal assumptions). No experiments expected.
- **System/implementation at TCHES:** real hardware numbers (CPU SIMD, GPU, FPGA,
  ASIC), per-phase prover breakdown, fair comparison with the strongest current
  release of the best library at the same security level, open source.
- **System and application papers at CCS/S&P/USENIX/NDSS:** end-to-end evaluation on
  realistic statements, a clear trust model (who runs setup, who holds the witness),
  deployment realism, artifact availability. Circuits must be shown correct
  (under-constraint is the classic objection) and the cost of witness generation
  included.
- **PoPETs:** the privacy goal the ZK proof serves (anonymous credentials, private
  attestations), leakage beyond the proof (metadata, timing), usability.
- **FC/AFT:** on-chain verification cost (gas, calldata), proof aggregation and
  recursion, rollup/bridge design, incentive and trust assumptions; ZK is one
  component of a system argument.

## 3. Typical rejection reasons (and the pre-emptive fix)

| reason | venues where it bites | fix in the paper |
|---|---|---|
| "Only a constant-factor engineering optimisation" | CRYPTO/EC/AC/TCC | name the structural mechanism (the PIOP or algebraic identity that changes); give a parameterised family and a cost theorem; if it is engineering, target TCHES or a systems venue and say so |
| "Soundness relies on an unstated conjecture" | all IACR, TCHES | state the conjecture (e.g. a proximity-gap or list-decoding conjecture) in the theorem; give a soundness table with provable and conjectured columns; report performance at both, or at the provable one |
| "No comparison with the current state of the art" (recent systems such as Plonky3, Binius, HyperPlonk, or the strongest current zkVM) | TCHES, security venues, FC/AFT | run the current release, pinned by commit (`skills/baseline-pin`); if a system cannot run your statement, say why and compare on the closest common statement; cite concurrent work with dates |
| "Inconsistent security levels across compared systems" | all with experiments | re-parameterise every arm to the same bits in the same regime; a soundness column in every comparison table; curve security stated honestly |
| "Inconsistent timing scope" | all with experiments | one timing-scope sentence (witness generation, preprocessing, setup in or out) used for every arm; excluded phases reported in their own table |
| "Only prover time reported" | all with experiments | P, V, proof size, memory together; recursion/wrapping costs separately |
| "Claims stronger than theorems" | CRYPTO/EC/TCC | scope every claim; knowledge soundness vs soundness, HVZK vs ZK stated; weakened CLAIMS wording |
| "Counterexample to a lemma" / "extractor does not work" | all | falsifier exhaustive search on small fields before submission; run the extractor on a toy instance (`skills/sage-check`) |
| "Fiat–Shamir transformation underspecified" | all | transcript contents listed explicitly; multi-round FS loss accounted for; code and paper agree ([fiat-shamir-audit](../fiat-shamir-audit/SKILL.md)) |
| "Circuit may be under-constrained" | security venues, FC/AFT | circuit audit results reported ([circuit-audit](../circuit-audit/SKILL.md)); witness-uniqueness argument for the gadgets that matter |
| "Key content only in the appendix" | EC/CRYPTO/AC | move the new protocol and its core soundness argument into the body, compress background instead |
| "Overlap with prior/concurrent work" | all | explicit delta paragraph covering ePrint and grey literature (project docs, blog posts); "what this paper is not" sentence |
| "Not self-contained / hard to follow" | all | technique overview passes the goal test; notation table; protocol boxes |
| "Missing threat model or ethics" | CCS/S&P/USENIX/NDSS/PoPETs | dedicated sections as the CFP requires (trust in setup, who is the adversary) |
| Format violation | all | camera-ready/submission checklists (`skills/camera-ready`, `templates/handoff/SUBMISSION.md`) |

## 4. Contribution type vs venue (observed heuristics, not rules)

- A new PIOP, PCS, folding scheme or compiler with a clean security proof and a
  new technique → CRYPTO/EUROCRYPT/ASIACRYPT; with an asymptotic separation or a
  new paradigm, also TCC.
- A new argument system with proofs **and** an implementation that wins at equal
  security → CRYPTO/EUROCRYPT or CCS/S&P, depending on whether the technique or the
  system is the headline.
- Prover acceleration (GPU/FPGA/ASIC kernels for MSM, NTT, sum-check, hashing) with
  real hardware numbers → TCHES, or a systems/security venue if the end-to-end
  system is new.
- Circuits or ZK applications (credentials, ML inference, identity, private
  payments) with end-to-end evaluation → CCS/S&P/USENIX/NDSS/PoPETs.
- Rollups, bridges, on-chain verifiers, proof aggregation for blockchains → FC/AFT,
  or CCS/S&P when the security argument is substantial.
- Porting a known PIOP to a neighbouring field or PCS with a small gain → second-tier
  venues unless the port needs a new idea (say which).
- "We organised the field" without a new result → SoK track (FC, S&P, USENIX) with a
  methodology, else workshop.
- Speedup size correlates weakly with venue tier; the structure used to obtain it
  correlates strongly. Roughly ≥1.3× at equal security is a minimum for a performance
  claim to matter, and a gain that disappears at the provable security level is not a
  gain.

## 5. Scoring rubric used by `mock-review`

Normalised six-point scale (map to the venue form when known):
1 strong reject · 2 reject · 3 weak reject · 4 weak accept · 5 accept · 6 strong accept.
Confidence 1–4. A paper that gets one champion (≥5, confidence ≥3) and no strong
detractor usually survives discussion at IACR venues; one well-argued technical
reject (e.g. a counterexample, a broken extractor) usually sinks it.

Calibration anchors:

- 6: new technique that will be reused; clean proofs; convincing evaluation at equal security.
- 5: clear technical contribution, minor presentation issues.
- 4: useful result, some doubts (baseline fairness, timing scope, conjecture use) that a rebuttal can fix.
- 3: interesting but claims exceed evidence, or novelty unclear vs a named prior work.
- 2: a soundness or correctness problem, or contribution judged incremental.
- 1: wrong, out of scope, or format violation.

Never report a probability of acceptance as if it were statistical; if asked, give a
subjective band with the conditions that move it.

## 6. Procedure

1. Fetch and quote the current CFP (WebFetch) into `SUBMISSION.md` §Venue.
2. Fill the table rows for the target venue with the quoted values.
3. Choose the mock-review personas and weights from §2.
4. Adjust the playbook budget (section shares, page limit, two-column vs LNCS).
5. Re-check the CFP one week before the deadline (rules and deadlines do change).
