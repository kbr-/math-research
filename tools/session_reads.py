#!/usr/bin/env python3
"""List what a Claude Code session opened of each file, from its transcript, and what a draft names of them.

Usage: tools/session_reads.py TRANSCRIPT.jsonl [--from TEXT] [--to TEXT] [--draft DRAFT.html]

Three drafts of 11 October 2026 described a file or a source's passage from its name or from a part of it: a
scratch file called corrected that was never opened, a draft taken for another document, and a passage judged
fifty lines short of the proposition that decided a test.  This lists, for the tool calls between the first
shell command containing FROM and the first later one containing TO (the whole transcript without them), each
file the session opened with the line ranges it read: the Read tool's ranges, `sed -n A,Bp FILE`, and, without
a range, the files other shell commands name.  For a TeX or Lean file read by ranges and still on disk it
prints the theorem-like statements that begin, unread, within 100 lines after a range that was read.  With a
draft it also prints the paths and line ranges the draft's text names, each beside what was opened of that
file.

It reads the commands' words: a file opened through a variable, a glob or a script is not seen, a command that
names a file without reading it counts as touching it, and a draft that speaks of a file without writing its
name or its lines gives the listing nothing to compare."""
import html
import json
import os
import re
import sys
from pathlib import Path

SED = re.compile(r"sed -n ['\"]?(\d+),(\d+)p['\"]?\s+([^\s;|&)]+)")
STATEMENT = re.compile(r'\\begin\{(theorem|thm|proposition|prop|lemma|lem|corollary|cor|claim)\*?\}'
                       r'|^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+)?(theorem|lemma)\s+(\S+)')
AHEAD = 100
PATH = re.compile(r"(?<![\w/.$-])(/?(?:[\w.$-]+/)*[\w.-]+\.(?:tex|lean|py|txt|html|json|md|out))\b")
LINES = re.compile(r'\blines? (\d+)(?:\s*(?:to|-|–|and)\s*(\d+))?')


def calls(lines):
    """(tool, input) for every tool call of the transcript, in order."""
    for line in lines:
        try:
            content = json.loads(line).get('message', {}).get('content', [])
        except (ValueError, AttributeError):
            continue
        for block in content if isinstance(content, list) else []:
            if isinstance(block, dict) and block.get('type') == 'tool_use':
                yield block.get('name'), block.get('input') or {}


def window(found, start, stop):
    """The calls from the first shell command containing `start` to the first later one containing `stop`."""
    inside, kept = start is None, []
    for name, given in found:
        command = str(given.get('command', '')) if name == 'Bash' else ''
        if not inside:
            inside = start in command
            continue
        if stop is not None and stop in command:
            break
        kept.append((name, given))
    return kept


READ_LINES = 2000      # what the reading tool returns of a file when no limit is given


def read_span(given):
    """The lines one call of the reading tool returned: from its offset, or the top, for its limit."""
    first = int(given.get('offset') or 1)
    return first, first + int(given.get('limit') or READ_LINES) - 1


def reads(found):
    """{file name: [ranges and None for a touch without a range]} over the calls; a file is keyed by its
    last path component, since a draft seldom writes the directory the session used."""
    opened = {}
    for name, given in found:
        if name == 'Read':
            opened.setdefault(Path(str(given.get('file_path', ''))).name, []).append(read_span(given))
        elif name == 'Bash':
            command, ranged = str(given.get('command', '')), set()
            for low, high, path in SED.findall(command):
                opened.setdefault(Path(path).name, []).append((int(low), int(high)))
                ranged.add(Path(path).name)
            for path in PATH.findall(command):
                if Path(path).name not in ranged:
                    opened.setdefault(Path(path).name, []).append(None)
    return opened


def ranged_paths(found):
    """{path as the session wrote it, variables expanded: [ranges]} for the reads that have a range."""
    paths = {}
    for name, given in found:
        if name == 'Read':
            paths.setdefault(str(given.get('file_path', '')), []).append(read_span(given))
        elif name == 'Bash':
            for low, high, path in SED.findall(str(given.get('command', ''))):
                paths.setdefault(os.path.expandvars(path), []).append((int(low), int(high)))
    return paths


def statements_ahead(text, spans, ahead=AHEAD):
    """(line, text) of the theorem-like statements of a source that begin at an unread line within `ahead`
    lines after the end of a range that was read: what a reading stopped short of."""
    lines, ranges = text.splitlines(), merged(spans)
    found = []
    for number, line in enumerate(lines, 1):
        if not STATEMENT.search(line) or any(low <= number <= (high or 10**9) for low, high in ranges):
            continue
        if any(high and high < number <= high + ahead for _, high in ranges):
            found.append((number, ' '.join(line.split())[:120]))
    return found


