#!/usr/bin/env python3
"""How many recorded entries the append tool's refusal of an unverified suggestion named as a next attempt
(tools/notebook-append.py: unverified_attempts) would have refused, by their follow-ups alone.

No statement tested: a measurement of a framework check on the notebooks' own records, for the build item
next-step-names-unverified-suggestion.  The next steps that accompanied past entries are not in the record, so
only follow-ups are measured.

Usage: measure.py NOTEBOOK [ANCHOR ...]
Prints: the number of articles; how many have a list of reviewer's suggestions; how many have a Follow-up
naming a next attempt; how many the check finds, by reason, with their anchors; whether each ANCHOR given is
among them; and the time.
"""
import importlib.util
import re
import sys
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[3] / 'tools'
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location('notebook_append', TOOLS / 'notebook-append.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def main():
    start = time.time()
    body = Path(sys.argv[1]).read_text()
    wanted = sys.argv[2:]
    record = body[body.index('<section id="research-record">'):]
    articles = re.findall(r'<article\b[^>]*\bid="([^"]+)"[^>]*>(.*?)</article>', record, re.S)
    listed = attempts = 0
    found = {}
    for anchor, text in articles:
        entry = f'<article id="{anchor}">{text}</article>'
        listed += bool(tool.SUGGESTIONS.search(entry))
        attempts += any(tool.ATTEMPT_SENTENCE.search(tool.plain(follow))
                        for follow in re.findall(r'<p><strong>Follow-up\.</strong>((?:(?!</p>).)*)</p>', entry, re.S))
        hits = tool.unverified_attempts(entry)
        if hits and not tool.CHECKED.search(entry):
            found[anchor] = hits[0][1]
    print(f'{len(articles)} articles ({len(body) / 1e6:.1f} MB); {listed} with a list of reviewer\'s suggestions; '
          f'{attempts} with a Follow-up naming a next attempt; {len(found)} the check would refuse')
    for reason in sorted(set(found.values())):
        anchors = [a for a, r in found.items() if r == reason]
        print(f'  {len(anchors)}: {reason}: {", ".join(anchors[:12])}{" ..." if len(anchors) > 12 else ""}')
    for anchor in wanted:
        print(f'  {anchor}: {"refused, " + found[anchor] if anchor in found else "not refused"}')
    print(f'time {time.time() - start:.2f} s')


if __name__ == '__main__':
    main()
