#!/usr/bin/env python3
"""Fetch the source of an arXiv paper into a scratch directory, so that its statements can be read in full.

    tools/arxiv_source.py 1204.3057 --out SCRATCH_DIR --expect WORDS OF THE TITLE MEANT

A web fetch tool returns a model's report of a page, not its text; a reading "in full" needs the text (review
of 11 October 2026: two entries read sources by report after naming a full reading as the next step).  arXiv
serves the authors' source at /e-print/ID: a gzipped TeX file, a gzipped tar archive, or a PDF.  This tool
downloads it, unpacks it and prints the files with their sizes, largest TeX first.

The text is third-party: the output directory must lie outside the repository, and nothing unpacked is to be
committed (AGENTS.md, licences).  Restate what is read; do not quote at length.
"""
import argparse
import gzip
import io
import re
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID_CHARS = set('0123456789.abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-/')


def repository_of(path):
    """The top level of the git checkout containing `path`, or None."""
    probe = path if path.is_dir() else path.parent
    while not probe.exists():
        probe = probe.parent
    done = subprocess.run(['git', '-C', str(probe), 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
    return Path(done.stdout.strip()) if done.returncode == 0 and done.stdout.strip() else None


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
        target = (out / member.name).resolve()
        if not member.isfile() or out.resolve() not in target.parents:
            continue                      # no links, devices, or paths leaving the directory
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.extractfile(member).read())
        names.append(member.name)
    return names


BRACED = re.compile(r'\\(title|author)\s*(?:\[[^\]]*\])?\s*\{')


def titles(out, names):
    """[(file, 'title' or 'author', text)] from the \\title{...} and \\author{...} of the unpacked TeX files,
    braces balanced, TeX commands left as written; for a TeX file with neither, its first three nonblank,
    uncommented lines.  On 12 October 2026 a paper fetched under a recalled identifier was an unrelated one,
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
        if not hits:
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
    parser.add_argument('--out', required=True, type=Path, help='scratch directory outside the repository')
    parser.add_argument('--expect', nargs='+', metavar='WORD',
                        help='words, of four letters or more, of the title of the paper meant: exit 3 when the '
                             'fetched title holds none')
    parser.add_argument('--unchecked', metavar='REASON',
                        help='fetch without --expect, saying why the title cannot be given (at least three words)')
    args = parser.parse_args(argv[1:])
    if not args.ident or set(args.ident) - ID_CHARS:
        print(f'Not an arXiv identifier: {args.ident}', file=sys.stderr)
        return 1
    inside = repository_of(args.out.resolve())
    if inside is not None:
        print(f'{args.out} lies inside the repository {inside}: third-party text goes to a scratch directory '
              'outside it and is not committed', file=sys.stderr)
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
