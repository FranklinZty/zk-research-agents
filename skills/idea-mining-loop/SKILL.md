---
name: idea-mining-loop
description: Run the 8-step idea-mining loop (probe, free a fixed parameter, exact/SAT synthesis, spot an anomaly, algebraic root cause, control experiment, real-system validation, generalise + lower bound) with a pre-gate and two gates. Use when a direction has a measurable bottleneck and intuition-driven attempts have stalled.
---

# idea-mining-loop

Reverse-engineered from how real results were found: an idea is not *chosen*, it is what **survives**. The
loop turns "numbers look odd" into "theorem + bound", and it is designed to let most candidates die cheaply.

Worked, runnable example (toy FRI cost model, synthetic numbers): `python3 skills/idea-mining-loop/scripts/toy_mining_demo.py`.
It sweeps folding factor × rate for proof size × verifier work, and shows an outlier, a naive hypothesis killed by
two control experiments, a closed-form cost model checked against a direct simulation, the price paid by the prover,
a lower bound, and an honest Gate-B failure (`--D 22`).

## When to use / not use

Use: a performance/complexity bottleneck you can compute in a few lines; 1–2 intuitive attempts already stalled;
you suspect a design constant (folding factor, rate, field, column count, gate degree, lookup table size, chunk
size, number of sum-check rounds, recursion depth) was fixed by habit rather than proven optimal. Do **not** use when you already have a precise theorem target —
just prove it.

## Pre-gate 0 — security-bearing object or computational substrate? (5 min)

Write one sentence: *"The object I want to compress/restructure is ___; it is / is not part of the argument's
soundness or zero-knowledge analysis, because ___."*
- **Security-bearing** (Fiat–Shamir transcript and challenge derivation, the field or extension challenges are
  sampled from, query count and proximity parameter, grinding, the SRS / trusted setup, masking and hiding
  randomness, the hash modelled as a random oracle, anything the soundness or ZK proof quantifies over): exclude
  structurally. Changing it changes the *theorem*, not just the cost: "fewer queries" or "a smaller challenge
  field" is a lower security level, not an optimisation. Route any such idea through [soundness-budget](../soundness-budget/SKILL.md) and
  [zk-definitions](../zk-definitions/SKILL.md) before it counts as a gain.
- **Substrate** (field arithmetic and representation, NTT/MSM scheduling, Merkle layout and leaf packing, memory
  layout, witness generation, parallelisation, constraint layout that provably preserves the relation): allowed —
  but passing this gate is necessary, not sufficient. Step 6 is still mandatory.
If you cannot write the sentence, the target is not specific enough: go back to Step 0.

## The steps (every step writes a dated note `notes/<slug>_<YYYY-MM-DD>.md`; never overwrite old notes)

| step | do | time box | output |
|---|---|---|---|
| 0 Probe target | State the bottleneck as a number computable in a few lines + baseline value + success criterion. Bad: "the prover is slow". Good: "field multiplications in the sum-check prover for a degree-3 gate over 2^20 rows; baseline 3.1·10^8 (toy)". | 5 min | `probe_target` note |
| 1 Cheap probes | One ≤50-line offline script per candidate direction; answers only "is there any hope in principle?". Kill if the small-scale probe cannot approach the target, or the gain is dwarfed by overhead. Keep negative results. | ≤30 min/direction | `<direction>_probe` note (also for dead ones) |
| 2 Representation tricks | Read neighbouring work asking "what did they turn from FIXED into a FREE variable?" — one line per paper. | 1–2 h | `representation_tricks` note |
| **Gate A** | Name the parameter that is fixed by history/engineering default, not by proof. Cannot name one → back to 2, or the direction has no minable freedom. | | line in IDEAS.md |
| 3 Parametrise + sweep | Make it a CLI parameter; sweep a range deliberately **wider** than intuition; cheap proxy metric first; structured output (JSON/CSV), not logs. | ≤1 h | `<param>_planner.py` + `results/<param>_sweep/` |
| 4 Exact synthesis | On survivors, let a solver (SAT/SMT/ILP/exhaustive search) find the true optimum (min constraints, min columns, min gate degree, min rounds, min queries at fixed soundness). Per-call timeout ≤5 min. **Re-verify every solver model with independent code.** | ≤2 h | table: candidate → optimum → re-verified? |
| **Gate B** | Look for an *outlier* — "better out of proportion, not explained by the other candidates" — not the best value. Smooth monotone curve → record "no anomaly", return to Step 2. | | IDEAS.md verdict |
| 5 Algebraic root cause | Test which algebraic or structural relation the outlier satisfies (divisibility of log-sizes, 2-adicity of the field, subgroup/coset structure of the domain, degree bound vs domain size, alignment with hash block or SIMD width). Target: one provable/refutable sentence "anomaly ⟺ property P". Keep the Sage/Wolfram code. | ≤1 h | `algebraic_root_cause` note + code |
| 6 Control experiment (**never skip**) | Build a candidate that shares the naive explanation's surface feature but lacks property P (and vice versa). Anomaly must vanish/appear accordingly. If not → P is wrong/incomplete, back to 5. | ≤30 min | `## Control experiment` section of the Step-5 note |
| 7 Real-system validation | Wall-clock in the real prover/verifier, baseline vs candidate vs a control candidate, same soundness level and regime, same flags/threads/machine, interleaved runs, ≥3 repeats (median + spread), **every proof verified**. Report component *and* end-to-end (Amdahl), absolute *and* relative, P *and* V *and* proof size. | ½ day | `results/<slug>_real/` + EVIDENCE rows |
| 8 Generalise + lower bound | (a) Replace the specific value by a family (one degree → all degrees; one field → all fields with the same 2-adicity; one gate → all gates of the class) and re-run 4–7. (b) Prove how close the result is to a lower bound (counting, information-theoretic, degree, rank, continuous relaxation). "X% faster" becomes "within Y of optimal". | 1–2 d | THEORY.md + CLAIMS.md entries |

