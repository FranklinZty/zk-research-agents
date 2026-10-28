# Reference books

Two books are the default sources for definitions and security analysis in this repository.
**This repository contains no part of either book**: no LaTeX source, PDF, figure, class file,
macro, page image or copied paragraph. `fetch.sh` downloads pinned copies into the git-ignored
`references/books/.cache/`; everything committed here (maps, glossary, tables of contents,
skills) is written in our own words and points into the books by section name and label.

| short name | book | use it first for |
|---|---|---|
| **CY24** | A. Chiesa, E. Yogev, *Building Cryptographic Proofs from Hash Functions* | security definitions (soundness, knowledge soundness, ZK, state restoration, RBR, special soundness), the random oracle model, Merkle commitments, Fiat–Shamir / Kilian / Micali / BCS / COS with explicit error bounds, security levels |
| **Thaler** | J. Thaler, *Proofs, Arguments, and Zero-Knowledge* | probabilistic-proof design (sum-check, GKR, PCP/IOP/MIP, FRI), front ends, discrete-log and pairing-based polynomial commitments (Bulletproofs, KZG, Dory), linear PCPs and Groth16-style SNARKs, composition and folding |

Division of labour: when both books treat a notion, CY24 is authoritative for the *definition* and for
hash-based security analysis; Thaler is authoritative for algebraic constructions and protocol design.
CY24 proves everything in the pure random oracle model; never transfer one of its bounds to a KZG/IPA/AGM
setting. Topics neither book covers (lookup arguments, folding beyond Nova, STIR/WHIR internals,
proximity gaps, Binius, small-field soundness) come from the original papers, cited as
"source: other" with a checked ePrint id or DOI. The canonical term list is [GLOSSARY.md](GLOSSARY.md);
chapter navigation is in [hash-snargs/MAP.md](hash-snargs/MAP.md) and [thaler/MAP.md](thaler/MAP.md).

## Pinned versions

### CY24

| field | value |
|---|---|
| source | <https://github.com/hash-based-snargs-book/hash-based-snargs-book> |
| authors | Alessandro Chiesa, Eylon Yogev |
| licence | CC BY-SA 4.0 (book and source) |
| pinned version | v1.2, commit `305fa3d9d19ee6dba135de64b3156d1760df8426` (commit message "Version 1.2", 2026-03-25) |
| fetched | 2026-10-27 |
| cache path | `references/books/.cache/hash-snargs/` (`snargs-book.tex` is the single source file) |

### Thaler

| field | value |
|---|---|
| download URL | <https://people.cs.georgetown.edu/jthaler/ProofsArgsAndZK.pdf> (linked from <https://people.cs.georgetown.edu/jthaler/ProofsArgsAndZK.html>) |
| author | Justin Thaler |
| licence | free download from the author's page; **not** an open licence. No LaTeX source is published. |
| PDF date | July 18, 2023 (title page; server `Last-Modified: Tue, 18 Jul 2023`) |
| downloaded | 2026-10-27 |
| sha256 | `ef4e0fdbce01f5a0a4b79524cb372378dbf43f4688f6d768055a27580f2c18e6` |
| size / pages | 5,377,045 bytes / 329 PDF pages (printed page = PDF page − 1) |
| structure | 19 chapters, 85 sections, 94 numbered subsections (verified TOC: [`../textbooks/toc/thaler-proofs-arguments-and-zero-knowledge.md`](../textbooks/toc/thaler-proofs-arguments-and-zero-knowledge.md)) |
| published version | Foundations and Trends in Privacy and Security 4(2–4):117–660, 2022, DOI `10.1561/3300000030` (verified with `skills/bib-verify` against Crossref, 2026-10-27). Section numbers in this repository refer to the **pinned PDF**, not to the published version. |
| cache path | `references/books/.cache/thaler/ProofsArgsAndZK.pdf` |

If the author replaces the PDF, `fetch.sh thaler` stops with a sha256 mismatch. Then: re-extract the
table of contents (`python3 scripts/check_book_refs.py --dump-thaler-toc FILE`), rewrite the TOC file,
re-run `scripts/check_book_refs.py` over the repository, and only then update the pinned sha256 here
and in `fetch.sh`.

```bash
references/books/fetch.sh all          # both books into references/books/.cache/
references/books/fetch.sh --selftest   # offline check of the script itself
python3 scripts/check_book_refs.py     # every CY24 / Thaler citation in the repository resolves
```

## Citation format

- **CY24**: `[CY24 §<section name>, <LaTeX label>]`, e.g.
  `[CY24 §Merkle commitment scheme, lemma:mt-binding]`. The section name is the name of the chapter or
  section that contains the label; the label must exist at the pinned commit (labels are more stable than
  numbers across versions). Labels of boxed results are the environment prefix plus the box key
  (`theorem:bcs-soundness`, `definition:narg-adaptive-soundness`, `construction:fs-for-sp`).
- **Thaler**: `[Thaler §<number>, <section title>]`, e.g. `[Thaler §15.2, KZG: Univariate Polynomial
  Commitments from Pairings and a Trusted Setup]`. The number is a chapter, section or subsection of the
  pinned PDF; the title must be that unit's title (a shortened prefix of it is accepted), so a reader can
  still find the place if numbering moves.
- Anything else: "source: other" plus an ePrint id or DOI that was actually checked; otherwise
  `needs verification`.

`scripts/check_book_refs.py` checks both formats against the cached copies.

## Paraphrase-only rules

1. Write definitions, statements and proofs **in our own words**. Mathematical formulas and factual
   results (an error bound, a parameter condition) may be stated; the prose around them may not be copied.
2. CY24: at most **one sentence** of direct quotation per place, in quotation marks, with the citation.
3. Thaler: **no** direct quotation at all.
4. Never commit files from the cache, screenshots of pages, or figures redrawn from the books. Notation
   macros for our papers are defined in `templates/paper/`, not taken from `snargs-book.cls`.
5. Before committing, `git ls-files references/books` must list only this README, `fetch.sh`,
   `GLOSSARY.md` and the two `MAP.md` files.

## BibTeX

CY24, as given in the book's own README:

```bibtex
@book{ChiesaYogev2024,
  author = {Chiesa, Alessandro and Yogev, Eylon},
  title = {Building Cryptographic Proofs from Hash Functions},
  url = {https://github.com/hash-based-snargs-book},
  year = {2024},
}
```

`skills/bib-verify` resolves URL-only sources through its URL path only for `@misc`/`@online` entries; as a
`@book` it falls back to a title search and reports `NOT_FOUND`. For a project `refs.bib`, either keep the
entry as above and mark it checked by hand (URL answers; Wayback snapshot
`https://web.archive.org/web/20260908092256/https://github.com/hash-based-snargs-book`), or verify a `@misc`
copy with `urldate`, which `bib-verify` reported `VERIFIED` on 2026-10-27.

Thaler, published version (verified with `skills/bib-verify`, Crossref, 2026-10-27):

```bibtex
@article{Thaler2022,
  author = {Thaler, Justin},
  title = {Proofs, Arguments, and Zero-Knowledge},
  journal = {Foundations and Trends in Privacy and Security},
  volume = {4},
  number = {2--4},
  pages = {117--660},
  year = {2022},
  doi = {10.1561/3300000030},
}
```
