#!/usr/bin/env python3
"""The registered claims nearest an entry's declared claims that its Record comparison does not name.

tools/claim_resemblance.py prints, for each claim of a draft's spec, the registered claims its summary most
resembles, and asks the author to say of each whether it is more general or a special case.  On 17 October 2026
an entry's Record comparison passed over cor:star-closure-ratio, which that listing had printed and which the
entry itself cited in its Best outcome, and called new a case the recorded closure already covered; its reviewer
found it.  So the finisher refuses an entry whose Record comparison paragraph does not name, by identifier, each
claim registered before the entry's own whose summary resembles a declared claim's at least AT, among the COUNT
nearest.  Naming is checked, not the comparison's content, which the reviewer reads.  A claim counts as named when
a named claim refines, supersedes or corrects it, or when a registry edge stating generality (GENERALITY, not a
bare "cites") joins it to a declared claim; and a research entry that declares claims must have the paragraph,
so that leaving it out does not skip the check (both from its reviewer, 17 October 2026).  Replayed on the 24 past
research entries with claims and a Record comparison paragraph, each against the claims registered before it
(research/results/exposed_degree_occupancy_20261017/coverage-replay.txt): at AT = 0.3 it would refuse 9 with 28
unnamed claims, at 0.4 3 with 5; 0.4 would miss the exposing case, whose score was 0.37 (coverage-exposing-case.txt
there: refused at 0.3 on cor:star-closure-ratio, the corrected draft passes).  Of the 28 one was judged, a real
omission (thm:conjunction-quotient-rank, which defines the count the pin transfer entry studies and which that entry
cites three times, but not in its comparison); the other 27 were not judged.  One finisher-path run on the corrected
draft took 0.37 s (coverage-timing.txt there).  An entry declaring data-claims="none" is not checked here; the
claim inventory check refuses one whose registered claims do not match its declaration.

Usage: resemblance_coverage.py --replay NOTEBOOK [--limit N]   (counts what the check would refuse in the last
N research entries that declare claims, each compared only with the claims registered before it).
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from claim_authoring import similar_claims
from claim_reads import CLAIM_ID
import notebook_math

COUNT = 5
AT = 0.3          # chosen by the replay printed in research/results/exposed_degree_occupancy_20261017/coverage-replay.txt

GENERALITY = ('refines', 'supersedes', 'corrects', 'rediscovers')
PARAGRAPH = re.compile(r'<p\b[^>]*>\s*<strong>Record comparison\.</strong>([\s\S]*?)</p>')


def comparison_ids(article):
    """The claim identifiers named in the article's Record comparison paragraphs."""
    named = set()
    for match in PARAGRAPH.finditer(article):
        named.update(CLAIM_ID.findall(notebook_math.strip_tags(match.group(1))))
    return named


def declared(article):
    match = re.search(r'<article\b[^>]*\bdata-claims="([^"]*)"', article)
    return [] if not match or match.group(1).strip() == 'none' else match.group(1).split()


def nearest(claims, own, count=COUNT, at=AT):
    """{own id: [(score, id), ...]} over the claims registered before the first of `own`, scores >= at."""
    order = {claim['id']: index for index, claim in enumerate(claims)}
    first = min((order[ident] for ident in own if ident in order), default=len(claims))
    earlier = [claim for claim in claims[:first] if claim['id'] not in own]
    summaries = {claim['id']: claim.get('summary', '') for claim in claims}
    return {ident: [(score, other) for score, other in similar_claims(earlier, summaries.get(ident, ''), count)
                    if score >= at]
            for ident in own if ident in summaries}


def covered(named, relationships):
    """The named claims and the earlier versions they refine, supersede or correct: naming the newer version of a
    listed claim compares with it (the coset ratio reduction of 16 October 2026 named lem:high-incidence-occupancy,
    which refines the listed lem:off-support-occupancy)."""
    older = {}
    for edge in relationships:
        if edge.get('type') in ('refines', 'supersedes', 'corrects'):
            older.setdefault(edge['source']['id'], set()).add(edge['target']['id'])
    out, todo = set(named), list(named)
    while todo:
        for target in older.get(todo.pop(), ()):
            if target not in out:
                out.add(target)
                todo.append(target)
    return out


def missing(article, claims, count=COUNT, at=AT, relationships=()):
    """[(own id, score, nearest id), ...] that the Record comparison does not name."""
    own = declared(article)
    if not own:
        return []
    named = covered(comparison_ids(article), relationships)
    # A registry edge that states generality between a declared claim and the listed one is the spec's verdict on
    # it; a "cites" edge is not, since one spec line would then pass without the comparison (its reviewer, 17
    # October 2026).
    for edge in relationships:
        ends = (edge['source']['id'], edge['target']['id'])
        if edge.get('type') in GENERALITY and (ends[0] in own or ends[1] in own):
            named.update(ends)
    return [(ident, score, other) for ident, found in nearest(claims, own, count, at).items()
            for score, other in found if other not in named]


def validate(article, root=ROOT):
    if declared(article) and 'data-kind="research"' in article[:article.find('>') + 1] and not PARAGRAPH.search(article):
        raise ValueError('A research entry that declares claims needs a <p><strong>Record comparison.</strong> paragraph, '
                         'written from the record\'s side (AGENTS.md, order of work); without it this check would '
                         'not run (its reviewer, 17 October 2026).')
    path = Path(root) / 'research/claims/index.json'
    if not path.exists():   # a checkout with no registry (the finisher's test fixtures) has nothing to compare with
        return
    registry = json.loads(path.read_text())
    gaps = missing(article, registry['claims'], relationships=registry['relationships'])
    if gaps:
        raise ValueError('The Record comparison does not name registered claims that resemble a declared claim (the '
                         'claim_resemblance listing): ' + '; '.join(f'{other} ({score:.2f}, beside {ident})'
                                                                  for ident, score, other in gaps)
                         + '. Read each and say there whether it is more general, a special case or neither '
                         '(AGENTS.md, record comparison).')


def replay(notebook, limit, root=ROOT):
    registry = json.loads((Path(root) / 'research/claims/index.json').read_text())
    claims = registry['claims']
    text = Path(notebook).read_text()
    articles = re.findall(r'<article\b[\s\S]*?</article>', text)
    chosen = [a for a in articles if 'data-kind="research"' in a and declared(a)][-limit:]
    without = [a for a in chosen if not PARAGRAPH.search(a)]
    print(f'{len(without)} of {len(chosen)} entries have no Record comparison paragraph (the rule is of 17 October '
          f'2026); they are left out')
    chosen = [a for a in chosen if PARAGRAPH.search(a)]
    start = time.time()
    for at in (0.2, 0.3, 0.4):
        refused = [(re.search(r'id="([^"]+)"', a).group(1), missing(a, claims, at=at, relationships=registry['relationships'])) for a in chosen]
        refused = [(ident, gaps) for ident, gaps in refused if gaps]
        print(f'threshold {at}: {len(refused)} of {len(chosen)} research entries with claims would be refused, '
              f'{sum(len(g) for _, g in refused)} unnamed claims')
        if at == AT:
            for ident, gaps in refused:
                print('  ' + ident + ': ' + ', '.join(f'{o} {s:.2f}' for _, s, o in gaps))
    print(f'{len(claims)} registered claims, {len(chosen)} entries, {time.time() - start:.1f} s')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--replay', required=True)
    parser.add_argument('--limit', type=int, default=60)
    args = parser.parse_args(argv)
    replay(args.replay, args.limit)


if __name__ == '__main__':
    main()
