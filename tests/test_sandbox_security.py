"""Sandbox security regression checks."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from sandbox.executor import CodeExecutor
from tools import get_tools


def test_security_suite_passes():
    executor = CodeExecutor(get_tools())
    report = executor.run_security_evaluation()
    assert report["total"] >= 5
    assert report["passed"] == report["total"]


if __name__ == "__main__":
    test_security_suite_passes()
    print("Sandbox security tests passed")
