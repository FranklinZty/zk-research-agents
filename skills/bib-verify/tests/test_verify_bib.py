"""Tests for verify_bib.py, offline only: network calls are replaced by fakes (run: python3 -m pytest -q)."""
# TOY: synthetic entries on example.org hosts
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import verify_bib as vb  # noqa: E402

CY24_STYLE = r"""
@book{ToyBook2024,
  author = {Toy, Ada and Example, Bob},
  title = {Building Toy Proofs from Toy Hashes},
  url = {https://github.example.org/toy-snargs-book},
  urldate = {2026-10-27},
  year = {2024},
}
"""


def _state(found_title=None, reachable=True, snapshot=True):
    def search(title, *rest):
        if found_title is None:
            return []
        return [{"title": found_title, "authors": ["Ada Toy", "Bob Example"], "year": 2024, "source": "fake"}]

    def probe(url, timeout):
        return reachable, "HEAD 200" if reachable else "GET <urlopen error timed out>"

    def wayback(url, timeout):
        return "http://web.archive.org/web/20260908/" + url if snapshot else None

    return {"delay": 0.0, "url_timeout": 1.0, "probe": probe, "wayback": wayback,
            "search_dblp": search, "search_crossref": search}


def _entry():
    (e,) = vb.parse_bib(CY24_STYLE)
    return e


def test_selftest_passes():
    assert vb.selftest(online=False) == 0


def test_book_with_url_not_in_indexes_uses_url_path():
    r = vb.check_entry(_entry(), False, _state(found_title=None))
    assert r["status"] == "VERIFIED"
    assert r["detail"].startswith("@book via URL (title search: no record")
    assert "accessed 2026-10-27" in r["detail"] and "snapshot" in r["detail"]


def test_book_with_url_needs_snapshot_and_reachability():
    assert vb.check_entry(_entry(), False, _state(snapshot=False))["status"] == "NEEDS_VERIFICATION"
    assert vb.check_entry(_entry(), False, _state(reachable=False))["status"] == "NEEDS_VERIFICATION"


def test_book_found_by_title_search_keeps_record_path():
    r = vb.check_entry(_entry(), False, _state(found_title="Building Toy Proofs from Toy Hashes"))
    assert r["status"] == "VERIFIED" and "@book via URL" not in r["detail"]


def test_offline_stays_unchecked():
    assert vb.check_entry(_entry(), True, _state())["status"] == "UNCHECKED"
