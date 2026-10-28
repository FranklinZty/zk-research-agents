---
name: baseline-pin
description: Identify the real strongest baseline proof system, prover library or zkVM, fetch it, pin an exact commit, build it with a recorded recipe, verify that its proofs verify, and record everything in baselines/MANIFEST.md with a ZK fairness checklist (equal security bits and regime, same statement, same timing scope, same hardware features, P/V/proof size together). Use at P4 before any comparison is measured, and again whenever a reviewer or falsifier questions a baseline.
---
# baseline-pin

## 1. Identify the *real* baseline (before fetching anything)

- The paper you are improving on is **not automatically** the baseline. Ask these
  questions:
  - Is its construction a re-derivation of earlier work? Search for the core idea
    under other names.
  - Has a follow-up already improved on it? Check citing papers and ePrint from the
    last 24 months.
  - Is a different library much faster for the same task? For example, an
    implementation in another language, over a different field (a small-field STARK
    vs a pairing-based SNARK), or with a GPU backend.
  - Is the paper's "baseline" a production system whose current release is much faster
    than the version the paper measured? ZK libraries move quickly; check the release
    notes and the project's own benchmark pages (grey literature) before fixing the bar.
- The strongest fair comparison beats the most convenient one. Write the decision in
  DECISIONS.md: "baseline = X because ..., rejected Y because ...".
- Record the **best reproducible local number** as the bar to clear. The paper's
  single-thread number may understate what the baseline achieves with trivial,
  standard optimisations such as parallelisation, its `asm`/SIMD features, or a
  different but supported field or hash. If a trivial engineering change
  makes the baseline much faster, that faster version is the bar.

## 2. Fetch and pin

```bash
references/baselines/fetch.sh "$PROJECT/baselines" gnark arkworks-algebra
# -> baselines/PINNED.tsv with full SHAs
```

- Pin a **full commit SHA**. A tag or branch name is not enough, because tags can move
  and branches always do.
- Research artifacts often ship as **patches to a library** rather than as a standalone
  program. Pin both: the upstream SHA and the patched fork's SHA or patch hash.
- Pin the **lock file** too (`Cargo.lock`, `go.sum`, `package-lock.json`): a ZK prover's
  speed depends on transitive field/curve/hash crates. For circuits, pin the circuit
  compiler (e.g. the Circom or Noir version) and record the hash of the compiled
  artifact (R1CS, ACIR, proving key), because a compiler upgrade changes the
  constraint count.
- Never commit third-party source trees into the research repo. Commit only the
  MANIFEST row and the fetch command.

## 3. Build recipe (exact, copy-pasteable)

Record the exact configure and build commands, compiler **and version**, flags,
dependency versions (Rust toolchain incl. nightly date, Go version, Node version for
witness generators, CUDA/driver version for GPU provers), Cargo **features** (`asm`,
`parallel`, `avx512`, `gpu`, `print-trace`), `RUSTFLAGS` (e.g. `-C target-cpu=native`
on both arms or neither), and environment variables needed at *runtime*.

Runtime linkage is a classic trap. If several versions of a shared library are
installed (CUDA runtime, a C++ prover backend, GMP), the binary may silently load the
wrong one. Set `LD_LIBRARY_PATH` explicitly, then check with `ldd`. A feature flag that
silently falls back (a GPU backend that runs on the CPU when no device is visible, an
`asm` feature ignored on the wrong target) is the ZK version of the same trap: print
the backend in use from inside the benchmark. Keep one build directory per configuration:
`build-release-native/`, `build-release-portable/`. **Never benchmark from a build
directory whose provenance you cannot state.** Stale builds from an earlier
configuration have produced wrong numbers many times. `crbench stale BIN SRC` flags
sources newer than the binary.

