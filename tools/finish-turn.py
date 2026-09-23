#!/usr/bin/env python3
"""Export timing, archive evidence, and fill one notebook timing placeholder."""
import argparse
import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from claim_registry import load as load_claims, render as render_claims
from claim_maintenance import check_revision
from notebook_context import check as check_context
from claim_attention import sync as sync_attention, brief as attention_brief

ROOT = Path(__file__).resolve().parents[1]


def session_name(value):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', value) or value in ('.', '..'):
        raise argparse.ArgumentTypeError('Use a simple session name, not a path')
    return value


REVIEW_PERIOD = 6    # research entries allowed in a row before a route review is required
STATUS_LIMIT = 300   # characters of status-line text, before the producer credit
KINDS = ('research', 'review', 'formalization')


def entry_tags(body, article):
    tag = body[article:body.index('>', article) + 1]
    found = {key: re.search(rf'data-{key}="([^"]*)"', tag) for key in ('kind', 'route')}
    return {key: match.group(1) if match else None for key, match in found.items()}


def validate_route(body, article):
    """Enforce AGENTS.md's periodic route review; active once the notebook declares route items."""
    items = set(re.findall(r'data-route-item="([^"]+)"', body))
    if not items:
        return
    tags = entry_tags(body, article)
    if tags['kind'] not in KINDS:
        raise ValueError('Tag the entry: <article ... data-kind="research|review|formalization" '
                         'data-route="ITEM">, ITEM a data-route-item of The remaining route or side-...')
    if tags['kind'] == 'formalization':
        return
    if tags['route'] not in items and not (tags['route'] or '').startswith('side-'):
        raise ValueError(f'data-route must be one of {sorted(items)} or start with side-; '
                         'name the top-level route item, not a sub-gap of the current line')
    if tags['kind'] == 'review':
        return
    record = body.find('<section id="research-record">')
    earlier = [m.start() for m in re.finditer(r'<article\b', body[:article]) if m.start() > record]
    streak = 0
    for position in reversed(earlier):
        kind = entry_tags(body, position)['kind']
        if kind == 'formalization':
            continue
        if kind != 'research':   # a review, or an entry from before the tags existed
            break
        streak += 1
    if streak >= REVIEW_PERIOD:
        raise ValueError(f'The last {streak} research entries have no route review. This entry must be '
                         'a route review (data-kind="review"): the general claim of the current line, '
                         'what the main goal needs from it, a falsification attempt, an estimate that '
                         'the line advances the goal, and the next step on the highest-risk route item')


GENERAL_RE = re.compile(r'<p><strong>General statement\.</strong>(.*?)</p>', re.S)
PROOF_WORDS = ('proof', 'refutation', 'counterexample', 'conditional result')


GENERAL_ID = re.compile(r'\b(?:conj|lem|thm|prop|cor):[A-Za-z0-9-]+')


def cases_only(body, article):
    """An entry that reports only cases: every registered claim is a finite check (ex:) and the
    status line names no proof, refutation, counterexample or conditional result."""
    tag = body[article:body.index('>', article) + 1]
    claims = (re.search(r'data-claims="([^"]*)"', tag) or [None, ''])[1].split()
    status = entry_status(body, article).lower()
    claims = [c for c in claims if c != 'none']
    reports_cases = 'finite check' in status or any(c.startswith('ex:') for c in claims)
    return (reports_cases and all(c.startswith('ex:') for c in claims)
            and not any(word in status for word in PROOF_WORDS))


def entry_status(body, article):
    meta = body.find('<p class="entry-meta">', article)
    return re.sub(r'<[^>]*>', '', body[meta:body.find('</p>', meta)]).split('Produced by')[0]


def validate_general(body, article, close):
    """AGENTS.md: restricted examples must test a named general statement; enforce it mechanically.
    Every research entry states its general claim for all parameters, and two finite-check entries
    in a row on one route (neither with a proof or refutation) are rejected."""
    if not re.search(r'data-route-item="', body):     # active once the notebook declares route items
        return
    tags = entry_tags(body, article)
    if tags['kind'] != 'research':
        return
    found = GENERAL_RE.search(body, article, close)
    text = re.sub(r'<[^>]*>', ' ', found.group(1)).strip() if found else ''
    if len(text) < 40:
        raise ValueError('A research entry needs a <p><strong>General statement.</strong> ...</p> '
                         'paragraph: the claim this cycle tests or proves, for all parameters, with '
                         'its conjectured bound as a formula (AGENTS.md, restricted examples)')
    ids = GENERAL_ID.findall(found.group(1))
    registry = ROOT / 'research/claims/index.json'
    if registry.exists():
        registered = {c['id'] for c in load_claims(registry)['claims']}
        ids = [i for i in ids if i in registered]
    if not ids:
        raise ValueError('The General statement must cite the registered claim ID (conj:, lem:, thm:, '
                         'prop: or cor:) that states it for all parameters; register a conjecture if '
                         'it is not proved')
    if not cases_only(body, article):
        return
    record = body.find('<section id="research-record">')
    earlier = [m.start() for m in re.finditer(r'<article\b', body[:article]) if m.start() > record]
    for position in reversed(earlier):
        previous = entry_tags(body, position)
        if previous['kind'] == 'formalization' or previous['route'] != tags['route']:
            continue
        if previous['kind'] == 'research' and cases_only(body, position):
            raise ValueError('The previous research entry on this route was also a finite check '
                             'without a proof or refutation. Stop adding cases: this entry must '
                             'attempt a proof or a refutation of its General statement (AGENTS.md)')
        break


