#!/usr/bin/env python3
"""Claude Code PreToolUse hook on Bash calls: must-read output, unchained heredocs, replace helpers, long runs,
stale branches.

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

It refuses a heredoc script that defines its own text-replacement helper, a function taking
(old, new) or a pattern matching a passage's words across any whitespace: tools/replace_text.py is
the committed, tested one, and the Edit tool makes exact edits.

It refuses, in the foreground, a long compute.sh run and a download whose length depends on the
network (a git or glab clone, a docker pull): both go to the background while other work goes on.

It refuses a workload run outside compute.sh: a test runner (pytest, unittest, the framework suite, a
repository's suite script) or a script in a scratchpad, at the start of a command segment. A program
run inside `docker exec`, an editor command given to git and an inline `python3 -c` are not at a
segment's start and pass.

And it refuses a git command that reads another branch, a local one with an upstream or a
remote-tracking one, while that upstream hasn't been fetched or pushed to here for FRESH seconds,
or while the local branch is behind it: another clone may have moved it, so what the command shows
can be out of date. A fetch of that remote earlier in the same command counts.
"""
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time

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
    # 11 October 2026: a search cut to its first six results by head hid, at rank ten, the recorded lemma a new one
    # refined.  A ranked search is read whole; its own -n sets the limit.
    (re.compile(INVOKED + r"search-claims\.py\b(?![^|;&\n]*\s--(?:show|list|help|json|out)\b)"),
     "tools/search-claims.py prints a ranked list whose later results are cut off by a filter (set the limit with "
     "its own -n N)"),
    # 11 October 2026: an item's history cut to its first four lines hid that eleven entries had developed it, one
    # of which had closed it for the reason a review then had to be told by its reviewer.
    (re.compile(INVOKED + r"lead_queue\.py\s+history\b"),
     "tools/lead_queue.py history lists every entry that developed the item, below its status"),
    # 11 October 2026: the append tool's output was sent to a file and its first lines read; the lines below said
    # that the item a next step called never developed had three entries.
    (re.compile(INVOKED + r"notebook-append\.py\b(?![^|;&\n]*\s--help\b)"),
     "tools/notebook-append.py prints, for each queue item the next step names, its latest follow-up and its "
     "earlier entries"),
    # 16 October 2026: "check_records.py --diff | tail -2 && git commit" committed a flagged commit hash, since a
    # pipeline's status is its last command's and tail succeeds.  A gate before a commit keeps its exit status.
    (re.compile(INVOKED + r"check_records\.py\b"),
     "tools/check_records.py is a gate whose exit status a pipe replaces with the filter's (a finding would no "
     "longer stop a following && git commit)"),
    # 16 October 2026: "check-claims.py | tail -1 && tools/ff-base.sh" fast-forwarded main past a failing claim
    # check, for the same reason.  The claim gates keep their exit status too.
    (re.compile(INVOKED + r"(?:check-claims|claim_rebase)\.py\b"),
     "tools/check-claims.py and tools/claim_rebase.py are gates whose exit status a pipe replaces with the "
     "filter's (a failure would no longer stop a following && tools/ff-base.sh or git rebase --continue)"),
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


# A text-replacement helper written into a heredoc script: a function taking (old, new), or a pattern that
# matches a passage's words across any whitespace. tools/replace_text.py is the committed, tested one.
ADHOC_REPLACE = re.compile(r"def\s+\w+\s*\(\s*(?:\w+\s*,\s*)?old\s*,\s*new\b|\.join\(\s*map\(\s*re\.escape")
# An inline Python script, from a heredoc or -c, that changes text and writes a file: a replace in place.
INLINE_PYTHON = re.compile(r"\bpython3?\s+(?:-I\s+)?(?:-\s*<<|-c\s)")
CHANGES_TEXT = re.compile(r"\.replace\(|\bre\.sub\(")
WRITES_FILE = re.compile(r"\.write_(?:text|bytes)\(|\bopen\([^)]*['\"][wa]")


# A Python script run by its path: python3 [-I] PATH.py
SCRIPT_RUN = re.compile(r"\bpython3?\s+(?:-I\s+)?(\S+\.py)\b")
REPOSITORY = Path(__file__).resolve().parents[2]


