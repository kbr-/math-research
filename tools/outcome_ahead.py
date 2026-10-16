#!/usr/bin/env python3
"""List a notebook's research entries that are firm in one place while their body hedges.

Usage: tools/outcome_ahead.py [--decided] NOTEBOOK.html | [--decided] --transcript SESSION.jsonl

Firm: the Architecture test reports Decided, or, without --decided, the status line also says proved, verified,
measured or working proof.  Hedge: a sentence of the body saying in outline, in shape only, not checked, not
verified, not run, not proved or the like.  The words cannot tell whether a hedge is about the matter the firm
word is about.  With --transcript it reads a Claude Code session's transcript and lists the first written
version of each entry, the draft before its review.

Measured on one notebook on 11 October 2026: with the status line the listing flags about half the recorded
research entries, where a proved lemma and a hedge about its consequence stand side by side by rule; with
--decided it flags one recorded entry and two first drafts.  The finisher prints the --decided report only."""
import html
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from notebook_math import strip_tags  # noqa: E402

ARTICLE = re.compile(r'(<article id="(entry-[^"]+)"[^>]*>.*?)</article>', re.S)
FIRM = re.compile(r'\b(?:proved|verified|measured|working proofs?)\b', re.I)
HEDGE = re.compile(r'\b(?:in outline|an outline|in shape only|not checked|unchecked|not verified|unverified|'
                   r'not run|not proved|unproved)\b', re.I)
TEST = re.compile(r'<p><strong>Architecture test\.</strong>(.*?)</p>', re.S)
SUGGESTIONS = re.compile(r"<h4>Reviewer's suggestions, unverified</h4>\s*<ul>.*?</ul>", re.S)


def plain(text):
    return ' '.join(html.unescape(strip_tags(text)).split())


def report(entry, status_line=True):
    """The lines for one research entry, or none: its firm sentences and, beside them, its hedging ones.

    The reviewer's suggestions are skipped, their heading saying unverified by rule."""
    if not re.search(r'<article\b[^>]*\bdata-kind="research"', entry):
        return []
    status = re.search(r'<p class="entry-meta">(.*?)</p>', entry, re.S)
    firm = [plain(status.group(1))] if status_line and status and FIRM.search(plain(status.group(1))) else []
    test = TEST.search(entry)
    if test and '<strong>Decided.</strong>' in test.group(1):
        firm.append('Architecture test. ' + plain(test.group(1))[:240])
    if not firm:
        return []
    body = SUGGESTIONS.sub(' ', entry)
    body = body.replace(status.group(0), ' ') if status else body
    hedges = [sentence for paragraph in re.findall(r'<(?:p|li)\b[^>]*>(.*?)</(?:p|li)>', body, re.S)
              for sentence in re.split(r'(?<=[.;:])\s+', plain(paragraph)) if HEDGE.search(sentence)]
    if not hedges:
        return []
    return ([f'  firm: {line[:300]}' for line in firm] + [f'  hedge: {sentence[:300]}' for sentence in hedges[:8]]
            + ([f'  and {len(hedges) - 8} more hedging sentences'] if len(hedges) > 8 else []))


def flags(text, status_line=True):
    """(entry, lines) for each flagged entry, and the numbers of entries and of research entries."""
    entries = ARTICLE.findall(text)
    research = sum('data-kind="research"' in body[:body.index('>')] for body, _ in entries)
    found = [(ident, lines) for body, ident in entries if (lines := report(body, status_line))]
    return found, len(entries), research


def first_drafts(lines):
    """The first version of each entry a Claude Code session wrote with its Write tool, joined as one text.

    The transcript is one JSON object per line; an entry's first written version is its draft before review,
    where a notebook's record holds the text after the reviewer's corrections."""
    drafts = {}
    for line in lines:
        try:
            content = json.loads(line).get('message', {}).get('content', [])
        except (ValueError, AttributeError):
            continue
        for block in content if isinstance(content, list) else []:
            if not (isinstance(block, dict) and block.get('type') == 'tool_use' and block.get('name') == 'Write'):
                continue
            text = str(block.get('input', {}).get('content', ''))
            ident = re.match(r'\s*<article id="(entry-[^"]+)"', text)
            if ident:
                drafts.setdefault(ident.group(1), text if '</article>' in text else text + '</article>')
    return '\n'.join(drafts.values())


def main():
    arguments = sys.argv[1:]
    decided = '--decided' in arguments
    transcript = '--transcript' in arguments
    paths = [argument for argument in arguments if argument not in ('--decided', '--transcript')]
    if len(paths) != 1 or paths[0].startswith('-'):
        sys.exit(__doc__.split('\n\n')[1])
    text = Path(paths[0]).read_text()
    found, entries, research = flags(first_drafts(text.splitlines()) if transcript else text, not decided)
    for ident, lines in found:
        print(ident)
        print('\n'.join(lines))
        print()
    print(f'{entries} entries, {research} research; {len(found)} flagged.')


if __name__ == '__main__':
    main()
