---
name: fiat-shamir-audit
description: Audit the Fiat–Shamir compilation of OUR OWN protocol, both as written in the paper and as implemented — statement and public inputs in the first hash, every commitment absorbed before its challenge, parameters and domain separation, multi-round loss (state-restoration via RBR or special soundness), hash-chain conditions, salts for ZK, uniform challenge sampling. Each check is tied to a CY24 result. Use for every non-interactive claim at P3 (paper) and P6 (code), and whenever the transcript code changes. Not for auditing other people's systems.
---
# fiat-shamir-audit: is the non-interactive argument the one the theorem is about?

## Scope

Only our own protocols, proofs and implementations. This skill is not for auditing, attacking or disclosing
issues in third-party systems; background papers on known Fiat–Shamir failures (source: other, ePrint 2016/771,
2023/691) are cited for the *kind* of mistake, not as targets.

The builder runs the audit on their own transcript; `falsifier` re-runs it independently (the proposer does not
judge their own claim).

## Why

Fiat–Shamir is where a correct interactive proof most often turns into an incorrect non-interactive one. The
theorems that make it safe have **preconditions on what is hashed and on what the interactive protocol
satisfies**; every check below is one such precondition, with the result it comes from. Background: definitions
in [GLOSSARY](../../references/books/GLOSSARY.md); chapters in the [map of CY24](../../references/books/hash-snargs/MAP.md).

## Checklist

Mark each item PASS / FAIL / N.A. with evidence (paper line, code line, test output).

1. **Statement in the first hash.** The first challenge must depend on the full statement: instance, public
   inputs, the circuit / index (or its commitment), and anything else the adversary could choose. If the
   statement is not hashed, the construction is at best *non-adaptively* sound: a prover can first see the
   challenge and then pick a false statement that passes
   ([CY24 §Lack of adaptive security, section:fs-lack-of-adaptive-soundness]; [Thaler §5.2, The Fiat-Shamir Transformation]
   calls the two variants strong and weak FS). The generic repair "prefix every query with the instance" costs a
   factor t in the error ([CY24 §Non-adaptive vs. adaptive security, lemma:non-adaptive-to-adaptive-soundness]); the
   constructions with direct adaptive proofs hash the instance in the first query
   ([CY24 §The Fiat--Shamir transformation for SPs, construction:fs-for-sp]).
2. **Every prover message before the challenge that depends on it.** Basic multi-round FS hashes the instance and
   all prover messages so far in each round ([CY24 §Construction, construction:basic-fs-for-public-coin-ip]); the
   hash-chain variant hashes the previous challenge, the new message and a salt
   ([CY24 §Construction, construction:hashchain-fs-for-public-coin-ip]). The implementation must match the
   variant whose theorem the paper cites, item by item and **in order**. Commitments (Merkle roots, PCS
   commitments) count as prover messages.
3. **Multi-round loss accounted for.** The FS theorems need **state-restoration** soundness of the interactive
   protocol, and a state-restoration attack on the protocol is an attack on its FS compilation
   ([CY24 §Lower bound on the soundness error, lemma:attack-against-narg-from-ip]; [CY24 §Soundness, theorem:basic-fs-for-public-coin-ip]).
   The paper must prove SR soundness or something that implies it: round-by-round soundness, error
   (t+k)·ε_rbr ([CY24 §RBR soundness implies SR soundness, theorem:rbr-soundness-to-sr-soundness]); special
   soundness, for knowledge ([CY24 §State-restoration knowledge soundness for IPs, theorem:ss-to-sr-knowledge-soundness-for-ip]);
   for Σ-protocols and PCPs a (t+1) factor ([CY24 §Comparison with standard soundness notions, lemma:sp-srs-to-soundness];
   [CY24 §State restoration, theorem:pcp-srs-to-soundness]). Ordinary soundness alone gives only the
   C(t+k, k)·ε bound, which is tight in general ([CY24 §State restoration, lemma:ip-sr-vs-standard]). The term
   enters the budget in `skills/soundness-budget`.
4. **Hash-chain conditions.** If the code chains challenges (each hash input starts from the previous output), the
   cited bound has an extra t²/2^λ and assumes every challenge has at least λ bits
   ([CY24 §Soundness, theorem:hashchain-fs-for-public-coin-ip]). A chain that passes on only a squeezed field
   element smaller than λ bits breaks that assumption: carry the full hash state or digest forward, or use basic FS.
5. **Salts for zero knowledge.** For an adaptive ZK claim, each FS query carries a fresh random salt, so the
   simulator can program positions the adversary cannot have queried; the ZK error gains t/2^{salt}
   ([CY24 §Zero knowledge, theorem:hashchain-fs-zero-knowledge]; without salts: [CY24 §Lack of adaptive security, section:fs-lack-of-adaptive-zk]).
   Merkle leaves that may be opened next to unopened siblings need salts too
   ([CY24 §Hiding, lemma:mt-root-hiding, lemma:mt-privacy]). No salt is needed for a soundness-only claim.