def scratch_script_replaces(command: str) -> bool:
    """A script outside the repository, run by its path, that changes text and writes a file.  On 16 October
    2026 replace scripts written to the scratchpad and run by path passed the inline check; three of them
    swallowed labels of the entry they edited.  Committed tools inside the repository are not read."""
    for path in SCRIPT_RUN.findall(command):
        file = Path(os.path.expandvars(path)).expanduser()
        try:
            if file.resolve().is_relative_to(REPOSITORY) or not file.is_file():
                continue
            source = file.read_text(errors="replace")[:200000]
        except OSError:
            continue
        # A test file writes fixtures and runs under the protected launcher, which owns its own checks: the one
        # false refusal counted on 16 October 2026 was a scratch copy of a test module.
        if re.search(r'^\s*import unittest\b|^\s*from unittest\b', source, re.M):
            continue
        if CHANGES_TEXT.search(source) and WRITES_FILE.search(source):
            return True
    return False


MKDIR_RESULTS = re.compile(r'\bmkdir\s+(?:-\w+\s+)*(\S*research/results/[^\s;&|]+)')


def existing_result_folder(command: str, cwd: str):
    """The reason when mkdir names a results folder that already holds files: on 16 October 2026 a new entry's
    folder took the name of an earlier review's, mkdir -p said nothing, and the new files overwrote the earlier
    entry's reviewer record."""
    for path in MKDIR_RESULTS.findall(command):
        folder = Path(os.path.expandvars(path))
        if not folder.is_absolute():
            folder = Path(cwd) / folder
        if folder.is_dir() and any(folder.iterdir()):
            return (f"{path} already exists and holds files of an earlier entry; a new entry's results go in a new "
                    "folder: choose another name (AGENTS.md: results are kept, never overwritten)")
    return None


def adhoc_replace_helper(command: str):
    """The reason when a heredoc script defines its own text-replacement helper, or an inline Python
    script, or a scratch script run by its path, replaces text in a file."""
    if ((HEREDOC.search(command) and ADHOC_REPLACE.search(command))
            or (INLINE_PYTHON.search(command) and CHANGES_TEXT.search(command) and WRITES_FILE.search(command))
            or scratch_script_replaces(command)):
        return ("a script replaces text in a file; replace a passage of prose with "
                "tools/replace_text.py FILE OLD_FILE NEW_FILE, which matches across line breaks and keeps the "
                "passage's indentation, or make an exact edit with the Edit tool (AGENTS.md: a recurring helper "
                "is a committed, tested tool)")
    return None


SED_SOURCE = re.compile(r"\.(?:py|sh|js|cjs|mjs|ts|tsx|c|h|cc|cpp|rs|go|java|toml|cfg|ini|ya?ml|json|html|css)$")
# The first address of a sed command is a range (12,15  /a/,/b/  0,/a/  5,+2), or its commands step to a next line.
SED_RANGE = re.compile(r"^\s*(?:\d+|\$|/(?:[^/\\]|\\.)*/)\s*,\s*(?:\+?\d+|\$|/(?:[^/\\]|\\.)*/)")
# (A brace after a dollar sign is a shell variable written into the script, ${n}, and no command.)
SED_NEXT_LINE = re.compile(r"(?:^|;|(?<!\$)\{)\s*[nN]\s*(?:;|\}|$)")
# One line named by its number, or the last by $: 129s/a/b/  12d  3{...}  $d  7!d  5a\text
SED_NUMBER = re.compile(r"^\s*(?:\d+|\$)\s*[a-zA-Z!{]")


def simple_commands(command: str):
    """The word lists of the simple commands a shell command runs, split where the shell splits them (a new
    line, ; & | and parentheses outside quotes), quoted words kept whole and heredoc bodies left out."""
    lines, kept, end = command.split("\n"), [], None
    for line in lines:
        if end is not None:
            end = None if line.strip() == end else end
            continue
        kept.append(line)
        match = HEREDOC.search(line)
        end = match.group(2) if match else None
    lexer = shlex.shlex("\n".join(kept), posix=True, punctuation_chars=True)
    lexer.whitespace = " \t\r"
    lexer.commenters = ""
    # Everything that is no space, quote, backslash or operator is part of a word: 12,15d is one word.
    lexer.wordchars = "".join(chr(code) for code in range(33, 127) if chr(code) not in "\"'\\();<>|&")
    commands, words = [], []
    try:
        for token in lexer:
            if token == "\n" or (token and set(token) <= set("();<>|&")):
                commands.append(words)
                words = []
            else:
                words.append(token)
    except ValueError:
        pass
    return [words for words in commands + [words] if words]