def short_lines(found):
    """A line for each statement the calls' ranged reads of TeX and Lean files on disk stopped short of."""
    lines = []
    for path, spans in sorted(ranged_paths(found).items()):
        if Path(path).suffix not in ('.tex', '.lean'):
            continue
        if not Path(path).is_file():
            lines.append(f'  NOT CHECKED: {path}, read by ranges, is not a file here (a path written with a '
                         'variable this process lacks, or a file since removed)')
            continue
        for number, line in statements_ahead(Path(path).read_text(errors='replace'), spans):
            lines.append(f'  STOPPED SHORT? {Path(path).name} line {number}, unread, within {AHEAD} lines '
                         f'after a range read: {line}')
    return lines


FINISHER = r'finish-turn\.py\b[^\n;|&]*--next\s+'


def after(found, pattern, last=False):
    """The calls after the first (or the last) shell command that matches `pattern`; none if none matches."""
    found = list(found)
    at = [index for index, (name, given) in enumerate(found)
          if name == 'Bash' and re.search(pattern, str(given.get('command', '')))]
    return found[(at[-1] if last else at[0]) + 1:] if at else []


def turn_lines(transcript_lines, turn):
    """The same for one measured turn: the calls after the finisher command that started it with --next."""
    return short_lines(after(calls(transcript_lines), FINISHER + re.escape(turn) + r'(?![\w-])'))


def current_lines(transcript_lines):
    """The same for the turn in progress: the calls after the session's last finisher command with --next, or
    all of them in a session that has run none yet."""
    found = list(calls(transcript_lines))
    started = any(name == 'Bash' and re.search(FINISHER, str(given.get('command', ''))) for name, given in found)
    return short_lines(after(found, FINISHER, last=True) if started else found)


def merged(spans):
    """Ranges joined where they touch; an open end swallows what follows."""
    out = []
    for low, high in sorted((low, high if high is not None else 10**9) for low, high in spans):
        if out and low <= out[-1][1] + 1:
            out[-1][1] = max(out[-1][1], high)
        else:
            out.append([low, high])
    return [(low, None if high == 10**9 else high) for low, high in out]


def shown(spans):
    ranges = merged([span for span in spans if span])
    text = ', '.join(f'{low}-{high}' if high else f'{low}-end' for low, high in ranges)
    touched = sum(span is None for span in spans)
    return text + ('; ' if text and touched else '') + (f'named in {touched} other commands' if touched else '')


def named(draft):
    """(paths, line ranges) the draft's text writes out."""
    plain = html.unescape(re.sub(r'<[^>]*>', ' ', draft))
    paths = sorted({Path(path).name for path in PATH.findall(draft)})
    return paths, sorted({(int(low), int(high or low)) for low, high in LINES.findall(plain)})


def covered(span, spans):
    low, high = span
    return any(a <= low and (b is None or high <= b) for a, b in merged([s for s in spans if s]))


def main():
    arguments, options = sys.argv[1:], {}
    for flag in ('--from', '--to', '--draft'):
        if flag in arguments:
            at = arguments.index(flag)
            options[flag] = arguments[at + 1]
            del arguments[at:at + 2]
    if len(arguments) != 1 or arguments[0].startswith('-'):
        sys.exit(__doc__.split('\n\n')[1])
    found = window(calls(Path(arguments[0]).read_text().splitlines()), options.get('--from'), options.get('--to'))
    opened = reads(found)
    print(f'{len(found)} tool calls in the window; {len(opened)} files opened or named.')
    for name in sorted(opened):
        print(f'  {name}: {shown(opened[name])}')
    for line in short_lines(found):
        print(line)
    if '--draft' in options:
        paths, ranges = named(Path(options['--draft']).read_text())
        print(f'The draft names {len(paths)} files and {len(ranges)} line ranges.')
        for name in paths:
            print(f'  {name}: ' + (shown(opened[name]) if name in opened else 'NOT OPENED in the window'))
        everything = [span for spans in opened.values() for span in spans]
        for low, high in ranges:
            where = [name for name, spans in sorted(opened.items()) if covered((low, high), spans)]
            print(f'  lines {low}-{high}: ' + ('read in ' + ', '.join(where) if where and everything
                                                 else 'NOT READ as a range of any file in the window'))


if __name__ == '__main__':
    main()