6. **Domain separation between oracles.** Every hash role (Merkle leaf, Merkle inner node, FS challenge of each
   round or sub-protocol, proof-of-work, PCS-internal challenges) is a separate oracle, derived from one hash
   function by a distinct, prefix-free tag ([CY24 §The setting of multiple random oracles, section:rom-derive-multiple-from-single, lemma:multiple-from-single-construction]).
   The bounds are stated for separate oracles; separating the Merkle roles also improves them slightly
   ([CY24 §Soundness, remark:micali-domain-separation]). When the protocol embeds a sub-protocol with its own
   transcript, the sub-transcript is bound to the outer one.
7. **Public coin, uniform challenges.** FS applies to public-coin protocols ([CY24 §Interactive arguments, definition:arg-public-coin]).
   Each challenge must be uniform over the set the soundness analysis uses: no modular bias (sample with
   rejection or with enough extra bits), the right field (extension vs base), the right size (the budget uses
   |C_i|). Record bits per challenge; `skills/soundness-budget` reads them.
8. **Parameters and versions hashed.** Field, extension degree, rate, number of queries, folding factor, PoW
   bits, protocol version / domain tag, and the verifier key or SRS digest when there is one: anything that
   changes the verifier's decision is part of the statement for item 1 (the same point is made for the circuit
   description in [Thaler §5.2, The Fiat-Shamir Transformation]).
9. **The verifier recomputes every challenge.** No challenge, PoW result or query position is read from the
   proof; the verifier derives them from its own transcript.
10. **Grinding nonce placement.** A proof-of-work nonce is absorbed after the messages it protects and before the
    challenge it protects; the PoW check is in the verifier (budget treatment: `skills/soundness-budget`).

## Procedure

1. **Paper.** Write the transcript table for the protocol as stated in the paper:
   `round | prover sends | absorbed (in order) | challenge | sampled from | bits | domain tag | salt`.
   Check items 1–10 against it and against the theorem the paper cites for FS.
2. **Code.** Locate the transcript object and every absorb/squeeze call; produce the same table from the code.
   Diff the two tables. Then test:
   - *sensitivity*: for each public input and parameter, flip it and check that the first challenge changes;
   - *order*: absorb a commitment after its challenge in a test build and check that the verifier rejects old proofs;
   - *recomputation*: the verifier ignores any challenge value in the proof (tamper and check rejection);
   - *domain tags*: list all tags and check they are distinct and prefix-free.
3. **Toy demonstration** (for the report and for reviewers who ask why item 1 matters):
   ```bash
   python3 skills/fiat-shamir-audit/scripts/toy_fs_attack.py            # demo with numbers
   python3 skills/fiat-shamir-audit/scripts/toy_fs_attack.py --selftest
   ```
   On a one-round identity check over F₁₀₁, weak FS lets a one-query prover pass a **false** statement every time;
   strong FS reduces it to grinding, measured between t·ε − C(t,2)·ε² and (t+1)·ε
   ([CY24 §Lower bound on the non-adaptive soundness error, lemma:attack-against-warmup-narg-from-sp];
   [CY24 §Adaptive soundness, theorem:narg-from-sp-adaptive-soundness]). The script also has a transcript lint
   (missing / out-of-order items) and a prefix-free tag check to reuse in tests.
4. **Report** to `falsify/<claim-id>/fs-audit.md` (format below) and link it from the claim's row in CLAIMS.md
   (falsify step 3).

## Report format

```markdown
# FS audit — <protocol>, paper <commit/section>, code <repo@commit>
FS variant cited: basic | hash-chain (theorem cited, with its CY24 label) · interactive input notion: RBR / special / SR proven in <THEORY.md §>

| # | check | paper | code | evidence |
|---|---|---|---|---|
| 1 | statement in first hash | PASS | FAIL | transcript.rs:L42 absorbs commitments but not public_inputs; sensitivity test T3 |
| 2 | messages before challenges, in order | PASS | PASS | table diff empty |
| 3 | SR / RBR / special soundness proven | PASS | n.a. | THEORY.md §4.2 (RBR, eps_rbr = d/|F|) |
| … | … | … | … | … |

Transcript tables: paper (…), code (…), diff (…).
Verdict: PASS / FAIL (items …). Handed to: theorist (paper fixes), prover-engineer (code fixes), soundness-budget (terms).
```

## Pitfalls

- Hashing the commitment to the witness but not the statement it is a witness for.
- Hashing a *pointer*, a length or a hash of only part of the public input.
- A transcript re-initialised for a sub-protocol (e.g. the PCS opening) so its challenges do not depend on the
  outer statement.
- Challenges squeezed as 64-bit integers reduced into a 31-bit field, or into the base field when the budget uses
  the extension.
- Same tag for Merkle leaves and inner nodes.
- A ZK claim with deterministic (unsalted) FS queries or unsalted Merkle leaves.
- A multi-round protocol whose paper proves only ordinary soundness and cites a Fiat–Shamir theorem that needs
  state-restoration or round-by-round soundness.
