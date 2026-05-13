#!/usr/bin/env python3
"""
Rename every 'stijn' / 'Stijn' / 'Stijn-style' mention in the active tree to
neutral RURO terminology.

Safe-haven exclusions (left fully untouched):
    - stijn/                       (original R notebooks; legitimate authorship)
    - docs/archive/                (sealed snapshot)
    - docs/ACKNOWLEDGEMENTS.md     (centralised personal acknowledgement)

Defensive citation guard: any line containing the literal "Stijn Van Houtven"
is left UNCHANGED, even outside the safe haven, and a warning is recorded.

Z: paths matching 'Z:/.../stijn_occ/...' are preserved (out-of-scope for the
rename — see Phase 5 of the plan).

Usage:
    python scripts/maintenance/rename_stijn_to_ruro.py                # dry-run
    python scripts/maintenance/rename_stijn_to_ruro.py --apply        # execute
    python scripts/maintenance/rename_stijn_to_ruro.py --apply --allow-dirty
"""
from __future__ import annotations

import argparse
import csv
import datetime
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]

SAFE_HAVENS: Set[Path] = {
    (REPO_ROOT / "stijn"),
    (REPO_ROOT / "docs" / "archive"),
    (REPO_ROOT / "docs" / "ACKNOWLEDGEMENTS.md"),
}

EXCLUDED_TREES: Set[Path] = {
    (REPO_ROOT / ".venv"),
    (REPO_ROOT / ".git"),
    (REPO_ROOT / "__pycache__"),
    (REPO_ROOT / ".mypy_cache"),
    (REPO_ROOT / ".ruff_cache"),
    (REPO_ROOT / ".pytest_cache"),
    (REPO_ROOT / "node_modules"),
}

# Plain-text extensions we will rewrite content for. Anything else: path-only.
TEXT_SUFFIXES = {
    ".py", ".pyi", ".md", ".txt", ".rst", ".yaml", ".yml", ".json", ".jsonl",
    ".toml", ".cfg", ".ini", ".csv", ".tsv", ".html", ".htm", ".xml", ".svg",
    ".log", ".ps1", ".sh", ".bat", ".cmd", ".R", ".Rmd", ".tex", ".gitignore",
    ".gitattributes", ".env", ".dockerignore", ".editorconfig",
}

# Replacement maps — order matters. Longest/most-specific patterns first.
PROSE_MAP: List[Tuple[str, str]] = [
    ("Stijn-style enhanced RURO baseline", "continuous RURO baseline"),
    ("Stijn-style enhanced branch", "enhanced continuous RURO branch"),
    ("Stijn-style enhanced", "enhanced continuous"),
    ("Stijn-style simulated data", "RURO-style simulated data"),
    ("Stijn proposal aliases", "proposal-component aliases"),
    ("Stijn prior correction", "proposal-density correction"),
    ("Stijn log_q aliases", "layered proposal components"),
    ("Stijn occupation M0", "RURO occupation-opportunity M0"),
    ("Stijn occupation", "RURO occupation-opportunity"),
    ("Stijn's R implementation", "the R reference implementation"),
    ("Stijn's continuous model", "the continuous RURO reference design"),
    ("Stijn's R work", "the R reference work"),
    ("Stijn's R files", "the R reference files"),
    ("Stijn Reference Work", "R Reference Work"),
    ("Stijn reference", "R reference"),
    ("Stijn alias columns", "proposal-alias columns"),
    ("Stijn-style", "continuous-RURO"),
    ("Stijn's", "the R reference's"),
    ("Stijn ", "R reference "),
]

IDENTIFIER_MAP: List[Tuple[str, str]] = [
    ("estimation_spec_stijn_occ_M0", "estimation_spec_ruro_occ_M0"),
    ("_canary_stijn_occ_M0", "_canary_ruro_occ_M0"),
    ("_validation_stijn_occ_M0", "_validation_ruro_occ_M0"),
    ("fr_2016_stijn_occ_gamspy", "fr_2016_ruro_occ_gamspy"),
    ("stijn_occ_M0", "ruro_occ_M0"),
    ("STIJN_vs_PYTHON_SPECIFICATION", "R_REFERENCE_vs_PYTHON_SPECIFICATION"),
    ("RURO_STIJN_COMPARISON_AND_ACTION_PLAN", "RURO_R_REFERENCE_COMPARISON_AND_ACTION_PLAN"),
    ("RURO_STIJN_COMPARISON_SECTOR_OPPORTUNITY_PLAN", "RURO_R_REFERENCE_COMPARISON_SECTOR_OPPORTUNITY_PLAN"),
    ("RURO_stijn_occ_", "RURO_ruro_occ_"),
    ("RURO_model_spec_contract_v2_stijn_enhanced", "RURO_model_spec_contract_v2_continuous_enhanced"),
    ("_stijn_enhanced", "_continuous_enhanced"),
    ("_stijn_occ", "_ruro_occ"),
]

