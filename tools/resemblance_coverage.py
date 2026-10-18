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
there: refused at 0.3 on cor:star-closure-ratio, the corrected draft passes).  All 28 were judged from their
summaries beside the entries' own claims (coverage-judgement.txt there, a judgement): 20 real omissions, 6 of them
claims the entry names elsewhere but not in its comparison, and 8 false refusals, all from setting words shared
across one theorem family (the majority transfers) without a shared statement.  One finisher-path run on the corrected
draft took 0.37 s (coverage-timing.txt there).  An entry declaring data-claims="none" is not checked here; the
claim inventory check refuses one whose registered claims do not match its declaration.

For a declared claim registered with a proof, the same listing at WITNESS_AT, over claims proved for some inputs,
must also be named in a Nonvacuity, Plainest bound or Baseline passage (witness_missing; 18 October 2026, a
witness twice offered that a resembling registered bound decided): replayed on the ultimate-matching notebook's 68
research entries with claims, it would refuse 29 with 76 unnamed claims at 0.35, and 0.4 would miss the exposing
case at 0.37, so the threshold is fitted to that case (research/provenance/framework/witness-coverage-replay-
20261018.txt).  Only the first ten refusals were judged, from the claims' summaries, nine related and one not
(witness-coverage-judgement-20261018.txt there, a judgement): the false-refusal rate is unknown.  Naming is
checked, not what the passage says of the claim, so a sentence that names it without evaluating it on the witness
passes (queued as witness-claim-evaluated).

