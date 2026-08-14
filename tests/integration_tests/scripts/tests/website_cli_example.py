"""
Confirms the command line example published on arelle.org still produces the
output committed alongside it.

The transcript in docs/arelle.org/examples/cli.txt is the contract: its
continued command block is the command the website displays, and the remaining
lines are the output that command must produce. This script joins the shell
continuations before running the command, so the two cannot drift apart.

The example filing resolves offline with no taxonomy package and no plugins,
so this test downloads nothing.
"""
from __future__ import annotations

import re
import shlex
from pathlib import Path

from tests.integration_tests.scripts.script_util import (
    assert_result,
    parse_args,
    run_arelle_cmd,
)

PROMPT = "$ arelleCmdLine "

errors: list[str] = []
this_file = Path(__file__)
repository_root = this_file.parents[4]
examples_directory = repository_root / "docs" / "arelle.org" / "examples"
filing_path = examples_directory / "filing" / "demo-20251231.xbrl"
transcript_path = examples_directory / "cli.txt"

args = parse_args(
    this_file.stem,
    "Confirm the arelle.org command line example still produces its "
    "published output.",
)

transcript = transcript_path.read_text().splitlines()
command_lines = []
for line in transcript:
    command_lines.append(line)
    if not line.endswith("\\"):
        break
command_line = re.sub(
    r"\\\r?\n[ \t]*",
    "",
    "\n".join(command_lines),
)
expected_output = [
    line for line in transcript[len(command_lines):]
    if line.strip()
]
assert command_line.startswith(PROMPT), (
    f"Unexpected command in transcript: {command_line}"
)

# The website shows bare filenames; run the same arguments against the
# committed files so the published command is the one actually executed.
paths_by_name = {filing_path.name: filing_path}
example_args = [
    str(paths_by_name.get(argument, argument))
    for argument in shlex.split(command_line.removeprefix(PROMPT))
]

print(f"Running published example: {command_line}")
result = run_arelle_cmd(
    args.arelle,
    additional_args=example_args,
    offline=args.offline,
)
if result.returncode != 0:
    errors.append(
        f"Arelle exited {result.returncode}: {result.stderr.decode().strip()}"
    )

output = (result.stdout + result.stderr).decode()
actual_output = [line.rstrip() for line in output.splitlines() if line.strip()]
if actual_output != expected_output:
    errors.append(
        "Published output is out of date. Update {} to match:\n{}".format(
            transcript_path.relative_to(repository_root),
            "\n".join(actual_output),
        )
    )

assert_result(errors)
