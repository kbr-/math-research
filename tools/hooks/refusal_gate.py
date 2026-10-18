#!/usr/bin/env python3
"""Claude Code PreToolUse hook (Edit|Write): a refused framework tool's input is not changed before the code
that emitted the refusal has been read (AGENTS.md, Order of work: "Before a second attempt at a refused step,
write in the reply the line of the refusal that names its rule and what in the input broke it, read from the
code that emits the refusal").

On 17 and 18 October 2026 the rule let the same mistake through repeatedly: a queue reordered by hand, an
answers line moved, a gate's wording changed, each before the refusing code was read (the queued build
refusal-cause-before-retry). The hook reads the session's transcript backwards from its end, over the last
MAX_USES tool calls, and finds the latest Bash run whose command names the file being edited. When that run
was refused by a framework tool (its result an error whose text has a line "NAME.py: ..." or "commit-msg: ...",
or FAILS lines of a skeleton check) and no later call read the code under tools/ (a grep, sed -n, rg, cat,
head or awk on a tools/ path, or a Read of a file under tools/), the edit is refused. A skeleton check
(notebook-append.py --check), the planning aid AGENTS.md describes, is gated only when its set of failing
lines repeats that of the check before it on the same file, the second attempt at the same refused step.
Usage: refusal_gate.py, with the hook JSON on stdin; exit 2 refuses.
       refusal_gate.py --replay TRANSCRIPT    print where the gate would have refused over a transcript."""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shell_commands import unambiguous_commands

MAX_USES = 120
MAX_BYTES = 60 << 20
BLOCK = 1 << 22
REFUSAL = re.compile(r'^(?:[\w.-]+\.py|commit-msg): (?P<rule>.+)$|^FAILS (?P<fails>.+)$', re.M)


def tool_calls(transcript, max_uses=MAX_USES, max_bytes=MAX_BYTES):
    """The session's last tool calls, oldest first, as dicts {name, input, error, text}; the file is read
    backwards in blocks, as far as max_uses tool calls or max_bytes."""
    results, uses, tail, read, seen = {}, [], b'', 0, set()
    with open(transcript, 'rb') as stream:
        end = stream.seek(0, 2)
        while end > 0 and len(uses) < max_uses and read < max_bytes:
            start = max(0, end - BLOCK)
            stream.seek(start)
            chunk = stream.read(end - start)
            read += len(chunk)
            lines = (chunk + tail).split(b'\n')
            tail, lines = (lines[0], lines[1:]) if start else (b'', lines)
            for line in reversed(lines):
                if b'"tool_result"' not in line and b'"tool_use"' not in line:
                    continue
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                # Only the session's own messages: other records (requests sent to the model) carry copies of
                # earlier messages, which made one refused check count as its own earlier repeat (the gate's
                # first firing, 18 October 2026, on a draft checked once).
                if (not isinstance(entry, dict) or entry.get('isSidechain')
                        or entry.get('type') not in ('assistant', 'user')):
                    continue
                parts = (entry.get('message') or {}).get('content')
                if not isinstance(parts, list):
                    continue
                for part in reversed(parts):
                    if not isinstance(part, dict):
                        continue
                    if part.get('type') == 'tool_result':
                        text = part.get('content')
                        if isinstance(text, list):
                            text = '\n'.join(str(p.get('text') or '') for p in text if isinstance(p, dict))
                        results[part.get('tool_use_id')] = (str(part.get('is_error')).lower() == 'true',
                                                            str(text or ''))
                    elif part.get('type') == 'tool_use' and part.get('id') not in seen:
                        seen.add(part.get('id'))
                        error, text = results.get(part.get('id'), (False, ''))
                        uses.append({'name': part.get('name'), 'input': part.get('input') or {},
                                     'error': error, 'text': text})
            end = start
    return uses[::-1]


def names(command, path):
    """Whether a command names the file: its path or, for a path in scratch, its basename as a word."""
    base = Path(path).name
    return path in command or bool(base) and re.search(r'(?<![\w.-])' + re.escape(base) + r'(?![\w.-])', command)


def refusal_lines(text):
    return [(m.group('rule') or m.group('fails')).strip()[:200] for m in REFUSAL.finditer(text)]


def refusal_line(text):
    found = refusal_lines(text)
    return found[0] if found else None


def emitter(text):
    """The file name of the tool the refusal text names ("notebook-append.py: ..."), or None.  The commit-msg hook's
    refusals come from tools/commit_message_checks.py: on 18 October 2026 reads of that module did not count,
    and only a search quoting the refusal did."""
    match = re.search(r'^([\w.-]+\.py): ', text, re.M)
    if match:
        return match.group(1)
    return 'commit_message_checks.py' if re.search(r'^commit-msg: ', text, re.M) else None


def quotes(command, line):
    """Whether the command searches for words of the refusal: twelve or more consecutive characters of it."""
    words = re.sub(r'\s+', ' ', line)
    return any(words[i:i + 12] in command for i in range(0, max(1, len(words) - 11)))


