# Figure pattern catalog (ZK papers)

A catalog of figure patterns that recur in good cryptography papers, adapted to
zero-knowledge papers (protocol/theory, system/implementation, application/circuit), written
**in words only** -- no harvested image is reproduced here. Each entry gives
when to use it, its anatomy, the usual mistakes, and the template in this
repo that implements it. Where a source is named, it is a public IACR ePrint
ID given as "see e.g.". It points to a paper that uses the pattern and does not
endorse every detail of that figure.

**How this catalog was built.** `harvester/harvest.py` was run on a local
corpus of 59 unique public ePrint/conference PDFs, mostly about FHE and
bootstrapping. It extracted 166 figures. The heuristic classifier sorted them
as follows: architecture/pipeline 42, line plot 25, other 24, pseudocode/boxed
text 19, circuit/cipher 12, heatmap/matrix 11, protocol/flow 10, lattice/geometric
7, scaling plot 6, tree/graph 6, bar 3, table-like 1. The classifier makes
mistakes, and these counts are approximate.

Main observations:

* **Diagrams outnumber data plots** in theory-heavy crypto papers: pipelines,
  bit layouts, dependency grids and functionality boxes. Most diagrams are
  vector TikZ with 2-3 colours and greyscale-safe fills. Those are the best
  figures in the corpus.
* **Performance plots are the weakest figures.** Recurring problems: pies for
  breakdowns, coloured plot backgrounds, bold sans-serif titles inside the axes,
  default-library colours, raster screenshots, legends that cover data, a
  number on every bar, and no run-to-run spread at all.
* **Nobody shows run-to-run variance.** Showing it is a cheap way to look more
  rigorous than the baseline paper (see C15).
* **The corpus was not a ZK corpus.** The "see e.g." ePrint IDs below come from
  it and illustrate the *visual* pattern only; the ZK use cases (prover-phase
  breakdowns, P-time vs proof-size fronts, scaling in the number of constraints,
  protocol boxes, PIOP-to-PCS compilation) follow community practice and have not
  been re-harvested. Re-run the harvester on a ZK corpus before citing ZK examples
  (needs verification).
* **Retired IDs.** C6 (noise waterfall), C7 (modulus bit layout), C8 (S-box
  heatmap), C9 (trail bounds) and D3 (cipher round function) were FHE/symmetric
  patterns and have been removed. The IDs are not reused, so an old reference fails
  loudly instead of pointing at a different figure.

Conventions used by every template: `style/crypto.mplstyle` plus a venue
sheet; ours = blue (`palette.OURS`), baselines = greys; each series also
gets a marker or dash (so it survives B/W print and CVD); one axis only; text
in ink colours, never series colours.

---

## Chart patterns (matplotlib, `templates/pNN_*.py`)

### C1 Speed-up bars with a baseline = 1 line -- `p01_speedup_bars.py`
* **Use when** several circuits, workloads or parameter sets are compared against
  one reference prover, all at the same soundness level and timing scope.
* **Anatomy:** the y-axis shows the ratio *baseline time / method time*. The
  reference is a horizontal rule at 1, labelled once; it is not a bar. Ours
  is the only saturated colour and other methods are grey. Only our bars get
  value labels (`3.4x`). The geometric mean is stated once, in the title or
  caption.
* **Pitfalls:** plotting raw times on a linear axis when magnitudes differ by
  100x (use ratios or a log axis). Using the arithmetic mean of ratios (use the
  geometric mean). Changing the reference between panels. Labelling every
  bar.

### C2 Prover-time breakdown (stacked, instead of a pie) -- `p02_breakdown_stacked.py`
* **Use when** the claim is "we shrank phase X" of the prover. Phases: witness
  generation, commitment (MSM / NTT / Merkle hashing), sum-check or quotient
  computation, opening (and recursion or wrapping as a separate segment if used).
  Also for proof-size breakdowns (commitments, evaluations, Merkle paths).
* **Anatomy:** one horizontal bar per prover. Phases appear in the same
  order and colour in every row, with a thin white gap between segments. The
  total goes at the bar end. One bracket or arrow states the headline
  ratio. See e.g. ePrint 2025/1532 (stacked latency bars with a ratio
  arrow) and 2025/1298 (modulus-consumption breakdown as horizontal
  stacked bars).
* **Pitfalls:** side-by-side pies. Readers cannot compare angles across pies,
  and totals disappear. More than 5 segments. Using a different stage order
  in different rows. Leaving witness generation in one row and out of another;
  the x-axis label or caption states the timing scope.

