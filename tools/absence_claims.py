#!/usr/bin/env python3
"""List the sentences of closing entries that say something is not kept, not recorded or not there.

Usage: tools/absence_claims.py NOTEBOOK.html

A draft of 11 October 2026 closed a queue item on two such statements about the framework itself (the drafts
are not kept; nothing records what a session read), both false and both checkable in the tree.  This lists,
for the entries of a record whose own Follow-up is Closed or Developed, each sentence that claims an absence,
so that a reader can check it where it can be checked.  The results of a registry search, after "Record
search.", are left out.  The words cannot tell a claim about the repository from one about mathematics or a
source."""
import html
import re
import sys
from pathlib import Path

ARTICLE = re.compile(r'<article id="(entry-[^"]+)"[^>]*>(.*?)</article>', re.S)
# The entry's own follow-up is a paragraph; a sub-idea's is a list item and removes no top-level item.
CLOSES = re.compile(r'<p><strong>Follow-up\.</strong>\s*(?:Closed|Developed)\b')
# What a registry search did not find is checked by the finisher against the session's logged searches.
SEARCHED = re.compile(r'<strong>Record search\.</strong>.*?(?=<strong>|$)', re.S)
WIDTH = 300
ABSENCE = re.compile(
    r'\b(?:is|are|was|were) (?:not|never) (?:kept|recorded|saved|logged|stored|tracked)\b'
    r'|\b(?:no|nothing) (?:\w+ ){0,3}(?:records?|logs?|keeps?|saves?|stores?|tracks?)\b'
    r'|\b(?:does|do|did) not exist\b|\bis gone\b|\bare gone\b|\bno longer exists?\b'
    r'|\b(?:is|are) not on record\b|\bnot (?:kept|recorded) anywhere\b', re.I)
SUGGESTIONS = re.compile(r"<h4>Reviewer's suggestions, unverified</h4>\s*<ul>.*?</ul>", re.S)


def sentences(entry):
    """The entry's sentences that claim an absence, the reviewer's suggestions apart."""
    body = SUGGESTIONS.sub(' ', entry)
    found = []
    for paragraph in re.findall(r'<(?:p|li)\b[^>]*>(.*?)</(?:p|li)>', body, re.S):
        plain = ' '.join(html.unescape(re.sub(r'<[^>]*>', ' ', SEARCHED.sub(' ', paragraph))).split())
        for sentence in re.split(r'(?<=[.;])\s+', plain):
            match = ABSENCE.search(sentence)
            if match:
                found.append(window(sentence, match))
    return found


def window(sentence, match):
    """At most WIDTH characters of the sentence that hold the matched words."""
    if len(sentence) <= WIDTH:
        return sentence
    start = max(0, min(match.start() - WIDTH // 2, len(sentence) - WIDTH))
    return ('… ' if start else '') + sentence[start:start + WIDTH] + (' …' if start + WIDTH < len(sentence) else '')


def report(entry):
    """Lines for a closing entry, or none."""
    if not CLOSES.search(entry):
        return []
    return [f'  absence: {sentence}' for sentence in sentences(entry)]


def survey(text):
    """(entry, lines) for each closing entry with such sentences, and the number of closing entries."""
    entries = ARTICLE.findall(text[text.find('<section id="research-record"'):])
    closing = [(ident, body) for ident, body in entries if CLOSES.search(body)]
    return [(ident, lines) for ident, body in closing if (lines := report(body))], len(closing)


def main():
    if len(sys.argv) != 2 or sys.argv[1].startswith('-'):
        sys.exit(__doc__.split('\n\n')[1])
    found, closing = survey(Path(sys.argv[1]).read_text())
    for ident, lines in found:
        print(ident)
        print('\n'.join(lines))
        print()
    print(f'{closing} closing entries; {len(found)} hold a sentence that claims an absence, '
          f'{sum(len(lines) for _, lines in found)} sentences in all.')


if __name__ == '__main__':
    main()