# External labels kept by the odd-prime name map (entry-2026-09-22-result-names); every other
# "Lemma K"-style code must be replaced by a descriptive name.
KEPT_LABELS = {'Corollary SL', 'Conjecture SR', 'Remark A.4'}
LABEL_NOUNS = 'Lemma|Theorem|Corollary|Conjecture|Proposition|Observation|Question|Remark|Criterion'


def letter_code_labels(html_text):
    """Letter-code result labels ("Lemma K", "Theorem NDX′", "Conjecture H1") in an entry's prose."""
    text = re.sub(r'<table\b.*?</table>', ' ', html_text, flags=re.S)   # name maps live in tables
    text = re.sub(r'<[^>]*>', ' ', text)
    found = []
    for m in re.finditer(r'\b(' + LABEL_NOUNS + r')\s+([A-Z][A-Za-z0-9.]*[′″]*)', text):
        code = m.group(2).rstrip('.')
        if re.fullmatch(r'[A-Z][a-z]{2,}', code):          # an ordinary capitalized word
            continue
        label = f'{m.group(1)} {code}'
        if label not in KEPT_LABELS and label not in found:
            found.append(label)
    return found


def validate_marker(body, marker):
    if body.count(marker) != 1:
        raise ValueError(f'Notebook must contain exactly one {marker}')
    position = body.index(marker)
    record = body.find('<section id="research-record">')
    end = body.find('</section>', record) if record >= 0 else -1
    article = body.rfind('<article', record, position) if record >= 0 else -1
    close = body.find('</article>', article) if article >= 0 else -1
    if not (0 <= record < article < position < close < end):
        raise ValueError('Timing marker must be inside a Research-record article')
    meta = body.find('<p class="entry-meta">', article, position)
    if meta < 0 or body.find('</p>', meta, position) < 0:
        raise ValueError('The entry needs a <p class="entry-meta"> status line before its timing marker')
    status = re.sub(r'<[^>]*>', '', body[meta:body.find('</p>', meta)]).split('Produced by')[0]
    if len(status.strip()) > STATUS_LIMIT:
        raise ValueError(f'The status line has {len(status.strip())} characters; keep it under '
                         f'{STATUS_LIMIT}: the status and one clause of scope, details in the entry')
    validate_route(body, article)
    validate_general(body, article, close)
    if '$' in body[article:close]:
        # MathJax treats a dollar sign as an inline-math delimiter; the notebook uses \( \).
        raise ValueError('The entry contains a dollar sign, which MathJax reads as a math delimiter; '
                         'write mathematics with \\( \\) and currency as "USD 5"')
    coded = letter_code_labels(body[article:close])
    if coded:
        raise ValueError('The entry names results by letter codes ' + ', '.join(coded) + ': cite them '
                         'by descriptive names (CLAUDE.md, Naming results), e.g. "the constant-row clamp" '
                         'rather than "Lemma K"; the claim ID usually gives the name')
    control = sorted({c for c in body[article:close] if ord(c) < 32 and c != '\n'})
    if control:
        # "\rho", "\text", "\bigl" written through a non-raw Python string become CR, TAB, BS.
        raise ValueError('The entry contains control characters ' + repr(control) + ': a TeX command '
                         'was written through a non-raw string (\\r, \\t, \\b, \\f); repair the formulas')


def credit_producer(body, marker, producer):
    """Name the recorded agent and model at the end of the entry's status line."""
    article = body.rfind('<article', 0, body.index(marker))
    meta = body.index('<p class="entry-meta">', article)
    close = body.index('</p>', meta)
    if producer in body[meta:close]:
        return body
    return (body[:close] + ' <span data-generated="finish-turn-producer-v1">'
            + producer + '</span>' + body[close:])


