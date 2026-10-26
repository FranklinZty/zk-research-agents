"""Smoke tests for the figures toolkit (run: python3 -m pytest figures/tests -q)."""
import importlib.util
import pathlib
import subprocess
import sys

import pytest

FIG = pathlib.Path(__file__).resolve().parents[1]
PY = sys.executable


def _load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # @dataclass needs the module registered
    spec.loader.exec_module(mod)
    return mod


def test_palette_selfcheck():
    subprocess.run([PY, str(FIG / "style" / "palette.py")], check=True)


def test_harvester_selftest():
    pytest.importorskip("fitz")
    subprocess.run([PY, str(FIG / "harvester" / "harvest.py"), "--selftest"], check=True)


def test_gallery_selftest():
    subprocess.run([PY, str(FIG / "harvester" / "gallery.py"), "--selftest"], check=True)


@pytest.mark.parametrize("script", sorted((FIG / "templates").glob("p[0-9][0-9]_*.py")), ids=lambda p: p.stem)
def test_template_renders(script, tmp_path):
    import matplotlib
    matplotlib.use("Agg")
    mod = _load(script)
    paths = mod.make(venue="lncs", outdir=tmp_path)
    assert paths and all(pathlib.Path(p).stat().st_size > 0 for p in paths)


def test_catalog_references_exist():
    # every template named in PATTERNS.md / README.md exists, and retired ones are gone
    import re
    names = set()
    for doc in ("PATTERNS.md", "README.md"):
        txt = (FIG / doc).read_text()
        names |= set(re.findall(r"\b(p\d\d_[a-z_]+)(?:\.py)?\b", txt))
        names |= {"tikz/" + m for m in re.findall(r"tikz/([a-z_]+)(?:\.tex)?\b", txt)}
    assert names
    for n in names:
        path = FIG / "templates" / (n + ".tex" if n.startswith("tikz/") else n + ".py")
        assert path.exists(), n
    for retired in ("p06_noise_waterfall", "p07_modulus_layout", "p08_sbox_ddt_heatmap", "p09_trail_bounds"):
        assert not (FIG / "templates" / f"{retired}.py").exists()
    assert not (FIG / "templates" / "tikz" / "spn_round.tex").exists()


def _neutral_stats():
    # empty drawing statistics, so only caption keywords decide the type
    return {"n_line": 0, "n_curve": 0, "n_rect": 0, "n_quad": 0, "n_paths": 0,
            "n_filled_rects": 0, "n_hlines": 0, "n_vlines": 0, "n_diag": 0, "n_arrowheads": 0,
            "n_ticks": 0, "n_hticks": 0, "n_vticks": 0, "n_images": 0, "img_eff_dpi": 0.0, "vector_colors": 0,
            "words": 0, "text_density": 0.0, "whitespace": 0.0, "pixel_colors": 0, "aspect": 0.0,
            "rect_width_cv": 0.0, "grid_like": False, "xor_symbols": 0, "math_chars": 0}


@pytest.mark.parametrize("caption,expected", [
    # ZK captions
    ("Fig. 3. The R1CS circuit for a toy range check with 8 constraints.", "zk-circuit"),
    ("Figure 2: Plonkish layout of the custom gates and witness columns.", "zk-circuit"),
    ("Fig. 4. AIR constraints of the toy execution trace.", "zk-circuit"),
    ("Fig. 5. Copy constraints enforced by the permutation argument.", "zk-circuit"),
    ("Figure 1: The PIOP between the prover and the verifier.", "interactive-protocol"),
    ("Fig. 6. One round of the sum-check protocol.", "interactive-protocol"),
    ("Fig. 7. Folding two instances: commitment and opening phases.", "interactive-protocol"),
    ("Fig. 8. Merkle commitment to the codeword.", "tree-graph"),
    ("Fig. 9. Prover time vs proof size for the toy systems (Pareto front).", "plot-line"),
    ("Fig. 10. Proof size as a function of the number of queries.", "plot-line"),
    # existing crypto captions must keep their type
    ("Fig. 1. Round function of the toy SPN cipher.", "circuit-cipher"),
    ("Figure 3: The S-box layer and key schedule.", "circuit-cipher"),
    ("Fig. 2. Circuit of the toy S-box with XOR gates.", "circuit-cipher"),
    ("Fig. 4. A 4-round differential trail of the toy Feistel cipher.", "circuit-cipher"),
    ("Fig. 5. Overview of the bootstrapping pipeline.", "architecture-pipeline"),
    ("Fig. 6. Messages exchanged between sender and receiver in the OT protocol.", "protocol-flow"),
    ("Fig. 7. Butterfly network of the NTT.", "tree-graph"),
])
def test_caption_classification(caption, expected):
    pytest.importorskip("numpy")
    hv = _load(FIG / "harvester" / "harvest.py")
    got, scores = hv.classify(caption, _neutral_stats())
    assert got == expected, (caption, scores)


def test_no_private_strings():
    # assembled at runtime so that this file itself passes the repo-wide grep
    bad = ["order" + "-4", "order" + "4", "symmetry" + "-graded", "#" + "528", "#" + "699", "192" + ".168.",
           "/ho" + "me/", "ac" + "pk", "soseri" + "halsona"]
    for f in FIG.rglob("*"):
        if f.is_file() and f.suffix in {".py", ".md", ".tex", ".sty", ".mplstyle"} and f.name != "test_figures.py":
            txt = f.read_text(errors="ignore").lower()
            for b in bad:
                assert b.lower() not in txt, (f, b)
