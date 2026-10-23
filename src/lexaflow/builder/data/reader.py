"""Bounded deterministic discovery and reading of untrusted local JSON."""

import hashlib
import json
import math
import os
import stat
from collections.abc import Iterator
from pathlib import Path


def reject_constant(value: str) -> None:
    raise ValueError("nonstandard JSON constant")


def finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("numeric value exceeds supported range")
    return number


def read_files(
    root: Path, max_bytes: int
) -> Iterator[tuple[str, str | None, str, object]]:
    """Yield relative path, byte hash, parse status, value; never follow links."""
    discovered = []
    failures = []

    def onerror(error: OSError) -> None:
        try:
            location = Path(os.fsdecode(error.filename)).relative_to(root).as_posix()
            if ".." in Path(location).parts:
                location = "."
        except (TypeError, ValueError, OSError):
            location = "."
        failures.append(location)

    for directory, dirs, files in os.walk(root, followlinks=False, onerror=onerror):
        dirs[:] = sorted(
            d
            for d in dirs
            if not (Path(directory) / d).is_symlink()
            and not getattr(Path(directory) / d, "is_junction", lambda: False)()
        )
        for name in files:
            if name.lower().endswith(".json"):
                discovered.append(Path(directory) / name)
    for path in sorted(discovered):
        relative = path.relative_to(root).as_posix()
        digest, value = None, None
        try:
            if (
                path.is_symlink()
                or not path.resolve().is_relative_to(root)
                or not stat.S_ISREG(path.stat().st_mode)
            ):
                yield relative, None, "unsafe_path", None
                continue
            with path.open("rb") as stream:
                raw = stream.read(max_bytes + 1)
            if len(raw) > max_bytes:
                status = "too_large"
            else:
                digest = hashlib.sha256(raw).hexdigest()
                try:
                    value = json.loads(
                        raw, parse_constant=reject_constant, parse_float=finite_float
                    )
                    status = "parsed"
                except (ValueError, UnicodeError, RecursionError):
                    status = "invalid_json"
        except OSError:
            status = "read_error"
        yield relative, digest, status, value
    for failure in sorted(failures):
        yield failure, None, "directory_error", None