def sed_scripts(command: str):
    """[(scripts, files)] for each `sed` with -i that a shell command runs: its script words (each -e, else
    the first word that is no option) and the files it edits."""
    found = []
    for words in simple_commands(command):
        # Variable assignments and wrappers before the program, as for a git command below.
        while words and (re.match(r"^\w+=", words[0]) or words[0] in ("env", "nohup", "time", "command", "sudo", "xargs")):
            words = words[1:]
        if not words or words[0] != "sed":
            continue
        words = words[1:]
        if not any(re.fullmatch(r"-[a-zA-Z]*i.*|--in-place.*", word) for word in words):
            continue
        plain = [word for i, word in enumerate(words) if not word.startswith("-") and (i == 0 or words[i - 1] != "-e")]
        scripts = [words[i + 1] for i, word in enumerate(words[:-1]) if word == "-e"] or plain[:1]
        found.append((scripts, plain if "-e" in words else plain[1:]))
    return found


def sed_in_place(command: str):
    """The reason when sed edits a source file in place over lines it does not name by their text: a range of
    lines, a step to the next line, or a line by its number. Such an edit left an old line in a test, and one
    by number removed a docstring's closing quotes, so that every test file failed to import; both were found
    only at the next run. Of 956 in-place sed edits of source in this project's sessions, 83 were by a range,
    4 with a next-line step and 262 by a line number (10 October 2026)."""
    for scripts, files in sed_scripts(command):
        prose = next((name for name in files if name.endswith(".md")), None)
        if prose:
            # Whatever the script: AGENTS.md has prose replaced with the tool that reads across line breaks.
            return (f"sed -i edits wrapped prose ({prose}): a pattern that a line break splits matches nothing and "
                    "sed says nothing. Replace the passage with tools/replace_text.py FILE OLD_FILE NEW_FILE, which "
                    "matches across line breaks, or make an exact edit with the Edit tool; then rewrap with "
                    "tools/rewrap_md.py")
        # A notebook or an entry draft is prose too: on 16 October 2026 a session replaced sentences of entry drafts
        # with sed substitutions a dozen times, where a pattern that misses says nothing.
        # A commit message is wrapped prose too: on 16 October 2026 two sed substitutions in rewrapped commit
        # messages matched nothing across a line break and said nothing.
        message = next((name for name in files if re.search(r"(?:^|/)(?:commit|msg)[^/]*\.txt$", name)), None)
        if message and any(re.search(r"(?:^|[;}\s])s(.).*\1.*\1", script) for script in scripts):
            return (f"sed -i substitutes in a wrapped commit message ({message}): a pattern that a line break "
                    "splits matches nothing and sed says nothing. Rewrite the message with the Write tool, or "
                    "replace a passage with tools/replace_text.py FILE OLD_FILE NEW_FILE, then rewrap it")
        page = next((name for name in files if name.endswith(".html")), None)
        if page and any(re.search(r"(?:^|[;}\s])s(.).*\1.*\1", script) for script in scripts):
            return (f"sed -i replaces prose in a page ({page}): a pattern that misses matches nothing and sed says "
                    "nothing. Make the edit with the Edit tool, which fails when the old text is not there, or "
                    "replace a passage with tools/replace_text.py FILE OLD_FILE NEW_FILE (AGENTS.md)")
        if not any(SED_SOURCE.search(name) for name in files):
            continue
        for part in (part for script in scripts for part in re.split(r";\s*", script)):
            how = ("over a range of lines" if SED_RANGE.match(part) else
                   "over a step to the next line" if SED_NEXT_LINE.search(part) else
                   "at a line named by its number" if SED_NUMBER.match(part) else None)
            if how:
                return (f"sed -i edits a source file {how} ({part.strip()[:60]}), lines it never shows: a wrong "
                        "one is found only when something later fails. Make the edit with the Edit tool, which "
                        "takes the old text and fails when it is not there")
    return None


