#!/usr/bin/env python3
"""Check that Research-record entries of a base revision are unchanged: the notebook is append-only.

Every <article id=...> of BASE:notebook.html must reappear in the working notebook with the same
text. Only presentation changes are tolerated, as AGENTS.md allows: <a ...> and </a> tags are
ignored (link repairs), a non-breaking space counts as a space (layout), and adding paired inline
MathJax delimiters around unchanged parenthesized text is allowed. Removing or moving existing
delimiters, or changing code or displayed mathematics, is not a presentation repair.
Usage: check-append-only.py [--base REF]   (default origin/main; exit 1 on any changed or missing entry)"""
import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def entries(body):
    record = body.find('<section id="research-record">')
    found = re.finditer(r'<article\b[^>]*\bid="([^"]+)"[^>]*>.*?</article>', body[max(record, 0):], re.S)
    matches = list(found)
    if len({m.group(1) for m in matches}) != len(matches):
        raise ValueError('Duplicate research article IDs')
    return {match.group(1): normalize(match.group(0)) for match in matches}


def normalize(article):
    article = re.sub(r'</?a\b[^>]*>', '', article)
    return article.replace('&nbsp;', ' ').replace('\u00a0', ' ')


def inline_math_view(text):
    """Plain parenthesized text and the spans already marked as inline mathematics.

    Positions refer to that plain text, so adding a delimiter does not move later spans.
    Protected HTML blocks, comments, tags and displayed mathematics remain byte-for-byte.
    """
    tokens = re.compile(
        r'<!--.*?-->|(?P<html><(?:[^>"\']|"[^"]*"|\'[^\']*\')*>)|'
        r'(?P<display>\\\[|\\\])|(?P<inline>\\\((?P<body>[^<]*?)\\\))', re.S)
    pieces, spans, protected, displayed, end, length = [], set(), [], False, 0, 0
    for token in tokens.finditer(text):
        gap = text[end:token.start()]
        pieces.append(gap)
        length += len(gap)
        value = token.group()
        if token.group('html'):
            tag = re.match(r'<(/?)([a-zA-Z][\w:-]*)', value)
            if tag:
                closing, name = tag.group(1), tag.group(2).lower()
                if protected and protected[-1] in ('script', 'style'):
                    if closing and name == protected[-1]:
                        protected.pop()
                elif name in ('pre', 'code', 'script', 'style'):
                    if not closing:
                        protected.append(name)
                    elif protected and name == protected[-1]:
                        protected.pop()
                    elif name in protected:
                        return None
        elif token.group('display') and not protected:
            if value == r'\[' and displayed:
                return None
            displayed = value == r'\['
        elif token.group('inline') and not protected and not displayed:
            if any(marker in token.group('body') for marker in (r'\(', r'\[', r'\]')):
                return None
            value = '(' + token.group('body') + ')'
            spans.add((length, length + len(value)))
        pieces.append(value)
        length += len(value)
        end = token.end()
    pieces.append(text[end:])
    return None if protected or displayed else (''.join(pieces), spans)


def presentation_equal(before, after):
    if before == after:
        return True
    old, new = inline_math_view(before), inline_math_view(after)
    return old is not None and new is not None and old[0] == new[0] and old[1] <= new[1]


def record_articles_text(body):
    """The record from its section tag through the last article's end."""
    start = body.find('<section id="research-record">')
    end = body.rfind('</article>')
    return body[start:end + len('</article>')] if 0 <= start < end else None


def violations(base_body, current_body):
    # Fast path: entries are appended at the record's end, so an untouched record starts with the base's.
    # Anything else (link repairs, layout spaces, real changes) takes the full comparison below.
    record = record_articles_text(base_body)
    if record is not None and current_body[current_body.find('<section id="research-record">'):].startswith(record):
        return [], []
    base, current = entries(base_body), entries(current_body)
    missing = [name for name in base if name not in current]
    changed = [name for name in base if name in current and not presentation_equal(base[name], current[name])]
    if [name for name in current if name in base] != [name for name in base if name in current]:
        changed.append('(historical entry order)')
    return missing, changed


def check(root, ref):
    from notebooks import paths
    root = Path(root)
    listing = subprocess.run(['git','ls-tree','-r','--name-only',ref],cwd=root,capture_output=True,text=True)
    if listing.returncode:
        return None
    before = [p for p in listing.stdout.splitlines() if p == 'notebook.html' or
              re.fullmatch(r'research/branches/[^/]+/notebook.html',p)]
    current = {p.relative_to(root).as_posix() for p in paths(root)}
    present = [p for p in before if p in current and (root/p).exists()]
    diff = subprocess.run(['git','diff','--name-only',ref,'--',*present],cwd=root,capture_output=True,text=True)
    differing = set(diff.stdout.splitlines()) if diff.returncode == 0 else set(present)
    missing, changed, compared_bytes = [], [], 0
    for path in before:
        if path not in current or not (root/path).exists():
            missing.append(path + ' (notebook deleted or unregistered)'); continue
        if path not in differing:   # identical to the base revision
            continue
        shown = subprocess.check_output(['git','show',f'{ref}:{path}'],cwd=root,text=True)
        current_text = (root/path).read_text()
        compared_bytes += len(shown.encode('utf-8')) + (root/path).stat().st_size
        left,right = violations(shown,current_text)
        missing.extend(path+'#'+x for x in left)
        changed.extend(path+'#'+x for x in right)
    print(f'Append-only input: {len(before)} registered notebook paths; {compared_bytes} compared bytes.')
    return missing, changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='origin/main')
    args = parser.parse_args()
    result = check(ROOT, args.base)
    if result is None:
        print(f'check-append-only.py: cannot read {args.base}:notebook.html; nothing checked')
        return 0
    missing, changed = result
    for name in missing:
        print(f'MISSING entry {name}')
    for name in changed:
        print(f'CHANGED entry {name}')
    if missing or changed:
        print('The notebook is append-only: restore these entries and put corrections in a new dated entry.')
        return 1
    print(f'Entries of {args.base} are unchanged.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