### C3 Log-log scaling in the number of constraints -- `p03_scaling_loglog.py`
* **Use when** claiming an asymptotic improvement (e.g. a linear-time prover vs.
  an NTT-based one), or showing where a constant factor stops mattering, as a
  function of the statement size (constraints, rows, cycles).
* **Anatomy:** log2 axes with `2^k` tick labels and markers at measured points
  only. Thin dashed grey guide lines (`O(n)`, `O(n log n)`) are anchored at
  the first data point and labelled beside the line. Series are
  direct-labelled at their right end, so no legend is needed. See e.g. ePrint
  2026/845 (error growth vs. depth).
* **Pitfalls:** a linear x-axis for powers of two. Guides that are not
  anchored, which suggest a false constant. Guide labels that collide with
  series labels. Constraint counts from different arithmetizations on one x-axis
  (use the statement size, e.g. hash invocations, or one panel per system).
  Stopping the sweep before the size where memory runs out; mark the last
  feasible size instead.

### C4 Parameter-plane feasibility region -- `p04_param_feasibility.py`
* **Use when** parameters are the contribution: choosing (n, log q), (h,
  log q), or (alpha, tau) under security and correctness constraints.
* **Anatomy:** constraint curves are labelled in-line (lambda = 80/128/192).
  A light tint covers the feasible set only. The correctness bound is a
  coloured rule. The chosen parameter set is a single star with a text label.
  "Insecure" and "incorrect" regions are named in muted italics. See e.g.
  ePrint 2026/845 (regime map in a 2-D parameter plane) and 2024/115 (impact
  of the secret-key weight and log q on security).
* **Pitfalls:** saturated region fills. Unlabelled contour levels. Security
  curves drawn from a toy formula without saying so. Only the
  lattice-estimator output belongs in the final paper.

### C5 Prover time vs. proof size, with a Pareto front -- `p05_pareto_tradeoff.py`
* **Use when** two costs trade off against each other (prover time vs. proof
  size across code rates, query counts, folding factors or PCS choices; proof size
  vs. verifier time) and there is no single winner. Every point must be at the
  same soundness level and regime; say so in the caption.
* **Anatomy:** dominated points are grey. Non-dominated points are joined by a
  step line in the accent colour. A "better" arrow points to the good corner.
  At most 3-4 named points. Log axes if the ranges span decades.
* **Pitfalls:** connecting all points in x-order. Labelling every point.
  Leaving "lower is better" implicit. Mixing points at different security levels
  (or proven and conjectured soundness) on one front. Dropping verifier time
  silently; give it in the caption or a second panel.

### C10 Error distribution with log-scale tails -- `p10_error_distribution.py`
* **Use when** justifying a decryption-failure or precision claim from
  experiments.
* **Anatomy:** histogram on a LOG y-axis with the sample count in the
  legend. The fitted Gaussian is a thin ink line. The correctness bound +-B
  appears as coloured verticals. The extrapolated failure probability is
  written as 2^-k, and the fit's assumption is named in the caption.
* **Pitfalls:** a linear y-axis, where tails, the only part that matters, are
  invisible. Extrapolating 2^-128 from 2^17 samples without an analytic
  argument.

### C11 Approximation: target + log-scale error -- `p11_approx_error.py`
* **Use when** presenting polynomial, Chebyshev, minimax or Fourier
  approximations (EvalMod, sign, comparison, LUT).
* **Anatomy:** two panels with a shared x-axis. The top panel shows the
  target function (thick grey) and the approximation (thin, dashed). The
  bottom panel shows |error| on a log scale for 2-4 degrees, direct-labelled,
  with the precision target as a horizontal rule. See e.g. ePrint 2025/1534
  (arcsin approximation and its difference plot), 2026/367 (Fourier extension
  convergence) and 2026/450 (Fourier expansions of bit functions).
* **Pitfalls:** plotting the error on a linear axis. Unreadable overlaid
  curves of near-identical colour. Omitting the interval endpoints where the
  error peaks.

### C12 Cost-model crossover -- `p12_crossover_cost.py`
* **Use when** two algorithms win in different regimes (lookup vs. native
  constraints, KZG vs. FRI-based PCS, schoolbook vs. NTT, MSM algorithm A vs. B).
* **Anatomy:** analytic curves, measured points as markers (showing the model
  is calibrated), a vertical line at the crossover with its value printed,
  and very light regime tints labelled "X wins". See e.g. ePrint 2026/213
  (linear cost model of CKKS operations, fitted to measurements).
* **Pitfalls:** using a model without measured points. Regime tints strong
  enough to fight the data.