def tool_removed(command: str):
    """The reason when rm deletes a file under tools/: a helper written there serves a job that recurs by
    nature, and on 16 October 2026 a browser retrieval tool was deleted after its first use failed, although
    the next source would need it (user: "It will be needed in the future..."). A tool is kept, tested and
    committed; one that is wrong is fixed, and one that is truly obsolete is removed with git rm, in a commit
    that says why."""
    for words in simple_commands(command):
        while words and (re.match(r"^\w+=", words[0]) or words[0] in ("env", "command", "sudo", "xargs")):
            words = words[1:]
        if not words or words[0] not in ("rm", "unlink", "shred"):
            continue
        for word in words[1:]:
            if not word.startswith("-") and re.search(r"(^|/)tools/[^/]", word):
                return (f"rm deletes {word}, a framework tool: keep it, make it work and commit it with a test, "
                        "since retrieval and similar jobs recur; remove an obsolete one with git rm in a commit "
                        "that says why")
    return None


def sed_ampersand(command: str):
    """The reason when an in-place sed substitution has an unescaped & in its replacement: sed inserts the
    whole match there, so a replacement holding an HTML entity such as &lt; pastes the matched text into
    the file. Twice on 16 October 2026 this garbled a notebook entry without any error."""
    for scripts, _files in sed_scripts(command):
        for script in scripts:
            for start in (m.start() for m in re.finditer(r"(?:^|[;\s}])s(?=[^\w\s\\])", script)):
                at = start + (0 if script[start] == "s" else 1)
                delim = script[at + 1]
                fields, field, i = [], "", at + 2
                while i < len(script) and len(fields) < 2:
                    if script[i] == "\\" and i + 1 < len(script):
                        field += script[i:i + 2]
                        i += 2
                        continue
                    if script[i] == delim:
                        fields.append(field)
                        field = ""
                    else:
                        field += script[i]
                    i += 1
                if len(fields) == 2 and re.search(r"(?<!\\)&", fields[1]):
                    return ("sed -i has an unescaped & in a replacement, which sed replaces by the whole match "
                            f"({fields[1][:60]}): escape it as \\& or make the edit with the Edit tool")
    return None


# A writer of --out FILE with its errors discarded: on 16 October 2026 tools/notebook-excerpt.py refused to replace
# an existing excerpt ("File exists") behind "> /dev/null 2>&1", and a reviewer read the previous review's excerpt.
WRITER_SILENCED = re.compile(r"\s--out[\s=][^;&|\n]*?(?:2>\s*/dev/null|&>\s*/dev/null|2>&1\s*>\s*/dev/null|"
                             r">\s*/dev/null\s+2>&1)")
STAGING_SILENCED = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?(?:add|commit)\b[^;&|\n]*?(?:2>\s*/dev/null|&>\s*/dev/null|2>&1\s*>\s*/dev/null|>\s*/dev/null\s+2>&1)")


def staging_silenced(command: str):
    """A git add or commit whose errors are thrown away: on 11 October 2026 a path that did not exist was staged
    with the error discarded, nothing was staged and the commit failed two steps later."""
    kept, end = [], None
    for line in command.split("\n"):   # a heredoc's body is text, not a command
        if end is not None:
            end = None if line.strip() == end else end
            continue
        kept.append(line)
        match = HEREDOC.search(line)
        end = match.group(2) if match else None
    if STAGING_SILENCED.search("\n".join(kept)):
        return ("git add and git commit run with their errors shown: a discarded error hides a path that does not "
                "exist or a refused commit. Drop the redirection of stderr")
    if WRITER_SILENCED.search("\n".join(kept)):
        return ("a command that writes --out FILE runs with its errors shown: a discarded error hides a refused "
                "write (FILE exists, a bad argument), and the old FILE is then read as new. Keep stderr; drop only "
                "stdout with > /dev/null")
    return None


