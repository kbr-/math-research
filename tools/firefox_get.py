#!/usr/bin/env python3
"""GET a path on a host with the cookies tools/firefox_cookies.py saved for it, and print what comes back.

Usage: tools/firefox_get.py HOST PATH [--cookies FILE] [--http] [--timeout SECONDS]

Sends one GET to https://HOST/PATH (PATH with its query string) with a Cookie header built from
~/.cache/cookies-HOST.json, or FILE. Prints the body: JSON indented, anything else as it came. The status
goes to standard error, and the exit status is 0 for a 2xx answer and 1 otherwise, with what a 401 or a 403
means. Only GET is sent: this reads, and a write stays a deliberate script of its own. A redirect to another
host is not followed, so the cookies never leave HOST. No cookie value is printed.
"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HINTS = {401: 'the session expired or the cookie names are wrong: sign in again in Firefox and save the cookies again',
         403: 'the signed-in account lacks the permission the answer names'}


class SameHost(urllib.request.HTTPRedirectHandler):
    """Follows a redirect only within the host the cookies belong to."""

    def redirect_request(self, request, fp, code, message, headers, new_url):
        if urllib.parse.urlsplit(new_url).netloc != urllib.parse.urlsplit(request.full_url).netloc:
            raise urllib.error.HTTPError(request.full_url, code, f'redirect to another host not followed: {new_url}',
                                         headers, fp)
        return super().redirect_request(request, fp, code, message, headers, new_url)


def cookie_header(path):
    """The Cookie header for the cookies saved in `path`."""
    return '; '.join(f"{cookie['name']}={cookie['value']}" for cookie in json.loads(path.read_text()))


def get(url, cookie, timeout):
    """(status, body text, content type) of one GET; an error status comes back like any other."""
    request = urllib.request.Request(url, headers={'Cookie': cookie, 'Accept': 'application/json, */*;q=0.5'})
    try:
        with urllib.request.build_opener(SameHost).open(request, timeout=timeout) as answer:
            return answer.status, answer.read().decode('utf-8', 'replace'), answer.headers.get('Content-Type', '')
    except urllib.error.HTTPError as error:
        body = error.read().decode('utf-8', 'replace') if error.fp else ''
        return error.code, body or str(error.reason), error.headers.get('Content-Type', '') if error.headers else ''


def main(argv=None, home=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('host')
    parser.add_argument('path', help='the path on the host, with its query string')
    parser.add_argument('--cookies', type=Path, help='default: ~/.cache/cookies-HOST.json')
    parser.add_argument('--http', action='store_true', help='plain HTTP, for a local server')
    parser.add_argument('--timeout', type=float, default=30)
    args = parser.parse_args(argv)
    saved = args.cookies or (home or Path.home()) / '.cache' / f'cookies-{args.host}.json'
    if not saved.exists():
        print(f'no cookies saved at {saved}: sign in to {args.host} in Firefox and run tools/firefox_cookies.py {args.host}',
              file=sys.stderr)
        return 1
    url = f"{'http' if args.http else 'https'}://{args.host}/{args.path.lstrip('/')}"
    try:
        status, body, kind = get(url, cookie_header(saved), args.timeout)
    except (urllib.error.URLError, OSError) as error:
        print(f'GET {url}: no answer: {getattr(error, "reason", error)}', file=sys.stderr)
        return 1
    try:
        print(json.dumps(json.loads(body), indent=2, ensure_ascii=False))
    except ValueError:
        print(body)
    print(f'GET {url}: {status}' + (f' ({kind})' if kind else '') + (f': {HINTS[status]}' if status in HINTS else ''),
          file=sys.stderr)
    return 0 if 200 <= status < 300 else 1


if __name__ == '__main__':
    raise SystemExit(main())
