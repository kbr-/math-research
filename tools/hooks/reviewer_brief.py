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
    if not UPDATE_CLAIM.search(text):
        return []
    now = now or datetime.now()
    recent = [(when, set(paths)) for when, _, paths in block_log.blocks(log)
              if 0 <= (now - when).total_seconds() <= window]
    # A refused call's file counts when the message names it by full path or, a second 16 October 2026 case, by
    # its file name alone ("the spec is spec.json beside it"); "checked on disk" lets through only the files
    # named in its own sentence, since in that case it was said of another file of the same message.
    checked = ' '.join(s for s in re.split(r'(?<=[.;:!?])\s+', text) if CHECKED.search(s))
    refused = {path for _, paths in recent for path in paths}
    named = list(dict.fromkeys(NAMED_FILE.findall(text)))
    # A file name alone stands for a refused file only when no full path in the message has that name: a message
    # naming /worktree/notebook.html is about that file, not about a refused /main/notebook.html.
    full_names = {Path(path).name for path in named}
    named += [path for path in sorted(refused) if path not in named and Path(path).name not in full_names
              and re.search(r'(?<![\w./-])' + re.escape(Path(path).name) + r'(?![\w])', text)]
    stale = []
    for path in named:
        if not Path(path).is_file() or path in checked or re.search(
                r'(?<![\w./-])' + re.escape(Path(path).name) + r'(?![\w])', checked):
            continue
        written = datetime.fromtimestamp(Path(path).stat().st_mtime)
        if any(path in paths and written < when for when, paths in recent):
            stale.append(path)
    return stale


ARTICLE_ID = re.compile(r'<article\b[^>]*\bid="([^"]+)"')


def unread_sentences(text, tools=TOOLS):
    """Entry drafts named in `text`, or in a brief file it names, on which tools/draft_claim_sentences.py has not
    run since they were last written: [path, ...].

    AGENTS.md asks for that run before the reviewer's brief, so that each sentence citing a claim is read beside
    the claim; on 16 October 2026 a review's sentences dropped their claims' qualifiers and the run had been
    skipped, so the reviewer found them instead.  A draft is an .html file holding an article; the tool logs each
    run with the article's id to research/logs/claim-searches.jsonl.  Without that log nothing is checked."""
    log = tools.resolve().parent / 'research' / 'logs' / 'claim-searches.jsonl'
    if not log.is_file():
        return []
    named = list(dict.fromkeys(NAMED_FILE.findall(text)))
    for path in list(named):
        if path.endswith(('.md', '.txt')) and Path(path).is_file():
            try:
                named += NAMED_FILE.findall(Path(path).read_text(errors='replace')[:200000])
            except OSError:
                pass
    runs = {}
    for line in log.read_text(errors='replace').splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        query = str(entry.get('query', ''))
        if query.startswith('draft_counts '):
            ident = query.split()[1]
            runs[ident] = max(runs.get(ident, 0), float(entry.get('unix_s', 0)))
    unread = []
    for path in dict.fromkeys(named):
        if not path.endswith('.html') or not Path(path).is_file():
            continue
        try:
            found = ARTICLE_ID.search(Path(path).read_text(errors='replace')[:20000])
        except OSError:
            continue
        if found and runs.get(found.group(1), 0) < Path(path).stat().st_mtime:
            unread.append(path)
    return unread


SENTENCES_REASON = ('tools/draft_claim_sentences.py has not run on {} since it was last written: run it '
                    '(tools/draft_claim_sentences.py DRAFT --notebook NOTEBOOK) and read each sentence that cites a '
                    'claim beside the claim before the brief (AGENTS.md)')


# A brief asking the reviewer to search the record: on 16 October 2026 two record searches in a row missed a
# registered result, and only the reviewer's own search, in the words of the next attempt's objects, found it;
# a search ranked by the draft's own words (tools/claim_resemblance.py, the agent's queries) did not.
SEARCH = re.compile(r'search-claims|\bclaim searche?s?\b|\brecord searche?s?\b|\bsearch(?:es)? (?:of |in )?the '
                    r'(?:registry|record)\b', re.I)
DENIES = re.compile(r"\b(?:no|not|without|need not|needn't|unnecessary|skip)\b", re.I)


def asks_search(prompt):
    """Whether a sentence of the brief asks for a record search without denying it ("no record search needed"
    cleared the check: the builds' reviewer, 17 October 2026)."""
    # The denial counts only near the request, in the words before it or the three after it: "report the
    # results the draft does not cite" asked for a search and was refused on its "not" (17 October 2026).
    def asked(sentence):
        match = SEARCH.search(sentence)
        if not match:
            return False
        before = sentence[max(0, match.start() - 40):match.start()]
        after = ' '.join(sentence[match.end():].split()[:3])
        return not (DENIES.search(before) or DENIES.search(after))
    return any(asked(s) for s in re.split(r'(?<=[.!?\n])\s+', prompt))


NO_SEARCH_REASON = ('the brief sends an entry draft but asks the reviewer for no record search; ask it to run one '
                    'or two tools/search-claims.py searches in the words of the objects the draft\'s proof or next '
                    'attempt works on, for registered results the draft does not cite')


