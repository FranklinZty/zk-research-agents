---
name: soundness-budget
description: Itemised concrete-soundness budget for a ZK argument — Schwartz–Zippel and sum-check terms, challenge field size, PCS proximity terms (proven vs conjectured regime), grinding, hash output length, Merkle and Fiat–Shamir losses, curve assumptions — combined by a union bound into one security level under a stated definition (worst-case or average-case). Use whenever a paper states "λ bits", picks parameters, or compares against a baseline that might not be at the same level; the falsifier recomputes it independently at P6.
---
# soundness-budget: where the "128 bits" comes from

## Why

The security level is the one number in a ZK paper that every other number depends on: fewer queries, a
smaller field or a cheaper hash all buy speed by spending soundness. Typical failures: a proven bound in one
table and a conjectured one in another; an interactive soundness error used for a Fiat–Shamir-compiled
argument; challenges sampled from the base field while the bound uses the extension; a level that silently
uses a different definition from the baseline's. This skill makes every term explicit, sourced and
recomputable. It takes over, for ZK, the role `skills/param-estimation` played for lattice and symmetric
parameters (that skill is still in the repository and is removed in a later batch).

Sources: hash-based terms and the definition of a security level from CY24 (pure ROM); algebraic terms from
Thaler; Reed–Solomon proximity and anything newer from the original papers ("source: other"). Never move a
CY24 bound into a KZG/IPA/AGM setting. Navigation: [map of CY24](../../references/books/hash-snargs/MAP.md),
[map of Thaler](../../references/books/thaler/MAP.md), terms: [GLOSSARY](../../references/books/GLOSSARY.md).

## Inputs

- The protocol as a list of rounds: what the prover sends, what the verifier samples and **from which set**,
  the number of rounds k, the PCS and its parameters (rate, queries, folding, proximity parameter).
- The security notion being budgeted (soundness or knowledge soundness; see `skills/zk-definitions`).
- Oracle output size λ (hash output bits), salt sizes, field and extension sizes, curve.
- The level definition required by the venue or the baseline you compare against.

## Procedure

1. **Fix the level definition first** and write it in the budget header
   ([CY24 §Security levels, section:security-levels]):
   - *worst-case* s bits: ε(t) ≤ 2^−s for every query bound t ≤ 2^s;
   - *average-case* s bits: t/ε(t) ≥ 2^s for every t ≤ 2^s (expected attack cost).
   Worst-case implies average-case and costs a larger λ (≈ 1.5× for t² terms, 2× for t terms, and a field of
   about 2^{2s} instead of 2^s for terms linear in t). Compare against a baseline only under the **same**
   definition. Also note the statistical bits of the interactive protocol, which is how most system papers
   report "λ" ([Thaler §5.3.1, “Bits of Security”: Statistical vs. Computational]).
2. **Lift interactive errors to the non-interactive setting.** A Fiat–Shamir prover attacks the protocol many
   times "in its head": the input to every FS theorem is **state-restoration** soundness, not ordinary
   soundness ([CY24 §Strong soundness properties, section:strong-soundness-properties]). Choose the tightest
   available route and name it:
   | protocol property | non-interactive term | source |
   |---|---|---|
   | Σ-protocol, soundness ε | (t+1)·ε | [CY24 §Adaptive soundness, theorem:narg-from-sp-adaptive-soundness] |
   | PCP, soundness ε | (t+1)·ε | [CY24 §State restoration, theorem:pcp-srs-to-soundness] |
   | IP/IOP with round-by-round error ε_rbr over k rounds | (t+k)·ε_rbr | [CY24 §RBR soundness implies SR soundness, theorem:rbr-soundness-to-sr-soundness] |
   | IP with special soundness (arities a_i, challenge sets C_i), knowledge | (t+1)·(1 − ∏(1 − (a_i−1)/\|C_i\|)) | [CY24 §State-restoration knowledge soundness for IPs, theorem:ss-to-sr-knowledge-soundness-for-ip] |
   | k-round IP, only ordinary soundness ε known | C(t+k, k)·ε — exponential in k, and tight in general | [CY24 §State restoration, lemma:ip-sr-vs-standard] |
   The last row is a warning, not a recipe: if it is the only route, the protocol needs an RBR or special
   soundness proof before it gets a budget.
