#!/usr/bin/env python3
"""Append a drafted research-record entry and optionally replace the Proposed next step.

The entry file holds one <article> element. It is inserted after the last article of the
selected notebook's research record. With --next FILE, the body of the proposed-next-step
section is replaced by the file's HTML (the section heading is kept). Fails closed if the entry's
anchor already exists, the record or section is missing, or the entry fails the existing
route/review reporting checks. Claim evidence remains a finalization check after registration.

It also refuses, before anything is written:
- an entry or a next step with a dollar sign, which MathJax reads as a math delimiter, or with an HTML
  character reference that lost its ampersand (tools/char_refs.py);
- a next step that parks the goal (a wait for a date, a feed or the user) while the notebook's Open
  statements section still lists a statement; an entry of a kind the branch's own module names
  (tools/branch_extension.py) is not checked;
- an entry while the notebook's Where we stand is the same as in the last commit, since every cycle
  reviews that section. --stand-unchanged REASON lets it through, and the entry then holds the reason
  in a paragraph labelled Where we stand, which tools/stand_reasons.py counts.
After these, a branch's own tools/append_checks.py, where it has one, is asked: its
check(source, entry, next_html) raises ValueError to refuse.
"""
# Copyright (c) 2026 Kamil Braun. SPDX-License-Identifier: MIT

import argparse
import functools
import html
import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import branch_extension
from char_refs import broken_entities
from notebooks import selected, ROOT

HEADING = '<h2>Proposed next step</h2>'
# While the goal is open the next step is always research (AGENTS.md): wording that parks it on a
# date, a feed or the user's approval is refused. A step may name other work that waits, as long as
# it is not itself a wait.
PARKING = re.compile(r'\b(cycles?|the spin|the goal|research|work)\s+(waits?|pauses?|stops?)\b'
                     r'|\bwaits?\s+(on|for)\s+your\s+(approvals?|answers?|decisions?)\b'
                     r'|\b(pause|park)(s|d|ed|ing)?\s+(the\s+)?(goal|spin|loop|research|cycles?)\b', re.I)
STAND_LABEL = '<p><strong>Where we stand.</strong> Unchanged: '


def section(source, name):
    """The section `name` of the notebook, or None when it has none."""
    start = source.find(f'<section id="{name}"')
    return None if start < 0 else source[start:source.index('</section>', start)]


def goal_open(source):
    """Whether the notebook still lists a statement needed for its goal: an Open statements section
    with a list item. A notebook without the section, such as one that records tasks, has no goal
    this tool can read as open."""
    return '<li' in (section(source, 'open-statements') or '')


def refuse_broken_text(what, text):
    if '$' in text:
        # The finisher refuses this too, but only after the entry is in the notebook.
        raise ValueError(f'{what} contains a dollar sign, which MathJax reads as a math delimiter; write '
                         'mathematics with \\( \\) and currency as "USD 5"')
    broken = broken_entities(text)
    if broken:
        raise ValueError(f'{what} has character references without their & ({", ".join(sorted(set(broken)))}), '
                         'the mark of a sed replacement; edit notebook text with an exact replacement')


def with_stand_reason(source, entry, committed, reason):
    """`entry`, checked against the rule that every cycle reviews Where we stand: refused while the
    section is as `committed` has it and no reason is given; with a reason, the entry gains the
    paragraph that records it. A changed section, a notebook without one or one not yet committed
    leaves the entry as it is."""
    stand = section(source, 'where-we-stand')
    if committed is None or stand is None or stand != section(committed, 'where-we-stand'):
        return entry
    if not reason or not reason.strip():
        raise ValueError('Where we stand is unchanged since the last commit. Update it for this cycle '
                         '(AGENTS.md: after every research turn), or pass --stand-unchanged REASON '
                         'saying why nothing in it changed')
    paragraph = f'{STAND_LABEL}{html.escape(reason.strip(), quote=False)}</p>'
    meta = re.search(r'<p class="entry-meta">.*?</p>', entry, re.S)
    at = meta.end() if meta else entry.rindex('</article>')
    return entry[:at] + '\n' + paragraph + ('\n' if not meta else '') + entry[at:]


