---
name: bib-verify
description: Verify every BibTeX entry against IACR ePrint, Crossref/DataCite and DBLP (and @misc URL sources, or URL-only @book entries such as open books, against the live URL + Wayback Machine) and flag fabricated, garbled or placeholder references. Use before any draft leaves the machine, after any agent adds citations, and as the P1 and P8 gate item.
---

# bib-verify

A fabricated reference is a research-integrity failure, not a typo. Typical LLM-era failure modes seen in
practice: invented co-author lists on a real paper; a placeholder like `{Chen and others}` + a journal name
propping up a row of a comparison table and a "nobody has done X" claim; a key that points at a *different*
paper by the same group; an ePrint number written from memory that belongs to another paper. When this repo's
own reading lists were drafted from memory, the verifier caught three such errors out of ~110 entries.

## Procedure

1. Run the checker (network needed; polite 1 req/s):
   ```bash
   python3 skills/bib-verify/scripts/verify_bib.py refs.bib --json bib-verify.json > bib-verify-report.md
   ```
   Resolution order: ePrint id (from `eprint=`, `url=`, `howpublished=`...) → OAI record; `doi=` → Crossref,
   then DataCite (Zenodo/LIPIcs/arXiv DOIs); `@misc`/`@online` with a URL and no ePrint id/DOI → URL-source
   check (below); otherwise a title search (DBLP if it answers, else Crossref). A `@book` with a `url`, no
   ePrint id and no DOI that the title search does **not** find (e.g. a book published from a Git repository,
   such as the CY24 entry in [references/books/README.md](../../references/books/README.md)) then goes through
   the same URL-source check; its detail starts with `@book via URL (title search: …)` so the report shows that
   no publisher record was found. A `@book` that the search does find keeps the record path.
2. Triage every non-`VERIFIED` row by hand:
   | status | meaning | action |
   |---|---|---|
   | `MISMATCH` | the id/DOI resolves to a *different* title or author set | fix the id or the metadata; if the cited claim was about the other paper, re-read and re-check the sentence that cites it |
   | `NOT_FOUND` | nothing plausible exists | treat as fabricated: delete, or find the real source and re-cite; re-check every sentence that relied on it |
   | `WEAK` | similar title only | open the landing page, compare authors/year/venue manually |
   | `NEEDS_VERIFICATION` | URL source (needs verification): unreachable, no Wayback snapshot, or no access date | archive the page, add `archiveurl=` and `urldate=`, re-run; if the page is gone and never archived, find a citable version or drop the citation |
   | `UNCHECKED` | offline / service error | re-run later; never ship with UNCHECKED rows |
3. URL sources (gray literature: project docs, HackMD notes, ethresear.ch posts, vendor blogs, audit reports —
   see the gray-literature pass in [`eprint-search`](../eprint-search/SKILL.md)). Such a source counts as
   `VERIFIED` only if **all three** hold:
   - the URL answers (HEAD, GET fallback; `--url-timeout`, default 10 s per request);
   - a Wayback snapshot exists — an explicit `web.archive.org/web/...` link in `archiveurl=` / `note=` /
     `howpublished=`, else the archive.org availability API finds one;
   - an access date is recorded: `urldate = {YYYY-MM-DD}` or `note = {Accessed YYYY-MM-DD}`.

   ```bibtex
   @misc{toy-blog,
     author = {Toy Author}, title = {A Toy Note on Sum-Check Batching}, year = {2026},
     url = {https://blog.example.org/toy-sumcheck}, urldate = {2026-01-15},
     archiveurl = {https://web.archive.org/web/20260115000000/https://blog.example.org/toy-sumcheck},
   }
   ```
   A failing URL source is `NEEDS_VERIFICATION`, not `NOT_FOUND`: blogs are not in DBLP/Crossref, so absence there
   is not evidence of fabrication — but it still blocks the gate. Authors and title of URL sources (and of
   URL-only books) are **not** machine-checked; compare them with the archived page by hand.

   ```bibtex
   @book{ToyBook2024,
     author = {Toy, Ada}, title = {Building Toy Proofs from Toy Hashes}, year = {2024},
     url = {https://github.example.org/toy-snargs-book}, urldate = {2026-10-27},
   }
   ```
4. Lint flags (placeholder authors, `and others` only, missing year, `% UNVERIFIED` marker, duplicate titles) must
   be cleared too.
5. For every *changed* entry, grep the paper for its key and re-read the citing sentence: a wrong reference often
   props up a wrong claim (a comparison row, a novelty statement, a parameter).
6. Record the run in `LITERATURE.md` (date, counts) and keep `bib-verify-report.md` next to `refs.bib`; the
   `phase-gate` script checks that the report is newer than the bib and clean.

## Rules

- Prefer the published version (DOI) for the final paper; keep the ePrint id in `eprint=` so it can be re-checked.
- If a blog/HackMD result was later written up on ePrint or at a venue, cite that version; keep the URL source
  only for content that exists nowhere else.
- Never "fill in" missing authors from memory. Copy from the ePrint/DOI landing page.
- Anything added without checking gets a `% UNVERIFIED` line directly above the entry until verified.
- Venue strings are not machine-verified; check them on the DOI landing page.
- Offline: `--offline` still runs the static lint; the gate stays closed until an online run passes.

## Files

- `scripts/verify_bib.py` — dependency-free checker (`--selftest`, `--selftest-online`, `--only k1,k2`, `--offline`,
  `--url-timeout`). `--selftest` is fully offline (URL, Wayback and title-search lookups are injected fakes).
- `tests/test_verify_bib.py` — pytest, offline: the @book URL fallback (found / not found / unreachable / no
  snapshot) and the self-test.
