---
name: prover-cost-model
description: Predict prover and verifier cost from operation counts before implementing — MSM sizes, NTT/FFT sizes, hashes and Merkle trees, sum-check rounds, memory traffic, proof size (with Merkle path pruning) — then compare the prediction with measurements phase by phase and explain every large gap before publishing. Use at P2 to screen designs (idea-mining step 4), at P5 when the first measurements arrive, and whenever a speed-up looks larger than the operation counts allow (bench-protocol rule 10).
---
# prover-cost-model: predict, measure, explain the gap

## Why

A ZK system paper's headline is a prover time. Without a prior operation count, nobody can tell whether a 3×
speed-up comes from the idea, from a smaller field, from fewer queries (a lower security level), or from work
moved out of the timed region. This skill makes the prediction first, phase by phase, in the cost primitives
that dominate ZK provers, and turns every large measured/predicted gap into a finding that must be explained
(`skills/bench-protocol` rule 10). Circuit sizes, the input of the model, come from `skills/constraint-cost`;
the PIOP and PCS come from `skills/piop-pcs-compile`; query counts and field sizes from `skills/soundness-budget`.

## Cost primitives

| primitive | count | rule of thumb | source |
|---|---|---|---|
| MSM (multi-scalar multiplication) | number of MSMs and their sizes N, scalar bits b | Pippenger: about N·b / log N group additions; each group operation costs roughly an order of magnitude more than a field multiplication | [Thaler §19.3.2, Relative Efficiency of Different Operations] |
| NTT / FFT | number of transforms and sizes (including the blow-up / coset domains) | (N/2)·log₂N butterflies; needs 2-adicity ≥ log₂N in the field | [Thaler §19.3.2, Relative Efficiency of Different Operations]; [Thaler §19.3.1, Field choice] |
| FRI / RS-code PCS | LDE size N/ρ, number of committed columns, folding rounds, queries q | the LDE (an FFT of size N/ρ) dominates the prover; the query phase dominates proof size | [Thaler §10.4.3, Costs of FRI] |
| Merkle trees | leaves, hashes (≈ 2·leaves per tree), number of trees; opening paths q·depth hash values per tree, or fewer with path pruning | pruned multi-opening = |copath(I) \ path(I)| hashes, between depth − log|I| and |I|·(depth − log|I|) | [CY24 §Definition, section:merkle-commitment-definition]; [CY24 §Path pruning, lemma:path-pruning-is-copaths-minus-paths, lemma:path-pruning-lower-and-upper] |
| hash-based argument size | Merkle roots, query answers, authentication paths, salts per round | the BCS argument-size expression sums these per round | [CY24 §Construction, construction:bcs-transformation, equation:bcs-prover-to-verifier] |
| sum-check | rounds v = log₂N, degree d per round, term evaluations Σ_j (d+1)·2^{v−j} = O(2^v) | prover linear in the table size if g's factors are multilinear tables; verifier O(v·d) | [Thaler §4.1, The Sum-Check Protocol] |
| PCS openings | KZG: one MSM per opening quotient; multilinear KZG: v MSMs of halving size; IPA: log N rounds of linear work | | [Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup]; [Thaler §15.3, Extension of KZG to Multilinear Polynomials]; [Thaler §14.4, Bulletproofs]; trade-off table [Thaler §16.3, Polynomial Commitment Schemes: Pros and Cons] |
| verifier | pairings, scalar multiplications, hashes (q·depth per tree), field operations | | as above |
| memory traffic | bytes read and written per phase (NTT passes, MSM bases and scalars, Merkle leaves) | at large N many kernels are memory-bound: a model in operations alone underestimates them | (our accounting) |

Which primitive dominates depends on size and field: for small instances FFTs can beat an MSM of the same
length, for large ones the comparison flips; in IOP-based provers FFT vs Merkle hashing likewise depends on N
([Thaler §19.3.2, Relative Efficiency of Different Operations]). Hence a model, not a slogan.

## Procedure

1. **Write the protocol as phases** (witness generation, commitments, permutation / lookup arguments,
   quotient or sum-check, openings, recursion or wrapping) with, per phase, the primitives above and their sizes
   as functions of N and the parameters (ρ, q, number of columns, degree). Reuse `lib/cryptomath/cryptomath/costmodel`
   (`Counter`, `count`, nested counters per phase; `CostFormula` for symbolic crossovers) rather than a
   spreadsheet.
2. **Calibrate unit costs** on the target machine: microbenchmark one field multiplication, one butterfly, one
   group addition, one hash of the leaf size, one pairing, and memory bandwidth (`skills/bench-protocol`;
   each unit cost is an EVIDENCE row). The toy script's unit costs are placeholders.
