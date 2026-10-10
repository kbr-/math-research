#!/usr/bin/env python3
"""Copy one site's login cookies out of Firefox into a private file, for scripts to send.

Usage: tools/firefox_cookies.py HOST [--prefix NAME] [--out PATH] [--db COOKIES_SQLITE]

Reads a copy of the Firefox profile's cookies.sqlite (Firefox locks the live one), keeps only
the cookies of exactly HOST, or of HOST whose names start with NAME, and writes them as JSON
(name, value, domain, path, expires) to PATH, readable by the owner only. A large session
cookie split into chunks (name.0, name.1, ...) comes out whole with --prefix. Prints each
cookie's name and value length, never a value. Without --db it uses the most recently
modified cookies.sqlite under ~/.config/mozilla/firefox or ~/.mozilla/firefox.
"""
import argparse
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

PROFILE_ROOTS = ('.config/mozilla/firefox', '.mozilla/firefox')


def find_db(home: Path) -> Path:
    found = [db for root in PROFILE_ROOTS for db in (home / root).glob('*/cookies.sqlite')]
    if not found:
        sys.exit('no Firefox cookies.sqlite found; pass --db')
    return max(found, key=lambda db: db.stat().st_mtime)


def read_cookies(db: Path, host: str, prefix: str) -> list[dict]:
    with tempfile.TemporaryDirectory() as tmp:
        for suffix in ('', '-wal'):
            source = Path(str(db) + suffix)
            if source.exists():
                shutil.copy2(source, Path(tmp) / ('cookies.sqlite' + suffix))
        connection = sqlite3.connect(Path(tmp) / 'cookies.sqlite')
        try:
            rows = connection.execute(
                'SELECT name, value, host, path, expiry FROM moz_cookies '
                "WHERE host IN (?, ?) AND substr(name, 1, length(?)) = ? ORDER BY name",
                (host, '.' + host, prefix, prefix)).fetchall()
        finally:
            connection.close()
    return [{'name': n, 'value': v, 'domain': h, 'path': p, 'expires': e}
            for n, v, h, p, e in rows]


def write_private(path: Path, cookies: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as handle:
        json.dump(cookies, handle)
    os.chmod(path, 0o600)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('host')
    parser.add_argument('--prefix', default='', help='keep only cookies whose names start with this')
    parser.add_argument('--out', type=Path, help='default: ~/.cache/cookies-HOST.json')
    parser.add_argument('--db', type=Path)
    args = parser.parse_args(argv)
    home = Path.home()
    cookies = read_cookies(args.db or find_db(home), args.host, args.prefix)
    if not cookies:
        print(f'no cookies for {args.host}{" named " + args.prefix + "*" if args.prefix else ""}: '
              'signed in to it in Firefox?', file=sys.stderr)
        return 1
    out = args.out or home / '.cache' / f'cookies-{args.host}.json'
    write_private(out, cookies)
    for cookie in cookies:
        print(f"{cookie['name']}: {len(cookie['value'])} characters")
    print(f'saved to {out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
