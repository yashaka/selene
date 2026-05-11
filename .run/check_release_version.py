#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

import tomllib


def _read_pyproject_version(pyproject_path: Path) -> str:
    data = tomllib.loads(pyproject_path.read_text())

    project = data.get("project", {})
    version = project.get("version")
    if version:
        return version

    poetry = data.get("tool", {}).get("poetry", {})
    version = poetry.get("version")
    if version:
        return version

    raise RuntimeError(
        "Version is not found in pyproject.toml (project.version or tool.poetry.version)"
    )


def _read_init_version(init_path: Path) -> str:
    content = init_path.read_text()
    match = re.search(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", content, re.MULTILINE)
    if not match:
        raise RuntimeError(f"__version__ is not found in {init_path}")
    return match.group(1)


def _git_branch() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "branch", "--show-current"], text=True
            ).strip()
            or "<detached>"
        )
    except Exception:
        return "<unknown>"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check release tag consistency with pyproject.toml and selene/__init__.py"
    )
    parser.add_argument(
        "--tag", default=os.getenv("RELEASE_TAG") or os.getenv("GITHUB_REF_NAME")
    )
    parser.add_argument("--pyproject", default="pyproject.toml")
    parser.add_argument("--init", default="selene/__init__.py")
    args = parser.parse_args()

    if not args.tag:
        print(
            "ERROR: release tag is not provided. Pass --tag or set RELEASE_TAG/GITHUB_REF_NAME.",
            file=sys.stderr,
        )
        return 2

    tag = args.tag
    pyproject_version = _read_pyproject_version(Path(args.pyproject))
    init_version = _read_init_version(Path(args.init))

    context = {
        "release_tag": tag,
        "release_target_commitish": os.getenv("RELEASE_TARGET_COMMITISH", "<unknown>"),
        "github_ref": os.getenv("GITHUB_REF", "<unknown>"),
        "github_ref_name": os.getenv("GITHUB_REF_NAME", "<unknown>"),
        "github_sha": os.getenv("GITHUB_SHA", "<unknown>"),
        "git_branch": _git_branch(),
    }

    print("Release check context:")
    for key, value in context.items():
        print(f"- {key}: {value}")

    errors: list[str] = []
    if pyproject_version != tag:
        errors.append(
            f"pyproject version mismatch: expected '{tag}', got '{pyproject_version}' ({args.pyproject})"
        )
    if init_version != tag:
        errors.append(
            f"__version__ mismatch: expected '{tag}', got '{init_version}' ({args.init})"
        )

    if errors:
        print("\nRelease version check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        print(
            "\nAction required: fix versions in source branch before creating/publishing release tag.",
            file=sys.stderr,
        )
        return 1

    print("\nRelease version check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
