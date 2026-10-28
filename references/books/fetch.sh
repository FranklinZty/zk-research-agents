#!/usr/bin/env bash
# fetch.sh -- fetch the two pinned reference books into a git-ignored local cache.
#
# Usage:
#   references/books/fetch.sh --list
#   references/books/fetch.sh cy24            # Chiesa-Yogev source, pinned commit, HEAD verified
#   references/books/fetch.sh thaler          # Thaler PDF from the author's page, sha256 verified
#   references/books/fetch.sh all
#   references/books/fetch.sh --dry-run all
#   references/books/fetch.sh --cache DIR cy24   # cache somewhere else (default: references/books/.cache)
#   references/books/fetch.sh --selftest      # offline: argument parsing and both verification paths
#
# Nothing fetched here may be committed (references/books/README.md): the cache directory is
# git-ignored, and the repository only cites the books by section name and label.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CACHE="$HERE/.cache"

# CY24: Chiesa, Yogev, "Building Cryptographic Proofs from Hash Functions", v1.2 (CC BY-SA 4.0)
CY24_URL='https://github.com/hash-based-snargs-book/hash-based-snargs-book.git'
CY24_COMMIT='305fa3d9d19ee6dba135de64b3156d1760df8426'
CY24_DIR='hash-snargs'

# Thaler, "Proofs, Arguments, and Zero-Knowledge", author's free PDF (dated July 18, 2023 on its title page)
THALER_URL='https://people.cs.georgetown.edu/jthaler/ProofsArgsAndZK.pdf'
THALER_SHA256='ef4e0fdbce01f5a0a4b79524cb372378dbf43f4688f6d768055a27580f2c18e6'
THALER_DIR='thaler'
THALER_FILE='ProofsArgsAndZK.pdf'

die() { echo "fetch.sh: $*" >&2; exit 1; }

sha256_of() {  # file -> hex digest
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'
  else shasum -a 256 "$1" | awk '{print $1}'; fi
}

verify_sha256() {  # file expected -> 0 if equal
  [ -f "$1" ] || return 1
  [ "$(sha256_of "$1")" = "$2" ]
}

verify_commit() {  # repo expected -> 0 if HEAD is exactly the expected commit
  [ -d "$1/.git" ] || return 1
  [ "$(git -C "$1" rev-parse HEAD 2>/dev/null)" = "$2" ]
}

fetch_cy24() {
  local dir="$CACHE/$CY24_DIR"
  if [ "$DRY" = 1 ]; then echo "would clone $CY24_URL -> $dir at $CY24_COMMIT"; return 0; fi
  mkdir -p "$CACHE"
  if [ -d "$dir/.git" ]; then
    echo "[cy24] exists, fetching"; git -C "$dir" fetch --quiet origin
  else
    echo "[cy24] cloning $CY24_URL"; git clone --quiet "$CY24_URL" "$dir"
  fi
  git -C "$dir" -c advice.detachedHead=false checkout --quiet "$CY24_COMMIT"
  verify_commit "$dir" "$CY24_COMMIT" || die "[cy24] HEAD is $(git -C "$dir" rev-parse HEAD), expected $CY24_COMMIT"
  echo "[cy24] pinned at $CY24_COMMIT"
}

fetch_thaler() {
  local dir="$CACHE/$THALER_DIR" out tmp
  out="$dir/$THALER_FILE"
  if [ "$DRY" = 1 ]; then echo "would download $THALER_URL -> $out and check sha256 $THALER_SHA256"; return 0; fi
  mkdir -p "$dir"
  if verify_sha256 "$out" "$THALER_SHA256"; then echo "[thaler] cached copy matches the pinned sha256"; return 0; fi
  tmp="$out.part"
  echo "[thaler] downloading $THALER_URL"
  curl -fsSL --retry 2 -o "$tmp" "$THALER_URL" || { rm -f "$tmp"; die "[thaler] download failed"; }
  if ! verify_sha256 "$tmp" "$THALER_SHA256"; then
    mv "$tmp" "$out.mismatch"
    die "[thaler] sha256 $(sha256_of "$out.mismatch") != pinned $THALER_SHA256.
  The author has updated the PDF: chapter and section numbers may have moved.
  Re-verify references/textbooks/toc/thaler-proofs-arguments-and-zero-knowledge.md against
  $out.mismatch (scripts/check_book_refs.py --dump-thaler-toc), then update THALER_SHA256 here and
  in references/books/README.md."
  fi
  mv "$tmp" "$out"
  echo "[thaler] sha256 ok ($THALER_SHA256)"
}

list() {
  printf '%-8s %-44s %s\n' NAME PIN SOURCE
  printf '%-8s %-44s %s\n' cy24 "commit $CY24_COMMIT" "$CY24_URL"
  printf '%-8s %-44s %s\n' thaler "sha256 ${THALER_SHA256:0:16}..." "$THALER_URL"
}

selftest() {
  local t rc=0 h
  t="$(mktemp -d)"; trap 'rm -rf "$t"' RETURN
  # status <want> <label> <command...>: run the command, compare its exit code with <want>
  status() {
    local want="$1" label="$2" got=0; shift 2
    "$@" >/dev/null 2>&1 || got=$?
    if [ "$got" = "$want" ]; then echo "ok   $label"; else echo "FAIL $label (exit $got, want $want)"; rc=1; fi
  }
  # sha256 path (abc is the FIPS 180-2 test vector)
  printf 'abc' > "$t/f"
  h='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
  status 0 "sha256 accepts the expected digest" verify_sha256 "$t/f" "$h"
  status 1 "sha256 rejects a wrong digest" verify_sha256 "$t/f" "$THALER_SHA256"
  status 1 "sha256 rejects a missing file" verify_sha256 "$t/missing" "$h"
  # commit path on a throwaway repository
  git init --quiet "$t/r"
  git -C "$t/r" -c user.name=t -c user.email=t@example.invalid commit --quiet --allow-empty -m a
  local c1; c1="$(git -C "$t/r" rev-parse HEAD)"
  git -C "$t/r" -c user.name=t -c user.email=t@example.invalid commit --quiet --allow-empty -m b
  status 1 "commit check rejects a moved HEAD" verify_commit "$t/r" "$c1"
  git -C "$t/r" -c advice.detachedHead=false checkout --quiet "$c1"
  status 0 "commit check accepts the pinned HEAD" verify_commit "$t/r" "$c1"
  status 1 "commit check rejects a non-repository" verify_commit "$t/none" "$c1"
  # argument parsing
  status 0 "--dry-run all parses" "$0" --dry-run all
  status 2 "unknown target exits 2" "$0" --dry-run nosuchbook
  status 2 "no target exits 2" "$0"
  status 2 "--cache without a directory exits 2" "$0" --cache
  [ "$rc" = 0 ] && echo "selftest: all checks passed" || echo "selftest: FAILED"
  return "$rc"
}

DRY=0; TARGETS=()
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    -l|--list) list; exit 0 ;;
    --selftest) selftest; exit $? ;;
    --dry-run) DRY=1 ;;
    --cache) [ $# -ge 2 ] || { echo "--cache needs a directory" >&2; exit 2; }; CACHE="$2"; shift ;;
    all) TARGETS+=(cy24 thaler) ;;
    cy24|thaler) TARGETS+=("$1") ;;
    *) echo "unknown target: $1 (see --list)" >&2; exit 2 ;;
  esac
  shift
done
[ ${#TARGETS[@]} -gt 0 ] || { echo "no target named; see --list" >&2; exit 2; }

for t in "${TARGETS[@]}"; do "fetch_$t"; done
