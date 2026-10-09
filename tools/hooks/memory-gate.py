#!/usr/bin/env python3
"""Claude Code PreToolUse hook: refuse writes to machine-local agent memory.

Lessons about how to work belong in the committed framework, a rule in AGENTS.md and, where it can be
checked, a mechanical check under tools/; a note in ~/.claude/projects/*/memory/ is invisible to the
repository, to other machines and to the user (user, 10 October 2026: "We need a mechanical check... No
memories....").  The hook reads the tool call as JSON on stdin and exits with status 2 (block, message on
stderr) when Write, Edit or NotebookEdit targets that directory, or when a Bash command names it and is not a
plain listing, read or deletion.
"""
import json
import re
import sys

MEMORY = re.compile(r"\.claude/projects/[^/\s\"']+/memory(?:/|\b)")
HARMLESS = re.compile(r"^\s*(?:ls|cat|rm|grep|rg|wc|head|tail)\b[^>|;&]*$")
MESSAGE = ("Refused: nothing is written to machine-local agent memory. Put the lesson into the committed "
           "framework instead: a rule in AGENTS.md and, where it can be checked, a mechanical check under tools/ "
           "(user, 10 October 2026: \"We need a mechanical check... No memories....\").")


def refusal(payload):
    """The refusal message for a tool call, or None when it may proceed."""
    tool, args = payload.get("tool_name"), payload.get("tool_input") or {}
    if tool in ("Write", "Edit", "NotebookEdit"):
        path = str(args.get("file_path") or args.get("notebook_path") or "")
        return MESSAGE if MEMORY.search(path) else None
    if tool == "Bash":
        command = str(args.get("command") or "")
        if MEMORY.search(command) and not HARMLESS.match(command):
            return MESSAGE
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    message = refusal(payload)
    if message:
        print(message, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
