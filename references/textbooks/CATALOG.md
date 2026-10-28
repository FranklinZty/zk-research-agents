# Textbook catalog

Bibliographic entries + topic tags + the ZK paper types that typically need each book.
**No PDFs are stored in this repository.** Each row links to a `toc/<slug>.md` file that holds only the
table of contents (extracted from a locally owned copy with
`skills/textbook-index/scripts/extract_toc.py`, or recalled from the publisher's public TOC and then
marked `TOC from public source`).

TOC source legend: **src** = generated from the pinned LaTeX source (labels, no page numbers) · **vf** = verified
against a pinned PDF (bookmarks + numbered headings, printed page numbers) · **bm** = embedded PDF bookmarks (pages = PDF physical pages) · **txt** = parsed from the
printed contents pages (pages = printed page numbers; OCR noise possible) · **pub** = chapter-level TOC from a
public source (verify before citing chapter numbers) · **stub** = bibliographic entry only (scanned / DjVu
without outline; fill from the publisher page) · **none** = no TOC file (catalogued only).

Use codes (ZK paper types): **PT** = protocol / theory (PIOPs, PCS, soundness proofs) · **SY** = systems /
implementation (provers, NTT/MSM, fields) · **AC** = applications / circuits (arithmetisation, gadgets) · ALL.

Entries marked `needs verification` were added without checking edition, year, venue or identifier; run
them through `skills/bib-verify` before citing, and fill in the missing fields only from the verified source.

## A. Algebra, finite fields, number theory

| slug | book | TOC | topic tags | use |
|---|---|---|---|---|
| [dummit-abstract-algebra](toc/dummit-abstract-algebra.md) | D. S. Dummit, R. M. Foote, *Abstract Algebra* (3rd ed., Wiley) | txt | groups, rings, modules, fields, Galois theory, finite fields, polynomial rings, CRT | ALL |
| [artin-algebra](toc/artin-algebra.md) | M. Artin, *Algebra* (2nd ed., Pearson) | bm | linear algebra, groups, bilinear forms, rings, factoring, Galois theory | ALL |
| [howie-fields-and-galois-theory](toc/howie-fields-and-galois-theory.md) | J. M. Howie, *Fields and Galois Theory* (Springer SUMS) | txt | field extensions, splitting fields, finite fields, Galois correspondence | PT, SY (extension fields) |
| [lidl-niederreiter-finite-fields](toc/lidl-niederreiter-finite-fields.md) | R. Lidl, H. Niederreiter, *Finite Fields* (Encyclopedia Math. Appl. 20) | pub | finite field structure, polynomials, factorisation, roots of unity, exponential sums, permutation polynomials | ALL |
| [ireland-a-classical-introduction-to-modern-number-theory](toc/ireland-a-classical-introduction-to-modern-number-theory.md) | K. Ireland, M. Rosen, *A Classical Introduction to Modern Number Theory* (GTM 84) | txt | congruences, primitive roots, finite fields, equations over finite fields, elliptic curves (intro) | SY (field / curve choice), PT |
| [schmidt-combinatorics-and-finite-fields](toc/schmidt-combinatorics-and-finite-fields.md) | K.-U. Schmidt, A. Winterhof (eds.), *Combinatorics and Finite Fields* (Radon Series 23) | bm | Weil sums, permutation polynomials, pseudorandomness, incidences in positive characteristic | (background) |

## B. Linear algebra and combinatorics

| slug | book | TOC | topic tags | use |
|---|---|---|---|---|
| [meyer-matrix-analysis-and-applied-linear-algebra](toc/meyer-matrix-analysis-and-applied-linear-algebra.md) | C. D. Meyer, *Matrix Analysis and Applied Linear Algebra* (SIAM) | bm | rank, vector spaces, DFT/FFT, Vandermonde, determinants | SY (NTT), AC (R1CS matrices) |
| [merris-combinatorics](toc/merris-combinatorics.md) | R. Merris, *Combinatorics* (2nd ed., Wiley) | bm | counting, inclusion–exclusion, permutations and cycles, generating functions, codes and designs | PT (union / counting bounds) |
| [west-introduction-to-graph-theory-with-solution-manual](toc/west-introduction-to-graph-theory-with-solution-manual.md) | D. B. West, *Introduction to Graph Theory* (2nd ed.) | bm | paths, cycles, trees, matchings, connectivity | AC (copy-constraint cycles, wiring graphs) |

## C. Cryptography and proof systems

The two pinned reference books (CY24, Thaler) are fetched by `references/books/fetch.sh`; pinning, licences,
citation format and the paraphrase-only rule are in [`references/books/README.md`](../books/README.md). The other
rows are not in the local corpus (TOC from public source).

