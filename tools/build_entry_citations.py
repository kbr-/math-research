#!/usr/bin/env python3
"""List a notebook's entries on build items that declare no claims, with the claim their General statement cites.

Usage: tools/build_entry_citations.py NOTEBOOK.html

Such an entry has no all-parameter claim, and until 11 October 2026 the finisher made it cite a registered one.
The listing shows each entry's paragraph, so that a reader can say which citations were made only for the check."""
import html
import re
import sys
from pathlib import Path

ARTICLE = re.compile(r'<article id="([^"]+)"([^>]*)>(.*?)</article>', re.S)
GENERAL = re.compile(r'<p><strong>General statement\.</strong>(.*?)</p>', re.S)
CLAIM = re.compile(r'\b(?:conj|lem|thm|prop|cor):[a-z0-9-]+')


def build_entries(text):
    """(entry, cited claims, paragraph) for each entry tagged with a build item and declaring no claims."""
    found = []
    for ident, tags, body in ARTICLE.findall(text):
        if not (re.search(r'\bdata-build="[^"]+"', tags) and 'data-claims="none"' in tags):
            continue
        general = GENERAL.search(body)
        paragraph = ' '.join(html.unescape(re.sub(r'<[^>]*>', ' ', general.group(1))).split()) if general else ''
        found.append((ident, CLAIM.findall(paragraph), paragraph))
    return found


def main():
    if len(sys.argv) != 2 or sys.argv[1].startswith('-'):
        sys.exit(__doc__.split('\n\n')[1])
    entries = build_entries(Path(sys.argv[1]).read_text())
    for ident, claims, paragraph in entries:
        print(f'{ident}\t{" ".join(claims) or "-"}\t{paragraph}')
    citing = sum(1 for _, claims, _ in entries if claims)
    print(f'{len(entries)} build entries without claims; {citing} name a claim identifier in their General statement '
          '(by its form; the registry is not consulted).')


if __name__ == '__main__':
    main()
