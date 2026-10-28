# CIRCUITS — circuit inventory, counts and audit status (owner: `circuit-engineer`)

Counts come from the compiler's own output and carry an EVIDENCE id (`skills/constraint-cost`).
Audit cell: `none` | `builder PASS|FAIL <commit>` | `falsifier PASS|FAIL <commit>` (`skills/circuit-audit`);
only a falsifier PASS supports a correctness claim in the paper.

| circuit | arithmetization / backend | constraints or rows (used / padded) | columns (adv/fix/inst) | max degree | nonzeros | lookups (table sizes) | EVIDENCE | audit (circuit-audit) |
|---|---|---|---|---|---|---|---|---|