PATH_SEGMENT_MAP: List[Tuple[str, str]] = [
    ("/stijn_occ/", "/ruro_occ/"),
    ("\\stijn_occ\\", "\\ruro_occ\\"),
]

CATCHALL_MAP: List[Tuple[str, str]] = [
    ("stijn_occ", "ruro_occ"),
    ("stijn", "ruro"),
]

# Used to rename filenames + directory components.
FILENAME_TOKEN_MAP: List[Tuple[str, str]] = [
    ("estimation_spec_stijn_occ_M0", "estimation_spec_ruro_occ_M0"),
    ("_canary_stijn_occ_M0", "_canary_ruro_occ_M0"),
    ("_validation_stijn_occ_M0", "_validation_ruro_occ_M0"),
    ("fr_2016_stijn_occ_gamspy", "fr_2016_ruro_occ_gamspy"),
    ("RURO_stijn_occ_", "RURO_ruro_occ_"),
    ("STIJN_vs_PYTHON_SPECIFICATION", "R_REFERENCE_vs_PYTHON_SPECIFICATION"),
    ("RURO_STIJN_COMPARISON_AND_ACTION_PLAN", "RURO_R_REFERENCE_COMPARISON_AND_ACTION_PLAN"),
    ("RURO_STIJN_COMPARISON_SECTOR_OPPORTUNITY_PLAN", "RURO_R_REFERENCE_COMPARISON_SECTOR_OPPORTUNITY_PLAN"),
    ("RURO_model_spec_contract_v2_stijn_enhanced", "RURO_model_spec_contract_v2_continuous_enhanced"),
    ("RURO_model_spec_contract_v3_stijn_occ", "RURO_model_spec_contract_v3_ruro_occ"),
    ("RURO_model_spec_contract_v4_stijn_occ", "RURO_model_spec_contract_v4_ruro_occ"),
    ("stijn_occ", "ruro_occ"),
]

Z_PATH_RE = re.compile(
    r"Z:[/\\][^\s'\"\)\,\>\}]*?stijn_occ[/\\][^\s'\"\)\,\>\}]*",
    re.IGNORECASE,
)
CITATION = "Stijn Van Houtven"


def _resolved(p: Path) -> Path:
    try:
        return p.resolve()
    except OSError:
        return p


_SAFE_HAVEN_RESOLVED = {_resolved(p) for p in SAFE_HAVENS}
_EXCLUDED_RESOLVED = {_resolved(p) for p in EXCLUDED_TREES}


def is_safe_haven(path: Path) -> bool:
    rp = _resolved(path)
    for sh in _SAFE_HAVEN_RESOLVED:
        if rp == sh:
            return True
        try:
            if sh in rp.parents:
                return True
        except (ValueError, OSError):
            pass
    return False


def is_excluded_tree(path: Path) -> bool:
    rp = _resolved(path)
    for et in _EXCLUDED_RESOLVED:
        if rp == et:
            return True
        try:
            if et in rp.parents:
                return True
        except (ValueError, OSError):
            pass
    return False


def is_binary(path: Path) -> bool:
    """Heuristic: NUL byte in first 4 KB indicates binary."""
    try:
        with path.open("rb") as f:
            chunk = f.read(4096)
        if not chunk:
            return False
        return b"\x00" in chunk
    except OSError:
        return True


def is_text_eligible(path: Path) -> bool:
    """Return True if we should attempt content rewrite on this file."""
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    # Fallback: small files with no extension we still treat as text if not binary.
    if not path.suffix and path.is_file() and path.stat().st_size < 256 * 1024:
        return not is_binary(path)
    return False


