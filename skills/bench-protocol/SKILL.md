---
name: bench-protocol
description: Measurement protocol for trustworthy timings. It covers interleaved A/B rounds, medians with IQR and bootstrap CIs, at least 3 repeats, warm-up, no stale builds, an isolated and locked machine, thread pinning, and recorded environment. Use for every ZK performance number (prover and verifier time, proof size, memory, setup, gas, zkVM cycles), with every timed proof verified, before it can enter EVIDENCE.md.
---
# bench-protocol

## Rules

1. **Interleave.** Run the arms in rounds with rotating order (A B, B A, ...). Never run
   all of A and then all of B. Machine state (thermal, turbo, co-tenants, page cache)
   drifts. Absolute times can swing by a factor of two across hours on a shared
   server, so **only ratios from back-to-back pairs in the same session are trusted.**
2. **Repeat.** Use at least 3 measured repeats plus at least 1 discarded warm-up round.
   Use at least 7 when the arms differ by less than 10% or the spread is large. Single
   measurements of the same binary can differ by nearly 2×.
3. **Report the median**, with the IQR and a bootstrap 95% CI. For a ratio, report
   `median(A)/median(B)` with a paired bootstrap CI. Never report the mean of a skewed
   timing distribution as the headline number. Never report the best of N unless the
   protocol states it for both arms.
4. **Lock and isolate.** Hold `crbench`'s file lock so benches never overlap. Run
   benches one at a time with low concurrency: parallel benches compete for memory
   bandwidth and inflate the arm that uses it more (MSM and NTT kernels are
   bandwidth-bound, so this matters more for provers than for most code). Keep the machine free of other
   heavy jobs. `crbench env` warns on high load and non-`performance` governors.
5. **Control threads.** Set `OMP_NUM_THREADS`, `RAYON_NUM_THREADS`, `GOMAXPROCS` and
   the MKL/OpenBLAS thread variables explicitly (`--threads`). Pin with `taskset`
   (`--cpus`) when comparing single-thread numbers. Report the single-thread comparison
   even when the headline is parallel, and a thread-scaling series (1, 2, 4, …, all
   physical cores) when parallelism is part of the claim.
6. **No stale builds.** Build from the pinned commit into a configuration-specific
   directory. Run `crbench stale BIN SRC` before each campaign. Record the build flags.
7. **Record the environment.** `crbench run` stores CPU, governor, load, compilers,
   git commit and dirty flag of `--target`, and the performance environment variables in
   `run.json`. Keep it.
8. **Record failures.** A crash, timeout or missing output stays in the ledger as a
   failed execution with its error. It is excluded from statistics but never deleted.
   If one arm fails systematically, that is a result: document the boundary.
9. **Every timed run verifies its proof.** The benchmark calls the verifier on the
   proof it just produced, with the real public inputs, and fails the run if it
   rejects; at least once per campaign it also checks that a tampered proof or public
   input is rejected. Verification is timed separately from proving. A fast prover
   emitting an invalid proof is not a data point.
10. **Explain surprises.** If a wall-clock speed-up exceeds the operation-count ratio
    (MSM size, NTT size, hashes, sum-check rounds; see
    [prover-cost-model](../prover-cost-model/SKILL.md)), find the mechanism before publishing.
    Examples: a smaller field or extension degree, fewer queries (i.e. a lower security
    level), a skipped phase (witness generation moved out of the timed region), cache
    effects, a GPU kernel that hides transfers. Otherwise, suspect the measurement.

## Command

```bash
crbench run \
  -a base='./target-base/release/prove --circuit toy_hash --log-rows 20 --verify' \
  -a new='./target-new/release/prove --circuit toy_hash --log-rows 20 --verify' \
  -n 7 -w 1 --order alternate --metric time \
  --threads 1 --cpus 2 --target ./impl --log-dir results/2026-01-01-toy-prove-ab

# per-phase numbers from a criterion bench (one bench function per phase)
crbench run -a new='cargo bench --bench prove -- toy_hash_2e20' \
  -n 5 -w 1 --parser criterion --reduce sum --threads 16 --target ./impl \
  --log-dir results/2026-01-01-toy-prove-mt

# peak memory of the same command
crbench run -a new='/usr/bin/time -v ./target-new/release/prove --circuit toy_hash --log-rows 20 --verify' \
  -n 3 -w 0 --parser gnu-time --metric max_rss --threads 16 --target ./impl
```

Outputs: `results/.../run.json` (all executions, environment, summary),
`results/.../<arm>/rNNN.log` (raw output of each execution), and a JSON summary on
stdout with the speed-up and its CI.

Have the prover print its per-phase times and the proof size on stdout (one
`name: value unit` line each) so a parser can pick them up; register a parser for the
format with `crbench.register_parser` rather than scraping by hand.

## Choosing the metric

Report these together; a table with only the metric where we win is not a result.

| metric | how to report | notes |
|---|---|---|
| prover time, **by phase** | witness generation / commit (MSM, NTT, Merkle) / sum-check or quotient computation / opening (and recursion or wrapping, if any) | the total alone hides where a gain comes from; state the timing scope once (witness, preprocessing, setup in or out) and keep it for every arm |
| verifier time | median over many verifications (it is short, so batch ≥ 100 calls per repeat) | native verifier; in-circuit verifier cost (constraints) is a separate row if recursion is used |
| proof size | bytes, from the serialized proof actually produced, not from a formula | break down into commitments, evaluations, Merkle paths when the claim is about size |
| peak memory | max RSS (`/usr/bin/time -v`, parser `gnu-time`, metric `max_rss`) | provers are often memory-bound at large sizes; report the largest size that fits |
| setup / SRS | setup time and SRS or proving-key size; universal vs circuit-specific | never folded into prover time |
| on-chain verification | gas for the verifier contract, calldata bytes | only when on-chain verification is part of the claim; name the wrapping used |
| thread scaling | single-thread **and** a 1…N-core series | report physical cores, SMT on/off |
| GPU | kernel time, host↔device transfer time and warm-up listed **separately**; first-run (cold) vs warm | discard the warm-up iteration from statistics but report it; name the GPU, driver, CUDA version |
| zkVM | cost per cycle (prover time / executed cycles) **and** end-to-end per program, over a named program set | cycle counts from the VM's own tracer; state whether continuations/segments and recursion are included |

Size series: sweep the statement size over powers of two (e.g. 2^16…2^24 rows or
constraints) rather than reporting one size; scaling plots (log-log) reveal the
crossover points that a single size hides.

## When numbers disagree across sessions

Rerun both arms back to back in one session. If the new pair contradicts an earlier
headline, the **same-session pair wins**. Withdraw the old number explicitly in
EVIDENCE.md (strike it through and add a reason) rather than silently replacing it.
Check whether the cache is really the variable before you blame it: run a cache-isolation
experiment.

## Hand-off

`run.json` and logs are in place, with at least 3 successful repeats per arm. Then
use `skills/log-to-evidence` to create EVIDENCE rows.
