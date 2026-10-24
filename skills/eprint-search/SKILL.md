---
name: eprint-search
description: Search IACR ePrint (with a submission-date window) plus Crossref/DBLP from the command line, and run the grey-literature pass (project docs, HackMD, ethresear.ch, vendor blogs, audit reports). Use for novelty checks ("is this idea already taken?"), for building the related-work matrix, and for finding the public ePrint id of a paper before citing it.
---

# eprint-search

## Commands

```bash
S=skills/eprint-search/scripts/eprint_search.py
python3 $S "lookup argument" "logarithmic derivative" --months 12       # union of phrasings, last 12 months
python3 $S "folding scheme" --crossref --min-year 2021                    # + published versions with DOI
python3 $S "sumcheck" --title-only                                        # title search only
python3 $S "..." --json > hits.json                                        # for scripting
python3 $S --selftest
```

Exit status 2 means *no source answered* (offline or blocked) — that is "novelty check not performed", never
"no hits". DBLP sometimes serves a bot challenge to scripts; the script detects it and you should add `--crossref`.

## Novelty-check procedure ("is it already taken?")

1. Write the idea as one falsifiable sentence (what object, what improvement, under which assumptions).
2. Generate **5–10 phrasings**: the technique name, the problem name, the object name, the synonym used by the
   neighbouring community (e.g. "lookup argument" / "lookup" / "table lookup" / "multiset check"), and the
   name of the closest known baseline.
3. Run them with `--months 12` (always) and without a window (for the classic literature). Add `--crossref`
   for published-only venues. Then run the **grey-literature pass** below with the same phrasings.
4. Read the abstract of every hit whose title shares two content words with the idea; open the PDF of any hit
   that shares the object *and* the technique. Snowball: check the "related work" of the 2–3 closest hits and
   the papers that cite the main baseline (Crossref/Google Scholar "cited by").
5. Verdict per idea, logged in `LITERATURE.md` → `## Novelty checks`:
   `- YYYY-MM-DD | query: "..." | sources: eprint,crossref,grey | window: 12m | hits reviewed: N | verdict: clear|overlap:<key>|taken:<key>`
   * `clear`: nothing shares object + technique.
   * `overlap:<key>`: same object or technique, different claim → add a matrix row and a precise "our delta".
   * `taken:<key>`: same claim → stop, tell `pi-orchestrator`; salvage is a new decision, not a rewording.
6. Re-run every 2 weeks while the project is live and once more right before submission (ePrint moves fast;
   the `lit-matrix` linter fails if the newest check is older than 14 days, the P1 gate; P8 requires ≤ 7 days).

## Grey-literature pass (ZK)

Many ZK results appear first, or only, outside ePrint: in project docs, design notes and code. A novelty check
that skips them is incomplete.

| source | how to search | typical content |
|---|---|---|
| project documentation and repos | docs sites, `docs/`/`book/` folders, design notes, RFCs and issues/PRs of the main ZK libraries and zkVMs | new gadgets, arithmetization tricks, PCS variants shipped before a paper |
| HackMD | `site:hackmd.io <phrasing>` | working notes, protocol sketches, benchmark write-ups |
| ethresear.ch | forum search + `site:ethresear.ch <phrasing>` | protocol proposals, folding/recursion ideas, soundness discussions |
| vendor technical blogs | `<phrasing> blog` restricted to the teams behind the baselines in `references/baselines/MANIFEST.md` | prover optimisations, new fields/PCS, benchmark claims |
| public audit reports | the auditor's published report index, the project's `audits/` folder | Fiat–Shamir and circuit pitfalls already known for a design |

Rules:

1. **Window**: the last 24 months for blogs, forums and HackMD (they are rarely superseded cleanly), all time for
   project docs and audit reports of the competitors marked in the matrix. Record the window in the log line.
2. **Provenance**: for every hit you keep, record the URL, the **access date** (YYYY-MM-DD) and an **archived
   copy** (a Wayback Machine snapshot; request one if none exists). Grey sources change or disappear; the archive
   link is what a reviewer can check.
3. **Citing**: a kept hit becomes a `@misc` entry with `url`, `urldate` and the archive link, checked by
   [bib-verify](../bib-verify/SKILL.md); if it cannot be verified it stays marked `needs verification`.
4. **Weight**: a grey source can make an idea `overlap` or `taken` just like a paper. It counts as prior art from
   its earliest verifiable date (archive snapshot, commit date), not from the date you found it.
5. Log grey hits with `sources: ...,grey` in the novelty line; `hits reviewed` counts them too.

## Pitfalls

- A concurrent ePrint published during your project is normal; record it with its date — reviewers accept
  "concurrent and independent" only if you can show when you knew.
- Do not trust search-engine summaries of a paper's content; read the paper.
- Title-only search misses papers that use a different name for the same object — always also run full-text.