def branch_checks(tools=None):
    """The branch's own check(source, entry, next_html), or None where it has no tools/append_checks.py."""
    path = (tools or Path(__file__).parent) / 'append_checks.py'
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location('append_checks', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.check


@functools.cache
def reporting_checks():
    """Reuse the finalizer's rules, without running its checkpoint operations."""
    spec = importlib.util.spec_from_file_location('append_reporting',
                                                Path(__file__).with_name('finish-turn.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def preflight(source, ident):
    if 'data-route-item="' not in source:
        return
    article = re.search(r'<article\b[^>]*\sid="' + re.escape(ident) + '"', source).start()
    close = source.index('</article>', article)
    checks = reporting_checks()
    checks.validate_route(source, article)
    checks.validate_convergence(source, article, close)
    checks.validate_progress(source, article, close, check_registered_claims=False)


def append(source, entry, next_html=None, committed=None, reason=None, tools=None):
    """The notebook `source` with `entry` appended and, with `next_html`, its next step replaced.
    `committed` is the notebook as of the last commit, for the Where we stand rule, and `reason`
    what --stand-unchanged gave."""
    entry = entry.strip()
    m = re.match(r'<article\b[^>]*?\sid="([^"]+)"', entry)
    if not m or not entry.endswith('</article>'):
        raise ValueError('entry must be one <article id="..."> ... </article> element')
    refuse_broken_text('entry', entry)
    if next_html is not None:
        refuse_broken_text('next step', next_html)
        parked = PARKING.search(re.sub(r'<[^>]+>', ' ', next_html))
        # A branch's own module may name kinds of entry whose next step may wait.
        may_wait = '|'.join(map(re.escape, branch_extension.ask('PARKING_KINDS', (), tools)))
        waiting_kind = may_wait and re.match(rf'<article\b[^>]*\bdata-kind="(?:{may_wait})"', entry)
        if parked and goal_open(source) and not waiting_kind:
            raise ValueError(f'the next step parks the goal ("{parked.group(0)}"); while the goal is open '
                             'the next step is research: open a new line or test a new idea (AGENTS.md)')
    entry = with_stand_reason(source, entry, committed, reason)
    own = branch_checks(tools)
    if own:
        own(source, entry, next_html)
    if f'id="{m.group(1)}"' in source:
        raise ValueError(f'anchor already present: {m.group(1)}')
    start = source.find('<section id="research-record">')
    if start < 0:
        raise ValueError('research-record section missing')
    close = source.find('</section>', start)
    last = source.rfind('</article>', start, close)
    at = last + len('</article>') if last >= 0 else close
    source = source[:at] + '\n' + entry + source[at:]
    if next_html is not None:
        a = source.find('<section id="proposed-next-step">')
        if a < 0:
            raise ValueError('proposed-next-step section missing')
        b = source.index('</section>', a)
        body = source[a:b]
        if HEADING not in body:
            raise ValueError('proposed-next-step heading missing')
        head = body[:body.index(HEADING) + len(HEADING)]
        source = source[:a] + head + '\n' + next_html.strip() + '\n' + source[b:]
    preflight(source, m.group(1))
    return source


def committed_version(path):
    """The notebook as of HEAD, or None outside a repository or for a notebook not yet committed."""
    try:
        rel = Path(path).resolve().relative_to(Path(ROOT).resolve())
    except ValueError:
        return None
    shown = subprocess.run(['git', '-C', str(ROOT), 'show', f'HEAD:{rel.as_posix()}'], capture_output=True, text=True)
    return shown.stdout if shown.returncode == 0 else None


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('entry', type=Path)
    parser.add_argument('--next', type=Path, dest='next_file')
    parser.add_argument('--notebook')
    parser.add_argument('--stand-unchanged', metavar='REASON',
                        help='why Where we stand needs no change in this cycle; recorded in the entry')
    args = parser.parse_args()
    path = Path(ROOT) / selected(args.notebook)['source']
    nxt = args.next_file.read_text() if args.next_file else None
    try:
        path.write_text(append(path.read_text(), args.entry.read_text(), nxt, committed_version(path),
                               args.stand_unchanged))
    except ValueError as err:
        sys.exit(f'notebook-append.py: {err}')
    print(f'Appended to {path.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
