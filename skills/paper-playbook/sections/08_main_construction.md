# 08 Main construction(s)

## Shape of each construction section

```
[opening]      One paragraph: what this section builds and where it is used.
[relation]     The relation proved (pointer to §2 if already defined), with the
               public/private split.
[PIOP]         The protocol in the oracle model, as a protocol box (below): rounds,
               oracles sent, challenges, queries, degree bounds.
[theorem]      Completeness and (knowledge) soundness error of the PIOP, ALL hypotheses
               explicit (field size, degree bounds, domain).
[compilation]  The PCS and Fiat–Shamir instantiation: which PCS properties are used,
               the resulting argument, its model and setup.
[cost]         Cost proposition in the paper's cost unit (the one "currency" used in
               abstract, intro, construction and experiments): prover field ops /
               MSM size / NTT size / hashes; verifier work; proof size in field and
               group elements.
[selection]    Rule that chooses parameters (rate, queries, batching, table size) from
               the instance, with no search if possible; tie-breaking stated.
[example]      A tiny worked example over a small field whose numbers can be
               recomputed by a script.
[remarks]      Boundary cases, what is NOT claimed, relation to prior work.
```

## Protocol boxes (P/V interaction)

A ZK construction is read through its protocol box; reviewers check it against the
proof line by line.

- **Two columns, one arrow per message.** Prover on the left, verifier on the right;
  each round is one prover message (commitments or oracles) and one verifier
  challenge. Sampling is written `ρ ←$ 𝕂`, never "the verifier picks a random value".
- **Inputs and outputs in the header.** "𝒫(𝕚, 𝕩, 𝕨)" and "𝒱(𝕚_V, 𝕩)" with the
  verifier's preprocessed index made explicit; the last line is the verifier's
  decision with every check numbered so the proof can cite "check (3)".
- **Oracle vs commitment.** In the PIOP box, messages are oracles [[f]] and the
  verifier makes queries; in the compiled box, they are commitments and openings.
  Do not mix the two in one box.
- **Degree bounds next to the oracle.** "[[f]] with deg f < n" — the soundness
  theorem depends on them.
- **The Fiat–Shamir version is not a separate protocol** unless it differs; say
  "ρ_i = ℋ(𝕚, 𝕩, C_1, …, C_i)" once, below the box.
- **Width.** LNCS fits two columns plus a narrow arrow column at `\footnotesize`;
  two-column venues need `\scriptsize` or a single-column (`figure*`) box.

### cryptocode skeleton

```latex
% \usepackage[n,advantage,operators,sets,adversary,landau,probability,notions,
%             logic,ff,mm,primitives,events,complexity,asymptotics,keys]{cryptocode}
\begin{figure}[t]
\centering\footnotesize
\pseudocode[head=\textbf{Protocol 1} ToyLookup PIOP for $\mathcal{R}_{\mathrm{lkp}}$]{%
  \textbf{Prover } \mathcal{P}(t, a) \< \< \textbf{Verifier } \mathcal{V}(t) \\[0.1\baselineskip][\hline]
  c := \mathrm{mult}(a, t) \< \< \\
  \< \sendmessageright*{[\![a]\!],\ [\![c]\!]} \< \\
  \< \< \gamma \sample \mathbb{K} \\
  \< \sendmessageleft*{\gamma} \< \\
  h := 1/(\gamma + a),\ g := c/(\gamma + t) \< \< \\
  \< \sendmessageright*{[\![h]\!],\ [\![g]\!]} \< \\
  \< \< \text{(1) } \textstyle\sum_i h_i = \sum_j g_j \\
  \< \< \text{(2) } h \cdot (\gamma + a) = 1 \\
  \< \< \text{(3) } g \cdot (\gamma + t) = c}
\caption{Toy PIOP (illustrative). Oracles are multilinear; products and inverses
are entrywise; (1) is checked by sum-check, (2) and (3) by a zero-check at a random
point.}
\end{figure}
```

Keep the cryptocode options identical to `templates/paper/macros.tex` when it gains
them; if cryptocode is not available, a two-column `tabular` with `\xrightarrow` arrows
is acceptable. Never put proof-relevant checks only in prose below the box.

## Rules distilled from review rounds

- **State every hypothesis.** "For sufficiently large fields" and "for typical
  parameters" invite a counterexample; replace with explicit conditions
  ("|𝕂| ≥ 2^{128}" or "ε ≤ (μ d + 1)/|𝕂|").
- **Run your own parameter table through every theorem** before submission. A
  soundness theorem whose hypothesis (field size, rate, proximity parameter) excludes
  some of your own benchmarked configurations is a guaranteed catch.
- **Separate the PIOP theorem from the compilation theorem.** Reviewers want to see
  which error comes from the information-theoretic part and which from the PCS and
  Fiat–Shamir; this is also what piop-pcs-compile <!-- TODO: link once skill exists -->
  checks.
- **Sufficient vs necessary.** Do not use a sufficient condition as if it were
  necessary. If only one direction is proven, say so.
- **Every "clearly"/"it is easy to see" is a falsifier target.** Ask the `falsifier`
  agent for a small-field exhaustive check (`skills/sage-check`).
- **Design choices need search evidence**, not "we chose": "we enumerated all folding
  schedules for d ≤ 2^{24} and selected the one minimising ...".
- **Families, not single instances.** Present a parameterised family
  `Scheme[k, ρ, t]` plus a recommended instance. This defends against "it is just
  parameter tuning".
- **One cost currency** used identically everywhere (e.g. "field multiplications +
  MSM size" for the prover, "hashes + field ops" for the verifier, "field elements +
  digests" for the proof); a cost formula with `\underbrace` labels per term helps.
- **Algorithm floats** for prover sub-routines: `Algorithm k  Name — one-line purpose.`
  with typed Input/Output lines; symbols identical to the protocol box.
- **Deliberately weaker variants** (e.g. an HVZK-only or non-hiding variant) can
  belong in the paper if they carry a conceptual point; label them clearly.

## Checklist

- [ ] Relation stated; protocol box with numbered verifier checks and degree bounds.
- [ ] PIOP theorem and compilation theorem separated; all hypotheses explicit and
      satisfied by every parameter set used.
- [ ] Fiat–Shamir transcript stated below the box.
- [ ] Each design choice backed by an enumeration/search statement (with script in artifact).
- [ ] Cost stated in the single paper-wide currency.
- [ ] Worked example reproducible by a script listed in EVIDENCE.
