---
name: constraint-cost
description: Choose an arithmetization (R1CS, Plonkish, AIR, CCS) and count what it costs — constraints, rows, columns, degree, nonzeros, lookups and table sizes — for our circuits; compare lookups with native constraints, estimate non-native field arithmetic, pick an in-circuit hash (Poseidon2/Rescue-type AO primitives vs Keccak/SHA via lookups), and account for recursion and curve cycles. Planning numbers come from a toy counter; paper numbers come only from the real compiler's output, recorded in EVIDENCE. Use at P2 (screening a design) and P5 (reporting circuit sizes).
---
# constraint-cost: the second currency of a ZK paper

## Why

"Our circuit has N constraints" is, after prover time, the most quoted number in application and system
papers, and the easiest to make incomparable: R1CS constraints vs Plonkish rows vs AIR trace cells, linear
constraints counted or not, padding to a power of two included or not, lookup tables amortised or not, a
custom gate of degree 5 counted as "one constraint". This skill fixes what is counted, for which
arithmetization, and where the number comes from. Costs of the *prover* on those circuits are predicted in
`skills/prover-cost-model`; correctness of the circuit is `skills/circuit-audit`.

Background: front ends (programs to circuits, memory checking, non-arithmetic operations) are in
[Thaler §6.5, Turning Computer Programs Into Circuit Satisfiability Instances] and
[Thaler §6.6, Alternative Transformations and Optimizations]; navigation in the [map of Thaler](../../references/books/thaler/MAP.md).
Lookup arguments, CCS, folding and binary-field systems are mostly not in either book: cite the original
papers ("source: other").

## 1. Choose the arithmetization, then the quantities to count

| arithmetization | what one unit is | count and report | source |
|---|---|---|---|
| R1CS | one rank-1 constraint ⟨a,z⟩·⟨b,z⟩ = ⟨c,z⟩ (one multiplication, any linear combinations) | constraints m, variables n (public / private), **nonzeros K** of A, B, C; linear-only constraints separately (some front ends eliminate them) | [Thaler §8.4, Extension from Circuit-SAT to R1CS-SAT]; size relation to circuits: [Thaler §8.4.1, Relationship Between R1CS-SAT and Arithmetic Circuit-SAT] |
| Plonkish | one row of a table with advice / fixed / instance columns, custom gates of degree d, copy constraints, lookups | used rows, padded height 2^k, number of advice, fixed and instance columns, max gate degree, number of copy constraints (permutation columns), lookups and table sizes, blinding rows | [Thaler §19.3.3, Intermediate Representations (IRs) Other than Arithmetic Circuits and R1CS]; PLONK (source: other, ePrint 2019/953) |
| AIR | one row of an execution trace with transition constraints between consecutive rows | trace width, trace length (padded), transition constraint degree and count, boundary constraints, number of preprocessed / permutation columns | [Thaler §19.3.3, Intermediate Representations (IRs) Other than Arithmetic Circuits and R1CS] |
| CCS | generalises R1CS, Plonkish and AIR: m constraints, n variables, t matrices, multisets of degree d | m, n, nnz, t, d | source: other, ePrint 2023/552 |

Rules of the count:
- **Degree is a cost, not a free lunch.** A degree-d gate typically multiplies the prover's quotient or sum-check
  work by a factor growing with d while it can shrink the circuit; a smaller circuit with higher degree wins
  only if the size reduction beats the per-gate increase ([Thaler §19.3.3, Intermediate Representations (IRs) Other than Arithmetic Circuits and R1CS]).
  Report rows *and* degree; never "one constraint" for a degree-9 gate without the degree.
- **The prover pays for nonzeros and for padded height**, not for "constraints": R1CS-based SNARK provers run in
  time proportional to the nonzero entries ([Thaler §8.4.1, Relationship Between R1CS-SAT and Arithmetic Circuit-SAT]);
  FFT-based provers pay for the next power of two of the height, times the blowup.
- **Lookup tables occupy rows.** In a Plonkish system a fixed table of 2^c entries makes the table height at
  least 2^c, whatever the number of lookups; amortisation only works when enough lookups share it.
- **Same unit across arms.** A comparison table uses one unit per column (R1CS constraints vs R1CS
  constraints, rows at the same degree and column count), or converts both to predicted prover cost.

## 2. Lookups vs native constraints

