#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python >= 3.11
except ModuleNotFoundError:  # pragma: no cover - CI on Python 3.10
    import tomli as tomllib  # type: ignore[no-redef]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: get_lock_version.py <package-name>", file=sys.stderr)
        return 2

    package_name = sys.argv[1]
    lock_path = Path("poetry.lock")
    if not lock_path.exists():
        print("poetry.lock not found", file=sys.stderr)
        return 1

    data: dict[str, Any] = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    for package in data.get("package", []):
        if package.get("name") == package_name:
            print(package["version"])
            return 0

    print(f"Package not found in poetry.lock: {package_name}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
