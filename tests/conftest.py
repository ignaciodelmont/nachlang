import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest


def _nachlang_binary():
    """
    Locate the nachlang console script, preferring the one from the
    interpreter running the tests so a poetry venv is picked up.
    """
    candidate = Path(sys.executable).parent / "nachlang"
    if candidate.exists():
        return candidate
    found = shutil.which("nachlang")
    if found:
        return Path(found)
    raise RuntimeError("nachlang console script not found -- run `poetry install`")


NACHLANG = _nachlang_binary()


class Nachlang:
    """
    Compiles and runs nachlang programs in a subprocess.

    Programs print through LLVM's printf, which writes to the process's file
    descriptor rather than to Python's sys.stdout, so capsys cannot see it.
    Running out of process captures the real output and keeps a segfault in
    generated code from taking the test session down with it.
    """

    def __init__(self, tmp_path):
        self._tmp_path = tmp_path
        self._counter = 0

    def _write(self, source):
        self._counter += 1
        path = self._tmp_path / f"program_{self._counter}.nach"
        path.write_text(dedent(source).strip() + "\n", encoding="utf-8")
        return path

    def run(self, source, *args):
        """
        Run a program and hand back the completed process, whether or not it
        succeeded. Use this to assert on failures.
        """
        path = self._write(source)
        return subprocess.run(
            [str(NACHLANG), str(path), *args],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

    def output(self, source, *args):
        """
        Run a program that is expected to succeed and return its stdout lines.
        """
        result = self.run(source, *args)
        assert result.returncode == 0, (
            f"expected the program to succeed, got exit {result.returncode}\n"
            f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
        )
        return result.stdout.splitlines()


@pytest.fixture
def nach(tmp_path):
    return Nachlang(tmp_path)
