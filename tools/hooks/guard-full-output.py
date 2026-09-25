#!/usr/bin/env python3
"""Claude Code PreToolUse hook: refuse filtered or redirected output of must-read commands.

Some commands print text the agent must read whole: the resume bundle
(`tools/resume.py`), the turn guidance and warnings of `./compute.sh start`, the
finisher's report (`tools/finish-turn.py`), and every computation run by `./compute.sh`
(`run`, or an option-led invocation), whose refusals and guard messages would otherwise be
filtered away; it displays only its own lines, and the workload's output is in the saved log. Piping them through head, tail, sed or
grep, or redirecting their standard output to a file, silently drops that text. The
hook reads the tool call as JSON on stdin and exits with status 2 (block, message on
stderr) for such commands.
"""
import json
import re
import sys

# The start of a command-list segment up to the program it runs: optional parentheses, variable
# assignments and env/nohup/time wrappers, then optionally an interpreter with its options.
INVOKED = (r"^\s*(?:(?:do|then|else)\s+)?\(*\s*(?:\w+=\S*\s+)*(?:(?:env|nohup|time)\s+)*"
           r"(?:\S*python[\d.]*\s+(?:-\S+\s+)*|(?:ba)?sh\s+)?(?:\S*/)?")
# Each must-read command, run at the start of a segment, with the reason shown when it is filtered.
# A command that only names the file, as in `grep x tools/resume.py | head`, is not guarded.
GUARDED = [
    (re.compile(INVOKED + r"resume\.py\b"),
     "tools/resume.py prints the restoration bundle, one part per call"),
    (re.compile(INVOKED + r"compute\.sh\s+start\b"),
     "./compute.sh start prints turn guidance and warnings that can appear anywhere"),
    (re.compile(INVOKED + r"finish-turn\.py\b"),
     "tools/finish-turn.py prints checks, warnings and staging instructions"),
    (re.compile(INVOKED + r"compute\.sh\s+(?:run\b|--(?!status\b))"),
     "./compute.sh runs print guard refusals and guidance, and only those (the output is in the saved log); "
     "save a full result with tools/save-run-output.py"),
]
# Command lists split on ;, &&, || and newlines; a remaining single | is a pipe.
SEPARATOR = re.compile(r"\|\||&&|;|\n")
# Redirection of standard output (> or 1>, not 2> or >&).
STDOUT_REDIRECT = re.compile(r"(?:^|[^0-9&>])1?>(?!&)")


def blocked(command: str):
    """Return the reason for the first filtered must-read command, or None."""
    for segment in SEPARATOR.split(command):
        for pattern, reason in GUARDED:
            match = pattern.search(segment)
            if match is None:
                continue
            rest = segment[match.end():]
            if "|" in rest or STDOUT_REDIRECT.search(rest):
                return reason
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    reason = blocked(command)
    if reason:
        print(f"Run this command bare and read its output in full: {reason}. Do not pipe it "
              "through head, tail, sed or grep or redirect it.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