def blocked(command: str):
    """Return the reason for the first filtered must-read command, or None."""
    for segment in SEPARATOR.split(shell_code(command)):
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
        # A timeout set above a minute says the run may take that long: four runs of a model on 32 windows were
        # each given just under the limit above and held the turn for a minute or two apiece.
        if seconds("--timeout") > FOREGROUND_EXPECT and "--expect" not in options:
            return (f"a compute.sh run allowed over {FOREGROUND_EXPECT} s goes to the background (run_in_background: "
                    f"true) unless it is expected to end within {FOREGROUND_EXPECT} s: say so with --expect SECONDS, which "
                    "the launcher prints against the time it took, or start it in the background and keep working "
                    "(COMPUTATION_RULES.md, long runs; user, 11 October 2026)")
    return None


# A download whose length depends on the network: a repository clone or an image pull, run at the start of a segment.
DOWNLOAD = re.compile(r"^\s*(?:(?:do|then|else)\s+)?\(*\s*(?:\w+=\S*\s+)*(?:(?:env|nohup|time)\s+)*"
                      r"(?:git(?:\s+-C\s+\S+)?\s+clone\b|glab\s+repo\s+clone\b|docker\s+(?:image\s+)?pull\b)")


def foreground_download(command: str, background: bool):
    """A clone or pull started in the foreground, which blocks the turn while other work could go on."""
    # A help request downloads nothing.
    if background or not any(DOWNLOAD.match(segment) and not re.search(r"\s(?:--help|-h)\b", segment)
                             for segment in SEPARATOR.split(command)):
        return None
    return ("a clone or an image pull goes to the background (run_in_background: true); keep working meanwhile "
            "and use its result when it finishes (user, 6 October 2026: \"Why are you not putting this stuff to "
            "background yourself\")")


# A segment's start, quoted strings emptied, up to the program it runs: assignments, env/nohup/time/timeout
# wrappers, `uv run`, and an interpreter with its options, `-m` among them.
PROGRAM = re.compile(r"^\s*(?:(?:do|then|else)\s+)?\(*\s*(?:\w+=\S*\s+)*"
                     r"(?:(?:env|nohup|time|timeout\s+\S+)\s+)*(?:uv\s+run\s+(?:-\S+\s+)*)?"
                     r"(?:\S*python[\d.]*\s+(?:-\S+\s+)*|(?:ba)?sh\s+)?([^\s;&|()]+)")
TEST_RUNNERS = {"pytest", "py.test", "unittest", "api-tests.sh", "suite_tips.sh"}


def shell_code(command: str):
    """The command without heredoc bodies and with quoted strings emptied, so that only what the shell runs
    as commands is left to split into segments."""
    lines, kept, end = command.split("\n"), [], None
    for line in lines:
        if end is not None:
            end = None if line.strip() == end else end
            continue
        kept.append(line)
        match = HEREDOC.search(line)
        end = match.group(2) if match else None
    return re.sub(r"\"(?:\\.|[^\"\\])*\"|'[^']*'", '""', "\n".join(kept))


def unprotected_workload(command: str):
    """A test runner, the framework suite or a scratchpad script run outside compute.sh."""
    for segment in re.split(r"\|\||&&|;|\n|\|", shell_code(command)):
        match = PROGRAM.match(segment)
        program = match.group(1) if match else ""
        # A segment that only assigns a variable (S=path) runs nothing.
        if re.match(r"\w+=", program):
            continue
        # A test module run as a program (python3 tools/tests/test_x.py) is a test runner too.
        if (program.rsplit("/", 1)[-1] in TEST_RUNNERS or program.endswith("tests/run.py")
                or re.search(r"(^|/)tests?/test_[^/\s]*\.py$", program)
                or (re.search(r"scratchpad/\S*\.(?:py|sh)$", program))):
            return (f"{program} runs a workload, which goes through ./compute.sh, small runs and other "
                    "repositories' tests included (COMPUTATION_RULES.md, enforced execution; user, 8 October "
                    "2026): run it as ./compute.sh [--threads N] [--timeout S] PROGRAM ... from the directory it "
                    "needs, calling compute.sh by its path there, with environment variables inside the command "
                    "(env NAME=VALUE PROGRAM ...), and read the saved log")
    return None


