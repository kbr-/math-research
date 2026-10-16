#!/usr/bin/env python3
"""The registered claims a draft's claim summaries resemble, before the review.

Registration refuses a new claim that resembles a registered one unless the spec relates the two
(claim_authoring.similar_claims), but registration comes after the entry is drafted and reviewed.  On 11 October
2026 an entry presented as new what a registered finite check already had for three of its six sizes; its
reviewer found the earlier claim.  This tool runs the same search on a compact spec when it is first drafted
and prints, for each of its claims, the registered claims its summary most resembles, with scores, whatever
the spec's relationships say and whatever the threshold: the author reads those records before writing the
entry's claim of novelty.

Usage: claim_resemblance.py SPEC.json [--count N] [--registry PATH]
The spec is the compact form `claim-index.py author build` takes (a "claims" list with "id" and "summary").
It also prints, per claim, the three Working mathematical context sentences of the notebook whose words the
claim most contains. Prints the registry's size, which the work grows with.
"""
import argparse
import math
import re
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from claim_authoring import SIMILAR_AT, similar_claims


DEFAULT_REGISTRY = ROOT / 'research' / 'claims' / 'index.json'
RUN_LOG = ROOT / 'research' / 'logs' / 'claim-searches.jsonl'


def log_run(idents, path=None):
    """Append this run to the ignored log of record searches, which the finisher reads: an entry of 11 October
    2026 said what its corollary added before the nearest registered claims were read, the tool having been
    run only after the review.  A log that cannot be written is not an error."""
    import time
    try:
        path = path or RUN_LOG
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a') as handle:
            handle.write(json.dumps({'unix_s': time.time(), 'query': 'claim_resemblance ' + ' '.join(idents)}) + '\n')
    except OSError:
        pass


def resemblances(registered, spec, count=5):
    """[(draft id, [(score, registered id, summary start), ...]), ...] for the spec's claims; a claim already
    registered under the same id is not compared with itself."""
    summaries = {claim['id']: claim.get('summary', '') for claim in registered}
    out = []
    for claim in spec.get('claims', []):
        others = [c for c in registered if c['id'] != claim['id']]
        found = similar_claims(others, claim['summary'], count)
        out.append((claim['id'], [(score, ident, summaries[ident][:160]) for score, ident in found]))
    return out


QUEUED_AT = 0.4     # measured 11 October 2026 on one notebook's 34 claims and 66 queued items: the known answered
                    # item scores 0.53, and 8 pairs reach 0.4 (34 reach 0.3, 211 reach 0.2)


def queued_matches(nodes, spec, threshold=QUEUED_AT):
    """[(share, draft id, queued id), ...], most alike first: queued items whose wording a draft claim's summary
    shares.  The share is the common content words over those of the queued item, so a long summary does not
    hide a short question.  On 11 October 2026 a queued check waited in the queue long after the lemma that
    answers it was registered by an entry developing another item; a hint to read the item, not a verdict."""
    import lead_queue
    flat = [(n.ident, lead_queue.content_words(n.text)) for top in nodes for n in [top] + top.children]
    out = []
    for claim in spec.get('claims', []):
        words = lead_queue.content_words('): ' + claim.get('summary', '') + ' ' + claim.get('assessment', ''))
        for ident, item in flat:
            if len(item) >= 5:
                share = len(words & item) / len(item)
                if share >= threshold:
                    out.append((round(share, 2), claim['id'], ident))
    return sorted(out, reverse=True)


CONTEXT_SHOWN = 3   # Working-context sentences printed per claim
CONTEXT_STOP = set('with that this from which their have each when only does into than then them they also must over '
                   'under were what where while about after before other these those such'.split())


def _stems(text):
    """Five-letter prefixes of the words of four or more letters, without markup and inline formulas: weights,
    weighted and weight share one."""
    text = re.sub(r'\\\(.*?\\\)', ' ', re.sub(r'<[^>]+>', ' ', text))
    return {w[:5] for w in re.findall(r'[a-z]{4,}', text.lower()) if w not in CONTEXT_STOP}