3. **List every term.** Walk this checklist and write one row per item that applies; "not applicable" is a row
   too, with the reason.
   - *Algebraic identity checks* (each verifier check of a polynomial identity at a random point):
     degree/|S| per check, |S| = the set the challenge is **sampled** from
     ([Thaler §3.4, Schwartz-Zippel Lemma]); sum-check d/|F| per round, v·d/|F| interactively
     ([Thaler §4.1, The Sum-Check Protocol]); random linear combinations with powers of one challenge
     (m−1)/|F| ([Thaler §3.4, Schwartz-Zippel Lemma]).
   - *Extension field*: if challenges live in F_{p^e}, use p^e in the terms above; if any challenge is drawn
     from the base field (a common implementation shortcut), that round uses p.
   - *PCS / proximity* (source: other): FRI, STIR, WHIR, Ligero, Brakedown. State the regime of every term:
     **proven** (unique decoding, or up to the Johnson bound δ < 1 − √ρ − η, e.g. the bound quoted in
     [Thaler §10.4.4, Details of FRI: Better Reed-Solomon Proximity Proofs via Interaction] from ePrint
     2020/654; Fiat–Shamir/RBR treatment ePrint 2023/1071) or **conjectured** (beyond Johnson, up to capacity).
     Conjectured terms are listed separately and never compared with a baseline's proven terms. Before using
     the conjectured regime at all, read ePrint 2025/2046 and 2025/2197 (`needs verification`: both question
     such conjectures in some parameter ranges; check what they cover for your parameters).
   - *Grinding / proof of work* (source: other, ePrint 2021/582): b bits of PoW checked by the verifier, with
     the nonce absorbed before the challenge, divide the per-attempt success of grinding that round by 2^b.
     Mark it `heuristic` unless the protocol's FS proof covers it.
   - *Hash output length λ*: Merkle binding t²/2^{λ+1} ([CY24 §Binding, lemma:mt-binding]); Merkle
     multi-extraction for the BCS/Micali compilers ([CY24 §Extractability, lemma:mt-multi-configuration-multi-extractability]);
     hash-chain FS t²/2^λ, which also requires every challenge to carry at least λ bits
     ([CY24 §Soundness, theorem:hashchain-fs-for-public-coin-ip]). With the simplified forms, BCS adds
     3.5·t²/2^λ ([CY24 §Soundness, theorem:bcs-soundness]) and Micali 2.5·t²/2^λ
     ([CY24 §Soundness, theorem:micali-soundness]).
   - *Curve / group assumptions* (discrete log, SDH, pairing groups): not functions of t. Enter them as a
     **cap** in bits with a cited estimate (source: other; e.g. ePrint 2017/334 for pairing curves); for
     BLS12-381 Thaler mentions a target of roughly 120 bits ([Thaler §15.1, Cryptographic Background]).
     Never cite a curve's nominal 128 bits without a current estimate.
   - *Zero-knowledge terms* (if the claim includes ZK): HVZK error + salt terms t/2^salt
     ([CY24 §Zero knowledge, theorem:hashchain-fs-zero-knowledge]) + Merkle hiding
     ([CY24 §Hiding, lemma:mt-privacy]). Budget them in a separate table: they are a different property.
4. **Union bound.** The total is the sum of the rows as functions of t. Do not take the minimum of per-term bits;
   a sum of terms of 2^−128 each is not 2^−128.
5. **Compute the level** with the script (exact rational arithmetic), not by hand:
   ```bash
   python3 skills/soundness-budget/scripts/soundness_calc.py --config soundness/budget.json --evidence
   python3 skills/soundness-budget/scripts/soundness_calc.py --example toy-bcs --level average-case
   python3 skills/soundness-budget/scripts/soundness_calc.py --selftest
   ```
   The config lists terms by kind (`const`, `rbr`, `sr_standard`, `fs_sigma`, `merkle_multi`, `hash_chain`,
   `micali`, `bcs`, `special_soundness`) with their regime and source; caps carry assumption bits. Each
   function's docstring names the label it implements.
6. **Write the table into THEORY.md** (format below) and add the EVIDENCE row the script prints
   (`skills/log-to-evidence`). The paper prints the level with its definition and regime, e.g. "128 bits
   (average-case, proven)".
7. **Independent recomputation.** The falsifier rebuilds the budget from the protocol description, not from
   this table (`skills/falsify`, step 6), and the two must agree term by term.

## Output format (THEORY.md, "Parameters and security")

