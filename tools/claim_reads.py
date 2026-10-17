#!/usr/bin/env python3
"""The claims whose full registered statement a session read, and the entry paragraphs that may name only those.

tools/notebook-excerpt.py --claims and tools/search-claims.py --show append the claims they print to the
ignored log research/logs/claim-reads.jsonl.  A search listing prints a shortened summary, not the statement:
on 17 October 2026 an entry's Record search named thm:finite-algebra-evaluation, which its search had
returned, as giving no binary descent, while the statement, unread, refuted the descent the entry left open.
So the finisher refuses a Record search or Record comparison paragraph that names a registered claim whose
statement no reading tool printed in the session.  It cannot tell whether a printed statement was read, nor
catch a claim named in words instead of by its identifier or in a paragraph outside PARAGRAPHS; reads logged
by another session in the same time window count, as the log has no session field.
"""
import json
import re
import time
from pathlib import Path

import notebook_math

LOG ='research/logs/claim-reads.jsonl'

# Registry identifier prefixes (claim-index.py list, 17 October 2026), longest first so that no prefix
# matches inside another.
PREFIXES = ('third-party', 'criterion', 'audit', 'check', 'draft', 'local', 'proof', 'conj', 'note', 'open', 'prop',
            'thm', 'lem', 'cor', 'obs', 'imp', 'def', 'ctx', 'rem', 'ex', 'q')
CLAIM_ID = re.compile(r'(?<![\w:-])((?:' + '|'.join(re.escape(p) for p in PREFIXES)
                      + r'):[A-Za-z0-9][A-Za-z0-9-]*[A-Za-z0-9])')   # IDs may hold capitals (CNF, IPS, PHP)

# The paragraphs whose verdicts on other claims must rest on their statements: the record searches, the
# comparison, the suggestions' Record lines, and the two that apply recorded results to the next attempt and to
# the goal (a reviewer showed on 17 October 2026 that the same dismissal passed in Own statements).
PARAGRAPHS = ('Record search', 'Record comparison', 'Record', 'Own statements', 'Bearing')


def log(root, ids):
    """Append `ids` to the read log; a log that cannot be written is not an error."""
    ids = sorted(set(ids))
    if not ids:
        return
    try:
        path = Path(root) / LOG
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a') as handle:
            handle.write(json.dumps({'unix_s': time.time(), 'claims': ids}) + '\n')
    except OSError:
        pass


def read_since(root, since):
    """The claims a reading tool printed at or after `since` (unix seconds)."""
    path = Path(root) / LOG
    read = set()
    for line in path.read_text().splitlines() if path.exists() else ():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get('unix_s', 0) >= since:
            read.update(row.get('claims', []))
    return read


def named(entry):
    """The claim identifiers each paragraph of PARAGRAPHS in `entry` names, in order."""
    found = []
    for label in PARAGRAPHS:
        for match in re.finditer(r'<strong>' + label + r'\.</strong>(.*?)(?=<strong>[A-Z][^<]*\.</strong>|</p>)',
                                 entry, re.S):
            text = notebook_math.strip_tags(match.group(1))
            found.extend(m.group(1) for m in CLAIM_ID.finditer(text))
    return list(dict.fromkeys(found))


def unread(entry, read, own=()):
    """The claims the entry's Record paragraphs name that are neither read nor declared by the entry itself."""
    return [ident for ident in named(entry) if ident not in read and ident not in set(own)]
