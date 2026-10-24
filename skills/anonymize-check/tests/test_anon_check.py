"""Tests for anon_check.py on small synthetic inputs (run: python3 -m pytest -q or python3 this_file)."""
# TOY: synthetic identities only ("Alice Example", "aexample")
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import anon_check as ac  # noqa: E402

DENY = ac.DenyList(["Alice Example", "aexample", "re:example\\s+univ(ersity)?"])

LEAKY_TEX = r"""\documentclass{llncs}
\begin{document}
\title{Toy}
\author{Alice Example}
\maketitle
In our earlier paper~\cite{a} we proved a bound.
See https://aexample.github.io/toy for code.
\end{document}
"""


def _kinds(findings):
    return {f.kind for f in findings}


def test_selftest_passes():
    assert ac.selftest() == 0


def test_tex_leaks_detected():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "main.tex"
        p.write_text(LEAKY_TEX)
        k = _kinds(ac.run([str(p)], DENY, []))
        assert {"tex-\\author", "first-person-self-cite", "deny-term"} <= k
        assert "url-deny-term" in k


def test_regex_deny_and_comment_downgrade():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "a.tex"
        p.write_text("% Example University internal note\nText from Example Univ.\n")
        fs = ac.run([str(p)], DENY, [])
        sev = sorted(f.severity for f in fs if f.kind == "deny-term")
        assert sev == ["HIGH", "MEDIUM"], sev


def test_allow_url():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "a.tex"
        p.write_text("\\url{https://github.com/thirdparty/lib}\n")
        assert "personal-host-url" in _kinds(ac.run([str(p)], DENY, []))
        assert "personal-host-url" not in _kinds(ac.run([str(p)], DENY, [r"github\.com/thirdparty"]))


def test_onchain_identifiers():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "a.md"
        addr = "0x" + "0" * 38 + "b2"
        p.write_text(f"Deployed at {addr} by toyteam.eth.\n"
                     f"Hash 0x{'cd' * 32}; null address 0x{'0' * 40}; mail me@x.eth; see www.eth.ch\n")
        fs = ac.run([str(p)], DENY, [])
        hits = {(f.kind, f.text.split()[0]) for f in fs if f.severity == "HIGH"}
        assert hits == {("eth-address", addr), ("ens-name", "toyteam.eth"), ("email", "me@x.eth")}, hits


def test_manifest_fields():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "Cargo.toml").write_text('[package]\nauthors = ["Toy <t@example.com>"]\nrepository = "https://example.com/r"\n')
        (d / "package.json").write_text('{\n  "author": "Toy",\n  "repository": {"url": "x"}\n}\n')
        (d / "other.toml").write_text('authors = ["Toy"]\n')
        fs = ac.run([str(d)], DENY, [])
        got = sorted((Path(f.file).name, f.kind) for f in fs if f.kind.startswith("manifest-"))
        assert got == [("Cargo.toml", "manifest-author"), ("Cargo.toml", "manifest-repository"),
                       ("package.json", "manifest-author"), ("package.json", "manifest-repository")], got
        (d / "Cargo.toml").write_text('[package]\nauthors = []\n')
        assert not [f for f in ac.run([str(d / "Cargo.toml")], DENY, []) if f.kind.startswith("manifest-")]


def test_notes_and_package_pages():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "a.tex"
        p.write_text("\\url{https://hackmd.io/ToyNote}\n\\url{https://crates.io/crates/toy}\n"
                     "\\url{https://www.npmjs.com/package/toy}\n")
        fs = ac.run([str(p)], DENY, [])
        assert sorted(f.kind for f in fs) == ["notes-host-url", "package-page-url", "package-page-url"]
        assert all(f.severity == "MEDIUM" for f in fs)


def test_allow_url_file():
    template = HERE.parent / "scripts" / "zk_allow_urls.example.txt"
    allow = ac.load_allow_url_file(str(template))
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "a.md"
        p.write_text("https://github.com/arkworks-rs/algebra\nhttps://www.github.com/Consensys/gnark\n"
                     "https://github.com/Consensys/other\nhttps://github.com/risc0-fork/x\n")
        flagged = [f.text.split()[0] for f in ac.run([str(p)], DENY, allow) if f.kind == "personal-host-url"]
        assert flagged == ["https://github.com/Consensys/other", "https://github.com/risc0-fork/x"], flagged


def test_embedded_figure_path():
    if not shutil.which("pdflatex"):
        return
    with tempfile.TemporaryDirectory() as td:
        figdir = Path(td) / "aexample_figs"
        figdir.mkdir()
        (figdir / "f.tex").write_text("\\documentclass{article}\\pagestyle{empty}\\begin{document}x\\end{document}\n")
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "f.tex"], cwd=figdir, capture_output=True)
        main = Path(td) / "m.tex"
        main.write_text("\\documentclass{article}\\usepackage{graphicx}\\begin{document}"
                        f"\\includegraphics{{{figdir / 'f.pdf'}}}\\end{{document}}\n")
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "m.tex"], cwd=td, capture_output=True)
        pdf = Path(td) / "m.pdf"
        if not pdf.exists():
            return
        fs = ac.run([str(pdf)], DENY, [])
        assert any(f.kind == "pdf-embedded-path" and f.severity == "HIGH" for f in fs), [f.fmt() for f in fs]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