# git subcommands that read the revisions they are given.
GIT_READS = {"show", "diff", "log", "cat-file", "rev-parse", "merge-base", "ls-tree", "grep", "rev-list",
             "range-diff", "cherry", "shortlog", "blame", "diff-tree", "archive", "rebase", "merge",
             "cherry-pick", "describe", "whatchanged", "format-patch", "name-rev", "show-branch"}
FRESH = 600   # seconds since the upstream's last fetch or push
# A reflog line's time: "<old> <new> Name <email> <seconds> <zone>\t<message>".
REFLOG_TIME = re.compile(r"> (\d+) [+-]\d{4}\t")


def _git(repo, *args):
    run = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    return run.stdout if run.returncode == 0 else None


def _ref_names(arg):
    """The names a revision argument can start from: ranges split, a :path and ~ ^ @{} suffixes cut."""
    names = []
    for part in re.split(r"\.\.\.?", arg):
        part = re.sub(r"(?:[~^]\d*|\^\{[^}]*\}|@\{[^}]*\})+$", "", part.split(":", 1)[0])
        if part:
            names.append(part)
    return names


def _last_update(git_dirs, tracking, url):
    """When `tracking` (remote/branch) was last fetched or pushed to: its reflog's last entry, or a
    FETCH_HEAD naming its branch of its remote, which a fetch writes even when nothing changed."""
    times = []
    common = git_dirs[-1]
    try:
        lines = Path(common, "logs/refs/remotes", tracking).read_text().splitlines()
        match = REFLOG_TIME.search(lines[-1]) if lines else None
        if match:
            times.append(int(match.group(1)))
    except OSError:
        pass
    branch = tracking.split("/", 1)[1]
    tail = re.sub(r"\.git$", "", url).split(":")[-1]
    for directory in git_dirs:
        path = Path(directory, "FETCH_HEAD")
        try:
            if any(f"branch '{branch}' of " in line and line.endswith(tail) for line in path.read_text().splitlines()):
                times.append(path.stat().st_mtime)
        except OSError:
            pass
    return max(times, default=None)


def _remotes_written(refspecs):
    """The remotes whose tracking refs a fetch's refspecs write: a fetch by address with
    '+refs/heads/*:refs/remotes/origin/*', the form used where the remote's own address cannot be reached,
    is a fetch of origin. Without such a refspec a fetch by address updates no tracking ref and counts for none."""
    return {match.group(1) for spec in refspecs for match in [re.search(r":refs/remotes/([^/*]+)/", spec)] if match}


def _stale(repo, names, fetched, now):
    refs = _git(repo, "for-each-ref", "--format=%(refname)%00%(upstream)%00%(symref)", "refs/heads", "refs/remotes")
    dirs = _git(repo, "rev-parse", "--path-format=absolute", "--git-dir", "--git-common-dir")
    if refs is None or dirs is None:
        return None
    upstream, remote_refs = {}, {}
    for line in refs.splitlines():
        ref, up, target = line.split("\0")
        if ref.startswith("refs/heads/"):
            upstream[ref[len("refs/heads/"):]] = up
        else:
            # A symbolic one, such as origin/HEAD, reads its target.
            remote_refs[ref[len("refs/remotes/"):]] = (target or ref)[len("refs/remotes/"):]
    head = (_git(repo, "symbolic-ref", "-q", "--short", "HEAD") or "").strip()
    for name in names:
        if name in upstream and name != head and upstream[name].startswith("refs/remotes/"):
            tracking = upstream[name][len("refs/remotes/"):]
        elif name in remote_refs:
            tracking = remote_refs[name]
        else:
            continue
        remote, branch = tracking.split("/", 1)
        if remote in fetched or "*" in fetched:
            continue
        local = f" (fetch {remote} {branch}:{branch} also fast-forwards the local {name})" if name in upstream else ""
        last = _last_update(dirs.split(), tracking, (_git(repo, "config", f"remote.{remote}.url") or "").strip())
        if last is None or now - last > FRESH:
            when = ("with no fetch or push recorded here" if last is None
                    else f"last fetched or pushed {int((now - last) // 60)} minutes ago")
            subject = f"`{name}` follows {tracking}," if name != tracking else f"`{name}` is"
            return (f"{subject} {when}, and another clone may have moved it, so what this "
                    f"command reads can be out of date. Fetch it first, in the same command if you like: "
                    f"git -C {repo} fetch {remote} {branch}{local}")
        if name in upstream and _git(repo, "merge-base", "--is-ancestor", f"refs/remotes/{tracking}",
                                     f"refs/heads/{name}") is None:
            return (f"the local `{name}` is behind or apart from {tracking}: read {tracking}, or fast-forward "
                    f"`{name}` with git -C {repo} fetch {remote} {branch}:{branch}")
    return None


