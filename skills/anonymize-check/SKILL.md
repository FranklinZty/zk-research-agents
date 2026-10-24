---
name: anonymize-check
description: Use before every double-blind submission, supplementary upload, anonymous artifact mirror or rebuttal attachment. Scans .tex/.bib/code/zip/PDF (text, metadata, embedded paths, compressed object streams) for author names, first-person self-citations, personal code-host URLs, e-mails, local paths, acknowledgements and funding lines, on-chain identifiers (Ethereum addresses, ENS names) and package-manifest author fields, using a configurable deny-list and a third-party URL allow-list.
---

# Anonymize check

## Script

`scripts/anon_check.py` (standard library only; uses PyMuPDF or poppler if present).

```bash
# 1. keep a private deny-list (never commit a filled-in one publicly)
cp skills/anonymize-check/scripts/denylist.example.txt paper/.denylist.txt   # then edit
# 1b. third-party URL allow-list (review it: drop any org you are affiliated with)
cp skills/anonymize-check/scripts/zk_allow_urls.example.txt paper/.allow_urls.txt

# 2. scan sources, the built PDF, the supplementary zip, the artifact directory
python3 skills/anonymize-check/scripts/anon_check.py paper/ paper/main.pdf \
        supplementary.zip artifact/ --deny-file paper/.denylist.txt \
        --allow-url-file paper/.allow_urls.txt --allow-url 'github\.com/<third-party-org>/'

# 3. self-test (synthetic sample; must print PASS)
python3 skills/anonymize-check/scripts/anon_check.py --selftest
```

Exit status 1 if any HIGH finding. `--json` for machine-readable output,
`--min-severity MEDIUM` to reduce noise. ZK papers cite many third-party libraries;
without an allow-list every `github.com` link is a MEDIUM finding and real leaks drown
in the noise. An allowed URL is skipped entirely, so never allow your own org.

## What it flags

| severity | finding |
|---|---|
| HIGH | deny-list term in text/code/filename/PDF bytes; e-mail; local path (`/home/<u>`, `/Users/<u>`, `C:\Users\<u>`); non-anonymous `\author`/`\institute`/`\thanks`/`\email`; acknowledgements section; PDF Author metadata; embedded figure path (`PTEX.FileName`) containing a username or deny term; `.git` inside an archive; URL containing a deny term; Ethereum address (`0x` + 40 hex, except the zero address); ENS name (`*.eth`); non-empty `authors`/`author`/`repository` field in `Cargo.toml` or `package.json` |
| MEDIUM | first-person self-citation ("our previous work", "we previously showed", "our paper~\cite"); personal code-host URL (github/gitlab/.github.io/...) not in the allow-list; `hackmd.io` link; crates.io / npmjs.com package page not in the allow-list; funding statement; PDF Title/Subject/Keywords metadata; `.git` directory in an artifact folder; hits inside comments (downgraded one level) |
| LOW | deny term inside `.bib` (allowed: self-citations stay in the bibliography with real authors, referred to in the third person); "camera-ready"/"de-anonymised" wording; Creator/Producer metadata (informational) |

## Manual checks the script cannot do

- Self-citations are written in the third person ("Example et al. [12] showed")
  and critiqued like any other work; not omitted, not "anonymised" in the bib.
- No "blinded" citation that is obviously the authors' own when a third-person
  citation would do (follow the venue's policy; IACR generally prefers third person).
- Supplementary/artifact README avoids "our prior paper", "same codebase as",
  "inherited from our earlier implementation".
- Anonymous mirrors (e.g. anonymous.4open.science) are refreshed after the last
  push, and each file URL returns HTTP 200 (a private source repository can make the
  mirror return 403). Check with `curl -sI`.
- Figures: no screenshots with usernames, terminal prompts, or window titles.
- Experiment logs in the artifact: hostnames, IPs, usernames stripped.
- Deployed verifier contracts and deployer addresses: a contract address, a block
  explorer link or a gas measurement tied to a specific transaction leads to the
  deployer's account and its history. Benchmark gas on a local devnet with a fresh
  key, or redeploy from a throwaway account before submission.
- Published packages (crates.io, npm, PyPI): the owners/maintainers page names the
  authors even when the paper links only the package. Cite the version via the
  anonymous mirror, or leave the package unnamed until camera-ready.
- Overleaf/Git history is not shared with reviewers.
- Submission form fields (conflicts, abstract) are separate from the PDF; the PDF
  itself must be anonymous.

## Remediation snippets

```latex
% Empty PDF metadata (hyperref)
\hypersetup{pdfauthor={},pdftitle={},pdfsubject={},pdfkeywords={},pdfcreator={},pdfproducer={}}
% Avoid embedding figure source paths (pdfTeX)
\pdfsuppressptexinfo=-1   % place in the preamble (pdfTeX >= 1.40.15)
```

```bash
# strip metadata from a finished PDF (qpdf/exiftool if available)
exiftool -all:all= -overwrite_original main.pdf && qpdf --linearize main.pdf main_clean.pdf
# zip an artifact without VCS data
git archive --format=zip -o artifact.zip HEAD   # or: zip -r artifact.zip artifact -x '*.git*'
```

Record the final clean run (command + summary line + PDF sha256) in `SUBMISSION.md`.
