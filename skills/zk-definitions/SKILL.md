---
name: zk-definitions
description: Pick and state the security notions and model of a ZK result before proving it — soundness vs knowledge soundness (straightline / rewinding / witness-extended emulation / special soundness), honest-verifier vs full ZK (perfect / statistical / computational), simulation-extractability, adaptive vs non-adaptive, ROM / AGM / GGM / standard model, trusted setup — and produce the assumption ledger and proof skeletons (reduction, extractor, oracle-programming simulator) for THEORY.md. Use at P3 before writing a theorem, at falsify step 1, and whenever a draft says "secure" without saying in which sense.
---
# zk-definitions: prove the statement you mean

## Why

With the wrong definition every later proof establishes some other proposition. The usual slips: soundness
proven, "argument of knowledge" claimed; HVZK of the interactive protocol claimed as ZK of the compiled
argument; non-adaptive security of a protocol whose statement the adversary chooses; an AGM proof presented
as a standard-model one; a trusted setup that appears in the construction but not in the theorem. This skill
fixes the notion, the model and the assumptions **before** the proof, and gives proof skeletons that make the
error terms explicit.

The canonical meanings are in [GLOSSARY](../../references/books/GLOSSARY.md) (it records where CY24 and
Thaler differ and which one we use). CY24 is the source for the definitions and for hash-based proofs (pure
ROM); Thaler for algebraic constructions; AGM, GGM, pairing and knowledge assumptions are **outside CY24** and
are cited from Thaler or the original papers.

## 1. The definition ladder

| family | from weaker to stronger | what the step up buys | read |
|---|---|---|---|
| soundness | non-adaptive soundness → adaptive soundness | the adversary may choose the statement after seeing the oracle (the default for any deployed or posted proof) | [CY24 §Non-interactive arguments, definition:narg-nonadaptive-soundness, definition:narg-adaptive-soundness] · [CY24 §Non-adaptive vs. adaptive security, remark:separate-adaptive-vs-nonadaptive-soundness] |
| knowledge | soundness → rewinding knowledge soundness → straightline knowledge soundness | a witness is extracted; straightline extraction needs no rewinding, composes (recursion, many proofs) and needs no programming | [CY24 §Knowledge soundness, definition:adaptive-rewinding-knowledge-soundness, definition:adaptive-straightline-knowledge-soundness] |
| knowledge (alt.) | witness-extended emulation | the extractor also reproduces the prover's view; implied by rewinding knowledge soundness in CY24's setting | [CY24 §Knowledge soundness, definition:narg-witness-extended-emulation] |
| interactive input notions | soundness → state-restoration soundness; special soundness and round-by-round soundness imply the SR notions | what Fiat–Shamir needs from a multi-round protocol | [CY24 §State restoration, definition:ip-state-restoration-soundness] · [CY24 §Extraction from forks and trees, definition:ip-special-soundness] · [CY24 §Definition, def:iop-round-by-round-soundness] |
| zero knowledge | HVZK (interactive) → non-adaptive ZK → once-adaptive ZK → multi-proof ZK | simulation for adversarially chosen statements and, at the top, for many proofs | [CY24 §Definition, definition:ip-hvzk] · [CY24 §Zero knowledge, definition:once-nonadaptive-zk-narg, definition:once-adaptive-zk-narg]; multi-proof: source: other, `needs verification` |
| ZK distance | computational → statistical → perfect | strength of the indistinguishability | [Thaler §11.1, What is Zero-Knowledge?] |
| malleability | knowledge soundness → simulation-extractability | extraction still works after the adversary sees simulated proofs (signatures of knowledge, posted proofs) | source: other, ePrint 2017/540, 2021/511 (not in CY24 or Thaler) |
| models | standard model ← ROM, AGM, GGM (idealised) | idealised models give simpler or tighter proofs; they are assumptions and must be named in the theorem | ROM: [CY24 §Definition, definition:the-rom]; AGM/GGM: [Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup], ePrint 2017/620 |
| setup | transparent ← universal/updatable SRS ← circuit-specific trusted setup | who must be trusted to destroy randomness | [CY24 §Preface, section:preface] (transparent) · [Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup] · Marlin ePrint 2019/1047 |

Two facts to keep in view:
- ZK in the ROM needs the simulator to **program** the oracle; without programming, ZK is impossible for
  hard languages ([CY24 §Limitation on zero knowledge, lemma:npro-limitation]).
- A ZK simulator in the ROM also produces accepting proofs of **false** statements
  ([CY24 §Simulation on instances not in the language, lemma:simulators-not-in-language]). This is why
  "ZK + knowledge soundness" does not give simulation-extractability for free.