def stale_branch(command: str, cwd: str, now: float):
    """The reason when a git command reads another branch whose upstream isn't fresh here, or None."""
    fetched = set()
    for segment in re.split(r"\|\|?|&&|;|\n", command):
        try:
            words = shlex.split(segment)
        except ValueError:
            continue
        # Variable assignments and wrappers (timeout DURATION, env, nohup, time, command) before the program.
        while words and (re.match(r"^\w+=", words[0]) or words[0] in ("env", "nohup", "time", "command", "timeout")):
            words = words[2:] if words[0] == "timeout" else words[1:]
        if len(words) > 1 and words[0] == "cd":
            cwd = os.path.join(cwd, os.path.expanduser(words[1]))
            continue
        if not words or words[0] != "git":
            continue
        i, repo = 1, cwd
        while i < len(words) and words[i].startswith("-"):
            if words[i] in ("-C", "-c") and i + 1 < len(words):
                if words[i] == "-C":
                    repo = os.path.join(repo, os.path.expanduser(words[i + 1]))
                i += 2
            else:
                i += 1
        if i >= len(words):
            continue
        sub, args = words[i], words[i + 1:]
        if sub in ("fetch", "pull"):
            given = [a for a in args if not a.startswith("-")]
            # A fetch naming no remote, or --all, may fetch any.
            fetched.add(given[0] if given else "*")
            fetched.update(_remotes_written(given[1:]))
            continue
        if sub not in GIT_READS:
            continue
        if "--" in args:
            args = args[:args.index("--")]
        names = [name for arg in args if not arg.startswith("-") for name in _ref_names(arg)]
        reason = _stale(repo, names, fetched, now) if names else None
        if reason:
            return reason
    return None


# A file a command writes by redirection or tee: "> f", ">> f", "2> f", "&> f", "tee -a f"; not ">&1" or /dev/null.
WRITTEN = re.compile(r"(?:(?<![<>&\w])(?:\d|&)?>>?\s*|\btee\s+(?:-a\s+)?)([^\s;&|<>()'\"]+)")


def unwritten_notice(command):
    """The notice, for a refused command, of the files it would have written, or None. On 16 October 2026 a
    commit message was written by a command the guard refused, and the next command appended to the old file
    and committed its stale subject: a refusal says nothing ran, but not which files are therefore unchanged."""
    paths = [p for p in dict.fromkeys(WRITTEN.findall(command)) if p != "/dev/null" and not p.startswith("&")]
    if not paths:
        return None
    return ("Nothing in the refused command ran, so these files were not written or changed: " + ", ".join(paths) +
            ". A later command that reads them reads what they held before.")


def main() -> int:
    status = check()
    if status == 2 and COMMANDS:
        notice = unwritten_notice(COMMANDS[-1])
        if notice:
            print(notice, file=sys.stderr)
    return status


def check() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command") or ""
    COMMANDS.append(command)
    background = bool(tool_input.get("run_in_background"))
    reason = (foreground_long_run(command, background) or foreground_download(command, background)
              or unprotected_workload(command))
    if reason:
        print(f"Refused: {reason}.", file=sys.stderr)
        return 2
    reason = (unchained_heredoc(command) or adhoc_replace_helper(command) or tool_removed(command) or sed_in_place(command)
              or sed_ampersand(command) or staging_silenced(command)
              or existing_result_folder(command, payload.get("cwd") or os.getcwd())
              or stale_branch(command, payload.get("cwd") or os.getcwd(), time.time()))
    if reason:
        print(f"Refused: {reason}.", file=sys.stderr)
        return 2
    reason = blocked(command)
    if reason:
        print(f"Run this command bare and read its output in full: {reason}. Do not pipe it "
              "through head, tail, sed or grep or redirect it.", file=sys.stderr)
        return 2
    if "git" in command and "commit" in command:
        # A long autonomous turn never reaches the Stop hook: its promises are checked at each commit.
        import during_run
        reason = during_run.commit(payload) or cannot_fail_tests()
        if reason:
            print(reason, file=sys.stderr)
            SAID.append(reason)
            return 2
    return 0


