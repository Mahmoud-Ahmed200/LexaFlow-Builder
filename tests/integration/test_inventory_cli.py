import subprocess
import sys
from pathlib import Path


def test_cli(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "lexaflow.builder.data.inventory",
            "--input",
            "tests/fixtures",
            "--output",
            str(tmp_path / "out"),
            "--catalog",
            "configs/inventory-catalog.json",
        ],
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "out" / "summary.json").is_file()
    rejected = subprocess.run(
        [
            sys.executable,
            "-m",
            "lexaflow.builder.data.inventory",
            "--input",
            str(tmp_path),
            "--output",
            str(tmp_path / "nested"),
        ],
        capture_output=True,
        check=False,
    )
    assert rejected.returncode == 2
