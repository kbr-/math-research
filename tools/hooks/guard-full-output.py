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

It also refuses a heredoc-fed program followed by further commands on later lines that are not
chained to it: those commands run even when the program fails, so a failed scripted edit is followed
by the appends, registrations and checkpoints meant to use its result.
"""
import json
import re
import shlex
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


HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1")


def unchained_heredoc(command: str):
    """The reason when non-blank lines follow a heredoc's terminator and the heredoc's command line does
    not chain what follows with && (as in `python3 - <<'EOF' && next`) or run under `set -e`."""
    if re.search(r"\bset\s+-e\b", command):
        return None
    lines = command.split("\n")
    for i, line in enumerate(lines):
        match = HEREDOC.search(line)
        if not match:
            continue
        end = next((j for j in range(i + 1, len(lines)) if lines[j].strip() == match.group(2)), None)
        if end is None:
            continue
        after = [x for x in lines[end + 1:] if x.strip() and not x.strip().startswith("#")]
        if after and not re.search(r"&&|\|\|", line[match.end():]):
            return ("commands after a heredoc run even when the heredoc's program fails; chain them on the "
                    "heredoc's first line (python3 - <<'EOF' && next ...) or split them into a separate call")
    return None


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


FOREGROUND_EXPECT, FOREGROUND_TIMEOUT = 60, 180   # seconds; compute.sh's default timeout is 180
COMPUTE_METADATA = {"start", "phase", "report", "stop", "--status", "--help", "-h"}


def launcher_options(segment: str):
    """compute.sh's own options in one command segment, as {name: value}, or None if the segment runs no
    workload through compute.sh.  Options end at `--` or at the workload's program."""
    try:
        words = shlex.split(segment)
    except ValueError:
        return None
    at = next((i for i, w in enumerate(words) if w.endswith("compute.sh")), None)
    if at is None or at + 1 >= len(words) or words[at + 1] in COMPUTE_METADATA:
        return None
    rest, options = words[at + 1:], {}
    if rest[0] == "run":
        rest = rest[2:]   # run SESSION
    i = 0
    while i < len(rest) and rest[i].startswith("-") and rest[i] != "--":
        name, _, value = rest[i].partition("=")
        if not value and i + 1 < len(rest) and not rest[i + 1].startswith("-"):
            value, i = rest[i + 1], i + 1
        options[name] = value
        i += 1
    return options


def foreground_long_run(command: str, background: bool):
    """A compute.sh run that may take long, started in the foreground (COMPUTATION_RULES.md, long runs)."""
    if background:
        return None
    for segment in SEPARATOR.split(command):
        options = launcher_options(segment)
        if options is None:
            continue
        def seconds(name):
            value = options.get(name, "")
            return int(value) if value.isdigit() else 0
        if seconds("--expect") > FOREGROUND_EXPECT or seconds("--timeout") > FOREGROUND_TIMEOUT:
            return (f"a compute.sh run expected over {FOREGROUND_EXPECT} s or allowed over {FOREGROUND_TIMEOUT} s "
                    "goes to the background (run_in_background: true); keep working meanwhile and reassess it at "
                    "5 minutes (COMPUTATION_RULES.md, long runs; user, 3 October 2026)")
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command") or ""
    reason = foreground_long_run(command, bool(tool_input.get("run_in_background")))
    if reason:
        print(f"Refused: {reason}.", file=sys.stderr)
        return 2
    reason = unchained_heredoc(command)
    if reason:
        print(f"Refused: {reason}.", file=sys.stderr)
        return 2
    reason = blocked(command)
    if reason:
        print(f"Run this command bare and read its output in full: {reason}. Do not pipe it "
              "through head, tail, sed or grep or redirect it.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