```markdown
### Soundness budget: <protocol>, parameter set <name>
Definition: worst-case | average-case [CY24 §Security levels, section:security-levels]. Notion: knowledge soundness.
λ = 256, field F_p (p ≈ 2^64), challenges in F_{p^2}, k = 32 rounds, 13 Merkle trees of 2^24 leaves.

| term | bound ε_i(t) | bits at t = 2^s | proven / conjectured / heuristic | source | EVIDENCE |
|---|---|---|---|---|---|
| IOP SR error via RBR | (t+k)·max(d/|F|, ε_fri) | … | proven | CY24 RBR theorem + PCS RBR theorem (ePrint …) | E12 |
| Merkle multi-extraction | 1.5(t−1)t/2^λ + 2(d+1)Σℓ/2^λ + t²/2^λ | … | proven | CY24 lemma:mt-multi-configuration-multi-extractability | E12 |
| hash-chain FS | t²/2^λ | … | proven | CY24 theorem:hashchain-fs-for-public-coin-ip | E12 |
| **total (union bound)** | Σ | **s** | proven | | E12 |
| conjectured variant (separate row set) | … | … | conjectured | … | E13 |
```

(Toy layout; the bits column is filled from the script output, never by hand.)

## Worked re-derivations (the script's self-test)

The unit tests use values we derived ourselves from the error bounds, not numbers copied from the book. They
double as a check that the security-level definitions are applied correctly.

| case | our derivation | result (s = 128) |
|---|---|---|
| hash commitment binding t²/2^{λ+1} ([CY24 §Binding, lemma:cm-binding]) | worst-case at t = 2^s: 2^{2s−1−λ} ≤ 2^{−s}; average-case: 2^{λ+1}/t ≥ 2^s at t = 2^s | λ = 3s−1 = 383 / 2s−1 = 255 |
| hash commitment hiding t/2^{salt} ([CY24 §Hiding, lemma:cm-hiding]) | worst-case 2^{s−salt} ≤ 2^{−s}; average-case ratio = 2^{salt} | salt = 2s / s |
| Micali, (t+1)ε_pcp + 2.5t²/2^λ, ε_pcp = 2^{−2s−2}, worst-case | 2.5·2^{2s−λ} ≤ 0.75·2^{−s} − 2^{−2s−2} ⇒ λ ≥ 3s + log₂(10/3) + o(1) | minimal λ = 3s+2; 3s+3 also works |
| Micali, average-case, ε_pcp = 2^{−s−1} | at t = 1 the ratio is 1/(2^{−s} + 2.5·2^{−λ}) < 2^s for every λ | s bits not reached (the miss is ≈2^{−125} bits, a boundary technicality); with ε_pcp = 2^{−s−2}: λ = 2s+2 |
| BCS, ε_sr + 3.5t²/2^λ, ε_sr ≤ 2^{−s−1} for all t | worst-case: 3.5·2^{2s−λ} ≤ 2^{−s−1} ⇒ λ ≥ 3s+2.81; average-case: endpoints t = 1 (λ ≥ s+3) and t = 2^s (λ ≥ 2s+1.81) | λ = 3s+3 / 2s+2 |
| FRI, proven Johnson regime, ρ = 1/16, \|F\| = 2^256, η = 2^−14, δ = 3/4 − 2η, d₀ = 2^16, 65 queries | ε₁ = (d₀+1)²/((2η)^7\|F\|) ≈ 2^{−133.0}, ε₂ = (1−δ)^65 ≈ 2^{−129.95} | ≈ 129.8 bits (interactive IOPP error) |

The Micali row shows why we re-derive: [CY24 §Concrete security for argument systems, section:concrete-security-for-micali]
works through the same example, and the exact check at the smallest query bound t = 1 is where an
inequality written for large t can slip. When a re-derivation disagrees with a source by more than such a
boundary effect, stop and report it to `theorist` and `falsifier`; do not pick the more convenient number.

## Rules

- Every row names its regime. A budget that contains one conjectured row is a conjectured budget; publish the
  proven budget next to it.
- The challenge-set size in a term is the size of the set the **code** samples from; check it against the
  implementation (`skills/fiat-shamir-audit`).
- One parameter set per table. Mixing the rate of one configuration with the query count of another is the
  budget version of a mixed-configuration benchmark row.
- Bits are computed, not rounded by eye: report the integer level the script prints and the definition.
- Thaler's bounds are asymptotic-style statements of interactive soundness; turning them into a
  non-interactive budget always goes through step 2.

## Pitfalls

- Interactive soundness v·d/|F| reported as the argument's soundness after Fiat–Shamir (ignores the t factor).
- Worst-case and average-case levels compared across papers.
- A 64-bit base field with challenges "in the extension", while one batching challenge is drawn from the base field.
- Grinding bits added to the total instead of to the one round they protect.
- The conjectured proximity regime used for "our" protocol and the proven one for the baseline (or the reverse).
- A hash-chain transcript whose challenges are shorter than λ bits, while the budget uses the hash-chain theorem.
- A curve whose current estimate is well below the nominal level, cited at the nominal level.