def read_text(path: Path) -> Optional[str]:
    for enc in ("utf-8", "latin-1"):
        try:
            with path.open("r", encoding=enc, newline="") as f:
                return f.read()
        except (OSError, UnicodeDecodeError):
            continue
    return None


def apply_content_rewrites(
    text: str, file_label: str, warnings: List[str]
) -> Tuple[str, int]:
    """Apply prose + identifier + path-segment + catch-all maps line-by-line.
    Returns (new_text, n_subs)."""
    out_parts: List[str] = []
    n_subs = 0

    # Splitlines with keepends so we preserve line endings exactly.
    for line_no, line in enumerate(text.splitlines(keepends=True), start=1):
        if CITATION in line:
            warnings.append(
                f"{file_label}:{line_no} contains '{CITATION}' citation — line preserved verbatim"
            )
            out_parts.append(line)
            continue

        # Mask Z: paths so they're not rewritten.
        masks: List[str] = []

        def _mask(m: "re.Match[str]") -> str:
            masks.append(m.group(0))
            return f"\x00ZPATH{len(masks) - 1}\x00"

        masked = Z_PATH_RE.sub(_mask, line)
        new = masked

        for old, repl in (PROSE_MAP + IDENTIFIER_MAP + PATH_SEGMENT_MAP + CATCHALL_MAP):
            if old in new:
                n_subs += new.count(old)
                new = new.replace(old, repl)

        # Restore Z: paths.
        for i, original in enumerate(masks):
            new = new.replace(f"\x00ZPATH{i}\x00", original)

        out_parts.append(new)

    return "".join(out_parts), n_subs


def compute_new_path(path_rel: Path) -> Path:
    """Apply filename token map to every path component."""
    parts = list(path_rel.parts)
    new_parts: List[str] = []
    for part in parts:
        for old, repl in FILENAME_TOKEN_MAP:
            if old in part:
                part = part.replace(old, repl)
        new_parts.append(part)
    return Path(*new_parts) if new_parts else path_rel


def needs_path_rename(path_rel: Path) -> bool:
    new = compute_new_path(path_rel)
    return new != path_rel


def walk_targets(root: Path) -> List[Path]:
    paths: List[Path] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if is_excluded_tree(p) or is_safe_haven(p):
            continue
        paths.append(p)
    return paths


