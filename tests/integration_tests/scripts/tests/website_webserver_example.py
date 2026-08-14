"""
Confirms the webserver example published on arelle.org still produces the
output committed alongside it.

The transcript in docs/arelle.org/examples/webserver.txt is the contract: its
first line is the command the website displays, and the remaining lines are
the output that command must produce. This script runs the displayed command
verbatim and compares its startup output with the published output, ignoring
Bottle's dependency-owned version banner and Arelle's operational warning.
"""
from __future__ import annotations

import shlex
import subprocess
import time
from pathlib import Path

from tests.integration_tests.scripts.script_util import (
    _get_arelle_args,
    assert_result,
    parse_args,
)

PROMPT = "$ arelleCmdLine "
IGNORED_OUTPUT_PREFIXES = (
    "Bottle v",
    "WARNING: Arelle's built-in webserver",
)

errors: list[str] = []
this_file = Path(__file__)
repository_root = this_file.parents[4]
transcript_path = (
    repository_root / "docs" / "arelle.org" / "examples" / "webserver.txt"
)

args = parse_args(
    this_file.stem,
    "Confirm the arelle.org webserver example still produces "
    "its published output.",
)

transcript = transcript_path.read_text().splitlines()
command_line, expected_output = transcript[0], [
    line for line in transcript[1:] if line.strip()
]
assert command_line.startswith(
    PROMPT,
), f"Unexpected command in transcript: {command_line}"

example_args = shlex.split(command_line.removeprefix(PROMPT))
print(f"Running published example: {command_line}")
process = subprocess.Popen(
    _get_arelle_args(
        args.arelle,
        additional_args=example_args,
        offline=args.offline,
    ),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)
try:
    time.sleep(2)  # Allow the server to emit its startup output.
finally:
    if process.poll() is None:
        process.kill()
    output, _ = process.communicate()

actual_output = [
    line.rstrip()
    for line in output.decode().splitlines()
    if line.strip() and not line.startswith(IGNORED_OUTPUT_PREFIXES)
]
if actual_output != expected_output:
    errors.append(
        "Published output is out of date. Update {} to match:\n{}".format(
            transcript_path.relative_to(repository_root),
            "\n".join(actual_output),
        )
    )

assert_result(errors)
