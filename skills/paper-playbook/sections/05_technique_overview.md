# 05 Technique Overview

Usually the longest part of the introduction (≈ 3–4 LNCS pages). Many reviewers read
only the introduction, the overview and the experiments carefully, so this part must
let a reader restate the core idea and believe the main theorem **without reading
the body**. Full procedure: [technique-overview](../../technique-overview/SKILL.md).

## Structure

```
[recall notation]   One paragraph: "We begin by recalling the routes ..., in the notation
                    of Section 2": define only the symbols the overview needs.
[prior routes]      One bold-headed paragraph per prior route, described per paper and at
                    a mathematical high level (formula, identity, cost). Each ends with a
                    factual sentence naming what that route leaves open.
[reduction]         "Taken together, the routes address (1) through distinct <structures>
                    of the same object. Whether they can be combined therefore reduces to
                    two questions: (i) ... (ii) ..."
[signpost]          "Insight 1 resolves (i) and Insight 2 resolves (ii), yielding the map
                    in Figure 1."
[figure]            One diagram placing prior works as points/corners, ours as the new
                    region; caption states the placement in one sentence.
[Insight 1]         Bold heading = a complete declarative sentence ("X bounds Y.").
                    Observation → reformulation → key formula → conclusion → why the
                    boundary case is tight.
[Insight 2]         Same format.
[composition]       The combined identity/algorithm, literally equal to the body version.
[scope extender]    Optional: one paragraph (or a short body section) showing the technique
                    applies to neighbouring schemes, quantified by formula only.
```

## Rules

- Include key formulas, one key identity, one figure and ideally one tiny worked
  numerical example.
- Insight headings are sentences, not noun phrases. Bad: "Window width." Good:
  "Window width, not table count, bounds the packing factor."
- Formulas in the overview are copied from the body theorem statements. A mismatch
  between overview and body is a classic mock-review catch.
- Introduce assumptions with "Suppose ..." before deriving, to avoid circularity.
- Asymptotic/density-type results: say "asymptotic density ... certified per instance
  by Lemma X", not "we prove the heuristic".
- Describe prior works by paper, at the level of mathematics, not by a tutorial with
  explanatory mini-headings ("Why the filter is needed", "Where the cost goes").
- The overview recalls prior routes; it does not repeat the related-work comparison.
- Late in the process, fix only obvious errors in the overview; do not restyle it.

## Toy skeleton (T1, ToyLookup; illustrative)

> **Recall.** A logarithmic-derivative lookup proves a ∈ t^m by checking
> Σ_i 1/(γ + a_i) = Σ_j c_j/(γ + t_j) at a random γ, where c_j counts how often t_j
> occurs in a. Prior work commits to the multiplicities c ∈ 𝔽^N, so the prover pays
> O(N) even when m ≪ N [..]; alternatively it preprocesses the table per circuit
> [..], leaving open whether the table can enter only through verifier-side
> evaluations.
> **Two questions.** (i) Can the right-hand sum be restricted to the support of c,
> of size ≤ m, without revealing it? (ii) Can the verifier evaluate the table's
> contribution in O(log N) for structured tables?
> **Insight 1: The support of the multiplicities, not the table, bounds the prover's
> commitments.** ... giving a prover cost of O(m) field operations plus one
> commitment of size m.
> **Insight 2: For structured tables the table side is a multilinear evaluation the
> verifier computes itself.** ...

## Checklist

- [ ] Every prior route recalled per paper with its formula and what it leaves open.
- [ ] Explicit reduction to numbered questions; each insight answers one.
- [ ] Insight headings are declarative sentences.
- [ ] Figure caption states placement of prior work vs ours in one sentence.
- [ ] Formulas string-identical to body statements.
