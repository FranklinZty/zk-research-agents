---
name: lean-bridge
description: Connect paper propositions to Lean4/Mathlib theorems with a proposition-to-Lean-name table, a zero-sorry policy and an axiom audit. Use when formalising the algebraic core of a ZK paper (sum-check, polynomial identities, PIOP completeness and soundness bounds), when a reviewer questions a proof, or before claiming "machine-checked" anywhere. Points to Lean ZK resources (ArkLib), draws the boundary with circuit-correctness verification, and covers Mathlib cache pitfalls and the lean-lsp MCP tools.
---
# lean-bridge: paper proposition ↔ Lean theorem

## Scope: what to formalise

Formalise the **finite algebraic core** of the argument. Good targets in ZK papers:

- **sum-check**: the round equation g_i(0) + g_i(1) = previous claim, completeness, and
  the soundness bound (μ·d/|𝔽| via Schwartz–Zippel over each round);
- **polynomial identities**: quotient divisibility by the vanishing polynomial Z_H,
  multilinear-extension identities, grand-product telescoping, the
  logarithmic-derivative identity behind lookups (and its characteristic hypothesis),
  batching by random linear combination;
- **PIOP completeness** (honest prover always accepted) and the **information-theoretic
  soundness error** of the PIOP as a counting statement over the challenge space;
- **degree and size bookkeeping**: degree bounds after each fold, domain sizes, query
  counts, cost formulas and the closed form of a soundness budget term;
- **coding-theory facts** in the proven range (Reed–Solomon distance, unique decoding
  radius).

Do **not** try to formalise computational assumptions (discrete log, AGM security of a
PCS, collision resistance), the conjectured proximity bounds, concrete hash behaviour,
or performance. A machine-checked PIOP plus a pen-and-paper compilation theorem is a
legitimate and common split; say exactly which part is which.

If a quantity is only *modelled*, say so in the table and in the paper. An example is
a random oracle or a PCS treated as an ideal oracle, or a soundness term taken as a
definition rather than derived. The paper may then claim only "the PIOP soundness
bound is machine-checked relative to the oracle model". It may **not** claim "the
SNARK is machine-checked".

### Boundary with circuit verification

Proving that a **circuit** (R1CS, Plonkish, AIR) correctly and uniquely constrains a
function (no under-constraint, no field wrap-around) is a different activity, with its
own tools (circuit DSLs embedded in Lean, SMT-based under-constraint checkers, mock
provers). It belongs to circuit-audit <!-- TODO: link once skill exists -->, which
decides when a Lean proof of a gadget is worth it. lean-bridge covers the protocol's
algebra, not the circuit's.

## ZK formalisation resources

Check the state of each project before relying on it; these move fast.

| resource | what it offers | status |
|---|---|---|
| ArkLib (`https://github.com/Verified-zkEVM/ArkLib`) | Lean 4 framework for SNARKs: interactive oracle reductions, composition, Fiat–Shamir and the BCS transform; work on sum-check, Spartan, Merkle trees, FRI and coding theory, STIR, WHIR, Binius | repository checked 2026-10; per its README it depends on Mathlib and VCV-io; reuse its definitions of IOPs and reductions instead of defining your own |
| VCV-io | Lean library for oracle computations and probabilistic reasoning, used by ArkLib for security games | needs verification (URL and current API) |
| Mathlib `Polynomial`, `MvPolynomial`, `Polynomial.card_roots'`, `MvPolynomial.schwartz_zippel_*` | univariate root counting, multivariate polynomials; a Schwartz–Zippel statement | lemma names change between Mathlib revisions; search with `lean_loogle` / `lean_local_search`, never from memory (needs verification) |
| Lean-embedded circuit DSLs and verified-zkEVM circuit projects | circuit correctness, not protocol algebra | out of scope here; see circuit-audit <!-- TODO: link once skill exists --> |

Note: `lib/lean-template/` still ships the inherited examples (`Cyclotomic.lean`,
`RootsOfUnity.lean`). They remain useful as a build-and-cache template; ZK-specific
example files (e.g. a sum-check round lemma) are planned for a later batch of
`lib/` changes.

## Procedure

1. Start from `lib/lean-template/`. Copy it and keep `lean-toolchain` and the Mathlib
   `rev` in sync.