def brief_replay(lines, tools=TOOLS):
    """[(time, prompt start)] for each reviewer Agent call of a session transcript (JSON lines) whose brief sends
    an entry draft and asks for no record search: the count of the search check's refusals on past briefs."""
    found = []
    for line in lines:
        if '"Agent"' not in line:   # transcripts run to hundreds of megabytes; parse only lines with an Agent call
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = (entry.get('message') or {}).get('content') if isinstance(entry, dict) else None
        if not isinstance(content, list):
            continue
        for part in content:
            if not (isinstance(part, dict) and part.get('type') == 'tool_use' and part.get('name') == 'Agent'):
                continue
            tool_input = part.get('input') or {}
            if 'review' not in str(tool_input.get('subagent_type', '')).lower():
                continue
            prompt = str(tool_input.get('prompt', ''))
            if research_drafts(prompt, tools) and not asks_search(prompt):
                found.append((entry.get('timestamp', ''), ('asks to search' if re.search(r'\bsearch', prompt, re.I)
                              else 'no search word') + ': ' + ' '.join(prompt.split())[:100]))
    return found


def research_drafts(prompt, tools=TOOLS):
    """The entry drafts a brief names: .html files outside the repository holding a research or review article.
    A framework tool's review names other pages (16 October 2026: the one such brief the replay flagged)."""
    repository = tools.resolve().parent
    drafts = []
    for path in dict.fromkeys(NAMED_FILE.findall(prompt)):
        if not path.endswith('.html') or Path(path).resolve().is_relative_to(repository):
            continue
        try:
            text = Path(path).read_text(errors='replace')[:20000]
        except OSError:
            continue
        if re.search(r'<article[^>]*data-kind="(?:research|review)"', text):
            drafts.append(path)
    return drafts


def refusal(payload, tools=TOOLS, log=None, now=None):
    """The reason to refuse this tool call, or None."""
    tool_input = payload.get('tool_input') or {}
    if payload.get('tool_name') == 'SendMessage':
        # A follow-up to a reviewer naming its corrected draft, before the draft is written.
        message = str(tool_input.get('message', ''))
        missing = missing_files(message)
        if missing:
            return 'the message names a file that does not exist: ' + ', '.join(missing) + '. Write it first'
        unread = unread_sentences(message, tools)
        if unread:
            return SENTENCES_REASON.format(', '.join(unread))
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
    unread = unread_sentences(prompt, tools)
    if unread:
        return SENTENCES_REASON.format(', '.join(unread))
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
    if research_drafts(prompt, tools) and not asks_search(prompt):
        return NO_SEARCH_REASON
    found = WHOLE.search(prompt)
    if not found:
        return None
    # A further tool that builds an excerpt, where the branch's own module names one.
    table = branch_extension.ask('EXCERPT_TOOL', '', tools)
    return (f'the brief sends the reviewer to read a whole document ("{found.group(0)}"). Brief it narrowly '
            '(AGENTS.md): name the rows or anchors to review and an excerpt file holding what they depend on, '
            f'built with {table}`tools/notebook-excerpt.py ANCHOR --out FILE` for the notebook, and let the '
            'reviewer search the source only for a claim it challenges')


def replay(lines, log=None, covered=None):
    """[(time, message start, stale files)] for each SendMessage of a session transcript (JSON lines) that the
    stale-file check refuses at the message's own time, against the block log: the count of its refusals on past
    messages, before a change to it is committed (AGENTS.md). File times are read now, so a file written after
    the message hides a refusal it would then have had, false or right, and only messages with a refused call in
    the block log within the window before them can be refused at all (`covered`, a list, collects their times):
    the count is a lower bound under the current file times and block-log coverage, not a false-refusal count."""
    found = []
    for line in lines:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = (entry.get('message') or {}).get('content') if isinstance(entry, dict) else None
        if not isinstance(content, list) or not entry.get('timestamp'):
            continue
        when = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00')).astimezone().replace(tzinfo=None)
        for part in content:
            if isinstance(part, dict) and part.get('type') == 'tool_use' and part.get('name') == 'SendMessage':
                message = str((part.get('input') or {}).get('message', ''))
                stale = stale_files(message, log or block_log.LOG, when)
                if covered is not None and any(0 <= (when - at).total_seconds() <= 600
                                               for at, _, _ in block_log.blocks(log or block_log.LOG)):
                    covered.append(when)
                if stale:
                    found.append((when, ' '.join(message.split())[:120], stale))
    return found


def main():
    if sys.argv[1:2] == ['--replay-briefs']:
        found, calls, read, size = [], 0, 0, 0
        for name in sys.argv[2:]:
            size += Path(name).stat().st_size
            with open(name, errors='replace') as stream:
                kept = []
                for line in stream:
                    read += 1
                    if '"Agent"' in line:
                        calls += line.count('"name":"Agent"') + line.count('"name": "Agent"')
                        kept.append(line)
                found += brief_replay(kept)
        for when, start in found:
            print(f'{when}\t{start}')
        print(f'{len(found)} reviewer briefs sending a draft without a record search, of {calls} Agent calls in '
              f'{len(sys.argv) - 2} transcripts ({read} lines, {size / 1e6:.0f} MB read).')
        return 0
    if sys.argv[1:2] == ['--replay']:
        lines = Path(sys.argv[2]).read_text(errors='replace').splitlines()
        covered = []
        found = replay(lines, covered=covered)
        for when, start, stale in found:
            print(f'{when.isoformat(timespec="seconds")}\t{", ".join(stale)}\t{start}')
        sends = sum(line.count('"name":"SendMessage"') + line.count('"name": "SendMessage"') for line in lines)
        print(f'{len(found)} of {sends} SendMessage calls would be refused ({len(lines)} transcript lines read); '
              f'{len(covered)} had a refused call in the block log within 600 s before them; a lower bound under '
              'the current file times and block-log coverage, not a false-refusal count.')
        return 0
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