def validate_append_only(root):
    """Earlier entries must match HEAD; corrections belong in a new dated entry."""
    checker = root / 'tools/check-append-only.py'
    if not checker.exists():
        return
    result = subprocess.run([sys.executable, str(checker), '--base', 'HEAD'], cwd=root,
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(result.stdout.strip())


def finish(root, turn, next_turn=None, notebook_name=None):
    from notebooks import selected, paths
    item = selected(notebook_name, root)
    notebook = root / item["source"]
    first = json.loads((root/'research/logs'/f'{turn}.jsonl').read_text().splitlines()[0])
    if first.get('notebook',item['name']) != item['name']:
        raise ValueError('Selected notebook differs from timing session notebook')
    marker = f'<!-- TIMING {turn} -->'
    owners = [p for p in paths(root) if marker in p.read_text()]
    if owners != [notebook]:
        raise ValueError("Timing marker must belong uniquely to selected notebook " + item["name"])
    validate_marker(notebook.read_text(), marker)
    check_context(root, item["name"])  # Fail before stopping timing, archiving, or changing the notebook.
    validate_append_only(root)
    if (root / 'research/claims/index.json').exists():
        claims = load_claims(root / 'research/claims/index.json')
        if (root / 'research/CLAIM_INDEX.md').read_text() != render_claims(claims):
            raise ValueError('Generated claim index is stale; run tools/claim-index.py render')
        contract = check_revision(claims, root=root)
        if not contract['passed']:
            raise ValueError('Changed-claim metadata incomplete:\n' + '\n'.join(contract['errors']))
    if next_turn and (root / 'research/logs' / f'{next_turn}.jsonl').exists():
        raise ValueError('Next session already exists; omit --next when retrying finalization')

    if (root / 'research/claims/index.json').exists():
        # The existing maintenance gate already requires reasoned significance
        # dispositions. Reuse that work; no second essay or automatic web audit.
        assessed = [r for r in contract['required_reviews'] if 'significance' in r['fields']]
        history, added = sync_attention(root, claims)
        print(f'Significance check: {len(assessed)} changed claim dispositions; '
              f'{len(added)} new/reopened attention items.')
        print(attention_brief(claims, history), end='')
        print('Stage attention history/view if changed: research/claims/attention.json research/ATTENTION.md')

    compute = str(root / 'compute.sh')
    fragment = root / 'research/results' / turn / 'timing.html'
    subprocess.run([compute, 'report', turn, '--stop', '--html-out', str(fragment)],
                   cwd=root, check=True, stdout=subprocess.PIPE, text=True)
    if next_turn:
        # Continuous research keeps the finished cycle's recorded agent and model.
        journal = root / 'research/logs' / f'{turn}.jsonl'
        first = json.loads(journal.read_text().splitlines()[0]) if journal.exists() else {}
        inherit = [f'--{key}={first[key]}' for key in ('agent', 'model') if first.get(key)]
        subprocess.run([compute, 'start', next_turn, *inherit, '--notebook', item['name']], cwd=root, check=True,
                       stdout=subprocess.PIPE, text=True)
        subprocess.run([compute, 'phase', next_turn, 'preparation', '--note',
                        f'Finalize checkpoint {turn}, then begin the next research cycle'],
                       cwd=root, check=True)

    # Archival may copy large outputs, so keep it inside the shared resource limits.
    archive = [compute]
    if next_turn:
        archive += ['--session', next_turn]
    archive += ['--threads', '1', '--category', 'local_processing',
                '--tail-bytes', '1000', sys.executable,
                str(root / 'tools/archive-session.py'), turn]
    subprocess.run(archive, cwd=root, check=True)

    # Re-read after commands so unrelated edits made meanwhile are retained.
    current = notebook.read_text()
    try:
        validate_marker(current, marker)
    except ValueError as error:
        raise ValueError(f'Timing and archive are saved, but {error}') from error
    first = json.loads((root / 'research/logs' / f'{turn}.jsonl').read_text().splitlines()[0])
    producer = (f"Produced by {html.escape(first.get('agent', 'unrecorded'))} "
                f"({html.escape(first.get('model', 'unrecorded'))}).")
    timing = fragment.read_text().strip()
    timing = timing.replace('<div class="timing-report"',
                            '<div data-generated="finish-turn-timing-v1" class="timing-report"', 1)
    updated = credit_producer(current, marker, producer).replace(marker, timing)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=root, prefix='.notebook-timing-',
                                         encoding='utf-8', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(updated)
        temporary.chmod(notebook.stat().st_mode & 0o777)
        os.replace(temporary, notebook)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(f'Finished {turn} in {item["name"]}: timing embedded and evidence archived; review and commit.')
    print(f'Stage with the entry: {item["source"]} '
          f'research/results/{turn}/timing.html research/provenance/session-records/{turn}')
    if next_turn:
        print(f'{next_turn} is running in preparation phase.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('turn', type=session_name)
    parser.add_argument('--next', dest='next_turn', type=session_name,
                        help='Start the next cycle immediately after the timing snapshot')
    parser.add_argument('--notebook', help='Research thread name; defaults to worktree selection or main')
    args = parser.parse_args()
    finish(ROOT, args.turn, args.next_turn, args.notebook)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'finish-turn.py: {error}', file=sys.stderr)
        sys.exit(1)