2. **Run a numeric check first** (`skills/sage-check`). Never start formalising a
   statement that has not survived toy parameters.
3. For each proposition, write the Lean *statement* first, with the proof as a
   placeholder on a WIP branch. Get the statement reviewed against the paper text.
   Most mismatches are in the statement, not the proof. Common ones: the Lean version
   is weaker, uses ℕ where the paper needs ℤ, or adds a hypothesis the paper omits.
4. Prove it. Useful tactics: `decide` for tiny concrete finite facts; `ring`,
   `field_simp`, `linear_combination` for identities; `omega` for linear
   ℕ/ℤ arithmetic; `norm_num`, `simp` for evaluation. Avoid `native_decide`.
5. Fill in the **table**, which is kept in the Lean project README and mirrored in
   THEORY.md:

   | paper statement | Lean name (fully qualified) | file | modelling notes |
   |---|---|---|---|
   | Lemma 3.2 (sum-check round soundness) | `Proj.SumCheck.round_sound` | `SumCheck.lean` | field 𝔽 finite; prover modelled as arbitrary functions |
   | Thm 1 (PIOP completeness) | `Proj.Lookup.complete` | `Lookup.lean` | oracle model; PCS and FS not formalised |

6. **Gate** (all must pass before the table is cited in the paper):
   - `lake build` is green on a clean checkout at the recorded commit;
   - `scripts_check_no_sorry.sh` reports no `sorry`/`admit`/`axiom`/`native_decide`;
   - an axiom audit of every headline theorem (`#print axioms T` or `lean_verify`)
     shows only `propext`, `Classical.choice`, `Quot.sound`;
   - the table rows match the paper numbering on the final PDF.
7. Record the Lean commit and the "green build" log in EVIDENCE.md, for example
   "N results, zero sorry" as the printed fact and the `lake build` log as its source.

## Lessons

- Lean often **finds redundant or insufficient hypotheses**. Run
  `lean_minimal_hypotheses` on key theorems. Sometimes a hypothesis the paper states
  is not needed, which gives a stronger theorem. Sometimes the Lean proof needs one
  the paper forgot, which is a correctness fix. Report both to `theorist` and
  `falsifier`.
- Formalising the *coefficient-level* or *evaluation-table* statement is usually much
  easier than the *polynomial-ring* statement. Prove a bridge lemma (for example,
  a multilinear polynomial is determined by its values on the hypercube) once and
  reuse it.
- Soundness bounds are probability statements; state them as **counting** over the
  finite challenge space (the number of bad challenges ≤ d) and derive the
  probability in one final step. This avoids most measure-theory overhead.
- Keep the field generic (`[Field F] [Fintype F]`) and the challenge field separate
  from the base field when the paper samples from an extension; a proof that silently
  uses the base field proves a weaker bound.
- Keep each file under a few hundred lines, with one namespace per paper section.
- An asymptotic cost claim ("prover cost O(m), independent of N") can be formalised
  as an explicit operation-count formula; pair it with the concrete count, because
  reviewers care about concrete sizes.

## Mathlib cache pitfalls

See `lib/lean-template/README.md`. In short: match the toolchain and the Mathlib rev;
run `lake exe cache get` after every `lake update`; never `import Mathlib` in project
files; allow minutes for the first cold import; look up renamed lemmas with search
tools, not from memory.

## lean-lsp MCP tools (if configured)

| need | tool | tip |
|---|---|---|
| quick compile of a snippet | `lean_run_code` | self-contained with imports; the server needs `lake` on PATH |
| goal at a line | `lean_goal` | omit the column to see the state before and after the line |
| errors | `lean_diagnostic_messages` | "no goals to be solved" means delete tactics |
| lemma by name fragment | `lean_local_search` | use before guessing a name |
| lemma by meaning | `lean_leansearch` / `lean_leanfinder` | rate-limited |
| lemma by type | `lean_loogle` | rate-limited, a few calls per 30 s |
| try tactics | `lean_multi_attempt` | `["simp", "ring", "omega", "decide", "norm_num"]` |
| which hypotheses are needed | `lean_minimal_hypotheses` | |
| axiom audit | `lean_verify` | fully qualified name |
| after adding imports | `lean_build` | slow; `fetch_cache=true` only for missing oleans |
