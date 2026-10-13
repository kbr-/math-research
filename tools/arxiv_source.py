#!/usr/bin/env python3
"""Fetch the source of an arXiv paper into a scratch directory, so that its statements can be read in full.

    tools/arxiv_source.py 1204.3057 --out SCRATCH_DIR --expect WORDS OF THE TITLE MEANT

A web fetch tool returns a model's report of a page, not its text; a reading "in full" needs the text (review
of 11 October 2026: two entries read sources by report after naming a full reading as the next step).  arXiv
serves the authors' source at /e-print/ID: a gzipped TeX file, a gzipped tar archive, or a PDF.  This tool
downloads it, unpacks it and prints the files with their sizes, largest TeX first.

The text is third-party: use external scratch or this Codex actor's managed, Git-ignored scratch.
Tracked destinations and links are refused; nothing unpacked is to be committed (AGENTS.md, licences).
Restate what is read; do not quote at length.
"""
import argparse
import gzip
import io
import os
import re
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path
from codex_state import scratch_directory

ROOT = Path(__file__).resolve().parents[1]
ID_CHARS = set('0123456789.abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-/')


def repository_of(path):
    """The top level of the git checkout containing `path`, or None."""
    probe = path if path.is_dir() else path.parent
    while not probe.exists():
        probe = probe.parent
    done = subprocess.run(['git', '-C', str(probe), 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
    return Path(done.stdout.strip()) if done.returncode == 0 and done.stdout.strip() else None


def validate_destination(out):
    """Admit external scratch or the current actor's ignored, untracked managed subtree."""
    if '..' in out.parts:
        raise ValueError('Source output path must not contain parent traversal')
    out = out.absolute()
    for path in (out, *out.parents):
        if path.name == '.git':
            raise ValueError(f'Source output must not enter Git metadata: {path}')
        if path.is_symlink():
            raise ValueError(f'Source output must not pass through a symlink: {path}')
    inside = repository_of(out)
    if inside is not None:
        inside = inside.resolve()
        thread = os.environ.get('CODEX_THREAD_ID')
        if thread:
            owned = scratch_directory(inside, thread)
        else:
            # compute.sh transports this opaque path, not the raw thread identity.
            inherited = os.environ.get('MATH_CODEX_SCRATCH', '')
            owned = Path(inherited) if inherited else None
            if owned is not None and (owned.parent != inside / 'research/tmp/codex'
                                      or not re.fullmatch(r'[0-9a-f]{64}', owned.name)):
                raise ValueError('Invalid inherited managed scratch path')
        if owned is None or (out != owned and owned not in out.parents):
            raise ValueError(f'{out} lies inside the repository {inside}: use external scratch or '
                             'the current Codex actor\'s managed scratch')
        relative = str(out.relative_to(inside))
        ignored = subprocess.run(['git', '-C', str(inside), 'check-ignore', '--quiet', '--no-index', '--',
                                  relative], capture_output=True)
        if ignored.returncode != 0:
            raise ValueError('Managed source output must be Git-ignored')
        tracked = subprocess.run(['git', '-C', str(inside), 'ls-files', '-z', '--', relative],
                                 capture_output=True)
        if tracked.returncode or tracked.stdout:
            raise ValueError('Managed source output must contain no tracked files')
    if out.exists() and not out.is_dir():
        raise ValueError('Source output must be a directory')
    for directory, dirs, files in os.walk(out):
        for name in dirs + files:
            path = Path(directory) / name
            if name == '.git':
                raise ValueError(f'Source output contains a nested repository: {path}')
            if path.is_symlink():
                raise ValueError(f'Source output contains a symlink: {path}')
            if path.is_file() and path.stat().st_nlink > 1:
                raise ValueError(f'Source output contains a hard link: {path}')
    return out


def unpack(data, out):
    """Write the files of an e-print payload under `out`; return their paths relative to it."""
    out.mkdir(parents=True, exist_ok=True)
    if data[:4] == b'%PDF':
        (out / 'paper.pdf').write_bytes(data)
        return ['paper.pdf']
    if data[:2] == b'\x1f\x8b':
        data = gzip.decompress(data)
    try:
        archive = tarfile.open(fileobj=io.BytesIO(data))
    except tarfile.ReadError:
        (out / 'paper.tex').write_bytes(data)
        return ['paper.tex']
    names = []
    for member in archive.getmembers():
        if '.git' in Path(member.name).parts:
            continue                      # a payload cannot introduce a nested repository
        target = (out / member.name).resolve()
        if not member.isfile() or out.resolve() not in target.parents:
            continue                      # no links, devices, or paths leaving the directory
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.extractfile(member).read())
        names.append(member.name)
    return names


BRACED = re.compile(r'\\(title|author)\s*(?:\[[^\]]*\])?\s*\{')
HAND = re.compile(r'\\(?:Large|LARGE|huge|Huge|large)\b')
HAND_LINES = 40
LAYOUT = re.compile(r'\s*\\(?:begin|end|vspace|vskip|hspace|hskip|setlength|baselineskip|maketitle|pagestyle|'
                    r'thispagestyle|newpage|bigskip|medskip|smallskip|noindent\s*$)\b')
ENDED = re.compile(r'\\(title|author)\b(?!\s*[\[{])(.*?)\\end\1\b', re.S)


def words_of(line):
    """A TeX line's words: accents joined to their letters, commands, braces and mathematics signs removed."""
    line = re.sub(r'\\(?:[\'"`^~=.]|[Hcvudbk](?![A-Za-z]))\s*\{\\?(\w)\}', r'\1', line)
    line = re.sub(r'\\[\'"`^~=.]\s*\\?(\w)', r'\1', line)
    return ' '.join(re.sub(r'\\[A-Za-z]+\*?|\\.|[{}$\[\]]', ' ', line).split())


def titles(out, names):
    """[(file, 'title' or 'author' or 'first lines', text)] from the \\title{...} and \\author{...} of the
    unpacked TeX files, braces balanced, TeX commands left as written, and from the AMS-TeX form ended by
    \\endtitle; for the file that begins the document and has no title of these forms, the first line of its
    body in large type; for a TeX file with nothing of these, the first three lines of its body that hold
    words, or of the file as they stand when it marks no body.  On 12 October 2026 a paper fetched under a recalled identifier was an unrelated one,
    and the title was looked at only afterwards by hand."""
    found = []
    for name in sorted(n for n in names if n.endswith('.tex')):
        text = (out / name).read_text(errors='replace')
        text = re.sub(r'(?<!\\)%.*', '', text)                       # comments
        hits = []
        for match in BRACED.finditer(text):
            depth, end = 1, match.end()
            while end < len(text) and depth:
                depth += {'{': 1, '}': -1}.get(text[end], 0)
                end += 1
            hits.append((name, match.group(1), ' '.join(text[match.end():end - 1].split())[:300]))
        for match in ENDED.finditer(text):                              # AMS-TeX: \title ... \endtitle
            hits.append((name, match.group(1), ' '.join(match.group(2).split())[:300]))
        parts = re.split(r'\\begin\{document\}|\\document\b', text, maxsplit=1)
        body = parts[-1]
        if len(parts) == 2 and not any(kind == 'title' for _, kind, _ in hits):
            # a title set by hand: large type among the first lines of the body of the file that begins the
            # document, read on to a line break or a blank line (a paper of 2004 met on 12 October 2026 was
            # refused for want of a title command and identified by hand)
            lines = body.splitlines()[:HAND_LINES]
            for index, line in enumerate(lines):
                if HAND.search(line):
                    run = []
                    for more in lines[index:index + 4]:
                        if not more.strip():
                            break
                        run.append(more)
                        joined = ' '.join(run)
                        if '\\\\' in more or joined.count('{') <= joined.count('}'):
                            break                     # a line break, or the group that set the size has closed
                    shown = words_of(' '.join(run))
                    if len(shown.split()) >= 2:
                        hits.append((name, 'title', shown[:300]))
                        break
        if not hits and len(parts) == 2:  # the body's first lines that hold words, layout commands removed
            lines = [shown for shown in (words_of(line) for line in body.splitlines() if not LAYOUT.match(line))
                     if shown][:3]
            hits = [(name, 'first lines', ' | '.join(lines)[:300])] if lines else []
        if not hits:                      # a file that marks no body: its first lines as they stand
            lines = [line.strip() for line in text.splitlines() if line.strip()][:3]
            hits = [(name, 'first lines', ' | '.join(lines)[:300])] if lines else []
        found += hits
    return found


def expected(found, wanted):
    """Whether some title found holds one of the words wanted, case ignored."""
    held = ' '.join(text.lower() for _, kind, text in found if kind == 'title')
    return any(word.lower() in held for word in wanted)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('ident', help='arXiv identifier, e.g. 1204.3057 or math/0601001')
    parser.add_argument('--out', required=True, type=Path, help='external or owned managed scratch directory')
    parser.add_argument('--expect', nargs='+', metavar='WORD',
                        help='words, of four letters or more, of the title of the paper meant: exit 3 when the '
                             'fetched title holds none')
    parser.add_argument('--unchecked', metavar='REASON',
                        help='fetch without --expect, saying why the title cannot be given (at least three words)')
    args = parser.parse_args(argv[1:])
    if not args.ident or set(args.ident) - ID_CHARS:
        print(f'Not an arXiv identifier: {args.ident}', file=sys.stderr)
        return 1
    try:
        args.out = validate_destination(args.out)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    if args.expect and any(len(word) < 4 for word in args.expect):
        print('--expect takes words of four letters or more: a shorter one matches nearly any title',
              file=sys.stderr)
        return 1
    if not args.expect and len((args.unchecked or '').split()) < 3:
        print('Give --expect WORDS of the title of the paper meant, so that a wrong identifier is caught, or '
              '--unchecked REASON', file=sys.stderr)
        return 1
    marker = args.out / 'NOT-THE-PAPER-EXPECTED.txt'
    request = urllib.request.Request(f'https://arxiv.org/e-print/{args.ident}',
                                     headers={'User-Agent': 'arxiv_source.py (research reading)'})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
    names = unpack(data, args.out)
    if marker.exists():
        marker.unlink()                   # of an earlier fetch into this directory, now replaced
    sized = sorted(((args.out / n).stat().st_size, n) for n in names)
    tex = [row for row in sized if row[1].endswith('.tex')][::-1]
    rest = [row for row in sized if not row[1].endswith('.tex')][::-1]
    print(f'{len(names)} files, {len(data)} bytes downloaded, in {args.out}')
    for size, name in tex + rest:
        print(f'{size:>9}  {name}')
    found = titles(args.out, names)
    for name, kind, text in found:
        print(f'{kind} in {name}: {text}')
    if not found:
        print('No title found: the payload has no TeX file with text; identify the paper before reading it.')
    if args.expect and not expected(found, args.expect):
        message = ('NOT THE PAPER EXPECTED: no title found holds any of ' + ', '.join(args.expect)
                   + '; do not read it as that paper.')
        marker.write_text(f'{args.ident}: {message}\n')              # for a later reader of the directory
        print(message, file=sys.stderr)
        return 3                          # not 2, which argparse uses for a mistyped option
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