Usage: resemblance_coverage.py --replay NOTEBOOK [--limit N]
       resemblance_coverage.py --draft DRAFT --spec SPEC   (the witness check before the spec is registered)   (counts what the check would refuse in the last
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


WITNESS_AT = 0.35   # the replay printed in research/provenance/framework/witness-coverage-replay-20261018.txt
PROVED = ('working_proof', 'conditional')
DECIDING = PROVED + ('established',)
WITNESS = re.compile(r'<strong>(?:Nonvacuity|Plainest bound|Baseline)\.</strong>([\s\S]*?)(?=<strong>(?!Plainest '
                     r'bound\.|Baseline\.|Composed\.)[A-Z][^<]{0,40}\.</strong>|</p>)')


def witness_missing(article, claims, count=COUNT, at=WITNESS_AT, relationships=()):
    """[(own id, score, nearest id), ...]: for each declared claim registered with a proof or a conditional proof,
    the earlier registered claims resembling it at least `at` that no Nonvacuity, Plainest bound or Baseline
    passage names.  On 18 October 2026 a witness was offered twice that a resembling registered bound decided,
    the second time lem:cost-weighted-slope-bound at 0.38, which those passages never named; the Record
    comparison may name a claim without anyone asking what it gives on the witness."""
    status = {claim['id']: claim.get('mathematical_status') for claim in claims}
    own = [ident for ident in declared(article) if status.get(ident) in PROVED]
    if not own:
        return []
    # Only a statement proved for some inputs can already decide a witness: a conjecture, a context note or a
    # retracted claim cannot, and the replay's first run listed conjectures among its refusals.
    claims = [claim for claim in claims if claim['id'] in declared(article) or status[claim['id']] in DECIDING]
    named = set()
    for passage in WITNESS.findall(article):
        named.update(CLAIM_ID.findall(notebook_math.strip_tags(passage)))
    named = covered(named, relationships)
    return [(ident, score, other) for ident, found in nearest(claims, declared(article), count, at).items()
            if ident in own for score, other in found if other not in named]


APPLIED = re.compile(r'<strong>(?:Plainest bound|Baseline|Nonvacuity|Own statements|Record comparison)\.</strong>'
                     r'([\s\S]*?)(?=<strong>[A-Z][^<]{0,40}\.</strong>|</p>|</li>)')


def class_missing(article, claims, table, marker):
    """[(own id, class, listed id), ...]: for each declared claim, the claims tools/claim_resemblance.py lists for
    its object's recorded class (the notebook's claim-classes.json), against the claims registered before the
    entry's own, that no Plainest bound, Baseline, Nonvacuity, Own statements or Record comparison passage names.
    18 October 2026: a ramp lemma's summary cited lem:cellwise-lipschitz-split, and the bound was still not applied
    to the ramp; a listing alone is a reading list, so the entry names each listed bound where it applies it, or
    says there why it does not apply (its reviewer, same day).  Naming is checked, not the application: the exposing
    entry named lem:cellwise-lipschitz-split without applying it, which this check does not catch.  Replayed on the
    ultimate-matching notebook it would refuse 10 of 72 research entries with claims, 6 judged real omissions and 4
    false (dualities and reductions, whose answer costs a sentence; research/provenance/framework/
    class-tool-search-judgement-20261018.txt)."""
    import claim_resemblance
    own = declared(article)
    if not own or not table or not marker:
        return []
    order = {claim['id']: index for index, claim in enumerate(claims)}
    first = min((order[ident] for ident in own if ident in order), default=len(claims))
    earlier = claims[:first]
    summaries = {claim['id']: claim.get('summary', '') for claim in claims}
    named = set()
    for passage in APPLIED.findall(article):
        named.update(CLAIM_ID.findall(notebook_math.strip_tags(passage)))
    return [(ident, name, other) for ident in own if ident in summaries
            for name, rows, _ in claim_resemblance.class_listing(earlier, summaries[ident], table, marker, own)
            for other, _ in rows if other not in named]


def validate(article, root=ROOT, notebook=None):
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
    gaps = witness_missing(article, registry['claims'], relationships=registry['relationships'])
    if gaps:
        raise ValueError('No Nonvacuity, Plainest bound or Baseline passage names registered claims that resemble a '
                         'proved declared claim: ' + '; '.join(f'{other} ({score:.2f}, beside {ident})'
                                                             for ident, score, other in gaps)
                         + '. Say there what each gives on the witness, or why it does not apply to it (AGENTS.md, '
                         'Nonvacuity: the witness must be one the recorded statements do not already cover).')
    if notebook is not None:
        import claim_resemblance
        gaps = class_missing(article, registry['claims'], claim_resemblance.class_table(notebook),
                             claim_resemblance.notebook_marker(notebook))
        if gaps:
            raise ValueError('No Plainest bound, Baseline, Nonvacuity, Own statements or Record comparison passage '
                             'names proved claims listed for a declared claim\'s recorded class (claim_resemblance, '
                             'the notebook\'s claim-classes.json): ' + '; '.join(f'{other} ({name}, beside {ident})'
                                                                                 for ident, name, other in gaps)
                             + '. Apply each to the object there, or say why it does not apply (AGENTS.md: a '
                             'search in the words of the smallest recorded class containing the object).')


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
            # An unnamed claim the entry cites elsewhere was in use there and left out of the comparison; one it
            # never cites needs reading to tell a miss from a false refusal.
            body = {re.search(r'id="([^"]+)"', a).group(1): set(CLAIM_ID.findall(notebook_math.strip_tags(a)))
                    for a in chosen}
            for ident, gaps in refused:
                print('  ' + ident + ': ' + ', '.join(f'{o} {s:.2f} ({"cited elsewhere" if o in body[ident] else "not cited"})'
                                                      for _, s, o in gaps))
            flat = [o in body[ident] for ident, gaps in refused for _, _, o in gaps]
            print(f'  of the {len(flat)} unnamed claims, {sum(flat)} are cited elsewhere in their entry and '
                  f'{len(flat) - sum(flat)} are not cited there')
    print(f'{len(claims)} registered claims, {len(chosen)} entries, {time.time() - start:.1f} s')
    proved = [a for a in articles if 'data-kind="research"' in a and declared(a)][-limit:]
    for at in (0.3, 0.35, 0.4):
        refused = [(re.search(r'id="([^"]+)"', a).group(1),
                    witness_missing(a, claims, at=at, relationships=registry['relationships'])) for a in proved]
        refused = [(ident, gaps) for ident, gaps in refused if gaps]
        print(f'witness passages, threshold {at}: {len(refused)} of {len(proved)} research entries with claims '
              f'would be refused, {sum(len(g) for _, g in refused)} unnamed claims')
        if at == WITNESS_AT:
            for ident, gaps in refused:
                print('  ' + ident + ': ' + ', '.join(f'{o} {s:.2f} beside {i}' for i, s, o in gaps))
    import claim_resemblance
    table, marker = claim_resemblance.class_table(notebook), claim_resemblance.notebook_marker(notebook)
    if table and marker:
        refused = [(re.search(r'id="([^"]+)"', a).group(1), class_missing(a, claims, table, marker)) for a in proved]
        refused = [(ident, gaps) for ident, gaps in refused if gaps]
        print(f'class listings (claim-classes.json): {len(refused)} of {len(proved)} research entries with claims '
              f'would be refused, {sum(len(g) for _, g in refused)} unnamed claims')
        for ident, gaps in refused:
            print('  ' + ident + ': ' + '; '.join(f'{o} ({n}, beside {i})' for i, n, o in gaps))
    else:
        print('class listings: the notebook declares no claim-classes.json, or is the main notebook')


def draft_check(draft, spec):
    """The witness check on a draft whose claims are not yet registered: its spec's claims are appended to the
    registry, after every registered claim, with their spec status."""
    registry = json.loads((ROOT / 'research/claims/index.json').read_text())
    known = {claim['id'] for claim in registry['claims']}
    claims = registry['claims'] + [{'id': c['id'], 'summary': c['summary'], 'mathematical_status': c.get('status')}
                                   for c in json.loads(Path(spec).read_text())['claims'] if c['id'] not in known]
    return witness_missing(Path(draft).read_text(), claims, relationships=registry['relationships'])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--replay')
    parser.add_argument('--limit', type=int, default=60)
    parser.add_argument('--draft', help='with --spec: run the witness check on a draft before registration')
    parser.add_argument('--spec')
    args = parser.parse_args(argv)
    if args.draft:
        gaps = draft_check(args.draft, args.spec)
        for ident, score, other in gaps:
            print(f'unnamed in the witness passages: {other} ({score:.2f}, beside {ident})')
        print(f'{len(gaps)} unnamed')
        return 1 if gaps else 0
    replay(args.replay, args.limit)


if __name__ == '__main__':
    sys.exit(main())