A k-bit range check costs about k booleanity constraints plus a recomposition when written with bits
([Thaler §6.5.4, Details of the Transformation]); with a table of the 2^c values [0, 2^c), it costs about k/c
lookups plus a recomposition, and the table itself ([Thaler §6.6.3, Efficiently Representing Non-Arithmetic Operations Over Large Prime-Order Fields],
which also describes the fingerprinting argument behind the lookup check). Modern lookup arguments: plookup
(source: other, ePrint 2020/315), logUp (ePrint 2022/1530), Lasso (ePrint 2023/1216). What to count:

- lookups (each one adds work to the lookup argument: helper columns, a permutation or log-derivative sum,
  and extra degree in the quotient or extra sum-check rounds);
- table size and whether the table is fixed (preprocessed) or committed per proof;
- the extra lookup that range-limits a narrower top limb when c does not divide k (forgetting it is an
  under-constraint, `skills/circuit-audit` item 5).

The toy counter builds all four encodings of "range-check n values to k bits", checks them on honest and
dishonest witnesses, and reads the counts off the built constraint lists:

```bash
python3 skills/constraint-cost/scripts/constraint_count.py                  # n = 1024, k = 64, c = 8 and 16
python3 skills/constraint-cost/scripts/constraint_count.py --n 4096 --k 32 --c 8 12 16
python3 skills/constraint-cost/scripts/constraint_count.py --selftest
```

Output for the default (toy planning numbers):

| encoding | constraints | rows | nonzeros | advice cols | fixed cols | max degree | lookups | table rows | height (2^k) |
|---|---|---|---|---|---|---|---|---|---|
| r1cs-bits | 66560 | | 264192 | | | 2 | 0 | | 131072 |
| plonk-bits | | 130048 | | 3 | | 2 | 0 | | 131072 |
| plonk-runsum | | 66560 | | 1 | | 2 | 0 | | 131072 |
| plonk-lookup c=8 | | 9216 | | 2 | 1 | 1 | 8192 | 256 | 16384 |
| plonk-lookup c=16 | | 5120 | | 2 | 1 | 1 | 4096 | 65536 | 65536 |

Reading: a custom running-sum gate halves the vanilla rows at equal degree; 8-bit limbs cut the height 8×;
16-bit limbs need fewer lookups but the 2^16-entry table now sets the height, so for this n they lose to c = 8.
The lookup rows' gate degree is 1, but the lookup argument itself adds degree and columns that this toy does not
count — exactly the kind of difference the real compiler's output settles.

## 3. Field choice and non-native arithmetic

The field is fixed by the backend: KZG/IPA/pairing-based systems work over the scalar field of their group;
FRI-based systems over FFT-friendly small fields and extensions; binary-field systems over towers of F_2
([Thaler §19.3.1, Field choice]; binary towers: source: other, ePrint 2023/1784). Prime fields simulate integer
arithmetic only below p, characteristic 2 simulates XOR natively ([Thaler §6.5.4, Details of the Transformation]).

