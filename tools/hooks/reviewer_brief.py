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
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import branch_extension

# A whole document handed over to read: "read the whole Path", "the entire theory", "PLAN.md in full".
WHOLE = re.compile(
    r"\b(?:whole|entire)\s+(?:`?Path`?|plan|theory|notebook|record)\b"
    r"|\b(?:PLAN\.md|notebook\.html)`?\s+(?:in full|in its entirety|from start to end)\b"
    r"|\bread\s+all\s+of\s+(?:the\s+)?(?:`?Path`?|plan|theory|notebook)\b", re.I)

# A file named by its full path: /dir/.../name.ext, not a directory and not a pattern.
NAMED_FILE = re.compile(r'(?<![\w.~*-])(/(?:[\w.+-]+/)+[\w+-][\w.+-]*\.[A-Za-z0-9]{1,5})(?![\w/*])')


def refusal(payload, tools=TOOLS):
    """The reason to refuse this tool call, or None."""
    if payload.get('tool_name') != 'Agent':
        return None
    tool_input = payload.get('tool_input') or {}
    if 'review' not in str(tool_input.get('subagent_type', '')).lower():
        return None
    prompt = str(tool_input.get('prompt', ''))
    # A file the brief names by its full path and that is not there: on 11 October 2026 a reviewer was launched
    # in the same step as the command that wrote its brief, the command was refused, and the stage went unanswered.
    missing = [path for path in dict.fromkeys(NAMED_FILE.findall(prompt)) if not Path(path).exists()]
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