If a configuration misbehaves only at one build profile, record which profile was used
for each number. Debug builds of Rust provers are often 10–100× slower and occasionally
expose overflow checks that release builds skip; benchmark only release (or the
project's own `bench`/`profiling` profile) and say which.

## 4. Verify before timing

- [ ] The library's own tests pass.
- [ ] End-to-end correctness on your statement: the proof **verifies**, with the
      baseline's own verifier, on the same public inputs; a deliberately wrong witness
      or public input is **rejected**. A benchmark that only runs the prover is not a
      baseline.
- [ ] The **runtime parameters are printed and diffed** against the paper you compare
      with: field and extension degree, curve, code rate, number of queries, folding
      factor, grinding bits, hash, PCS, number of rows/columns or constraints, and the
      claimed security level **with its regime** (provable or conjectured). A library
      default named "100-bit" or "128-bit" can rest on a conjectured proximity bound,
      or on a curve whose real security is below the label; if the paper's speed-up
      used different parameters from the library default, the denominator changed.
      Recompute the level with [soundness-budget](../soundness-budget/SKILL.md).
- [ ] The **statement** is the same: the same computation (e.g. the same hash over
      the same input length, the same VM program), not merely a circuit of the "same
      size". Record each system's own constraint/row/cycle count from its compiler or
      tracer output.
- [ ] Record the failure modes. If a configuration is infeasible, document the
      *boundary* with the exact error message, for example "domain size exceeds the
      field's 2-adicity", "SRS too small for circuit", out-of-memory at 2^k rows, or
      "GPU memory exhausted". Make the harness catch the error and print
      `FAILED (<reason>)` instead of dumping core.

## 5. MANIFEST row (the project's `baselines/MANIFEST.md`)

```markdown
| name | url | commit (full SHA) | tag | build recipe | compiler + flags | threads | bench command | parser | role | fairness notes |
|---|---|---|---|---|---|---|---|---|---|---|
| toyprover | https://example.org/toyprover.git | 0123456789abcdef0123456789abcdef01234567 | v0.4.0 | `RUSTFLAGS="-C target-cpu=native" cargo build --release --features asm,parallel` (Cargo.lock pinned) | rustc 1.xx (toy), target-cpu=native on both arms | 1 and 16 | `cargo bench --bench prove -- toy_hash_2e20` | criterion | strongest public prover for statement S (toy hash chain, 2^20 rows) | default config: rate 1/2, 100 queries, 16 grinding bits = toy "100-bit conjectured"; we re-parameterise both arms to the same proven level; P time includes witness generation, excludes preprocessing; proof verified in every run |
```

Add a "Practical build priority" list: which baseline to reproduce first, and why.

## 6. Fairness checklist (sign off before handing to `experimenter`)

- [ ] **Same security bits, same regime.** Both arms reach the same number of bits,
      computed the same way ([soundness-budget](../soundness-budget/SKILL.md)),
      and both are provable or both conjectured. If not, re-parameterise the baseline
      and report both its default and the matched configuration. Curves count too:
      a pairing curve's real security can sit below its nominal label.
- [ ] **Same statement.** The same computation on the same input sizes. Constraint
      counts from different arithmetizations (R1CS, Plonkish, AIR, CCS) are not a
      common unit; compare end-to-end on the same workload and report each system's
      own count.
- [ ] **Same timing scope.** State for every arm whether P time includes witness
      generation, preprocessing (key generation, circuit compilation, commitment to
      fixed columns) and setup (SRS generation or download). Report the excluded parts
      separately; never fold them in for one arm only.
- [ ] Same threads. Report single-thread as well as parallel.
- [ ] **Same hardware features**: compiler, `RUSTFLAGS`, `asm`/AVX2/AVX-512/NEON
      features, GPU model and driver. A GPU arm is compared with a GPU arm, or the
      table says so explicitly.
- [ ] Same machine, same session, interleaved rounds.
- [ ] **P, V and π together.** Prover time, verifier time and proof size are reported
      for every arm, plus peak memory; never only the metric where we win.
- [ ] **Recursion and wrapping listed separately.** If an arm compresses its proof by
      recursion or by wrapping into a pairing-based SNARK (e.g. Groth16) for on-chain
      verification, report the inner proof and the wrapping cost as separate columns,
      and compare like with like (wrapped vs wrapped, or unwrapped vs unwrapped).
- [ ] Every cited baseline number has been re-measured locally. Cited and local numbers
      are never mixed in one ratio.
- [ ] The strongest known baseline is included, not only the one the target paper used.
- [ ] Build freshness is verified, runtime library linkage is verified with `ldd`, and
      the backend in use (CPU/GPU, feature set) is printed by the benchmark itself.

## Hand-off

The row is complete, every checklist box is ticked or has a written exception, and a
single-arm reference run (`crbench run -a base=...`, at least 3 repeats) is logged.
Next agent: `experimenter`.
