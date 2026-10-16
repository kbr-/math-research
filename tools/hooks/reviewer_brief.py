#!/usr/bin/env python3
"""PreToolUse hook for the Agent tool: refuse a reviewer brief that sends the reviewer to read a whole
plan, Path, theory or notebook.

AGENTS.md has reviewers briefed narrowly: exact files and anchors, and dependency excerpts in a scratch
file. A brief that says "read the whole Path" makes every run pay for the whole document however few
rows it audits: on 9 October 2026 a review of 10 table rows cost about as much as one of 190. The
refusal names the tools that build the excerpt: `tools/notebook-excerpt.py` for the notebook, and a
further one where the branch's own module (tools/branch_extension.py) names it.

It reads the hook's JSON from stdin and acts only on an Agent call whose `subagent_type` names a
reviewer. Exit status 2 refuses the call, with the reason on stderr.
"""
from datetime import datetime, timedelta
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import block_log
import branch_extension

# A whole document handed over to read: "read the whole Path", "the entire theory", "PLAN.md in full".
WHOLE = re.compile(
    r"\b(?:whole|entire)\s+(?:`?Path`?|plan|theory|notebook|record)\b"
    r"|\b(?:PLAN\.md|notebook\.html)`?\s+(?:in full|in its entirety|from start to end)\b"
    r"|\bread\s+all\s+of\s+(?:the\s+)?(?:`?Path`?|plan|theory|notebook)\b", re.I)

# A file named by its full path: /dir/.../name.ext, not a directory and not a pattern.
NAMED_FILE = re.compile(r'(?<![\w.~*-])(/(?:[\w.+-]+/)+[\w+-][\w.+-]*\.[A-Za-z0-9]{1,5})(?![\w/*])')


def missing_files(text):
    """Files named by full path in `text`, or in a brief file (.md or .txt) it names, that do not exist.

    On 16 October 2026 a reviewer was started twice on a brief file that existed while the excerpt files it
    named did not: the command building them had been refused, and the check read only the prompt."""
    named = list(dict.fromkeys(NAMED_FILE.findall(text)))
    missing = [path for path in named if not Path(path).exists()]
    for path in named:
        if path.endswith(('.md', '.txt')) and Path(path).is_file():
            try:
                inner = Path(path).read_text(errors='replace')[:200000]
            except OSError:
                continue
            missing += [p for p in dict.fromkeys(NAMED_FILE.findall(inner)) if not Path(p).exists()
                        and p not in missing]
    return missing


# A message saying a named file now holds a change: "updated", "rewritten", "now written", "corrected".
UPDATE_CLAIM = re.compile(r'\b(?:updated|rewritten|rewrote|now written|corrected|revised)\b', re.I)
# The words by which a message says the file was read back after the refusal, which lets it through.
CHECKED = re.compile(r'\bchecked on disk\b', re.I)


def stale_files(text, log, now=None, window=600):
    """Files named by full path in `text`, which says something was updated, that a call refused by a hook
    within `window` seconds before `now` also named, and that were last written before that refusal.

    On 16 October 2026 a follow-up told a reviewer that a spec was updated when the command writing
    it had been refused, and the reviewer first read the old spec. Only the refused call's own files
    count (the block log keeps them, tools/hooks/block_log.py), so an unrelated refusal or a file the
    message names beside the updated one does not refuse it. Not caught: refusals by hooks other than
    the Bash guard, which record no paths, and files a refused command named by a relative path."""
    if not UPDATE_CLAIM.search(text) or CHECKED.search(text):
        return []
    now = now or datetime.now()
    recent = [(when, set(paths)) for when, _, paths in block_log.blocks(log)
              if 0 <= (now - when).total_seconds() <= window]
    stale = []
    for path in dict.fromkeys(NAMED_FILE.findall(text)):
        if not Path(path).is_file():
            continue
        written = datetime.fromtimestamp(Path(path).stat().st_mtime)
        if any(path in paths and written < when for when, paths in recent):
            stale.append(path)
    return stale


def refusal(payload, tools=TOOLS, log=None, now=None):
    """The reason to refuse this tool call, or None."""
    tool_input = payload.get('tool_input') or {}
    if payload.get('tool_name') == 'SendMessage':
        # A follow-up to a reviewer naming its corrected draft, before the draft is written.
        message = str(tool_input.get('message', ''))
        missing = missing_files(message)
        if missing:
            return 'the message names a file that does not exist: ' + ', '.join(missing) + '. Write it first'
        stale = stale_files(message, log or block_log.LOG, now)
        return (('the message says ' + ', '.join(stale) + ' was updated, but a call naming it was refused '
                 'after it was last written: read it back, write the update again if it is missing, and say '
                 '"checked on disk" in the message') if stale else None)
    if payload.get('tool_name') != 'Agent':
        return None
    if 'review' not in str(tool_input.get('subagent_type', '')).lower():
        return None
    prompt = str(tool_input.get('prompt', ''))
    # A file the brief names by its full path and that is not there: on 11 October 2026 a reviewer was launched
    # in the same step as the command that wrote its brief, the command was refused, and the stage went unanswered.
    missing = missing_files(prompt)
    if missing:
        return ('the brief names a file that does not exist: ' + ', '.join(missing) + '. Write the brief and its '
                'excerpts in one step and launch the reviewer in the next')
    # A brief that sends an entry draft (an .html file) for review also sends the drafted commit message: on
    # 16 October 2026 a commit message called a PK_oplus2 corollary an AC0[2]-Frege bound, outside every text the
    # reviewer read.
    # A draft is an .html file outside the repository (external scratch); pages inside the checkout, such as
    # notebook.html or a site fixture named in a layout review, are not treated as drafts. Not caught: drafts in
    # ignored scratch inside the checkout (research/tmp/, Codex's managed scratch), drafts named by relative
    # paths, drafts sent as .txt or .md excerpts, and commit messages in files whose names do not start with
    # "commit".
    named = list(dict.fromkeys(NAMED_FILE.findall(prompt)))
    repository = tools.resolve().parent
    drafts = [path for path in named if path.endswith('.html')
              and not Path(path).resolve().is_relative_to(repository)]
    messages = [path for path in named if Path(path).name.lower().startswith('commit')
                and Path(path).suffix in ('.txt', '.md', '')]
    if drafts and not messages:
        return ('the brief sends an entry draft but no drafted commit message; write the commit message to a '
                'file whose name starts with "commit" (.txt or .md) and name it in the brief, so the reviewer '
                'reads it beside the entry')
    found = WHOLE.search(prompt)
    if not found:
        return None
    # A further tool that builds an excerpt, where the branch's own module names one.
    table = branch_extension.ask('EXCERPT_TOOL', '', tools)
    return (f'the brief sends the reviewer to read a whole document ("{found.group(0)}"). Brief it narrowly '
            '(AGENTS.md): name the rows or anchors to review and an excerpt file holding what they depend on, '
            f'built with {table}`tools/notebook-excerpt.py ANCHOR --out FILE` for the notebook, and let the '
            'reviewer search the source only for a claim it challenges')


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    reason = refusal(payload)
    if reason:
        print(f'Refused: {reason}.', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    status = main()
    if status == 2:
        import block_log
        block_log.record('reviewer_brief')
    sys.exit(status)
