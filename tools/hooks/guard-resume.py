#!/usr/bin/env python3
"""Claude Code PreToolUse hook: refuse filtered or redirected resume.py output.

The resume bundle must reach the agent whole, one part per call. Piping
`tools/resume.py` through head, tail, sed or grep, or redirecting it to a file,
silently drops restoration text. The hook reads the tool call as JSON on stdin
and exits with status 2 (block, message on stderr) for such commands.
"""
import json
import re
import sys

RESUME = re.compile(r"(?:^|[\s/;&|(])resume\.py\b")
# Command lists split on ;, &&, || and newlines; a remaining single | is a pipe.
SEPARATOR = re.compile(r"\|\||&&|;|\n")
# Redirection of standard output (> or 1>, not 2> or >&).
STDOUT_REDIRECT = re.compile(r"(?:^|[^0-9&>])1?>(?!&)")

MESSAGE = (
    "Run tools/resume.py bare: its output is the restoration bundle and must be read whole, "
    "one part per call. Do not pipe it through head, tail, sed or grep or redirect it; "
    "run `python3 tools/resume.py` alone, then each `--read ID --part N` alone."
)


def blocked(command: str) -> bool:
    for segment in SEPARATOR.split(command):
        match = RESUME.search(segment)
        if match is None:
            continue
        rest = segment[match.end():]
        if "|" in rest or STDOUT_REDIRECT.search(rest):
            return True
    return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    if blocked(command):
        print(MESSAGE, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
