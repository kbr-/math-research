"""The audit entry for the odd-prime-reslin-php lead and bridge queue (3 October 2026), from the saved verdicts.

Items are keyed by (kind, id): a review's lead and bridge share the id ANCHOR:N.  Final verdict of a passed item: the
strict second pass's for items the first pass judged properly closed (confirmed keeps it closed), the first pass's
otherwise.  The packets second-1/2 were built from an id-keyed map, so rows whose packet held the same-id bridge are
discarded and second-3 reruns those leads with the right packets.  Reopen and undecided items are reopened (when
unsure, queue it).  An idea of an older review is queued (verdict queue or undecided) unless a later standard item it
names is itself queued, which already carries it.  Writes DIR/final.json and DIR/entry.html.
Usage: python3 opr_queue_audit_entry.py DIR"""
import html
import json
import re
import sys
from pathlib import Path

D = Path(sys.argv[1])
NB = Path('research/branches/odd-prime-reslin-php/notebook.html').read_text()


def lines(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def key(item):
    return item['kind'], item['id']


items = lines(D / 'items.jsonl')
batches = [i for b in range(1, 6) for i in lines(D / f'batch-{b}.jsonl')]
fv = [v for b in range(1, 6) for v in lines(D / f'verdicts-batch-{b}.jsonl')]
assert [key(i) for i in batches] == [key(i) for i in items] and [i['id'] for i in items] == [v['id'] for v in fv]
first = {key(i): v for i, v in zip(items, fv)}
closed_ok = [key(i) for i in items if first[key(i)]['verdict'] == 'properly-closed']
rows = [r for k in (1, 2) for r in lines(D / f'second-{k}.jsonl')]
sv = [v for k in (1, 2) for v in lines(D / f'second-verdicts-{k}.jsonl')]
assert len(rows) == len(sv) == len(closed_ok) and all(r['id'] == v['id'] for r, v in zip(rows, sv))
second = {k: v for k, r, v in zip(closed_ok, rows, sv) if key(r) == k}
rerun = lines(D / 'second-verdicts-3.jsonl')
assert sorted(('lead', v['id']) for v in rerun) == sorted(set(closed_ok) - set(second))
second.update({('lead', v['id']): v for v in rerun})
final = {}
for item in items:
    k = key(item)
    v = second.get(k, first[k])
    verdict = {'confirmed': 'kept-closed', 'properly-closed': 'kept-closed'}.get(v['verdict'], v['verdict'])
    final[k] = dict(v, id=item['id'], kind=item['kind'], verdict=verdict, stage='second' if k in second else 'first',
                    closed=bool(item['trail']) and item['trail'][-1]['outcome'] == 'Closed')
# an id names a lead and a bridge alike: count it as queued only when every item with that id is queued
queued = {i for _, i in final} - {i for (_, i), v in final.items() if v['verdict'] not in ('reopen', 'undecided')}
ids = {i for _, i in final}
older = lines(D / 'older-verdicts-1.jsonl') + lines(D / 'older-verdicts-2.jsonl')
older_check = lines(D / 'second-verdicts-older.jsonl')
order = [m.group(1) for m in re.finditer(r'<article\b[^>]*\bid="([^"]+)"', NB)]
older.sort(key=lambda o: order.index(o['review']))    # record order of the source reviews (stable within one)
for o in older:
    refs = [r for r in re.findall(r'entry-[\w-]+:\d+', o['reason'] + ' ' + o['text']) if r in ids]
    o['carried_by'] = [r for r in refs if r in queued]
    o['final'] = 'carried' if o['carried_by'] else ('queue' if o['verdict'] in ('queue', 'undecided') else 'exhausted')
assert {(c['review'], c['title']) for c in older_check} == {(o['review'], o['title']) for o in older
                                                             if o['verdict'] == 'exhausted'}
(D / 'final.json').write_text(json.dumps({'items': list(final.values()), 'older': older}, ensure_ascii=False,
                                         indent=1) + '\n')


def esc(text):
    return html.escape(text, quote=False)


def title(k):
    return next(i['text'] for i in items if key(i) == k).split('. ')[0][:160]


def count(verdict):
    return sum(v['verdict'] == verdict for v in final.values())


def link(k):
    return f'<a href="#{k[1].rsplit(":", 1)[0]}">{k[1]}</a> ({k[0]})'


reopen = [k for k, v in final.items() if v['verdict'] in ('reopen', 'undecided') and v['closed']]
already = [k for k, v in final.items() if v['verdict'] in ('reopen', 'undecided') and not v['closed']]
new = [o for o in older if o['final'] == 'queue']
overturned = sum(v['verdict'] != 'confirmed' for v in second.values())
followups = '\n'.join(
    f'<li data-{k[0]}="{k[1]}">{link(k)}, {esc(title(k))}: {esc(final[k]["reason"])} Next: '
    f'{esc(final[k]["next_attempt"] or "develop it against the open statements")} <strong>Follow-up.</strong> '
    f'Reopened: {"undecided, so queued" if final[k]["verdict"] == "undecided" else "closed before it was squeezed"}'
    f' ({final[k]["stage"]} pass).</li>' for k in reopen)


def recovered(kind):
    return '\n'.join(f'<li data-source="{o["review"]}"><a href="#{o["review"]}">{o["review"]}</a>: '
                     f'<strong>{esc(o["title"])}.</strong> {esc(o["text"])} Audit: {esc(o["reason"])}'
                     f'{" (undecided, so queued)" if o["verdict"] == "undecided" else ""}</li>'
                     for o in new if o['kind'] == kind)


kept = '\n'.join(f'<li>{link(k)}: {esc(v["reason"])}</li>' for k, v in final.items() if v['verdict'] == 'kept-closed')
n_older = len((D / 'older-reviews.txt').read_text().split())
confirmed_older = sum(c['verdict'] == 'confirmed' for c in older_check)
entry = f'''<article class="research-entry" id="entry-2026-10-03-queue-audit" data-kind="audit" data-route="scope-and-review" data-claims="none" data-claim-note="Audit of the thread's Outside leads and Absurd bridges against the squeeze rule, creating the lead and bridge queue; no mathematical claim.">
<h3>Queue audit: {len(reopen)} closed leads and bridges reopened, {len(new)} ideas of older reviews queued, and the lead and bridge queue created</h3>
<p class="entry-meta">3 October 2026 · Audit · every passed lead and bridge of the record · cycle odd-prime-queue-audit.</p>
<p><strong>Question.</strong> The thread predates the lead and bridge queue and the squeeze rule (AGENTS.md, user, 3 October 2026: squeeze an item until it can produce nothing more; close it only for a reason the attempt found). Which of its {len(items)} passed Outside leads and Absurd bridges were closed before they were squeezed, and which ideas did its {n_older} reviews without the standard sections list that no later entry exhausted? The user's standard: "I don't want any idea lost or closed prematurely"; when unsure, queue it.</p>
<p><strong>Method.</strong> Packets (<code>research/tools/opr_queue_audit_packets.py</code>) give each passed item its text and every later follow-up naming it. Five readers judged batches of about 33 items against a written bar (<code>BAR.md</code>), opening each closing entry; two more read the older reviews for leads and bridges outside the standard sections and searched later entries for their development. A stricter second pass rechecked every verdict that a closure was proper, opening the closing entry and every cited source. Sixteen leads share their id with a bridge of the same review, and their first second-pass packets held that bridge's text; they were rechecked with the right packets (<code>second-verdicts-3.jsonl</code>). The older ideas judged exhausted were rechecked the same way ({confirmed_older} of {len(older_check)} confirmed, <code>second-verdicts-older.jsonl</code>). Final verdicts: the second pass's where it ran, otherwise the first's; reopen and undecided items are queued. All verdicts, with reasons and the anchors opened, are in <code>research/results/opr-20261003-queue-audit/</code> (<code>final.json</code>, built by <code>research/tools/opr_queue_audit_entry.py</code>).</p>
<p><strong>Outcome.</strong> Of {len(items)} passed items: {count('reopen')} reopened, {count('undecided')} undecided and queued, {count('kept-closed')} kept closed. The first pass judged {len(second)} closures proper; the second pass overturned {overturned} of them. The older reviews list {len(older)} ideas: {len(new)} newly queued, {sum(o['final'] == 'carried' for o in older)} already carried by a queued standard item, {sum(o['final'] == 'exhausted' for o in older)} exhausted by later entries. {len(already)} item(s) were never closed and are queued as they stand.</p>
<h4>Reopened</h4>
<ul>
{followups}
</ul>
<h4>Outside leads</h4>
<ul>
{recovered('lead')}
</ul>
<h4>Absurd bridges</h4>
<ul>
{recovered('bridge')}
</ul>
<h4>Kept closed</h4>
<ul>
{kept}
</ul>
<p><strong>Remaining gap.</strong> The audit judges closures from the record; it develops no item. Research entries develop the queue from its head under the squeeze rule.</p>
<!-- TIMING opr-20261003-queue-audit -->
</article>
'''
(D / 'entry.html').write_text(entry)
print(f'reopen {count("reopen")}, undecided {count("undecided")}, kept closed {count("kept-closed")}, overturned '
      f'{overturned} of {len(second)}; older: queued {len(new)}, carried {sum(o["final"] == "carried" for o in older)}, '
      f'exhausted {sum(o["final"] == "exhausted" for o in older)}; never closed {len(already)}')
