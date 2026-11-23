#!/usr/bin/env python3
"""Idempotent, non-destructive installer. Run from project folder.

The package contains *new* modules and never changes the original app, scorer,
rules, YAML configs, fixture HTML or existing observations. Optional --force
backs up previously installed upgrade files in a dated local directory.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

FILES = [
    "app_v2.py", "platform_insights_v2.py", "validation_v2.py", "model_v2.py", "seo_audit_v2.py",
    "recommendations_v2.py", "analytics_contract_v2.py", "rule_review_v2.py",
    "data/synthetic_owned_metrics.csv", "tests/test_upgrade_v2.py", "tests/test_platform_insights_v2.py",
    "sql/quality_checks.sql", "docs/UPGRADE_STRATEGY_AND_SOURCES.md",
    "docs/SECTIONS_4_TO_7_PATCH.md",
    "requirements-upgrade.txt", ".streamlit/config.toml",
]


def install(project_root: Path, source_root: Path, force: bool = False,
            dry_run: bool = False) -> tuple[list[str], list[str]]:
    project = project_root.resolve()
    source = source_root.resolve()
    must_exist = ["scoring.py", "rules.py", "config/state_policy.yml", "data/state_policy_fixture.html"]
    missing = [part for part in must_exist if not (project / part).is_file()]
    if missing:
        raise ValueError("Run from the existing demo folder. Missing: " + ", ".join(missing))
    if not (project / "config").is_dir() or not (project / "data").is_dir():
        raise ValueError("Required project folders are unavailable")
    for part in FILES:
        candidate = (source / part).resolve()
        if not candidate.is_relative_to(source) or not candidate.is_file():
            raise ValueError("Missing upgrade package file: " + part)

    write: list[str] = []
    skip: list[str] = []
    conflicts: list[str] = []
    for part in FILES:
        dest = project / part
        if dest.is_symlink():
            raise ValueError("Refusing to overwrite a symbolic link: " + part)
        if dest.exists():
            if dest.read_bytes() == (source / part).read_bytes():
                skip.append(part)
            elif part == ".streamlit/config.toml":
                skip.append(part)  # Preserve an existing user theme.
            elif force:
                write.append(part)
            else:
                conflicts.append(part)
        else:
            write.append(part)
    if conflicts:
        raise ValueError("Different upgraded files already exist: " + ", ".join(conflicts) +
                         ". No files changed. Use --force for timestamped backups + update.")
    if dry_run:
        return write, skip

    backed_up = []
    backup_dir = project / ".pew-upgrade-backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
    for part in write:
        destination = project / part
        if destination.exists():
            location = backup_dir / part
            location.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, location)
            backed_up.append(part)
    for part in write:
        destination = project / part
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Source comes from a finite, literal manifest, not from user input.
        shutil.copy2(source / part, destination)
    return write, skip


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the candidate's accessible optimization demo")
    parser.add_argument("--force", action="store_true", help="Back up and replace prior upgrade files only")
    parser.add_argument("--dry-run", action="store_true", help="List changes without writing files")
    args = parser.parse_args()
    try:
        written, unchanged = install(Path.cwd(), Path(__file__).resolve().parent,
                                     force=args.force, dry_run=args.dry_run)
    except (OSError, ValueError) as error:
        print(f"INSTALL STOPPED: {error}", file=sys.stderr)
        return 1
    print("DRY RUN" if args.dry_run else "Upgrade installed successfully.")
    print("Installed/upgraded: " + (", ".join(written) or "none"))
    print("Already present/preserved: " + (", ".join(unchanged) or "none"))
    print("Original app.py, scoring.py, rules.py and portfolio configs were not modified.")
    print("Next: python -m pip install -r requirements.txt -r requirements-upgrade.txt")
    print("Then: python -m pytest -q tests && python -m streamlit run app_v2.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