### C13 Sparsity patterns of structured matrices -- `p13_sparsity_pattern.py`
* **Use when** explaining a factorisation of a linear transform (FFT/NTT
  butterflies, CoeffToSlot and SlotToCoeff factors, packing matrices), where
  the number of non-zero diagonals drives the rotation count.
* **Anatomy:** small multiples of equal-size square panels on a hairline
  grid, with non-zeros filled in one dark colour. Under each panel: its
  symbol and the number of diagonals. See e.g. ePrint 2025/696 (butterfly
  matrices of an inverse NTT) and 2024/164 (bit-reversal butterfly structures).
* **Pitfalls:** unequal panel sizes. Colouring by value when only the support
  matters.

### C14 Parameter-sweep heatmap with the optimum outlined -- `p14_param_sweep_heatmap.py`
* **Use when** a tuning space has two discrete knobs (folding factor x code rate,
  columns x gate degree, MSM window x batch size).
* **Anatomy:** a single-hue ramp whose colour-bar label states "lower is
  better". The value is printed in each cell with one decimal. Infeasible
  cells are hatched grey, not coloured. The optimum cell gets an accent
  outline. See e.g. ePrint 2026/845 (runtime and ciphertext-size heatmaps
  over two parameters).
* **Pitfalls:** a rainbow ramp. Colouring infeasible cells as if they had
  a value. Too many cells to print values (above ~12x12, drop the numbers).

### C15 Repeated-run distributions (A/B bench) -- `p15_bench_distribution.py`
* **Use when** reporting any speed-up that a sceptical reviewer might doubt.
  This pairs with the bench harness (`lib/bench`): interleaved runs, median,
  IQR and a bootstrap CI.
* **Anatomy:** one small panel per workload. Individual runs appear as
  jittered dots, with median and IQR marks beside them. The title states the
  median ratio with its 95% CI and the number of runs. Absent from the
  harvested corpus, which makes it an easy way to stand out.
* **Pitfalls:** error bars of +-1 std on skewed timing data (use IQR or a
  CI). Hiding warm-up runs without saying so.

### C16 Results table: best in bold, runner-up underlined -- `p16_results_table.py`
* **Use when** reporting the main comparison. Tables often beat charts for
  fewer than ~30 numbers.
* **Anatomy:** booktabs rules with no vertical lines. Column headers carry
  units and direction arrows. Numbers are right-aligned with a fixed number
  of decimals per column. Ours is the last row, below a midrule. The best
  value per column is bold and the second best underlined. There is a
  speed-up column relative to a named baseline, and "--" entries are
  explained in a footnote.
* **Pitfalls:** bolding ours when it is not best. Mixed precision in a column.
  Comparing numbers from different machines without flagging them (the
  EVIDENCE ledger should record machine and commit).

---

## Diagram patterns (TikZ, `templates/tikz/*.tex`, style `crypto-tikz.sty`)

### D1 Protocol box: prover/verifier interaction -- `tikz/protocol_flow.tex`
* **Use when** presenting an interactive proof, a PIOP or a compiled argument
  (prover on the left, verifier on the right), a security game, or an ideal
  functionality. In a paper body, cryptocode's `\pseudocode` gives the same layout
  (`skills/paper-playbook/sections/08_main_construction.md`).
* **Anatomy:** party names with their inputs in bold on top (𝒫(x; w), 𝒱(x)),
  each party's local computation left- or right-aligned in its own column, and
  messages as labelled horizontal arrows in the middle, top to bottom. Round
  numbers go in muted text on the margin. Challenges are sampled explicitly
  (ρ ←$ 𝕂). The verifier's checks are numbered so the proof can cite them, and the
  accept condition is the last line. For ideal functionalities, use a framed box with a
  bold title such as "Functionality F_x" and numbered steps. See e.g. ePrint
  2025/1834 (functionality boxes for random sharings and coin tossing),
  2026/840 (simplified client-server sequence diagrams) and 2024/109 (the
  bootstrapping functionality as a figure).
* **Pitfalls:** diagonal message arrows, which suggest timing that is not
  modelled. Mixing algorithm names in italic and sans serif (define
  `\alg{}` once). Frames drawn with heavy rules. Mixing oracles and commitments
  in one box. Verifier checks written only in the prose below the box. A message
  label that collides with the computation line above it.

### D2 Prover pipeline / architecture of a multi-stage procedure -- `tikz/pipeline.tex`
* **Use when** the contribution modifies one or two phases of a known pipeline
  (prover phases, circuit compilation and witness generation, recursion layers).
