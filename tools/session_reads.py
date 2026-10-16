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
sys.path.insert(0, str(Path(__file__).resolve().parent))
from notebook_math import strip_tags  # noqa: E402

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


ASSIGNED = re.compile(r'(?:^|[;&\s])([A-Za-z_]\w*)=([^\s;&|]+)')
CHANGED = re.compile(r'(?:^|[;&]\s*)cd\s+([^\s;&|]+)')


def resolved(command, path):
    """A path of a shell command with the variables that the same command assigns put in, then the process's,
    and, if relative, under the directory the command changes to before it.  On 12 October 2026 three files
    read by ranges were printed as not checked because their paths were written R=...; sed ... $R/FILE, and
    the unread end of one of them held the sentence that mattered."""
    def filled(text):
        for name, value in ASSIGNED.findall(command):
            text = text.replace('${' + name + '}', value)
            text = re.sub(r'\$' + re.escape(name) + r'(?!\w)', lambda _: value, text)
        return os.path.expandvars(os.path.expanduser(text))
    moved = CHANGED.findall(command[:command.find(path)] if path in command else command)
    path = filled(path)
    if moved and not os.path.isabs(path):
        path = os.path.join(filled(moved[-1]), path)
    return same(path)


def same(path):
    """One spelling for a file on disk, so that its ranges read by an absolute and by a relative path are
    joined; a path that is no file here is left as written."""
    return os.path.realpath(path) if os.path.isfile(path) else path


def ranged_paths(found):
    """{path as the session wrote it, variables expanded: [ranges]} for the reads that have a range."""
    paths = {}
    for name, given in found:
        if name == 'Read':
            paths.setdefault(same(str(given.get('file_path', ''))), []).append(read_span(given))
        elif name == 'Bash':
            command = str(given.get('command', ''))
            for low, high, path in SED.findall(command):
                paths.setdefault(resolved(command, path), []).append((int(low), int(high)))
    return paths


HEADINGS = 4      # headings printed for each unread part of a Markdown file, its last ones


def unread_ends(entry, found):
    """Lines for the files an entry names that the calls read only by ranges ending before the file's last
    line: what of each was left unread, to be read or to be said beside any conclusion about the file."""
    found, lines = list(found), []
    plain = html.unescape(strip_tags(entry))       # the entry's words, not its links
    for path, spans in sorted(ranged_paths(found).items()):
        name = Path(path).name
        if not Path(path).is_file() or not re.search(r'(?<![\w.-])' + re.escape(name) + r'(?![\w-])', plain):
            continue
        text = Path(path).read_text(errors='replace').splitlines()
        ranges = merged(spans)
        gaps = [(a + 1, b - 1) for (_, a), (b, _) in zip([(0, 0)] + ranges, ranges + [(len(text) + 1, 0)])
                if b - 1 >= a + 1]
        if gaps:
            lines.append(f'  UNREAD: {name}, {len(text)} lines, named in the entry: not read are lines '
                         + ', '.join(f'{low}-{high}' for low, high in gaps))
            # the headings of a Markdown file's unread parts: what the reading left out, by its own titles
            for low, high in gaps if Path(path).suffix == '.md' else []:
                heads = [number for number in range(low, high + 1) if text[number - 1].startswith('#')]
                # the last headings of each unread part, a record's latest notes being at its end
                lines += [f'    unread heading, line {number}: {" ".join(text[number - 1].split())[:110]}'
                          for number in heads[-HEADINGS:]]
    return lines


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


SAYS = re.compile(r'\b(?:reports?|says?|records?|states?|holds no|does not (?:report|say|record|state))\b')
WHOLE = r'\bcat\b[^;|&\n]*'      # the one command taken to show a whole file; a search of it shows its matches