When the statement lives in another field F_q (ECDSA over secp256k1 inside a BN254 circuit, BN254 arithmetic
inside a 64-bit field, a foreign curve's base field in recursion), estimate the emulation before committing to a
design:
- limbs L = ⌈log₂ q / b⌉ of b bits each, with b chosen so that products and accumulated carries stay below p;
- one F_q multiplication ≈ L² limb products (schoolbook) + the reduction modulo q (another multiplication by the
  quotient, of similar size) + range checks on the quotient and every limb and carry;
- so the cost per F_q multiplication is on the order of 2L² multiplications plus O(L) range checks, each
  possibly a lookup. Optimised gadgets (CRT-based or lazy reduction) do better: take the gadget library's own
  count (`needs verification` for any specific library's number) and record which library and version.

Report non-native operations as their own row (count of F_q multiplications × cost per multiplication), so
that a reader can swap in a better gadget.

## 4. In-circuit hash choice

| option | in-circuit cost driver | native cost | notes |
|---|---|---|---|
| AO permutations: Poseidon (source: other, ePrint 2019/458), Poseidon2 (ePrint 2023/323), Rescue-Prime (ePrint 2020/1143), MiMC | S-boxes × cost per S-box; `lib/cryptomath/cryptomath/symmetric/afcost.py` (`hades_cost`, `mimc_cost`, `power_mult_cost`) gives S-box and multiplication counts | slower than SHA-2/BLAKE3 natively | round numbers depend on field, width, α and security target: take them from the current specification, and record its version; newer cryptanalysis has revised some parameters |
| Keccak / SHA-256 via lookups | bitwise ops on limbs through tables (XOR/AND/rotation tables), or bits in a binary field | fast natively, required for compatibility (EVM, existing standards) | count lookups and table sizes; in prime fields bit-level code is expensive ([Thaler §6.6.3, Efficiently Representing Non-Arithmetic Operations Over Large Prime-Order Fields]) |
| hash outside the circuit | none | — | only if the statement does not need it in-circuit (the verifier hashes) |

```bash
python3 skills/constraint-cost/scripts/constraint_count.py --poseidon 3 8 57   # toy: 81 S-boxes, 243 R1CS constraints
```

That number is a formula (one constraint per multiplication, linear layers free); real gadgets merge constraints
differently. Use it to compare options at P2 and the compiled gadget's count in the paper.

## 5. Recursion and curve cycles

Proving a verifier inside a circuit is costed like any circuit: list the verifier's operations (group operations,
pairings, field operations, hashes, transcript) and the field each lives in. With a pairing- or DL-based inner
SNARK, the verifier's group arithmetic is over the curve's **base** field, so the outer circuit should be over
that field: hence 2-cycles of curves (Pasta-style), or a pair of curves for one level of composition; doing the
group arithmetic non-natively is possible but expensive ([Thaler §18.2, Deeper Compositions of SNARKs];
[Thaler §18.4, SNARKs for Iterative Computation via Recursion]). For hash-based inner proofs the cost is
dominated by in-circuit hashing of Merkle paths and FS transcripts (section 4) and extension-field arithmetic.
Folding (Nova, source: other, ePrint 2021/370; CycleFold, ePrint 2023/1192) replaces the full verifier by a
small "folding verifier" circuit: count that circuit, plus the final SNARK, plus any cycle-curve circuit, as
separate rows ([Thaler §18.5, SNARKs for Iterative Computation via Homomorphic Commitments]).

## 6. Where paper numbers come from

The toy counter is for screening. **Every circuit-size number in the paper comes from the compiler or framework
used for the experiments**, run at a pinned commit, with the command and log recorded as an EVIDENCE row
(`skills/log-to-evidence`). Examples (`needs verification` for the exact flags and output format of the
version you pin):

| stack | where the count comes from |
|---|---|
| Circom | the compiler's summary of non-linear and linear constraints (`circom c.circom --r1cs`), and `snarkjs r1cs info` on the `.r1cs` |
| gnark | the compiled constraint system's constraint count (`GetNbConstraints`) for the chosen backend (R1CS for Groth16, SCS for PLONK) |
| halo2 | the configured number of columns, used rows and the chosen `k` (height 2^k); `MockProver` run at that `k` |
| Noir | `nargo info` (ACIR opcodes) and the backend's gate count for the same program |
| AIR-based (Plonky3, Stwo, Winterfell…) | trace width, trace length and constraint degree as reported by the prover's own logging |
| zkVM | cycle counts from the VM's tracer (prover cost per cycle is a `skills/bench-protocol` metric) |

EVIDENCE row (synthetic):

```markdown
| E21 | 66 560 constraints (2^17 padded) | circom range64x1024.circom --r1cs --O1 | results/circuits/range64.log | 1a2b3c4 | host:3f9a | 2026-01-01 | 1 |
```

`CIRCUITS.md` (owned by `circuit-engineer`) keeps one row per circuit or gadget:

```markdown
| circuit | arithmetization / backend | constraints or rows (used / padded) | columns (adv/fix/inst) | max degree | nonzeros | lookups (table sizes) | EVIDENCE | audit (circuit-audit) |
```

## Pitfalls

- Comparing our Plonkish rows with a baseline's R1CS constraints, or our count without padding with theirs with.
- A "constraints" number that omits linear constraints for us and includes them for the baseline.
- Lookup tables whose height exceeds the circuit, left out of the height.
- A degree-5 custom gate counted as one constraint against a degree-2 baseline, with no prover-cost comparison.
- Non-native arithmetic estimated with a formula in the paper instead of the gadget library's count.
- Poseidon/Rescue round numbers copied from an old version of the specification.
- Recursion overhead reported as the inner circuit only, without the verifier circuit, the cycle curve's circuit
  or the final wrapping proof.
- Numbers from the toy counter printed in the paper.