## Mini-examples across ZK design axes (toy, for orientation)

| design axis | fixed-by-habit parameter (Gate A) | cheap probe / proxy | what an anomaly + control would look like |
|---|---|---|---|
| FRI-style LDT | folding factor k (same in every round) and code rate ρ | proof size × verifier work at fixed bits and regime | an outlier along k → check whether log₂ k divides log₂ d (padding); control: same k, mixed arity (see demo) |
| Field choice | Goldilocks vs BabyBear vs M31 vs a binary tower field | field mults per constraint × cost per mult (incl. extension-field challenges and NTT/2-adicity limits) | a field that wins out of proportion on one circuit → check whether the circuit's native word size matches the field (e.g. 32-bit limbs); control: same circuit with mismatched word size |
| Sum-check PIOPs | gate degree vs number of columns (wide-low-degree vs narrow-high-degree) | prover field mults ≈ rows × (degree + 1) × columns touched per round | a degree where cost drops more than the column count explains → check for a shared factor or zero columns; control: same degree, dense columns |
| Custom gates | maximum gate degree in a Plonkish layout | rows × columns × quotient degree (blow-up factor) | a degree at which the quotient blow-up jumps (next power of two) → control: same degree with a larger domain already in use |
| Lookup vs native | range check / bit decomposition via lookup or via native constraints | constraints + table size amortised over the number of lookups | a crossover far from the naive estimate → check table-size padding and multiplicity columns; control: same number of lookups, different table size |
| PCS choice | KZG vs IPA vs FRI/STIR/WHIR vs a multilinear PCS | (P time, V time, proof size, setup) at the same bits, regime and statement | a PCS that dominates on one size only → check which term (MSM, NTT, hashing) crosses over; control: same size with that term removed from the cost model |
| Recursion vs folding | where the boundary between folding steps and a final SNARK/wrapper sits | per-step cost + final-proof cost + verifier circuit size | an outlier batch size → check the verifier circuit's own constraint count at that size; control: same batch with a cheaper in-circuit hash |

## Prompt patterns that produced real ideas (generalised)

1. **Read before thinking.** First make the agent summarise *tried / abandoned / current best*. No free association in a vacuum.
2. **Ignition = concrete book chapter + concrete step.** "Use the structures in <textbook, chapter> to attack <specific algorithm step>" — never "give me ideas".
3. **Human step: spot the constant.** For every specific object in the agent's output ask "why this one? what if it varied?" — this is Gate A and is the least automatable step.
4. **Exhaust and falsify.** "Not only the value that worked — every member of the family, including the ones theory says should be better — run them for real."
5. **Reachability audit.** "Check item by item whether each theoretical saving is actually reachable."
6. **Theorem-ise the survivor**, then **ask for the lower bound** and "how far from it are we?".
7. **Measured, not predicted.** Any number without a command and a log is a prediction; say so.
8. **Ask for the price.** "Why is the speedup so large? What got worse (proof size, verifier time, prover memory, setup, recursion cost, soundness regime)?"
9. **Let branches die, and file them.** A failed branch becomes a documented negative result or a pure-theory remark — never a drag on the main claim.

## Anti-patterns (from real post-mortems)

- Trusting a hand proof over a computation: an "established" theorem later found false. Verify every algebraic claim in Sage/Lean before it enters a draft.
- Skipping Step 6: correlation (a shared surface feature) mistaken for cause.
- Sweep range too narrow: outliers often sit outside the "sensible" range.
- One real-system run: that is a smoke test, not a result.
- Comparing hand-written code with a library without matching compiler flags / build options first: a large "anomaly" that is only `-march=native`.
- Reporting only the ratio: the component speedup can rise while the end-to-end gain falls, because the denominator shrank.
- A cost model that ignores fan-out/hidden terms (Merkle path sharing, extension-field arithmetic, witness generation, memory traffic): a solver "finds" a 30× gain that an explicit simulation erases. Validate the cost model on a small instance by direct simulation before trusting any optimum.
- Structure that exists only for one specific value (an algebraic coincidence of one constant) rarely generalises; test the generalisation early (Step 8a) before building a paper on it.
- A "speed-up" that silently lowers soundness (fewer queries, a smaller challenge field, a conjectured instead of a proven proximity bound): compare at the same bits **and** the same regime, or it is not a result.
- Benchmarks that never run the verifier: a fast prover emitting rejected proofs looks like a breakthrough.
- Comparing constraint counts across arithmetizations (R1CS vs Plonkish vs AIR) as if they were the same unit: compare the same computation end to end.

## Log

Append one row per run to the project's `IDEAS.md` table:
`| date | target | freed parameter | anomaly | root cause | control passed? | real-system result | verdict |`.