| slug | book | TOC | topic tags | use |
|---|---|---|---|---|
| [chiesa-yogev-building-cryptographic-proofs-from-hash-functions](toc/chiesa-yogev-building-cryptographic-proofs-from-hash-functions.md) | A. Chiesa, E. Yogev, *Building Cryptographic Proofs from Hash Functions* (v1.2, CC BY-SA 4.0; pinned commit `305fa3d`) | src | ROM, FS, Merkle, BCS, concrete security; state restoration, RBR and special soundness, Micali, COS | PT, SY |
| [thaler-proofs-arguments-and-zero-knowledge](toc/thaler-proofs-arguments-and-zero-knowledge.md) | J. Thaler, *Proofs, Arguments, and Zero-Knowledge* (author's PDF of July 18, 2023, pinned by sha256; published as FnT Privacy and Security 4(2–4), 2022, DOI 10.1561/3300000030) | vf | sum-check, GKR, Fiat–Shamir, front ends, PCP/IOP, FRI, polynomial commitments (IPA, KZG, Dory), linear PCPs, SNARK recursion and folding | ALL |
| [boneh-shoup-graduate-course-in-applied-cryptography](toc/boneh-shoup-graduate-course-in-applied-cryptography.md) | D. Boneh, V. Shoup, *A Graduate Course in Applied Cryptography* (free draft) | pub | hashing, pairings, Sigma protocols, proving properties in zero-knowledge | PT |
| [katz-lindell-introduction-to-modern-cryptography](toc/katz-lindell-introduction-to-modern-cryptography.md) | J. Katz, Y. Lindell, *Introduction to Modern Cryptography* (3rd ed.) | pub | definitions, reductions, hash functions, number-theoretic assumptions | PT |

## D. Coding theory, Reed–Solomon codes and proximity (public material; no TOC file)

FRI/STIR/WHIR-style soundness statements are proved in papers, not textbooks: cite the paper for the
proximity parameter regime (unique decoding, Johnson bound, conjectured list-decoding), and a textbook
only for the underlying coding facts.

| slug | entry | TOC | topic tags | use |
|---|---|---|---|---|
| — | V. Guruswami, A. Rudra, M. Sudan, *Essential Coding Theory* (draft book, freely available) — `needs verification` (draft date / version) | none | Reed–Solomon codes, distance, Johnson bound, list decoding | PT |
| — | R. M. Roth, *Introduction to Coding Theory* (Cambridge University Press) — `needs verification` (edition / year) | none | linear codes, GRS codes, decoding, bounds | PT |
| — | F. J. MacWilliams, N. J. A. Sloane, *The Theory of Error-Correcting Codes* (North-Holland) — `needs verification` (year) | none | linear codes, weight enumerators, MDS and Reed–Solomon codes | PT |
| — | V. Guruswami, *Algorithmic Results in List Decoding* (survey monograph) — `needs verification` (venue / year) | none | list decoding of RS codes, Johnson bound | PT |
| — | V. Guruswami, M. Sudan, "Improved decoding of Reed–Solomon and algebraic-geometry codes" — `needs verification` (venue / year) | none | RS list decoding up to the Johnson radius | PT |
| — | E. Ben-Sasson, I. Bentov, Y. Horesh, M. Riabzev, "Fast Reed–Solomon Interactive Oracle Proofs of Proximity" (FRI) — `needs verification` (venue / year) | none | FRI, RS proximity testing | PT, SY |
| — | E. Ben-Sasson, D. Carmon, Y. Ishai, S. Kopparty, S. Saraf, "Proximity Gaps for Reed–Solomon Codes" (ePrint 2020/654) — `needs verification` | none | proximity gaps, correlated agreement, batched FRI soundness | PT |
| — | E. Ben-Sasson, L. Goldberg, S. Kopparty, S. Saraf, "DEEP-FRI: Sampling Outside the Box Improves Soundness" — `needs verification` (venue / identifier) | none | out-of-domain sampling, FRI soundness beyond unique decoding | PT |
| — | G. Arnon, A. Chiesa, G. Fenzi, E. Yogev, "STIR: Reed–Solomon Proximity Testing with Fewer Queries" — `needs verification` (venue / identifier) | none | rate-shifting proximity tests, query complexity | PT, SY |
| — | G. Arnon, A. Chiesa, G. Fenzi, E. Yogev, "WHIR: Reed–Solomon Proximity Testing with Super-Fast Verification" — `needs verification` (venue / identifier) | none | constrained RS proximity, multilinear PCS from RS codes | PT, SY |

## Adding a book

```bash
python3 skills/textbook-index/scripts/extract_toc.py /path/to/my/books --out-dir references/textbooks/toc --summary /tmp/toc.json
```

Then add one row here (slug, bibliographic entry, TOC code, tags, use) and, if the book fills a gap,
a line in [TOPIC-MAP.md](TOPIC-MAP.md). Never commit the PDF; never paste body text. Do not invent
bibliographic fields: if unsure, give title + authors and mark `needs verification`.