* **Anatomy:** boxes left to right, joined by thin arrows. The quantity the paper
  tracks (memory held, data size, field) sits above the boxes on one baseline.
  The changed phase is tinted blue and every other box stays white. A brace
  underneath quantifies the claim (peak memory, hashes, MSM size). See e.g. ePrint 2024/109 (previous vs. new
  pipeline, drawn as two figures with the same layout), 2025/1594 (steps
  that benefit are highlighted), 2025/1534 (a dotted separator per level) and
  2023/1304 (abstract "fat vs. thin" bootstrapping).
* **Pitfalls:** clip-art icons. More than ~7 boxes in a row (wrap or group
  them). "Before" and "after" pipelines drawn with different layouts.

### D4 Lattice / geometric picture -- `tikz/lattice_basis.tex`
* **Use when** building intuition for reduction, CVP/BDD decoding, rounding
  or fundamental domains.
* **Anatomy:** small grey lattice points, a reduced basis in blue and a long
  basis in grey, with the fundamental parallelepiped lightly tinted and the
  origin marked. The legend is text in a white box. See e.g. ePrint 2025/686
  (a hardness-vs-approximation-factor axis diagram).
* **Pitfalls:** a 3-D perspective. Too many points. Non-integral coordinates
  that make the figure lie about the lattice.

### D5 Commutative diagram -- `tikz/commutative_diagram.tex`
* **Use when** stating correctness or homomorphism (Encode, Enc, Eval, Dec
  commute with f), or relating encodings.
* **Anatomy:** tikz-cd with sans-serif algorithm names via `\alg{}` and
  script letters for spaces. The one "new" arrow is in the accent colour.
  See e.g. ePrint 2026/233 (encoding/decoding vs. homomorphic
  encoding/decoding).
* **Pitfalls:** labels containing commas without braces (tikz-cd parse
  error). More than 3x3 nodes.

### D6 Dependency grid / dataflow DAG (NTT, sum-check, recursion) -- adapt `tikz/pipeline.tex`
* **Use when** a computation has a 2-D dependency structure. Examples: NTT
  butterfly networks, the variables bound per sum-check round, FRI folding
  layers, a recursion or aggregation tree, digit-extraction grids.
* **Anatomy:** a `matrix` of nodes, with arrows labelled by the polynomial
  or operation applied. The critical path is drawn in the accent colour, and
  axes name the two indices. See e.g. ePrint 2023/1304 and 2024/115 (digit
  extraction and removal grids), 2026/1089 (digit-extraction dataflow) and
  2022/1364 (critical path of digit removal).
* **Pitfalls:** unlabelled arrows. Mixing dashed and solid arrows without a
  legend.

### D7 PIOP-to-PCS compilation pipeline -- `tikz/piop_compile.tex`
* **Use when** the paper's construction follows the PIOP + PCS + Fiat--Shamir
  route and the contribution sits in one step (a new PIOP, a new PCS, a new
  compiler), or when the security section must show where each error term comes
  from.
* **Anatomy:** boxes left to right: relation, PIOP, interactive argument,
  SNARK. Each arrow names the ingredient added (arithmetization, PCS,
  Fiat--Shamir). Under each arrow, in muted text, the properties that step of the
  compilation theorem needs (binding, extractability, evaluation binding, hiding;
  round-by-round soundness and a complete transcript). The contributed step is
  tinted blue. A brace states the error accounting
  (κ ≤ ε_PIOP + ε_PCS + ε_FS).
* **Pitfalls:** listing properties the proof never uses, or omitting one it does
  (the figure becomes a checklist reviewers will hold you to). Drawing the
  "before" and "after" constructions with different layouts.

---

## Checklist before a figure goes into `paper/figs/`

1. It was made at final size: `palette.figure(venue, width=...)`, then
   `\includegraphics[width=\textwidth]` or `\columnwidth` with **no
   scaling**. Figure text is 7-8 pt, matching the caption.
2. It is vector (PDF), with fonts embedded (Type 42) and matching the body
   font: CM for LNCS, Times/Libertine for IEEE/ACM.
3. Colours are assigned in fixed order, ours = blue and baselines = grey,
   with a marker or dash per series. It is still readable in greyscale
   (`pdftoppm -gray`).
4. One y-axis. Units in labels. Log axes wherever the range exceeds ~30x.
5. There is a legend for 2 or more series, with direct labels where
   possible. No value printed on every mark.
6. Every number in the figure has an EVIDENCE row (command, commit,
   machine), and the figure script path is recorded in the EVIDENCE entry.
7. Synthetic or toy content is labelled as such in the caption.
8. Performance figures state the soundness level and regime and the timing
   scope (witness generation, preprocessing, setup) in the caption.
9. The caption states the take-away in its first sentence.
