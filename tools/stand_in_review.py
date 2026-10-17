#!/usr/bin/env python3
"""A stand-in for the user's review of a session's work, run at a checkpoint and at most once in 20 minutes.

Usage: tools/stand_in_review.py [--transcript FILE] [--minutes N] [--force]     run it if it is due
       tools/stand_in_review.py --unanswered                                    the review an entry still owes an answer
       tools/stand_in_review.py --answered                                      that review was answered

A reviewer with no memory of the session (Opus, tools/haiku_judge.py's call) reads the rules the work is held
to, then the instruction to check whether they were followed, then what the assistant wrote since the reviewer
last ran, from the session's Claude Code transcript; at its first run, the last two hours. The rules are the
rules file the branch keeps as a skill, where it has one, and AGENTS.md otherwise. It lists at most five things
the user would object to, each with a quote of that text; an objection whose quote is not in the text is
dropped. They are printed and kept under research/logs/stand-in-review/, which git ignores.

It runs only when it has not run for --minutes (40 at the finisher; a tool with shorter cycles gives fewer),
so checkpoints made in quick succession share one review, of everything since the last. The next
entry answers each objection in a paragraph starting "Review." (the tool that runs the review, such as
tools/finish-turn.py, refuses an entry without one while a review is unanswered): fixed, queued, or wrong and
why. Measured on two long sessions (10 and 11 October 2026): of ten sampled objections about seven held
against the record in the first; in the second, a research session, three held, five held in the main with a
detail wrong and one misread the text. So each is checked against the record before it is acted on. It made
the same point as 4 of 18 and 2 of 12 of the user's own corrections, each match in a review that ran after
the user had spoken, so those figures are upper bounds.

It reads a Claude Code transcript or a Codex session file, whichever the running session writes. It never
fails a checkpoint: no transcript, no rules, a model that gives no verdict are said and passed, and outside
both kinds of session it does not run, since the transcript it would find is another session's. A
branch turns it off with a line "review" in tools/hooks/checks_off. A run takes about 20 s.
"""
import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import sys

sys.path[:0] = [str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parent / 'hooks')]
import haiku_judge
import stop_checks

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'claude-opus-5-5'
SKILL = 'skills/engineering-discipline/SKILL.md'
# The rules the reviewer is given, the first that exists, with the words the instruction calls them by.
RULES = ((SKILL, dict(what='skill', were='was', these='it', are='is')),
         ('AGENTS.md', dict(what='rules', were='were', these='they', are='are')))
STATE = 'research/logs/stand-in-review'
MINUTES = 20
FIRST = timedelta(hours=2)      # what the first review reads
CAP = 120_000                   # characters of text given, the end kept
BLOCK = 1 << 20
TIMEOUT = 180

PROMPT = '''{skill}

Check whether the {what} above {were} followed during the stretch of work reported below. The text is what an
assistant wrote about its work over the last stretch of a long session: several work cycles, in order, each
ended by a checkpoint. You stand in for the engineer whose {what} {these} {are}. List what he would object to: where a
directive of the {what} was not followed, and anything else he would not let pass (an unmeasured claim, a
mistake fixed with no prevention, an anomaly passed over, a question left to him that the assistant should
have settled, work stopped that should have gone on, anything unclear). You see only this text, not the record
it cites: where a sentence's support lies in a cited file or entry, object to what the text leaves unclear about
it, not to a status you cannot see (a bound the text calls checked numerically may be proved in the entry). At
most five, the strongest first; none if nothing.
Answer with JSON only: {{"objections": [{{"quote": "<words copied exactly from the text, one line of it>",
"objection": "<one sentence, as he would say it>"}}]}}

THE ASSISTANT'S TEXT:
{text}
'''


def written_since(transcript, since):
    """The assistant's own text in a transcript from the time `since` on, oldest first. The file is read
    backwards from its end, in blocks, only as far as that time."""
    start_text = since.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
    found, tail = [], b''
    with open(transcript, 'rb') as stream:
        end = stream.seek(0, 2)
        while end > 0:
            start = max(0, end - BLOCK)
            stream.seek(start)
            lines = (stream.read(end - start) + tail).split(b'\n')
            tail, lines = (lines[0], lines[1:]) if start else (b'', lines)
            older = False
            for line in reversed(lines):
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(entry, dict):
                    continue
                if str(entry.get('timestamp') or start_text) < start_text:
                    older = True
                    break
                text = own_text(entry)
                if text:
                    found.append(text)
            if older:
                break
            end = start
    return found[::-1]


def own_text(entry):
    """What the session's own agent wrote in one record of a Claude Code transcript or of a Codex session
    file; '' for a subagent's text, a tool's output, the user's words and the agent's private reasoning."""
    message = entry.get('message') if isinstance(entry.get('message'), dict) else {}
    payload = entry.get('payload') if isinstance(entry.get('payload'), dict) else {}
    if entry.get('type') == 'assistant' and not entry.get('isSidechain'):
        parts = message.get('content')
    elif entry.get('type') == 'response_item' and payload.get('type') == 'message' and payload.get('role') == 'assistant':
        parts = payload.get('content')
    else:
        return ''
    # A part that is no text (a tool call, the reasoning) has no text of its own.
    return '\n'.join(str(part.get('text') or '') for part in parts if isinstance(part, dict)).strip() if isinstance(parts, list) else ''