3. **Predict** per phase: operation counts, predicted time, memory traffic, proof size. For screening (P2),
   compare designs on the counts and on the predicted totals at several N (log-log), not at one size.
4. **Measure** the implementation with per-phase timers printing one `phase: value ms` line each (the
   bench-protocol convention) and the same phase names as the model.
5. **Compare** phase by phase. A phase outside [1/t, t] of its prediction (default t = 1.5), a measured phase
   the model does not have, and a modelled phase that was not measured are all flagged.
6. **Explain each flag before publishing** (bench-protocol rule 10). Typical mechanisms: unit costs not
   calibrated; a phase that includes extra work (witness generation, serialization, a transpose); memory-bound
   kernels; GPU transfers; a different field, extension, rate or query count from the modelled one (often a lower
   security level, check against `skills/soundness-budget`); a commitment round the model missed or the
   implementation skipped. Fix the model or the implementation; write down which, and why.
7. **Record**: the prediction table and the comparison go to `results/<exp>/cost-model.md`; numbers that reach the
   paper (e.g. "MSM is 71% of prover time") get EVIDENCE rows (`skills/log-to-evidence`).

## Toy model

```bash
python3 skills/prover-cost-model/scripts/prover_cost_model.py --n 1048576 --field bn254 --piop plonk --pcs kzg
python3 skills/prover-cost-model/scripts/prover_cost_model.py --n 1048576 --field goldilocks --piop plonk --pcs fri --queries 80
python3 skills/prover-cost-model/scripts/prover_cost_model.py --n 1048576 --piop plonk --pcs kzg --demo-log > m.log
python3 skills/prover-cost-model/scripts/prover_cost_model.py --n 1048576 --piop plonk --pcs kzg --compare m.log
python3 skills/prover-cost-model/scripts/prover_cost_model.py --selftest
```

Inputs: constraints n, field (bn254, bls12-381, goldilocks, babybear), PIOP (`plonk`: univariate quotient over a
4N coset; `sumcheck`: Spartan-style multilinear), PCS (`kzg`, `fri`). It refuses KZG over a field that is not a
pairing group's scalar field and NTTs beyond the field's 2-adicity. The self-test checks the formulas against
real computations: a radix-2 NTT over F_97 (butterfly count and output), an honest sum-check prover over F_97
(term count), and the path-pruning count against the CY24 bounds.

Comparison against the synthetic log (bn254, plonk + kzg, n = 2^20; toy unit costs, made-up "measurement"):

| phase | predicted ms | measured ms | measured/predicted | flag |
|---|---|---|---|---|
| commit | 25495.50 | 28045.05 | 1.10 | ok |
| permutation | 8750.16 | 8312.65 | 0.95 | ok |
| quotient | 48768.01 | 156057.64 | 3.20 | EXPLAIN |
| open | 17311.57 | 15580.41 | 0.90 | ok |

The model's own table for that run shows why "quotient" is the phase to look at first: it is the only one with
13 NTTs (≈4.6·10^8 butterflies) and by far the largest memory traffic, so a memory-bound NTT is the first
hypothesis to test, before suspecting the measurement.

## Output format (`results/<exp>/cost-model.md`)

```markdown
# Cost model — <design>, N = 2^20, <field>, <PIOP> + <PCS>, rho = 4, q = 80 (from soundness budget E12)
Unit costs: E30–E35 (microbenchmarks, host:3f9a, 2026-01-01).
| phase | MSM (count × size) | NTT (count × size) | hashes | sum-check rounds | field mults | traffic | predicted | measured | ratio | flag / explanation |
|---|---|---|---|---|---|---|---|---|---|---|
| quotient | 3 × 2^20 | 13 (4 × 2^20, 9 × 2^22) | 0 | 0 | 8.4e7 | 55 GB | 48.8 s | 156 s | 3.2 | memory-bound coset NTT; confirmed by bandwidth counter (E37); model updated |
Proof size: predicted 359 kB (pruned), measured 362 kB (E38).
```

## Pitfalls

- Predicting with one set of parameters (rate, queries, field) and measuring another.
- Counting MSM points but not the scalar size; counting NTT size N when the code transforms the 4N coset.
- Comparing totals only: compensating errors hide in phases.
- Treating a flagged phase as noise and publishing the measured number unexplained.
- Proof sizes from a formula instead of the serialized proof (bench-protocol "proof size" row); unpruned Merkle
  paths in the model when the code prunes them, or the reverse.
- Unit costs taken from another machine or another library version.
