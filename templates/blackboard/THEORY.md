# THEORY — statements, proof status, formalisation (owner: `theorist`)

| paper label | statement (short) | notion and model | proof status (sketch/full/checked) | numeric check (script) | Lean name | sorry-free? |
|---|---|---|---|---|---|---|

## Assumption ledger

One block per theorem (format: `skills/zk-definitions` §3).

## Parameters and security

One table per parameter set (format: `skills/soundness-budget`, "Output format"). Name the level definition
(worst-case or average-case, `references/books/GLOSSARY.md`); keep conjectured terms in a separate row set.
The falsifier recomputes every table independently.

### Soundness budget: <protocol>, parameter set <name>
Definition: <worst-case | average-case>. Notion: <soundness | knowledge soundness>. λ = <hash output>, field <F>, challenges in <set>.

| term | bound ε_i(t) | bits at t = 2^s | proven / conjectured / heuristic | source | EVIDENCE |
|---|---|---|---|---|---|
| **total (union bound)** | Σ | | | | |
