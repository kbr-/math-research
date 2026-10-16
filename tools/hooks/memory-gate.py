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
# Rules and improvements go into AGENTS.md, not CLAUDE.md (user, 17 October 2026: "Please don't perform
# improvements in CLAUDE.md. the place is AGENTS.md"): an edit of a CLAUDE.md file is refused, and so is a shell
# command that writes to one (a redirection, sed -i, tee, a rewrap).
CLAUDE_FILE = re.compile(r"(?:^|/)CLAUDE\.md$")
CLAUDE_WRITE = re.compile(r"(?:>>?|\btee\b(?:\s+-a)?|\bsed\s+-i[^\s|;&]*(?:\s+[^\s|;&]+)*?|\brewrap_md\.py|"
                          r"\breplace_text\.py)\s+[^|;&]*?CLAUDE\.md\b")
# A commit message or a heredoc's body naming the tools is not a write (17 October 2026: replayed over 6376 calls,
# the first version refused 2 replace_text.py commands whose heredoc mentioned CLAUDE.md, and one commit command).
HEREDOC_BODY = re.compile(r"(<<-?\s*['\"]?(\w+)['\"]?[^\n]*)\n.*?\n\2\b", re.S)   # keeps the marker's own line
QUOTED = re.compile(r"'[^']*'|\"[^\"]*\"")
CLAUDE_MESSAGE = ("Refused: CLAUDE.md takes no rules or improvements; put them in AGENTS.md (user, 17 October 2026: "
                  "\"Please don't perform improvements in CLAUDE.md. the place is AGENTS.md\").")
MESSAGE = ("Refused: nothing is written to machine-local agent memory. Put the lesson into the committed "
           "framework instead: a rule in AGENTS.md and, where it can be checked, a mechanical check under tools/ "
           "(user, 10 October 2026: \"We need a mechanical check... No memories....\").")


def refusal(payload):
    """The refusal message for a tool call, or None when it may proceed."""
    tool, args = payload.get("tool_name"), payload.get("tool_input") or {}
    if tool in ("Write", "Edit", "NotebookEdit"):
        path = str(args.get("file_path") or args.get("notebook_path") or "")
        if CLAUDE_FILE.search(path):
            return CLAUDE_MESSAGE
        return MESSAGE if MEMORY.search(path) else None
    if tool == "Bash":
        command = str(args.get("command") or "")
        if CLAUDE_WRITE.search(QUOTED.sub("''", HEREDOC_BODY.sub(r"\1", command))):
            return CLAUDE_MESSAGE
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
