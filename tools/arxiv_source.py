#!/usr/bin/env python3
"""Fetch the source of an arXiv paper into a scratch directory, so that its statements can be read in full.

    tools/arxiv_source.py 1204.3057 --out SCRATCH_DIR

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


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('ident', help='arXiv identifier, e.g. 1204.3057 or math/0601001')
    parser.add_argument('--out', required=True, type=Path, help='scratch directory outside the repository')
    args = parser.parse_args(argv[1:])
    if not args.ident or set(args.ident) - ID_CHARS:
        print(f'Not an arXiv identifier: {args.ident}', file=sys.stderr)
        return 1
    inside = repository_of(args.out.resolve())
    if inside is not None:
        print(f'{args.out} lies inside the repository {inside}: third-party text goes to a scratch directory '
              'outside it and is not committed', file=sys.stderr)
        return 1
    request = urllib.request.Request(f'https://arxiv.org/e-print/{args.ident}',
                                     headers={'User-Agent': 'arxiv_source.py (research reading)'})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
    names = unpack(data, args.out)
    sized = sorted(((args.out / n).stat().st_size, n) for n in names)
    tex = [row for row in sized if row[1].endswith('.tex')][::-1]
    rest = [row for row in sized if not row[1].endswith('.tex')][::-1]
    print(f'{len(names)} files, {len(data)} bytes downloaded, in {args.out}')
    for size, name in tex + rest:
        print(f'{size:>9}  {name}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
