# Phases P0–P8 — the research pipeline

Each phase has an **owner**, **inputs**, **outputs** and a **gate**. The `pi-orchestrator`
only advances `STATE.md` when every gate box is ticked. Any agent can send work *back*.
The same gate list is in `agents/pi-orchestrator.md`; change both together.

| Phase | Owner (helpers) | Output | Gate (all must hold) |
|---|---|---|---|
| **P0 Scoping** | pi-orchestrator | `STATE.md` thesis, venue, deadline | thesis is one falsifiable sentence; paper type (protocol / system / application) and the agents it needs; measurable target + baseline value; venue CFP read + deadline; in/out-of-scope list; compute/time budget; kill date and kill criteria |
| **P1 Literature** | lit-scout | `LITERATURE.md`, `refs.bib`, `MATH-REFS.md` | related-work matrix with ≥ 15 verified works incl. the 2–4 true competitors; strongest baseline named; novelty / pre-emption check (ePrint + grey literature) ≤ 14 days old, verdict ≠ taken; refs.bib passes bib-verify; reading notes per competitor; baseline candidates with code status |
| **P2 Ideation** | idea-miner (falsifier screens) | `IDEAS.md`, first `CLAIMS.md` rows | ≥ 1 idea with a cost-model gain (constraint-cost / prover-cost-model / piop-pcs-compile) and a kill criterion; Gate A + Gate B recorded (or honest negative); top idea registered as falsifiable CLAIMS rows; novelty re-check of the chosen idea |
| **P3 Theory** | theorist (lit-scout for MATH-REFS) | `THEORY.md`, `lean/` | every lemma numerically checked on small params (`sage-check`); main theorem proof complete (soundness notion, model and setup explicit; [zk-definitions](../skills/zk-definitions/SKILL.md) assumption ledger); soundness budget table with every term marked proven or conjectured and the level definition named ([soundness-budget](../skills/soundness-budget/SKILL.md)); lower bound or "none known" |
| **P4 Baselines** | baseline-engineer (prover-engineer aligns the build) | `baselines/MANIFEST.md` | strongest baseline builds at a pinned commit; its published numbers reproduced within tolerance or the discrepancy documented; every competitor signed off at the same soundness level as ours (bits, proven/conjectured regime, level definition); build configuration identical to `impl/BUILD.md` or the differences recorded |
| **P5 Experiments** | experimenter (prover-engineer, circuit-engineer build) | `results/`, `EVIDENCE.md`, `CIRCUITS.md` | protocol fixed before running; interleaved runs, ≥ 3 repeats, medians; environment captured; every timed run verified its proof; every candidate paper number (times, sizes, constraint counts) has an EVIDENCE row; prediction vs measurement compared phase by phase ([prover-cost-model](../skills/prover-cost-model/SKILL.md)) |
| **P6 Falsification gate** | falsifier | `CLAIMS.md` verdicts | no `open` claims; refuted claims removed from narrative, weakened wording adopted; soundness budget recomputed independently by the falsifier; Fiat–Shamir audit ([fiat-shamir-audit](../skills/fiat-shamir-audit/SKILL.md)) and circuit audit ([circuit-audit](../skills/circuit-audit/SKILL.md)) passed in the falsifier's own re-run (the builders' self-audits do not count); price of each gain stated; PI decision logged |
| **P7 Writing + figures** | writer, figure-artist | `paper/` | playbook sections complete; every number ↔ EVIDENCE row (`crbench audit-tex` passes); every claim ↔ survived/weakened CLAIMS row; 0 undefined refs; figures from logged data by script in house style; related work from the matrix |
| **P8 Review → submit → rebuttal → camera-ready** | reviewer-sim, submission-rebuttal | `REVIEWS.md`, `SUBMISSION.md` | mock-review action items closed; bib-verify clean; anonymisation (`anon_check`) and page limit; checklist done; artifact builds clean; final novelty re-check ≤ 7 days old |

## Feedback loops
- P6 refutes a core claim → back to **P2** (new idea) or **P3** (weaker theorem).
- P6 finds an unfair or unreproduced baseline → back to **P4/P5**.
- P8 mock review finds a missing experiment → **P5**; a presentation problem → **P7**.
- Pre-emption found at any time → **P1** threat assessment → PI decides pivot/position/kill in `DECISIONS.md`.

## Multi-agent workflows (run with Claude Code's Workflow tool, `scriptPath`)
| script | phase | pattern |
|---|---|---|
| `lit-sweep.js` | P1 | multi-modal sweep → per-item existence verification → synthesis |
| `idea-tournament.js` | P2 | 5 mining angles → falsifier screening pipeline → 3-criterion judge panel |
| `falsify-round.js` | P6 | per claim: 3 diverse-lens falsifiers, majority vote → ledger |
| `mock-review-panel.js` | P8 | 3 reviewer personas → meta-review with routed action items |

Example: `Workflow({scriptPath: "workflows/falsify-round.js", args: {project: "/abs/path/my-paper"}})`.
Without the Workflow tool, ask the orchestrator: "run P6 using agents/falsifier.md on every open claim".