## 2. Choose the target notion

Answer each question in THEORY.md; each answer is a line of the assumption ledger.

1. Who chooses the statement, and when? If the prover can pick it after seeing hash outputs (almost always),
   claim **adaptive** soundness / knowledge soundness / ZK.
2. Is a witness needed downstream (recursion, folding, proofs of possession, identification)? Then
   **knowledge soundness**; prefer **straightline** when the proof will be composed or run many times.
3. Will proofs be published and could an adversary maul one into another? Then argue
   **simulation-extractability** or state that it is not claimed.
4. Privacy: HVZK of the interactive protocol is an *input*; the claim about the compiled argument is
   (once-adaptive) ZK in the programmable ROM, plus hiding of every commitment that is opened
   ([CY24 §Hiding, lemma:mt-privacy]) or masking of every revealed evaluation
   ([Thaler §13.3, Zero-Knowledge via Masking Polynomials]).
5. Model and assumptions: ROM only? Which hash plays which oracle? AGM/GGM? Which group assumption (DL, SDH,
   knowledge-of-exponent)? Which setup?
6. Concrete or asymptotic? Concrete (explicit ε in t, λ, n) is the default here; the level definition comes from
   `skills/soundness-budget`.

## 3. Assumption ledger (THEORY.md)

```markdown
## Assumption ledger — Theorem <id>

| # | item | our choice | alternatives rejected (why) | source |
|---|---|---|---|---|
| A1 | relation R | R = {(x; w) : …}; public: x = (…); index i = circuit (preprocessing) | — | [CY24 §The preprocessing setting, definition:indexed-relation-and-language] |
| A2 | soundness notion | adaptive knowledge soundness, straightline | rewinding (would not compose with recursion) | [CY24 §Knowledge soundness, definition:adaptive-straightline-knowledge-soundness] |
| A3 | ZK notion | once-adaptive statistical ZK, programmable ROM | HVZK only (insufficient after FS) | [CY24 §Zero knowledge, definition:once-adaptive-zk-narg] |
| A4 | model | ROM; oracles derived by domain separation from one hash | — | [CY24 §The setting of multiple random oracles, section:rom-derive-multiple-from-single] |
| A5 | computational assumptions | none (hash-based) / DL in G / SDH / AGM | … | Thaler § / ePrint … |
| A6 | setup | transparent / universal SRS (updatable) / circuit-specific | … | … |
| A7 | conjectures | none / proximity conjecture X in regime Y (budget marked conjectured) | … | ePrint … |
| A8 | input property of the interactive protocol | RBR knowledge soundness with ε_rbr = … | ordinary soundness (FS loss exponential in k) | [CY24 §Definition, def:iop-round-by-round-knowledge] |
| A9 | security-level definition | worst-case / average-case | … | [CY24 §Security levels, section:security-levels] |
```

`writer` copies A2–A7 into the theorem statement verbatim; `falsifier` checks that the proof uses nothing
outside the ledger.

## 4. Proof skeletons

Write the probability experiments in the form "Pr[ event | experiment ]" with every sampled object listed
([CY24 §Probabilistic experiments, section:probabilistic-experiments]). Each skeleton names the error terms it
produces; those terms go into the soundness budget.

**(a) Soundness by reduction to state restoration (FS, BCS, Micali).** Given a t-query adversary P̃ against the
non-interactive argument, build a state-restoration prover for the underlying protocol that uses P̃ as a black
box: each oracle query of P̃ that would derive a challenge becomes a move in the state-restoration game; a
query that P̃ makes "on the side" is answered by lazy sampling. Bound the bad events separately (a collision
or inversion of the oracle, a Merkle opening inconsistent with the extracted tree, a hash chain that cannot
be traced back). The result has the shape ε_arg(t) ≤ ε_sr(t) + (commitment / chain terms).
Models: [CY24 §Soundness, theorem:basic-fs-for-public-coin-ip, theorem:bcs-soundness, lemma:ibcs-sr-soundness-reduction].

**(b) Straightline knowledge extraction.** The extractor receives only the proof and the prover's oracle
trace. Step 1: from the trace, rebuild every Merkle tree the prover committed to and read off the leaves
(fill missing leaves arbitrarily); every opening the verifier accepts agrees with these leaves except with
the multi-extraction error ([CY24 §Extractability, lemma:mt-multi-extractability, construction:mt-extractor]).
Step 2: run the IOP's straightline (state-restoration) extractor on the recovered oracle messages; with RBR
knowledge soundness that extractor works round by round
([CY24 §Round-by-round soundness, construction:straightline-extractor-from-rbr-extractor, theorem:rbr-knowledge-soundness-to-sr-knowledge-soundness]).
Model: [CY24 §Knowledge soundness, construction:bcs-extractor-direct, theorem:bcs-knowledge-soundness].
Algebraic PCS: extraction comes from the PCS's own extractability, usually in the AGM or from a knowledge
assumption ([Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup]) — not
from CY24.

