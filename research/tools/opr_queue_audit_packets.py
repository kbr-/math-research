"""Packets for the odd-prime-reslin-php lead and bridge audit (3 October 2026).

For every passed Outside lead or Absurd bridge of a review with the standard sections, writes one JSON line: its
queue id, kind, review anchor, full text, and every follow-up list item that later names it, in record order, with
the naming entry's anchor and outcome.  Also lists the reviews without the standard sections (older format), whose
leads the queue tool cannot see, for a separate reading.
Usage: python3 opr_queue_audit_packets.py OUTDIR"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, 'tools')
import lead_queue as lq  # noqa: E402

NB = 'research/branches/odd-prime-reslin-php/notebook.html'
out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
body = open(NB).read()
arts = lq.record_articles(body)


def plain(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html)).strip()


trail = {}
for tag, text in arts:
    ident = re.search(r'\bid="([^"]+)"', tag)
    for kind, item_id, item in lq.FOLLOWUP_ITEM.findall(text):
        outcome = lq.OUTCOME_RE.search(item)
        trail.setdefault((kind, item_id), []).append(
            {'entry': ident.group(1) if ident else None, 'outcome': outcome.group(1) if outcome else None,
             'text': plain(item)})
items = []
for tag, text in arts:
    ident = re.search(r'\bid="([^"]+)"', tag)
    for kind, item_id in lq.review_passed(tag, text):
        section = (lq.LEADS_RE if kind == 'lead' else lq.BRIDGES_RE).search(text)
        n = int(item_id.rsplit(':', 1)[1])
        li = re.findall(r'<li\b[^>]*>(.*?)</li>', section.group(1), re.S)[n - 1]
        items.append({'id': item_id, 'kind': kind, 'review': ident.group(1), 'text': plain(li),
                      'trail': trail.get((kind, item_id), [])})
with open(out / 'items.jsonl', 'w') as f:
    for item in items:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')
older = [re.search(r'\bid="([^"]+)"', t).group(1) for t, x in arts
         if 'data-kind="review"' in t and not (lq.LEADS_RE.search(x) or lq.BRIDGES_RE.search(x))
         and re.search(r'\bid="', t)]
(out / 'older-reviews.txt').write_text('\n'.join(older) + '\n')
print(len(items), 'passed items;', len(older), 'reviews without the standard sections')