def partial_conclusions(entry, found):
    """Lines for sentences of an entry that say what a named file reports, says, records or states while the
    calls read that file only by ranges that stop before its last line, the file being on disk; a paragraph
    that gives a line range is passed, since it says what was read.

    An entry of 12 October 2026 said what a project's audit record "reports, for the present state" after
    reading its lines 1 to 60 and 180 to 225 of 277; the last note, unread, said that no build had been made
    for that state.  A file the calls opened whole (the reading tool without a range reaching its end, or a
    command that goes through it), one they never opened by a range, and one not found on disk are not
    listed: this is about a partial reading taken for the whole, and it reads the commands' words.  A search of
    the file does not count as reading it: that entry's session had searched the record for three words.

    Printed, not refused.  Built as a refusal first and withdrawn at its review: the verbs are also nouns, an
    end read with tail or a script is not seen, and a file that grew after a whole read looks partly read.  The
    sentence of that entry itself, which said "the upstream audit record" and named no file, is not matched;
    the unread lines and headings printed by unread_ends are what shows such a case."""
    found = list(found)
    ranged = ranged_paths(found)
    commands = [str(given.get('command', '')) for name, given in found if name == 'Bash']
    lines = []
    for paragraph in re.findall(r'<(?:p|li)\b[^>]*>(.*?)</(?:p|li)>', entry, re.S):
        plain = html.unescape(strip_tags(paragraph))
        if LINES.search(plain):
            continue
        for sentence in re.split(r'(?<=[.;:])\s+', plain):
            for name in sorted({Path(path).name for path in PATH.findall(sentence)}):
                # the verb within three words after the file's name: "the record FILE reports", not a noun
                # elsewhere in the sentence ("the record", "17 states") or what a reviewer says
                if not re.search(re.escape(name) + r'(?:,?\s+[\w\'-]+){0,3}?,?\s+' + SAYS.pattern, sentence):
                    continue
                if any(re.search(WHOLE + re.escape(name) + r'(?![\w.-])', command) for command in commands):
                    continue
                # every file of that name the calls read by ranges, each on disk and each short of its end
                ends = [(max(high for _, high in merged(spans)), len(Path(path).read_text(errors='replace').splitlines()))
                        for path, spans in ranged.items() if Path(path).name == name and Path(path).is_file()]
                if ends and all(last < length for last, length in ends):
                    last, length = ends[0]
                    lines.append(f'  PARTIAL READ: {name} was read to line {last} of {length}, and the entry '
                                 f'says what it says: "{" ".join(sentence.split())[:160]}"')
    return lines


def turn_partial(transcript_lines, turn, entry):
    """The same for one measured turn's calls (those after the finisher command that started it)."""
    return partial_conclusions(entry, after(calls(transcript_lines), FINISHER + re.escape(turn) + r'(?![\w-])'))


FINISHER = r'finish-turn\.py\b[^\n;|&]*--next\s+'


def after(found, pattern, last=False):
    """The calls after the first (or the last) shell command that matches `pattern`; none if none matches."""
    found = list(found)
    at = [index for index, (name, given) in enumerate(found)
          if name == 'Bash' and re.search(pattern, str(given.get('command', '')))]
    return found[(at[-1] if last else at[0]) + 1:] if at else []


def about(found, entry):
    """The lines for a set of calls: statements stopped short of and, given the entry's or draft's text, the
    unread parts of files it names and its sentences on what a partly read file says."""
    found = list(found)
    return short_lines(found) + (unread_ends(entry, found) + partial_conclusions(entry, found) if entry else [])


def turn_lines(transcript_lines, turn, entry=None):
    """The same for one measured turn: the calls after the finisher command that started it with --next."""
    return about(after(calls(transcript_lines), FINISHER + re.escape(turn) + r'(?![\w-])'), entry)


def current_lines(transcript_lines, entry=None):
    """The same for the turn in progress: the calls after the session's last finisher command with --next, or
    all of them in a session that has run none yet."""
    found = list(calls(transcript_lines))
    started = any(name == 'Bash' and re.search(FINISHER, str(given.get('command', ''))) for name, given in found)
    return about(after(found, FINISHER, last=True) if started else found, entry)


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
    plain = html.unescape(strip_tags(draft))
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
        for line in unread_ends(Path(options['--draft']).read_text(), found):
            print(line)
        for line in partial_conclusions(Path(options['--draft']).read_text(), found):
            print(line)
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
