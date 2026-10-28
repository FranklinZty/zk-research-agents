#!/usr/bin/env python3
"""check_book_refs.py -- check every reference-book citation in the repository.

    python3 scripts/check_book_refs.py                  # scan the repository
    python3 scripts/check_book_refs.py FILE_OR_DIR ...  # scan selected paths
    python3 scripts/check_book_refs.py --dump-thaler-toc [PDF]   # Markdown TOC from the pinned PDF
    python3 scripts/check_book_refs.py --dump-cy24-toc [TEX]     # chapter/section list of CY24
    python3 scripts/check_book_refs.py --selftest       # offline

Citation formats (references/books/README.md):

  [CY24 §<section name>, <label>[, <label> ...]]
      every label must exist in snargs-book.tex at the pinned commit, and <section name> must be
      the title of the part, chapter, section or subsection that contains the label.
      Labels come from \\label{...} and from the boxed environments
      \\begin{ImportantTheorem|ImportantDefinition|ImportantConstruction}{title}{key}, whose
      label is theorem:key / definition:key / construction:key.
  [Thaler §<n>[.<m>[.<k>]], <title>]
      the number must be a chapter, section or subsection of the pinned PDF and <title> must be
      that unit's title (a word-level prefix of it is accepted). The TOC is extracted from the
      PDF: chapters and sections from the bookmarks, subsections from the numbered headings.

Without the cache (references/books/.cache/, filled by references/books/fetch.sh) the
corresponding checks are skipped with a notice. Thaler checks also need PyMuPDF.
Exit status: 0 clean (or skipped), 1 at least one bad citation.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "references", "books", ".cache")
CY24_TEX = os.path.join(CACHE, "hash-snargs", "snargs-book.tex")
CY24_COMMIT = "305fa3d9d19ee6dba135de64b3156d1760df8426"
THALER_PDF = os.path.join(CACHE, "thaler", "ProofsArgsAndZK.pdf")
THALER_SHA256 = "ef4e0fdbce01f5a0a4b79524cb372378dbf43f4688f6d768055a27580f2c18e6"

TEXT_EXT = {".md", ".py", ".js", ".tex", ".txt", ".sh", ".bib", ".json", ".yml", ".yaml"}

CY24_RE = re.compile(r"\[CY24 §(?P<sec>[^\]\n]+?), (?P<labels>[A-Za-z-]+:[^\s,\]]+(?:, [A-Za-z-]+:[^\s,\]]+)*)\]")
THALER_RE = re.compile(r"\[Thaler §(?P<num>\d+(?:\.\d+){0,2}), (?P<title>[^\]\n]+)\]")
ANY_RE = re.compile(r"\[(CY24|Thaler)\b[^\]\n]*\]")


# ------------------------------------------------------------------ helpers ---

def norm(s: str) -> str:
    """Comparable form of a title: TeX and punctuation removed, ASCII letters/digits only."""
    s = re.sub(r"\\(emph|textbf|textit|text)\{([^}]*)\}", r"\2", s)
    s = s.replace("\\ ", " ").replace("~", " ")
    s = re.sub(r"\\[A-Za-z]+", " ", s)                     # remaining macros
    s = unicodedata.normalize("NFKD", s)       # accents become combining marks: drop them;
    s = "".join(ch if ord(ch) < 128 else ("" if unicodedata.combining(ch) else " ") for ch in s).lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def title_matches(cited: str, actual: str) -> bool:
    c, a = norm(cited).split(), norm(actual).split()
    return bool(c) and a[: len(c)] == c


def repo_files(paths: list[str]) -> list[str]:
    if paths:
        out = []
        for p in paths:
            if os.path.isdir(p):
                for d, dirs, files in os.walk(p):
                    dirs[:] = [x for x in dirs if x not in {".git", ".cache", "node_modules"}]
                    out += [os.path.join(d, f) for f in files]
            else:
                out.append(p)
        return out
    try:
        r = subprocess.run(["git", "-C", ROOT, "ls-files", "-co", "--exclude-standard"],
                           capture_output=True, text=True, check=True)
        return [os.path.join(ROOT, f) for f in r.stdout.splitlines()]
    except Exception:
        return repo_files([ROOT])


def scan(files: list[str]):
    """Yield (path, line_no, kind, match_or_text)."""
    for f in files:
        if os.path.splitext(f)[1] not in TEXT_EXT or not os.path.isfile(f):
            continue
        if os.path.abspath(f) == os.path.abspath(__file__):
            continue  # this file documents the formats with placeholders
        try:
            lines = open(f, encoding="utf-8").read().splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(lines, 1):
            spans = []
            for m in CY24_RE.finditer(line):
                spans.append(m.span()); yield f, i, "cy24", m
            for m in THALER_RE.finditer(line):
                spans.append(m.span()); yield f, i, "thaler", m
            for m in ANY_RE.finditer(line):
                inside = any(a <= m.start() < b for a, b in spans)
                if not inside and "<" not in m.group(0):    # "<label>" placeholders are documentation
                    yield f, i, "malformed", m.group(0)


# --------------------------------------------------------------------- CY24 ---

ENV_PREFIX = {"ImportantTheorem": "theorem", "ImportantDefinition": "definition",
              "ImportantConstruction": "construction"}


def cy24_index(tex: str) -> dict[str, list[str]]:
    """label -> titles of the enclosing part, chapter, section, subsection."""
    ctx = {"part": "", "chapter": "", "section": "", "subsection": ""}
    order = ["part", "chapter", "section", "subsection"]
    idx: dict[str, list[str]] = {}
    for line in tex.splitlines():
        if line.lstrip().startswith("%"):
            continue
        m = re.match(r"\s*\\(part|chapter|section|subsection)\*?(?:\[[^\]]*\])?\{(.*)\}\s*$", line)
        if m:
            kind, title = m.groups()
            ctx[kind] = title
            for k in order[order.index(kind) + 1:]:
                ctx[k] = ""
        labels = re.findall(r"\\label\{([^}]*)\}", line)
        labels += [f"{ENV_PREFIX[e]}:{k}" for e, k in
                   re.findall(r"\\begin\{(Important(?:Theorem|Definition|Construction))\}\{.*?\}\{([^}]*)\}", line)]
        for lab in labels:
            idx[lab] = [t for t in (ctx[k] for k in order) if t]
    return idx


def check_cy24(m, idx) -> list[str]:
    errs = []
    sec = m.group("sec").strip()
    for lab in [x.strip() for x in m.group("labels").split(",")]:
        if lab not in idx:
            errs.append(f"label {lab!r} not found at commit {CY24_COMMIT[:7]}")
        elif not any(norm(sec) == norm(t) for t in idx[lab]):
            errs.append(f"label {lab!r} is not inside a unit titled {sec!r} (enclosing: {' / '.join(idx[lab])})")
    return errs


def cy24_outline(tex: str) -> list[tuple[str, str]]:
    out = []
    for line in tex.splitlines():
        m = re.match(r"\s*\\(part|chapter|section)\*?(?:\[[^\]]*\])?\{(.*)\}\s*$", line)
        if m and not line.lstrip().startswith("%"):
            out.append((m.group(1), m.group(2)))
    return out


# ------------------------------------------------------------------- Thaler ---

def _fitz():
    try:
        import pymupdf as fitz  # type: ignore
    except Exception:
        try:
            import fitz  # type: ignore
        except Exception:
            return None
    return fitz


def thaler_toc(pdf: str) -> dict[str, list[str]]:
    """number -> candidate titles (bookmark title and/or body heading)."""
    fitz = _fitz()
    doc = fitz.open(pdf)
    toc: dict[str, list[str]] = {}
    ch = sec = 0
    for level, title, _page in doc.get_toc():
        if level == 1:
            ch, sec = ch + 1, 0
            toc.setdefault(f"{ch}", []).append(title)
        elif level == 2:
            sec += 1
            toc.setdefault(f"{ch}.{sec}", []).append(title)
    num_re = re.compile(r"^(\d+\.\d+(?:\.\d+)?)$")
    for pno in range(doc.page_count):
        lines = []
        for b in doc[pno].get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                spans = [s for s in l["spans"] if s["text"].strip()]
                if spans:
                    lines.append((l["bbox"], spans))
        for bb, spans in lines:
            s0 = spans[0]
            m = num_re.match(s0["text"].strip())
            if not (m and ("Medi" in s0["font"] or "Bold" in s0["font"]) and s0["size"] > 11):
                continue
            size, parts = s0["size"], []
            for bb2, sp2 in lines:
                same_row = abs(bb2[1] - bb[1]) < 3
                below = 0 < bb2[1] - bb[1] < 2.6 * size and bb2[0] > bb[0] + 5
                # heading text is set in a bold ("Medi") face or a math face; run-in body text is not.
                # Same row: keep math sub/superscripts; a wrapped second line: heading size only.
                floor = 0.55 * size if same_row else 0.9 * size
                if same_row or below:
                    parts += [(bb2[1], s["bbox"][0], s["text"]) for s in sp2
                              if s is not s0 and s["size"] >= floor and "Regu" not in s["font"]]
            title = " ".join(t for _, _, t in sorted(parts)).strip()
            if title:
                toc.setdefault(m.group(1), []).append(title)
            else:
                toc.setdefault(m.group(1), [])
    return toc


def check_thaler(m, toc) -> list[str]:
    num, title = m.group("num"), m.group("title").strip()
    if num not in toc:
        return [f"§{num} does not exist in the pinned PDF"]
    if not toc[num]:
        return [f"§{num}: heading title could not be extracted; check {title!r} by hand"]
    if not any(title_matches(title, t) for t in toc[num]):
        return [f"§{num} is titled {toc[num][0]!r}, not {title!r}"]
    return []


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------- main ---

def run(paths, cy24_tex=CY24_TEX, thaler_pdf=THALER_PDF, out=sys.stdout) -> int:
    cites = list(scan(repo_files(paths)))
    n_cy = sum(k == "cy24" for _, _, k, _ in cites)
    n_th = sum(k == "thaler" for _, _, k, _ in cites)
    bad = 0
    idx = toc = None
    if os.path.isfile(cy24_tex):
        idx = cy24_index(open(cy24_tex, encoding="utf-8").read())
        head = os.path.join(os.path.dirname(cy24_tex), ".git")
        if os.path.isdir(head):
            r = subprocess.run(["git", "-C", os.path.dirname(cy24_tex), "rev-parse", "HEAD"],
                               capture_output=True, text=True)
            if r.stdout.strip() != CY24_COMMIT:
                print(f"WARN CY24 cache is at {r.stdout.strip()[:12]}, pinned {CY24_COMMIT[:12]}; "
                      "run references/books/fetch.sh cy24", file=out)
    else:
        print(f"SKIP CY24: no cache at {os.path.relpath(cy24_tex, ROOT)} "
              f"({n_cy} citations unchecked); run references/books/fetch.sh cy24", file=out)
    if os.path.isfile(thaler_pdf):
        if _fitz() is None:
            print(f"SKIP Thaler: PyMuPDF not installed ({n_th} citations unchecked); pip install pymupdf", file=out)
        else:
            if sha256(thaler_pdf) != THALER_SHA256:
                print("WARN Thaler PDF sha256 differs from the pinned one; numbering may have moved", file=out)
            toc = thaler_toc(thaler_pdf)
    else:
        print(f"SKIP Thaler: no cache at {os.path.relpath(thaler_pdf, ROOT)} "
              f"({n_th} citations unchecked); run references/books/fetch.sh thaler", file=out)
    for f, i, kind, m in cites:
        where = f"{os.path.relpath(f, ROOT)}:{i}"
        if kind == "malformed":
            print(f"FAIL {where}: malformed book citation {m!r}", file=out); bad += 1
        elif kind == "cy24" and idx is not None:
            for e in check_cy24(m, idx):
                print(f"FAIL {where}: {m.group(0)} -- {e}", file=out); bad += 1
        elif kind == "thaler" and toc is not None:
            for e in check_thaler(m, toc):
                print(f"FAIL {where}: {m.group(0)} -- {e}", file=out); bad += 1
    print(f"checked {n_cy} CY24 and {n_th} Thaler citations"
          f"{'' if idx is not None else ' (CY24 skipped)'}{'' if toc is not None else ' (Thaler skipped)'}: "
          f"{bad} problem(s)", file=out)
    return 1 if bad else 0


def dump_thaler(pdf: str) -> None:
    toc = thaler_toc(pdf)
    key = lambda k: [int(x) for x in k.split(".")]
    for k in sorted(toc, key=key):
        depth = k.count(".")
        titles = toc[k]   # chapters/sections: bookmark first; subsections: body heading only
        title = titles[0] if titles else "(title not extracted: contains math, read the heading)"
        title = re.sub(r":(?=\S)", ": ", re.sub(r"\s+", " ", title))
        print(f"{'  ' * depth}- {k} {title}")


def selftest() -> int:
    tex = "\n".join([
        r"\part{What are Cryptographic Proofs?}",
        r"\chapter{The random oracle model}",
        r"\label{chapter:what-is-rom}",
        r"\section{Non-adaptive vs.\ adaptive security}",
        r"\label{section:non-adaptive-security}",
        r"\begin{lemma}\label{lemma:toy}",
        r"% \label{lemma:commented-out}",
        r"\chapter{Merkle commitment scheme}",
        r"\begin{ImportantTheorem}{}{toy-binding}",
    ])
    idx = cy24_index(tex)
    ok = True

    def expect(cond, msg):
        nonlocal ok
        print(("ok   " if cond else "FAIL ") + msg)
        ok &= bool(cond)

    expect("lemma:toy" in idx and "lemma:commented-out" not in idx, "CY24 labels parsed, comments ignored")
    expect(idx.get("theorem:toy-binding") == ["What are Cryptographic Proofs?", "Merkle commitment scheme"],
           "boxed environment yields theorem:<key> with its chapter")
    good = CY24_RE.search("see [CY24 §Non-adaptive vs. adaptive security, lemma:toy].")
    expect(good and not check_cy24(good, idx), "CY24 citation with matching section passes")
    multi = CY24_RE.search("[CY24 §The random oracle model, chapter:what-is-rom, lemma:toy]")
    expect(multi and not check_cy24(multi, idx), "several labels in one citation")
    wrong_sec = CY24_RE.search("[CY24 §Merkle commitment scheme, lemma:toy]")
    expect(wrong_sec and check_cy24(wrong_sec, idx), "CY24 label in another chapter fails")
    missing = CY24_RE.search("[CY24 §The random oracle model, lemma:nope]")
    expect(missing and check_cy24(missing, idx), "missing CY24 label fails")
    toc = {"5": ["Publicly Verifiable, Non-interactive Arguments via Fiat-Shamir"],
           "5.2": ["The Fiat-Shamir Transformation"], "12": ["-Protocols and Commitments"],
           "12.2.1": ["Σ-Protocols"], "4.2": []}
    t = lambda s: THALER_RE.search(s)
    expect(not check_thaler(t("[Thaler §5.2, The Fiat–Shamir Transformation]"), toc), "Thaler title match (dash variants)")
    expect(not check_thaler(t("[Thaler §5, Publicly Verifiable]"), toc), "Thaler title prefix accepted")
    expect(not check_thaler(t("[Thaler §12.2.1, Σ-Protocols]"), toc), "Thaler subsection with a Greek letter")
    expect(check_thaler(t("[Thaler §5.2, Random Oracle Model]"), toc), "Thaler wrong title fails")
    expect(check_thaler(t("[Thaler §5.9, Anything]"), toc), "Thaler missing number fails")
    expect(check_thaler(t("[Thaler §4.2, First Application]"), toc), "Thaler unextracted title is flagged")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "x.md")
        open(p, "w", encoding="utf-8").write(
            "ok [CY24 §The random oracle model, chapter:what-is-rom]\n"
            "bad [CY24 lemma:toy]\nplaceholder [CY24 §<section name>, <label>]\n"
            "[Thaler §5.2, The Fiat-Shamir Transformation]\n")
        kinds = [k for _, _, k, _ in scan([p])]
        expect(kinds == ["cy24", "malformed", "thaler"], "scanner finds citations, flags malformed, skips placeholders")
        texp = os.path.join(d, "book.tex")
        open(texp, "w").write(tex)
        sink = open(os.devnull, "w")
        expect(run([p], cy24_tex=texp, thaler_pdf=os.path.join(d, "none.pdf"), out=sink) == 1,
               "run() fails on the malformed citation, skips Thaler without a cache")
        open(p, "w").write("[CY24 §The random oracle model, chapter:what-is-rom]\n")
        expect(run([p], cy24_tex=os.path.join(d, "none.tex"), thaler_pdf=os.path.join(d, "none.pdf"), out=sink) == 0,
               "no cache: checks skipped, exit 0")
    print("selftest:", "all checks passed" if ok else "FAILED")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dump-thaler-toc", nargs="?", const=THALER_PDF, metavar="PDF")
    ap.add_argument("--dump-cy24-toc", nargs="?", const=CY24_TEX, metavar="TEX")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.dump_thaler_toc:
        if _fitz() is None:
            print("PyMuPDF is required for --dump-thaler-toc", file=sys.stderr)
            return 2
        dump_thaler(a.dump_thaler_toc)
        return 0
    if a.dump_cy24_toc:
        for kind, title in cy24_outline(open(a.dump_cy24_toc, encoding="utf-8").read()):
            print({"part": "", "chapter": "- ", "section": "  - "}[kind] + (f"**{title}**" if kind == "part" else title))
        return 0
    return run(a.paths)


if __name__ == "__main__":
    sys.exit(main())
