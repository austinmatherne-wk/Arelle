"""
Confirms the plugin example published on arelle.org still produces the output
committed alongside it.

The transcript in docs/arelle.org/examples/plugin.txt is the contract: its
command occupies the first line and any backslash-continued lines, and the
remaining lines are the output that command must produce. This script runs the
displayed command verbatim, against the plugin the website displays, so the
published rule, the published command and the published output cannot drift
apart.
"""
from __future__ import annotations

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
plugin_path = examples_directory / "house_rules"
transcript_path = examples_directory / "plugin.txt"

args = parse_args(
    this_file.stem,
    (
        "Confirm the arelle.org plugin example still produces "
        "its published output."
    ),
)

transcript = transcript_path.read_text().splitlines()
command_lines = []
output_start = 0
while output_start < len(transcript):
    line = transcript[output_start]
    command_lines.append(line)
    output_start += 1
    if not line.endswith("\\"):
        break
command_line = "\n".join(command_lines)
expected_output = [line for line in transcript[output_start:] if line.strip()]
assert command_line.startswith(PROMPT), (
    f"Unexpected command in transcript: {command_line}"
)

# The website shows bare filenames; run the same arguments against the
# committed files so the published command is the one actually executed.
paths_by_name = {filing_path.name: filing_path, plugin_path.name: plugin_path}
command_text = command_line.removeprefix(PROMPT).replace("\\\n", " ")
example_args = [
    str(paths_by_name.get(argument, argument))
    for argument in shlex.split(command_text)
]

print(f"Running published example: {command_line}")
result = run_arelle_cmd(
    args.arelle,
    additional_args=example_args,
    offline=args.offline,
)
if result.returncode != 0:
    errors.append(
        f"Arelle exited {result.returncode}: "
        f"{result.stderr.decode().strip()}"
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