def session_transcript(root, home=None, env=None):
    """The file the running session writes what it says to, or None where none can be told for sure: inside
    a Codex session, the one session file named by its thread; inside a Claude Code session, that session's
    transcript among those of `root`, or the last written there. Outside both, None: the last transcript of a
    directory is some other session's."""
    env, home = os.environ if env is None else env, home or Path.home()
    if env.get('CODEX_THREAD_ID') and not env.get('CLAUDE_CODE_SESSION_ID'):
        sessions = Path(env.get('CODEX_HOME') or home / '.codex') / 'sessions'
        found = list(sessions.rglob(f"*-{env['CODEX_THREAD_ID']}.jsonl")) if re.fullmatch(r'[0-9a-fA-F-]{36}', env['CODEX_THREAD_ID']) else []
        return found[0] if len(found) == 1 else None
    if not env.get('CLAUDECODE'):
        return None
    folder = home / '.claude' / 'projects' / re.sub(r'[^A-Za-z0-9]', '-', str(root))
    own = folder / f"{env.get('CLAUDE_CODE_SESSION_ID', '')}.jsonl"
    found = sorted(folder.glob('*.jsonl'), key=lambda path: path.stat().st_mtime)
    return own if own.is_file() else found[-1] if found else None


def squeezed(text):
    return ' '.join(text.split()).lower()


def state_of(root):
    try:
        return json.loads((Path(root) / STATE / 'state.json').read_text())
    except (OSError, ValueError):
        return {}


def keep(root, state):
    folder = Path(root) / STATE
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'state.json').write_text(json.dumps(state, indent=1) + '\n')


def review(root, transcript, now, minutes=MINUTES, force=False, ask=haiku_judge.ask):
    """Run the review if it is due; the lines to print."""
    if 'review' in stop_checks.checks_off(root):
        return []
    state = state_of(root)
    last = datetime.fromisoformat(state['fired']) if state.get('fired') else None
    if last and not force and now - last < timedelta(minutes=minutes):
        return [f'Stand-in review: it ran {int((now - last).total_seconds() // 60)} minutes ago; the first checkpoint '
                f'{minutes:g} minutes after that run gets the next, of everything since.']
    rules, words = next(((Path(root) / name, words) for name, words in RULES if (Path(root) / name).is_file()), (None, None))
    if transcript is None or rules is None:
        missing = ' and '.join(name for name, _ in RULES)
        return [f'Stand-in review not run: {"no transcript of this session was found" if transcript is None else f"neither of {missing} is here"}.']
    text = '\n\n'.join(written_since(transcript, last or now - FIRST))
    if not text.strip():
        return ['Stand-in review not run: the assistant wrote nothing since it last ran.']
    given = text[-CAP:]
    try:
        answer = ask(PROMPT.format(skill=rules.read_text(), text=given, **words), TIMEOUT, model=MODEL, thinking=True)
    except haiku_judge.Failed as error:
        return [f'Stand-in review gave no verdict ({error}); this checkpoint passes without one.']
    listed = [o for o in answer.get('objections', []) if isinstance(o, dict) and str(o.get('quote', '')).strip()
              and squeezed(str(o['quote'])) in squeezed(given) and str(o.get('objection', '')).strip()]
    stamp = now.strftime('%Y%m%dT%H%M%S')
    keep(root, {'fired': now.isoformat(), 'unanswered': f'{STATE}/{stamp}.json' if listed else state.get('unanswered')})
    (Path(root) / STATE / f'{stamp}.json').write_text(json.dumps(
        {'fired': now.isoformat(), 'since': (last or now - FIRST).isoformat(), 'characters': len(text), 'given': len(given),
         'objections': listed, 'dropped': len(answer.get('objections', [])) - len(listed)}, indent=1, ensure_ascii=False) + '\n')
    since = f'{(last or now - FIRST).astimezone(timezone.utc):%H:%M} UTC'
    if not listed:
        return [f'Stand-in review of {len(given)} characters written since {since}: no objection.']
    lines = [f'Stand-in review of {len(given)} characters written since {since}: {len(listed)} objections '
             f'({STATE}/{stamp}.json). Check each against the record; the next entry answers them in a paragraph starting "Review."']
    for number, objection in enumerate(listed, 1):
        lines += [f'{number}. {" ".join(str(objection["objection"]).split())}', f'   on: "{" ".join(str(objection["quote"]).split())}"']
    return lines


def unanswered(root):
    """The path of the review the next entry still owes an answer, or None."""
    path = state_of(root).get('unanswered')
    return path if path and (Path(root) / path).is_file() else None


def main(argv=None, root=ROOT, now=None, ask=haiku_judge.ask):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--transcript', type=Path)
    parser.add_argument('--minutes', type=float, default=MINUTES)
    parser.add_argument('--force', action='store_true', help='run it now, however lately it ran')
    parser.add_argument('--unanswered', action='store_true')
    parser.add_argument('--answered', action='store_true')
    args = parser.parse_args(argv)
    if args.unanswered:
        print(unanswered(root) or '', end='\n' if unanswered(root) else '')
        return 0
    if args.answered:
        keep(root, {**state_of(root), 'unanswered': None})
        return 0
    now = now or datetime.now(timezone.utc)
    lines = review(root, args.transcript or session_transcript(root), now, args.minutes, args.force, ask)
    print('\n'.join(lines), end='\n' if lines else '')
    return 0


if __name__ == '__main__':
    sys.exit(main())
