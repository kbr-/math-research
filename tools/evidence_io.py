#!/usr/bin/env python3
"""Lossless zstd-3 evidence storage. Read raw or .zst; pack new evidence without rewriting history.

Usage: python3 tools/evidence_io.py read PATH
       python3 tools/evidence_io.py pack PATH... [--replace]
       python3 tools/evidence_io.py check-staged

pack prints the actual .zst paths to cite. --replace removes a raw input only after verified
decompression and refuses files already committed at HEAD. Summaries, manifests, documentation,
timing views and executable source remain readable; new data under results/provenance is compressed.
"""
from __future__ import annotations

import argparse
from collections.abc import Iterator
from contextlib import contextmanager
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import BinaryIO, IO


@contextmanager
def open_binary(path: Path) -> Iterator[IO[bytes]]:
    if path.suffix != '.zst':
        with path.open('rb') as stream:
            yield stream
        return
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen(['zstd', '-q', '-d', '-c', '--', str(path)],
                                   stdout=subprocess.PIPE, stderr=errors)
        assert process.stdout is not None
        try:
            yield process.stdout
        finally:
            process.stdout.close()
            code = process.wait()
            if code:
                errors.seek(0)
                raise OSError(f'Cannot decompress {path}: {errors.read().decode(errors="replace").strip()}')


def read_text(path: Path, encoding: str = 'utf-8', errors: str = 'strict') -> str:
    return read_bytes(path).decode(encoding, errors)


def read_bytes(path: Path) -> bytes:
    with open_binary(path) as stream:
        return stream.read()


def read_git_text(path: str, revision: str = '', root: Path | None = None) -> str:
    """Read raw or zstd text from an exact Git tree/index, never the working copy."""
    found = subprocess.run(['git', '-C', str(root or Path.cwd()), 'show', f'{revision}:{path}'],
                           capture_output=True)
    if found.returncode:
        return ''
    data = found.stdout
    if path.endswith('.zst'):
        data = subprocess.run(['zstd', '-q', '-d', '-c'], input=data,
                              capture_output=True, check=True).stdout
    return data.decode('utf-8', errors='replace')


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with open_binary(path) as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


@contextmanager
def compressed_writer(target: Path) -> Iterator[BinaryIO]:
    if target.suffix != '.zst':
        raise ValueError('Compressed evidence must have a .zst suffix')
    if target.exists():
        raise FileExistsError(f'Refusing to overwrite {target}')
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.evidence-', dir=target.parent) as temporary:
        raw, packed = Path(temporary) / 'raw', Path(temporary) / 'packed.zst'
        with raw.open('wb') as stream:
            yield stream
        subprocess.run(['zstd', '-q', '-3', '-T1', '-o', str(packed), '--', str(raw)], check=True)
        if digest(raw) != digest(packed):
            raise OSError('Compression round-trip hash mismatch')
        os.link(packed, target)


def compress_file(source: Path, target: Path | None = None) -> Path:
    destination = target or source.with_name(source.name + '.zst')
    expected = digest(source)
    with source.open('rb') as src, compressed_writer(destination) as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)
    if digest(destination) != expected or digest(source) != expected:
        raise OSError(f'{source}: source changed during compression; raw input retained')
    return destination


def payload(path: str) -> bool:
    item = Path(path)
    if not any(item.is_relative_to(root) for root in (Path('research/results'), Path('research/provenance'))):
        return False
    if item.suffix in {'.zst', '.md', '.html', '.py', '.pyi', '.sh', '.c', '.h', '.cpp', '.hpp',
                       '.rs', '.lean', '.m2', '.sing', '.g', '.gp', '.js', '.ts', '.toml', '.ini', '.cfg'}:
        return False
    if item.name in {'summary.json', 'manifest.json', 'index.json', '.gitignore',
                     'archive-exclusions.json'} or item.name.startswith(('summary.', 'source-manifest.')):
        return False
    return True


def staged_raw(root: Path) -> list[str]:
    result = subprocess.run(['git', '-C', str(root), 'diff', '--cached', '--name-only', '--diff-filter=A', '-z'],
                            capture_output=True, text=True, check=True)
    return [name for name in result.stdout.split('\0') if name and payload(name)]


def invalid_staged_zstd(root: Path) -> list[str]:
    names = subprocess.check_output(['git', '-C', str(root), 'diff', '--cached', '--name-only',
                                     '--diff-filter=AM', '-z', '--', 'research/results', 'research/provenance'], text=True)
    invalid = []
    for name in names.split('\0'):
        if not name.endswith('.zst'):
            continue
        with tempfile.TemporaryFile() as errors:
            source = subprocess.Popen(['git', '-C', str(root), 'show', ':' + name], stdout=subprocess.PIPE, stderr=errors)
            assert source.stdout is not None
            checked = subprocess.run(['zstd', '-q', '-t'], stdin=source.stdout, stdout=subprocess.DEVNULL, stderr=errors)
            source.stdout.close()
            if source.wait() or checked.returncode:
                invalid.append(name)
    return invalid


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)
    reader = commands.add_parser('read')
    reader.add_argument('path', type=Path)
    pack = commands.add_parser('pack')
    pack.add_argument('paths', nargs='+', type=Path)
    pack.add_argument('--replace', action='store_true')
    commands.add_parser('check-staged')
    args = parser.parse_args()
    if args.command == 'read':
        with open_binary(args.path) as stream:
            shutil.copyfileobj(stream, sys.stdout.buffer)
    elif args.command == 'check-staged':
        found = staged_raw(Path.cwd())
        invalid = invalid_staged_zstd(Path.cwd())
        if invalid:
            print('Invalid staged zstd evidence:\n' + '\n'.join(invalid), file=sys.stderr)
            return 1
        if found:
            print('New result/provenance data must use zstd level 3. Run tools/evidence_io.py pack --replace PATH...,\n'
                  'update links to the printed .zst paths, and restage. Existing committed data is unchanged.\n'
                  + '\n'.join(found), file=sys.stderr)
            return 1
    else:
        root = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()).resolve()
        paths = list(dict.fromkeys(path for given in args.paths
                     for path in (sorted(given.rglob('*')) if given.is_dir() else [given])
                     if path.is_file() and payload(str(path.resolve().relative_to(root)))))
        if not paths:
            raise ValueError('No raw result/provenance payloads selected')
        for path in paths:
            relative = str(path.resolve().relative_to(root))
            if path.is_symlink() or not payload(relative):
                raise ValueError(f'Not a raw evidence payload: {path}')
            if args.replace and subprocess.run(['git', 'cat-file', '-e', f'HEAD:{relative}'],
                                               capture_output=True).returncode == 0:
                raise ValueError(f'{path}: historical evidence; migration must be done separately')
        for path in paths:
            destination = compress_file(path)
            if args.replace:
                path.unlink()
            print(f'{destination}' + (' (raw input removed; zstd -d restores it)' if args.replace else ''))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f'evidence_io: {error}', file=sys.stderr)
        sys.exit(1)