**(c) Rewinding extraction from special soundness.** Run the prover once; if it convinces, rewind it to the
last commitment and re-run with fresh distinct challenges until a fork (Σ-protocol) or tree (multi-round) of
accepting transcripts with the required arity is collected, then apply the special-soundness extractor. The
expected number of re-runs, and the error (a_i − 1)/|C_i| per round, come out of the analysis
([CY24 §Knowledge soundness for SPs, construction:ss-fork-finder, theorem:ss-to-knowledge-soundness-for-sp] ·
[CY24 §Knowledge soundness for IPs, construction:ss-tree-finder, theorem:ss-to-knowledge-soundness-for-ip]).
After Fiat–Shamir, use the state-restoration version, which costs a (t+1) factor
([CY24 §State-restoration knowledge soundness for IPs, theorem:ss-to-sr-knowledge-soundness-for-ip]).
State the extractor's **expected** running time; a rewinding extractor is not straightline and does not
compose freely. Algebraic examples (Schnorr, Bulletproofs): [Thaler §12.2.2, Schnorr’s Σ-Protocol for the Discrete Logarithm Relation],
[Thaler §14.4, Bulletproofs].

**(d) Zero-knowledge simulator that programs the oracle.** Sample a simulated view of the honest verifier
with the HVZK simulator; for each round sample a fresh salt and **program** the oracle at the query the honest
verifier would make (instance, prover message, salt; or the chained previous challenge) to return the
simulated challenge; simulate Merkle commitments and authentication paths for the opened positions with the
Merkle simulator. Bad event: the adversary queried a programmed position before seeing the proof, which the
salt makes unlikely (t/2^{salt} per oracle). Error = HVZK error + salt terms + Merkle hiding terms
([CY24 §Zero knowledge, construction:fs-simulator, theorem:hashchain-fs-zero-knowledge] ·
[CY24 §Zero knowledge, construction:bcs-simulator, theorem:bcs-zero-knowledge] · [CY24 §Hiding, lemma:mt-privacy]).
Without salts the simulator cannot be adaptive ([CY24 §Lack of adaptive security, section:fs-lack-of-adaptive-zk]).
Algebraic route: masking polynomials or commit-and-prove make the revealed values simulatable
([Thaler §13.3, Zero-Knowledge via Masking Polynomials], [Thaler §13.1, Proof Length of Witness Size Plus Multiplicative Complexity]);
hiding PCS openings are then part of the simulator.

**(e) Algebraic-model proofs (out of CY24's scope).** KZG binding reduces to SDH; KZG extractability needs a
knowledge assumption or the GGM/AGM ([Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup]);
Groth16-style SNARKs are analysed in the GGM/AGM ([Thaler §17.5, Non-Interactivity and Public Verifiability];
source: other, ePrint 2016/260, 2017/620). When an AGM proof is combined with a ROM Fiat–Shamir step, say so in
the model line (ROM + AGM), and do not reuse CY24's error terms for the AGM part.

## 5. Checks before a theorem is accepted (also falsify step 1)

- The theorem names: relation (with public inputs), notion (A2/A3), model, assumptions, setup, conjectures,
  error terms. Nothing used in the proof is missing from the statement.
- The notion proven is the notion claimed in the abstract and in the comparison table.
- Knowledge claims come with an extractor and its running time; straightline vs rewinding is stated.
- ZK claims say HVZK-of-the-IOP vs ZK-of-the-argument, statistical vs computational, and how openings are
  hidden.
- Adaptive claims: the statement is bound into the first challenge ([CY24 §Lack of adaptive security, section:fs-lack-of-adaptive-soundness]);
  hand the transcript to `skills/fiat-shamir-audit`.
- A symbol keeps one meaning across abstract, theorem and experiments.
- Run `sage-check` on the extractor or simulator on a toy instance (`skills/sage-check`, "knowledge soundness"
  and "zero knowledge" rows).

## Pitfalls

- "Proof of knowledge" with only a soundness proof.
- A rewinding extractor used inside a recursive composition without accounting for its running time.
- HVZK claimed as ZK after Fiat–Shamir with unsalted commitments.
- CY24's ROM bound quoted for a KZG-based construction.
- Simulation-extractability assumed because the argument is ZK and knowledge sound.
- Trusted setup present in the construction section, absent from the theorem and the abstract.