def cannot_fail_tests(run=subprocess.run, notice=sys.stderr):
    """The refusal of a commit that adds a framework test which still passes with every tool function it calls
    stubbed to a wrong value or a refusal (tools/test_can_fail.py), or None. On 16 October 2026 a new test
    compared an immutable string with itself, and only the reviewer caught it. It runs only in a Claude Code
    session of this checkout (Codex sessions do not get it), outside ./compute.sh since it runs only the
    commit's new tests; when the check times out or fails without a verdict, the commit goes through with a
    notice saying so."""
    tool = Path(__file__).resolve().parents[1] / 'test_can_fail.py'
    # Only in a session of this checkout, as the block log does: a test of the guard leaves the variable unset
    # or names another directory, and must not run the check against the repository's working tree.
    project = os.environ.get('CLAUDE_PROJECT_DIR')
    if not tool.exists() or not (project and tool.resolve().is_relative_to(Path(project).resolve())):
        return None
    try:
        done = run([sys.executable, str(tool), '--base', 'HEAD'], cwd=str(tool.parents[1]), capture_output=True,
                   text=True, timeout=60)
    except subprocess.TimeoutExpired:
        print('Notice: tools/test_can_fail.py timed out after 60 s; the commit is not checked for tests that '
              'cannot fail.', file=notice)
        return None
    flagged = [line for line in done.stdout.splitlines() if line.startswith('CANNOT FAIL')]
    if done.returncode == 1 and flagged:
        return ('Refused: a test this commit adds cannot fail (tools/test_can_fail.py):\n' + '\n'.join(flagged) +
                '\nMake its assertions depend on what the tool returns, or test the tool through a call the '
                'check can stub.')
    if done.returncode != 0:
        print('Notice: tools/test_can_fail.py failed without a verdict (exit status '
              f'{done.returncode}): ' + (done.stderr or done.stdout).strip()[-300:], file=notice)
    return None


SAID = []   # what the commit's checks said when they blocked, for the block log
COMMANDS = []   # the command checked, whose named files the block log keeps


def replay_silenced(paths):
    """Print each past Bash command of the session transcripts at `paths` that staging_silenced refuses, with the
    count: a refusal on a command's words is counted over past commands before it is committed (AGENTS.md)."""
    found, commands, read = [], 0, 0
    for name in paths:
        with open(name, errors="replace") as stream:
            for line in stream:
                read += len(line)
                if '"Bash"' not in line or "/dev/null" not in line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                content = (entry.get("message") or {}).get("content") if isinstance(entry, dict) else None
                for part in content if isinstance(content, list) else []:
                    if isinstance(part, dict) and part.get("type") == "tool_use" and part.get("name") == "Bash":
                        commands += 1
                        command = str((part.get("input") or {}).get("command", ""))
                        reason = staging_silenced(command)
                        if reason:
                            found.append((entry.get("timestamp", ""), reason.split(":")[0], " ".join(command.split())[:120]))
    for when, kind, start in found:
        print(f"{when}\t{kind}\t{start}")
    print(f"{len(found)} refused of {commands} Bash commands that mention /dev/null, in {len(paths)} transcripts "
          f"({read / 1e6:.0f} MB read).")


if __name__ == "__main__" and sys.argv[1:2] == ["--replay-silenced"]:
    replay_silenced(sys.argv[2:])
    sys.exit(0)

if __name__ == "__main__":
    status = main()
    if status == 2:
        import block_log
        block_log.record("bash_guard", what=''.join(SAID), paths=block_log.paths_in(''.join(COMMANDS)))
    sys.exit(status)