def git(*args: str, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True, text=True, check=check,
    )


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true",
                    help="Actually apply changes (default: dry-run).")
    ap.add_argument("--allow-dirty", action="store_true",
                    help="Skip the clean-tree check.")
    ap.add_argument("--no-commit", action="store_true",
                    help="Apply but don't git-commit (default: commit).")
    args = ap.parse_args(argv)

    if not args.allow_dirty:
        s = git("status", "--porcelain")
        if s.stdout.strip():
            print("ERROR: git working tree is dirty. Pass --allow-dirty to override.")
            print(s.stdout[:2000])
            return 2

    print(f"Repo root      : {REPO_ROOT}")
    print(f"Safe havens    : {sorted(str(p.relative_to(REPO_ROOT)) for p in SAFE_HAVENS)}")
    print(f"Excluded trees : {sorted(str(p.name) for p in EXCLUDED_TREES if p.exists())}")
    print()

    paths = walk_targets(REPO_ROOT)

    content_entries: List[Dict] = []
    rename_entries: List[Dict] = []
    all_warnings: List[str] = []
    n_binary_skipped = 0

    for p in paths:
        rel = p.relative_to(REPO_ROOT)
        rel_label = str(rel).replace("\\", "/")

        # Content
        if is_text_eligible(p):
            text = read_text(p)
            if text is not None and ("stijn" in text or "Stijn" in text):
                warnings: List[str] = []
                new_text, n_subs = apply_content_rewrites(text, rel_label, warnings)
                if new_text != text:
                    content_entries.append({
                        "path": p, "new_text": new_text,
                        "n_subs": n_subs, "warnings": warnings,
                    })
                all_warnings.extend(warnings)
        else:
            # Binary or non-text — still considered for path rename below.
            if is_binary(p):
                n_binary_skipped += 1

        # Path
        if needs_path_rename(rel):
            new_rel = compute_new_path(rel)
            new_abs = REPO_ROOT / new_rel
            if new_abs != p:
                rename_entries.append({"old": p, "new": new_abs})

    # Manifest CSV
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    manifest_path = REPO_ROOT / "Results" / f"rename_stijn_to_ruro_manifest_{ts}.csv"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["kind", "old_path", "new_path", "n_content_subs", "warnings"])
        for ent in content_entries:
            old = str(ent["path"].relative_to(REPO_ROOT)).replace("\\", "/")
            writer.writerow(["content", old, old, ent["n_subs"],
                             " | ".join(ent["warnings"])])
        for ent in rename_entries:
            old = str(ent["old"].relative_to(REPO_ROOT)).replace("\\", "/")
            new = str(ent["new"].relative_to(REPO_ROOT)).replace("\\", "/")
            writer.writerow(["rename", old, new, "", ""])

    print(f"Manifest                            : {manifest_path}")
    print(f"Files with content rewrites         : {len(content_entries)}")
    print(f"Path renames                        : {len(rename_entries)}")
    print(f"Binary files skipped (content)      : {n_binary_skipped}")
    print(f"Citation guard hits (preserved)     : {len(all_warnings)}")
    if all_warnings[:10]:
        print("First citation-guarded lines (≤10):")
        for w in all_warnings[:10]:
            print(f"  - {w}")

    if not args.apply:
        print("\nDRY-RUN. Use --apply to execute.")
        return 0

    # =====================
    # APPLY
    # =====================
    print("\n--- APPLY: content rewrites ---")
    for ent in content_entries:
        ent["path"].write_text(ent["new_text"], encoding="utf-8")
    print(f"Rewrote {len(content_entries)} file(s).")

    if not args.no_commit:
        git("add", "-A")
        r = git("commit", "-m", "rename(stijn->ruro): content rewrites")
        if r.returncode != 0 and "nothing to commit" not in (r.stdout + r.stderr):
            print(f"WARNING: content commit returned {r.returncode}:\n{r.stdout}\n{r.stderr}")

    print("\n--- APPLY: path renames ---")
    # Sort by depth descending — leaf files first.
    sorted_renames = sorted(
        rename_entries,
        key=lambda e: (len(e["old"].parts), str(e["old"])),
        reverse=True,
    )

    # Track which folders' names need changing so we can rmdir leftovers after.
    folder_renames_to_check: Set[Path] = set()
    for ent in rename_entries:
        old_rel = ent["old"].relative_to(REPO_ROOT)
        new_rel = ent["new"].relative_to(REPO_ROOT)
        for i, (op, np_) in enumerate(zip(old_rel.parts[:-1], new_rel.parts[:-1])):
            if op != np_:
                folder_renames_to_check.add(REPO_ROOT.joinpath(*old_rel.parts[: i + 1]))

    moved = 0
    for ent in sorted_renames:
        old_abs = ent["old"]
        new_abs = ent["new"]
        if not old_abs.exists():
            continue  # already moved as part of an earlier op
        new_abs.parent.mkdir(parents=True, exist_ok=True)
        rel_old = str(old_abs.relative_to(REPO_ROOT))
        rel_new = str(new_abs.relative_to(REPO_ROOT))
        r = git("mv", rel_old, rel_new)
        if r.returncode != 0:
            # Fallback: shutil move + git add.
            try:
                shutil.move(str(old_abs), str(new_abs))
                git("add", "-A")
            except OSError as e:
                print(f"FAIL move {rel_old} -> {rel_new}: {e}; git error: {r.stderr.strip()}")
                continue
        moved += 1
    print(f"Moved {moved} file(s).")

    # Remove leftover empty folders (bottom-up).
    sorted_folders = sorted(folder_renames_to_check, key=lambda p: len(p.parts), reverse=True)
    for old_folder in sorted_folders:
        if not old_folder.exists():
            continue
        try:
            # rmdir only if empty
            if not any(old_folder.iterdir()):
                old_folder.rmdir()
        except OSError:
            pass

    if not args.no_commit:
        git("add", "-A")
        r = git("commit", "-m", "rename(stijn->ruro): path renames")
        if r.returncode != 0 and "nothing to commit" not in (r.stdout + r.stderr):
            print(f"WARNING: rename commit returned {r.returncode}:\n{r.stdout}\n{r.stderr}")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
