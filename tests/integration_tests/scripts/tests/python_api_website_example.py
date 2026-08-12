"""
Confirms the Python API example published on arelle.org still produces the
output committed alongside it.

The transcript in docs/arelle.org/examples/python-api.txt is the contract: its
first line is the command the website displays, and the remaining lines are
the output that command must produce. This script runs the published script
itself, so the code on the website and the output beneath it cannot drift
apart.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from tests.integration_tests.scripts.script_util import assert_result, parse_args

errors: list[str] = []
this_file = Path(__file__)
repository_root = this_file.parents[4]
examples_directory = repository_root / "docs" / "arelle.org" / "examples"
filing_directory = examples_directory / "filing"
script_path = examples_directory / "revenue.py"
transcript_path = examples_directory / "python-api.txt"
prompt = f"$ python {script_path.name}"

args = parse_args(
    this_file.stem,
    "Confirm the arelle.org Python API example still produces its published output.",
    arelle=False,
)

transcript = transcript_path.read_text().splitlines()
command_line, expected_output = transcript[0], [line for line in transcript[1:] if line.strip()]
assert command_line == prompt, f"Unexpected command in transcript: {command_line}"

# The published script resolves the filing relative to the working directory,
# so run it the way the website tells the reader to.
environment = dict(os.environ, PYTHONPATH=str(repository_root))
print(f"Running published example: {command_line}")
result = subprocess.run(
    [sys.executable, str(script_path)],
    capture_output=True,
    cwd=filing_directory,
    env=environment,
)
if result.returncode != 0:
    errors.append(f"Example exited {result.returncode}: {result.stderr.decode().strip()}")

actual_output = [line.rstrip() for line in result.stdout.decode().splitlines() if line.strip()]
if actual_output != expected_output:
    errors.append(
        "Published output is out of date. Update {} to match:\n{}".format(
            transcript_path.relative_to(repository_root),
            "\n".join(actual_output),
        )
    )

assert_result(errors)