def context_sentences(notebook_text):
    """[(sentence html, first link href or ''), ...] of the notebook's Working mathematical context section."""
    found = re.search(r'<section id="working-context">(.*?)</section>', notebook_text, re.S)
    if not found:
        return []
    body = ' '.join(re.sub(r'<h[1-6][^>]*>.*?</h[1-6]>', ' ', found.group(1), flags=re.S).split())
    out = []
    for sentence in re.split(r'(?<=[.;])\s+(?=[A-Z<])', body):
        link = re.search(r'href="([^"]+)"', sentence)
        out.append((sentence, link.group(1) if link else ''))
    return [(s, link) for s, link in out if len(_stems(s)) >= 2]


def context_matches(sentences, spec, count=CONTEXT_SHOWN):
    """[(draft id, [(share, sentence text, link), ...]), ...]: the living context sentences most of whose words,
    weighted by inverse frequency among the sentences, a draft claim's summary and assessment contain.

    The character error thin-tail spec of 16 October 2026 scored 0.21 or less against every registered claim
    while the Working context already said "Sparse weights give h_w(K) >= h(K)/s", the result its first two parts
    restate; measured on the context of that day, this share ranks that sentence first, at 0.62."""
    frequency = {}
    for sentence, _ in sentences:
        for stem in _stems(sentence):
            frequency[stem] = frequency.get(stem, 0) + 1
    weight = {stem: math.log(1 + len(sentences) / seen) for stem, seen in frequency.items()}
    out = []
    for claim in spec.get('claims', []):
        mine = _stems(claim.get('summary', '') + ' ' + claim.get('assessment', ''))
        scored = []
        for sentence, link in sentences:
            stems = _stems(sentence)
            total = sum(weight[s] for s in stems)
            share = sum(weight[s] for s in stems & mine) / total if total else 0.0
            text = ' '.join(re.sub(r'<[^>]+>', ' ', sentence).split())
            scored.append((round(share, 2), text, link))
        out.append((claim['id'], sorted(scored, key=lambda row: -row[0])[:count]))
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('spec')
    parser.add_argument('--count', type=int, default=5)
    parser.add_argument('--registry', default=str(DEFAULT_REGISTRY))
    parser.add_argument('--notebook', help='notebook file whose queue is compared (default: the selected one)')
    args = parser.parse_args(argv)
    registered = json.loads(pathlib.Path(args.registry).read_text())['claims']
    spec = json.loads(pathlib.Path(args.spec).read_text())
    if args.registry == str(DEFAULT_REGISTRY):       # a run on the record: logged for the finisher, as searches are
        log_run([claim['id'] for claim in spec.get('claims', [])])
    print(f'{len(registered)} registered claims compared; registration refuses a score of {SIMILAR_AT} or more '
          'unless the spec relates the two.')
    related = {tuple(edge[:1] + edge[2:3]) for edge in spec.get('relationships', [])}
    for ident, found in resemblances(registered, spec, args.count):
        print(f'{ident}:')
        for score, other, start in found:
            mark = ' (related in the spec)' if (ident, other) in related or (other, ident) in related else ''
            print(f'  {score:.2f} {other}{mark}: {start}')
    if args.notebook or args.registry == str(DEFAULT_REGISTRY):
        import lead_queue
        if args.notebook:
            import notebooks
            notebook = notebooks.notebook_file(args.notebook)
        else:
            import notebooks
            notebook = ROOT / notebooks.selected()['source']
        text = notebook.read_text()
        for ident, rows in context_matches(context_sentences(text), spec):
            print(f'{ident}: nearest Working mathematical context sentences (read each; a result stated there is '
                  'not new):')
            for share, sentence, link in rows:
                print(f'  {share:.2f} {sentence[:200]}' + (f' [{link}]' if link else ''))
        found = lead_queue.parse_tree(text)
        nodes = found[1] if found else []
        count = sum(1 + len(n.children) for n in nodes)
        matches = queued_matches(nodes, spec)
        print(f'{count} queued items compared; a share of {QUEUED_AT} or more of an item\'s words is listed.')
        for share, ident, queued in matches:
            print(f'  {share:.2f} {ident} ~ queued {queued}: read the item; if the claim answers it, close it '
                  'in this entry\'s follow-up list')
    return 0


if __name__ == '__main__':
    sys.exit(main())