def reads_code(call: dict, line: str = '', tool: str | None = None) -> bool:
    """A read of the code behind the refusal: of a file under tools/ that is the emitting tool, or a search of
    tools/ quoting the refusal's words (an unrelated grep of tools/ does not count: the bypass tried before the
    commit of 18 October 2026)."""
    if call.get('error'):
        return False
    if call['name'] == 'Read':
        path = str(call['input'].get('file_path') or '')
        return '/tools/' in path and (tool is None or path.endswith('/' + tool) or not line)
    if call['name'] in ('Grep', 'Glob'):
        text = json.dumps(call['input'])
        return 'tools' in text and (not line or quotes(text, line) or bool(tool and tool in text))
    command = str(call['input'].get('command') or '') if call['name'] == 'Bash' else ''
    for words in unambiguous_commands(command, chain=True):
        while words and (re.match(r'^\w+=', words[0]) or words[0] in ('command', 'env')):
            words = words[1:]
        if not words:
            continue
        verb = Path(words[0]).name
        if verb not in ('grep', 'rg', 'sed', 'cat', 'head', 'awk'):
            continue
        if verb == 'sed' and (not any(w == '-n' for w in words[1:])
                              or any(w == '--in-place' or w.startswith(('-i', '--in-place=')) for w in words[1:])):
            continue
        if verb == 'awk':
            # Arbitrary awk programs can edit files or run subprocesses; require a native Read instead.
            continue
        operands = words[1:]
        if verb in ('grep', 'rg'):
            # A pattern naming tools/ is not the file operand; recognize explicit -e/--regexp too.
            index, explicit = 0, False
            while index < len(operands) and operands[index].startswith('-'):
                option = operands[index]
                index += 1
                if option in ('-e', '--regexp', '-f', '--file'):
                    explicit = True
                    index += 1
                elif option.startswith(('-e', '--regexp=', '-f', '--file=')):
                    explicit = True
                elif option in ('-g', '--glob', '--iglob', '-t', '--type', '--type-not', '-m', '--max-count'):
                    index += 1
            operands = operands[index if explicit else index + 1:]
        elif verb == 'sed':
            operands = [w for w in operands if not w.startswith('-')][1:]
        named = [w for w in operands if re.search(r'(?:^|/)tools/', w)]
        if named and (not line or quotes(' '.join(words), line) or bool(tool and any(tool in w for w in named))):
            return True
    return False


def pending(calls, path):
    """The refusal line that gates an edit of path, or None."""
    runs = [i for i, c in enumerate(calls) if c['name'] == 'Bash' and names(str(c['input'].get('command') or ''), path)]
    if not runs:
        return None
    last = calls[runs[-1]]
    line = refusal_line(last['text']) if last['error'] else None
    if not line:
        return None
    if '--check' in str(last['input'].get('command') or ''):
        earlier = [calls[i] for i in runs[:-1] if '--check' in str(calls[i]['input'].get('command') or '')]
        # A check lists every failing paragraph, some deferred on purpose: only a second check failing on exactly
        # the same set is a retry that changed nothing the check reads (the replay of 18 October 2026: a deferred
        # first line gated unrelated edits).
        if (not earlier or not earlier[-1]['error']
                or set(refusal_lines(earlier[-1]['text'])) != set(refusal_lines(last['text']))):
            return None
    tool = emitter(last['text'])
    if any(reads_code(c, line, tool) for c in calls[runs[-1] + 1:]):
        return None
    return line


def replay(transcript, max_uses=100000, max_bytes=300 << 20):
    """The lines of a replay over a transcript: at each Edit or Write, would the gate have refused it, given the
    MAX_USES calls before it; every firing is printed, to be read against its source."""
    calls = tool_calls(transcript, max_uses, max_bytes)
    lines, edits, fired = [f'{len(calls)} tool calls read'], 0, 0
    for i, call in enumerate(calls):
        if call['name'] not in ('Edit', 'Write'):
            continue
        edits += 1
        path = str(call['input'].get('file_path') or '')
        line = pending(calls[max(0, i - MAX_USES):i], path)
        if line:
            fired += 1
            lines.append('FIRES on ' + Path(path).name + ' | ' + line[:150])
    return lines + [f'{edits} edits or writes; {fired} would be refused']


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--replay':
        print('\n'.join(replay(sys.argv[2])))
        return 0
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    if payload.get('tool_name') not in ('Edit', 'Write'):
        return 0
    path = str((payload.get('tool_input') or {}).get('file_path') or '')
    transcript = payload.get('transcript_path')
    if not path or not transcript or not os.path.isfile(transcript):
        return 0
    line = pending(tool_calls(transcript), path)
    if line is None:
        return 0
    print('Refused: the last run that named ' + Path(path).name + ' was refused ("' + line[:160] + '"). Before '
          'changing its input, read the code that emits the refusal (grep tools/ for its words) and write in the '
          'reply the line that names its rule and what in the input broke it (AGENTS.md, Order of work).',
          file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main())
