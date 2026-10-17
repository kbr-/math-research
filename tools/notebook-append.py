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
  in a paragraph labelled Where we stand, which tools/stand_reasons.py counts;
- a next step that names no queued item, by identifier or by a link to an entry that developed one, while
  the notebook's queue is draining. For each item a next step names it prints the item's queued text and
  its latest follow-up, to write the description against;
- a next step that names a queued item by its identifier, when the item has a latest follow-up, without
  quoting eight consecutive words of that follow-up or of the item's queued text;
- a passage of eight or more words that such a next step puts in quotation marks and that is not in the
  latest follow-up or queued text of any item it names;
- a next-step section wrapper or retained heading, and an invalid living-section structure in the
  proposed notebook (the same parser used by the context-budget check).
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
from notebook_math import strip_tags
from notebooks import selected, ROOT
from notebook_context import excerpt, living_sections

HEADING = '<h2>Proposed next step</h2>'
# While the goal is open the next step is always research (AGENTS.md): wording that parks it on a
# date, a feed or the user's approval is refused. A step may name other work that waits, as long as
# it is not itself a wait.
PARKING = re.compile(r'\b(cycles?|the spin|the goal|research|work)\s+(waits?|pauses?|stops?)\b'
                     r'|\bwaits?\s+(on|for)\s+your\s+(approvals?|answers?|decisions?)\b'
                     r'|\b(pause|park)(s|d|ed|ing)?\s+(the\s+)?(goal|spin|loop|research|cycles?)\b', re.I)
STAND_LABEL = '<p><strong>Where we stand.</strong> Unchanged: '
STAND_WORDS = 6


def section(source, name):
    """The section `name` of the notebook, or None when it has none."""
    start = source.find(f'<section id="{name}"')
    return None if start < 0 else source[start:source.index('</section>', start)]


def goal_open(source):
    """Whether the notebook still lists a statement needed for its goal: an Open statements section
    with a list item. A notebook without the section, such as one that records tasks, has no goal
    this tool can read as open."""
    return '<li' in (section(source, 'open-statements') or '')


PLACEHOLDER = re.compile(r'\[written after\b', re.I)
REVIEW_CREDIT = re.compile(r'\breview(?:ed|er|s)?\b|\bpass(?:es)?\b', re.I)


def refuse_early_review_credit(entry):
    """A status line that credits a review while the entry still holds a '[written after ...]' placeholder was
    written before the review it credits (17 October 2026: "with a reviewed correction pass" stood in a draft whose
    Verification gate was still a placeholder). The record's 125 research status lines that mention a review were
    written after it, and none of their entries holds a placeholder."""
    meta = re.search(r'<p class="entry-meta">(.*?)</p>', entry, re.S)
    # A placeholder in the status line itself ("[status written after the review]") credits nothing.
    status = re.sub(r'\[[^\]]*written after[^\]]*\]', ' ', meta.group(1), flags=re.I) if meta else ''
    if REVIEW_CREDIT.search(status) and PLACEHOLDER.search(entry):
        raise ValueError('the status line credits a review while the entry still holds a "[written after ...]" '
                         'placeholder: write the status line after the review returns, from the reviewed body '
                         '(AGENTS.md: title and status line written after the review)')


MISSING_CONSTRUCTION = re.compile(r'\bno (?:recorded )?construction (?:has|does|gives|exists)\b'
                                  r'|\bthe record has no (?:such )?construction\b', re.I)
BUILDS_NEXT = re.compile(r'\b(?:build|builds|construct|constructs|constructed|built)\b', re.I)


def refuse_unbuilt_obstacle(entry):
    """A review whose Obstacle says the line is stuck at a mechanism no construction has must have its Decision
    build a candidate for it next: on 17 October 2026 two reviews in a row located that mechanism (cross-boundary
    correction of the running field) and sent the next entries to further exclusions, and the user asked why no
    construction was attempted."""
    if 'data-kind="review"' not in entry[:600]:
        return
    obstacle = re.search(r'<h4>Obstacle</h4>((?:(?!<h4>).)*)', entry, re.S)
    if not obstacle or not MISSING_CONSTRUCTION.search(strip_tags(obstacle.group(1))):
        return
    decision = re.search(r'<strong>Decision\.</strong>((?:(?!</p>).)*)', entry, re.S)
    if not decision or not BUILDS_NEXT.search(strip_tags(decision.group(1))):
        raise ValueError('the Obstacle says no construction has the mechanism the line needs, and the Decision '
                         'builds none: name in the Decision the construction the next research entries build '
                         'and test (user, 17 October 2026: "You identified exactly what is needed ... But you did '
                         'not make any attempt to construct this?")')


NONLINEAR_CLAIM = re.compile(r'\b(?:is|are)\s+(?:not linear|nonlinear|non-linear) in the counts\b'
                             r'|\b(?:this|that|the|its)\s+(?:\w+\s+){0,3}(?:flow|rule|map|construction|scheme)s?,\s*'
                             r'(?:not linear|nonlinear|non-linear) in the counts\b', re.I)
ADDITIVITY_WITNESS = re.compile(r'additiv|their sum|the sum of|superposition', re.I)


def refuse_unwitnessed_nonlinearity(entry):
    """A sentence asserting that a rule or flow is (not linear | nonlinear) in the counts gives, in that sentence,
    the defining relation failing: two inputs and their sum (AGENTS.md: a property defined over all inputs is not
    concluded from one computed instance). On 17 October 2026 a draft called a flow nonlinear because its amplitudes
    solve cubic equations, while its own two-value model had cubic stationarity with a linear solution. Replayed over
    every notebook, the assertion form matches one earlier sentence (an exit scheme "is not linear in the counts");
    the appositive form ("..., nonlinear in the counts") is not matched, since six of the nine such sentences in the
    record name a class of flows, not a property of one."""
    plain = strip_tags(entry)
    for sentence in re.split(r'(?<=[.;])\s+', ' '.join(plain.split())):
        said = re.sub(r'"[^"]{0,300}"', ' ', sentence)          # a quoted form is mentioned, not asserted
        if NONLINEAR_CLAIM.search(said) and not ADDITIVITY_WITNESS.search(sentence):
            raise ValueError('a sentence says a rule is nonlinear (or not linear) in the counts without the defining '
                             'relation failing in it (two inputs and their sum, or additivity): "' + sentence[:200] +
                             '" (AGENTS.md: a property defined over all inputs is shown by exhibiting it fail)')


def refuse_off_route(source, entry, ask=None):
    """A research entry of a notebook whose goal is open states its Shortest route and, read by the route judge
    (tools/route_judge.py, Haiku), takes it or says why not (user, 17 October 2026: "When you identify a direct
    shortest route above all else, you prioritize it above all else"). The judge's outage never blocks."""
    if 'data-kind="research"' not in entry[:600] or not goal_open(source):
        return
    import route_judge
    reason = route_judge.refusal(entry, source, **({'ask': ask} if ask else {}))
    if reason:
        raise ValueError(reason)


# A computation declined for not deciding the question. On 17 October 2026 three entries declined to build and
# measure a flow because "at reachable sizes a measurement cannot tell" what the limit needs; built at the user's
# choice ("Build it. What if you are wrong....."), its run took minutes and showed an instability no entry had
# predicted. Not deciding the limit is not being uninformative: the decline gives the step's measured cost, or
# the output of a run already made.
DECLINED_RUN = re.compile(r'\bNot taken\b', re.I)
UNDECIDING = re.compile(r'\b(?:measurement|computation|run|simulation|test)s?\b[^.;]{0,80}\b(?:cannot|can not|could '
                        r'not|does not|do not|would not)\s+(?:tell|decide|distinguish|show|bear)\b'
                        r'|\bno (?:computation|measurement|run) at reachable sizes\b|\bdecides? nothing\b', re.I)
RUN_COST = re.compile(r'\bmeasured\b[^.;]{0,60}\b(?:cost|time|\d+(?:\.\d+)?\s*(?:s|min|minutes|seconds))\b'
                      r'|research/(?:results|logs)/', re.I)


def refuse_unmeasured_decline(entry):
    """The Shortest route of a research entry that declines a computation because it cannot decide the question
    says what that computation costs, measured, or cites the output of a run made: [] or the refusal."""
    given = re.search(r'<strong>Shortest route\.</strong>((?:(?!</p>).)*)', entry, re.S)
    plain = ' '.join(strip_tags(given.group(1)).split()) if given else ''
    if DECLINED_RUN.search(plain) and UNDECIDING.search(plain) and not RUN_COST.search(plain):
        raise ValueError('the Shortest route declines a computation because it cannot decide the question ("'
                         + UNDECIDING.search(plain).group(0)[:120] + '") without its measured cost or the output '
                         'of a run made: a run that cannot decide the limit can still show the object something '
                         'unforeseen; give its measured cost (a smoke run) or run it (user, 17 October 2026: '
                         '"Build it. What if you are wrong.....")')


NONTRIVIAL = re.compile(r'Nontrivial because[:,]?\s+((?:\S+\s+){7,}\S+)', re.I)


def refuse_trivial_smallest_case(entry):
    """A draft naming a next attempt gives, in its Smallest case, the reason the instance is nontrivial for that
    attempt: what the attempt's mechanism has to act on there. On 17 October 2026 a Smallest case took one cut
    with no coarser load, where the rule has nothing to choose, and the two-level case, which decided the attempt,
    was not taken; the next draft's Smallest case then dropped the setting's order of steps."""
    follow = re.search(r'<strong>Follow-up\.</strong>((?:(?!</p>).)*)', entry, re.S)
    plain = strip_tags(follow.group(1)) if follow else ''
    if not re.match(r'\s*Continuing', plain) or not re.search(r'\bnext attempt\b', plain, re.I):
        return
    given = re.search(r'<strong>Smallest case\.</strong>((?:(?!</p>)(?!</li>).)*)', entry, re.S)
    said = strip_tags(given.group(1)) if given else ''
    if not NONTRIVIAL.search(said):
        raise ValueError('the Smallest case of a next attempt says, after "Nontrivial because:" in at least eight '
                         'words, what the attempt\'s mechanism acts on in that instance (a load it reads, a choice '
                         'it makes), so a degenerate instance is not taken for the smallest one (AGENTS.md: next '
                         'attempts are first tried on their smallest nontrivial instance)')


UNCOMPUTED = re.compile(r'\bnot\s+(?:yet\s+)?(?:computed|tried|run|checked|attempted)\b'
                        r'|\b(?:remains?\s+)?to\s+be\s+(?:computed|tried|checked)\b'
                        r'|\bremains?\s+to\s+(?:compute|try|check)\b', re.I)


def refuse_uncomputed_smallest_case(entry):
    """A Smallest case reports the try on the instance it names. On 17 October 2026 one named a chain of gadgets
    "its ratio not yet computed" and the entry called the question open, while a four-level family decided it in a
    few lines (the reviewer's). Over the record, 8 of 61 Smallest case paragraphs held such a phrase, 6 of them an
    instance named and left untried (research/provenance/framework/smallest-case-uncomputed-replay-20261017.txt).
    A sentence that calls itself a judgement, or gives the measured cost of the step it leaves, is exempt."""
    for given in re.finditer(r'<strong>Smallest case\.</strong>((?:(?!</p>)(?!</li>).)*)', entry, re.S):
        # whole sentences: a qualifier in a later clause ("...not tried; as a judgement ...") covers it (the
        # stand-in review of 17 October 2026: a split at ";" cut a judgement off the clause it qualifies)
        for sentence in re.split(r'(?<=\.)\s+(?=[A-Z\\(])', strip_tags(given.group(1))):
            if UNCOMPUTED.search(sentence) and not re.search(r'\bjudgement\b|\bmeasured\b', sentence, re.I):
                raise ValueError('the Smallest case leaves its instance uncomputed ("' + sentence.strip()[:160]
                                 + '"): run the attempt on it, or on a smaller instance that decides it, before '
                                 'the entry calls the question open; a sentence that is a judgement says so, and '
                                 'one leaving a step for its cost gives the measured cost (AGENTS.md: next '
                                 'attempts are first tried on their smallest nontrivial instance)')


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
    # 17 October 2026: "--stand-unchanged x", carried over from skeleton checks, passed and wrote "Unchanged: x"
    # into an entry whose result belonged in the section; the 368 reasons in the record have at least 7 words.
    if len(reason.split()) < STAND_WORDS:
        raise ValueError(f'--stand-unchanged needs a reason of at least {STAND_WORDS} words saying why nothing in '
                         'Where we stand changed; it is written into the entry')
    paragraph = f'{STAND_LABEL}{html.escape(reason.strip(), quote=False)}</p>'
    meta = re.search(r'<p class="entry-meta">.*?</p>', entry, re.S)
    at = meta.end() if meta else entry.rindex('</article>')
    return entry[:at] + '\n' + paragraph + ('\n' if not meta else '') + entry[at:]


def named_items(source, next_html):
    """The queued items a next step names, by identifier or by a link to an entry that developed one, each as
    (identifier, queued text, anchor of its latest development, that entry's Follow-up); None when the notebook
    has no queue.

    A next step of 11 October 2026 described a queued check as asking another question than its text asks, and
    the cycle went to a form the item's own closure had judged not to bear: the item's words and its latest
    follow-up are shown beside the next step, and a next step that takes a queue item says which."""
    import lead_queue
    found = lead_queue.parse_tree(source)
    if found is None:
        return None
    nodes = found[1] + [child for node in found[1] for child in node.children]
    # Keyed by kind and identifier: a lead and a bridge of one review share REVIEW:1, and keyed by identifier
    # alone the bridge's text was printed with the lead's entries (11 October 2026).
    queued = {(node.kind, node.ident): node for node in nodes}
    linked = set(re.findall(r'href="#([^"]+)"', next_html))
    named = []
    for kind, ident in queued:
        if not mentioned(ident, next_html):
            continue
        shared = [k for k, i in queued if i == ident]
        # among items sharing the identifier, the one whose kind is the word before it; all when none is said
        said = [k for k in shared if re.search(r'\b' + k + r'[\s:]+' + re.escape(ident) + r'(?![\w:-])', next_html)]
        if len(shared) == 1 or not said or kind in said:
            named.append((kind, ident))
    developments = {}
    for tag, text in lead_queue.record_articles(source):
        anchor = re.search(r'\bid="([^"]+)"', tag)
        item = re.search(r'\bdata-(' + lead_queue.NAMES + r')="([^"]+)"', tag)
        if anchor and item and item.groups() in queued:
            follow = lead_queue.own_follow_ups(text)
            developments[item.groups()] = (anchor.group(1), plain(follow[-1]) if follow else '')
            if anchor.group(1) in linked and item.groups() not in named:
                named.append(item.groups())
    return [(Named(i, k, sum(1 for _, other in queued if other == i) > 1), plain(queued[k, i].text),
             *developments.get((k, i), ('', ''))) for k, i in named]


def mentioned(ident, text):
    """Whether `text` names the queue identifier, bare or as KIND:IDENTIFIER, and not as part of a longer one.

    A colon after it continues a longer identifier only when a word follows: "item:s1: the check" names item:s1
    (on 16 October 2026 such a step's quotation of the item was checked against other items only)."""
    import lead_queue
    return re.search(r'(?<![\w:#-])(?:(?:' + lead_queue.NAMES + r'):)?' + re.escape(ident) + r'(?![\w-]|:[\w-])',
                     text)


class Named(str):
    """A queued item's identifier that remembers its kind, for identifiers two kinds share."""

    def __new__(cls, ident, kind=None, shared=False):
        named = super().__new__(cls, ident)
        named.kind = kind
        named.full = f'{kind}:{ident}' if kind else str(ident)     # what the queue tool's lookups take
        named.label = named.full if shared else str(ident)         # what a message prints: the kind where needed
        return named


def item_history(source, ident):
    """Every record entry that developed the queued item `ident`, oldest first, as (anchor, title).

    A review of 11 October 2026 gave its decisive test to a queued item after reading that item's latest
    entry only; an earlier entry on the same item already answered the test.  The whole list is printed
    beside the next step, so that the entries to read are named."""
    import lead_queue
    history = []
    kinds = getattr(ident, 'kind', None) or lead_queue.NAMES      # one kind when the identifier carries it
    for tag, text in lead_queue.record_articles(source):
        anchor = re.search(r'\bid="([^"]+)"', tag)
        item = re.search(r'\bdata-(?:' + kinds + r')="([^"]+)"', tag)
        # also entries filed under another item that give this one an outcome in a follow-up list item: an item
        # of 11 October had been closed and reopened so, as a sub-idea of its former parent, and the list of
        # entries filed under its own identifier showed neither
        listed = re.search(r'<li data-(?:' + kinds + r')="' + re.escape(ident) + r'"', text)
        if anchor and ((item and item.group(1) == ident) or listed):
            title = re.search(r'<h3>(.*?)</h3>', text, re.S)
            history.append((anchor.group(1), plain(title.group(1)) if title else ''))
    return history


QUOTED_WORDS = 8    # consecutive words of an item's follow-up or text that a next step naming it must quote


def words(text):
    return [w for w in (re.sub(r'^\W+|\W+$', '', token).lower() for token in plain(text).split()) if w]


def quotes(step, source, length=QUOTED_WORDS):
    """Whether `step` contains `length` consecutive words of `source`."""
    have, given = words(step), words(source)
    runs = {tuple(given[i:i + length]) for i in range(len(given) - length + 1)}
    return any(tuple(have[i:i + length]) in runs for i in range(len(have) - length + 1))


def require_quoted_items(source, next_html):
    """A next step that names a queued item by its identifier, when the item has a latest follow-up, quotes
    it or the item's text.

    Printing the item's words (above) showed, on 11 October 2026, a next step whose reason did not match its
    item, and the step was committed with the mismatch.  A quotation of eight consecutive words is a mechanical
    proxy: the description is then written from the item's words.  An item named only through a link to an
    entry is not held to this, a link often pointing at the item being left."""
    for ident, text, anchor, follow in named_items(source, next_html) or []:
        by_name = mentioned(ident, next_html)
        if by_name and follow and not (quotes(next_html, follow) or quotes(next_html, text)):
            raise ValueError(f'the next step names queue item {ident.label} and quotes neither its latest follow-up '
                             f'(#{anchor}) nor its queued text: quote at least {QUOTED_WORDS} consecutive words '
                             'of one of them, so that what the item asks is written from its own words '
                             f'(tools/lead_queue.py history NOTEBOOK {ident.label} --status)')
    refuse_stale_quotations(source, next_html)


QUOTATION = re.compile(r'“([^”]*)”|"([^"]*)"')


def contains_words(source, passage):
    """Whether the words of `passage` occur consecutively in `source`."""
    have, want = words(source), words(passage)
    return bool(want) and any(have[i:i + len(want)] == want for i in range(len(have) - len(want) + 1))


def refuse_stale_quotations(source, next_html):
    """Every passage of QUOTED_WORDS or more words that a next step naming queued items puts in quotation marks
    occurs in one of those items' latest follow-up or queued text.

    On 16 October 2026 a next step quoted the next attempt of an entry draft whose follow-up the review had since
    rewritten; it passed the eight-word check through a phrase common to both versions ("the item's last turn
    before its spell boundary") and was patched by hand after the append.  A quotation is the step's claim about
    what the item now says, so it is held to the current words."""
    named = named_items(source, next_html) or []
    sources = [part for _, text, _, follow in named for part in (follow, text) if part]
    if not sources:
        return
    for match in QUOTATION.finditer(plain(next_html)):
        passage = match.group(1) if match.group(1) is not None else match.group(2)
        if len(words(passage)) >= QUOTED_WORDS and not any(contains_words(part, passage) for part in sources):
            labels = ', '.join(ident.label if hasattr(ident, 'label') else str(ident) for ident, *_ in named)
            raise ValueError(f'the next step quotes “{passage.strip()}”, which is not in the latest follow-up or '
                             f'queued text of the item it names ({labels}): quote the current words, or drop the '
                             'quotation marks if the passage is not a quotation of the item')


def review_due(articles):
    """Whether the notebook's next entry must be the scheduled review."""
    checks = reporting_checks()
    kinds = (re.search(r'\bdata-kind="([^"]*)"', tag) for tag, _ in articles)
    run, _ = checks.review_cadence(match.group(1) if match else None for match in kinds)
    return run >= checks.REVIEW_PERIOD


def plain(fragment):
    return ' '.join(html.unescape(strip_tags(fragment)).split())


def require_named_item(source, next_html):
    """While the queue drains every research entry develops a queued item, so its next step names one."""
    import lead_queue
    items = named_items(source, next_html)
    if items is None or items or not lead_queue.is_draining(source) or not goal_open(source):
        return
    if review_due(lead_queue.record_articles(source)):
        return      # the next entry is the route review, which develops no item
    raise ValueError('the queue is draining, so the next entry develops a queued item, and this next step names '
                     'none: give the item\'s identifier, or link an entry that developed it, and describe what '
                     'it asks from its queued text (tools/lead_queue.py history NOTEBOOK ID --status)')


_MATCH_CACHE = {}


def registry_matches(text, limit=3, data=None, home=None):
    """Cached by its arguments when the registry is read here (data None): the append's check of unapplied matches
    and its printed listing ask for the same item's matches; on 17 October 2026 one search took 5.93 s, and 11.14 s
    for the queue item's text and follow-up, before the index of tools/search-claims.py brought the latter to
    0.88 s (research/provenance/framework/registry-match-timing-20261017.txt)."""
    if data is None:
        key = (text, limit, home)
        if key not in _MATCH_CACHE:
            _MATCH_CACHE[key] = _registry_matches(text, limit, None, home)
        return _MATCH_CACHE[key]
    return _registry_matches(text, limit, data, home)


def _registry_matches(text, limit=3, data=None, home=None):
    """The registered claims nearest to a queued item's text, as (identifier, start of summary), best first;
    an empty list where the registry cannot be read.

    On 11 October 2026 a reading named on a queue item was deferred in two entries while its statement had
    been registered for a day: the item's words were never put to the registry.  The matches are printed
    beside the item when a next step names it; they are not logged as a search of the author's.

    With `home`, a part of a record address that marks the notebook's own claims, those come first, each
    group in its order of score: across two blocks of entries the three matches printed were mostly claims
    of other notebooks, which share common words and say nothing of the item."""
    spec = importlib.util.spec_from_file_location('search_claims', Path(__file__).parent / 'search-claims.py')
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        if data is None:
            data = module.read_json(module.REGISTRY)
        found = module.search(data, [plain(text)])
    except (OSError, ValueError, KeyError):
        return []
    if home:
        found = sorted(found, key=lambda pair: home not in str(pair[1].get('record', '')))   # stable
    return [(claim['id'], ' '.join(claim['summary'].split())[:140]) for _score, claim in found[:limit]]


OWN_CLAUSE = re.compile(r'<strong>Own statements\.</strong>((?:(?!<strong>[^<]{1,40}\.</strong>).)*)', re.S)


def unapplied_matches(entry, matches):
    """The claims of `matches` (the registry matches printed for the queue item an entry develops) that no Own
    statements clause of the entry names.  On 17 October 2026 the append tool printed thm:per-level-count-matchings
    beside the item mixed-level-counts, the next entry did not apply it, and its reviewer found that it reframed
    the entry's next attempt; the listing was read and not used.  A claim the entry declares itself is exempt.
    Its limits, from its reviewer: a claim named in a dismissive clause passes, the check not telling an application
    from a mention; an entry developing an item without a data-check, data-lead, data-bridge, data-build or
    data-idea attribute is not checked; and the matches are recomputed at append time from the item's text and
    latest follow-up, so they need not be the ones printed when the next step named the item.  Replayed over the
    last twelve research entries (research/provenance/framework/unapplied-matches-judged-20261017.txt): 16 findings,
    10 of them claims registered in that entry or later, which cannot occur at append time, and 6 claims the entry
    named outside Own statements: every finding it could have made then asked only to move or repeat a name, a
    false-refusal rate of up to six in six on that replay, whether any would have changed an entry not judged."""
    own = ' '.join(OWN_CLAUSE.findall(entry))
    tag = re.search(r'<article\b[^>]*>', entry)
    declared = set(re.search(r'data-claims="([^"]*)"', tag.group(0)).group(1).split()) if tag and \
        'data-claims="' in tag.group(0) else set()
    return [claim for claim in matches if claim not in declared and not re.search(r'(?<![\w:-])' + re.escape(claim)
                                                                                + r'(?![\w-])', own)]


def refuse_unapplied_matches(source, entry, home=None):
    """Refuse an entry developing a queue item whose Own statements leave out a registry match of that item."""
    tag = re.search(r'<article\b[^>]*>', entry)
    found = re.search(r'\bdata-(check|lead|bridge|build|idea)="([^"]+)"', tag.group(0)) if tag else None
    if not found:
        return
    items = named_items(source, f'<p>{found.group(1)}:{found.group(2)}</p>') or []
    for ident, text, _anchor, follow in items:
        if ident.full != f'{found.group(1)}:{found.group(2)}':
            continue
        matches = [claim for claim, _ in registry_matches(f'{text} {follow or ""}', home=home)]
        if not matches:
            # registry_matches returns nothing when the registry cannot be read: say so rather than pass silently
            print(f'notebook-append.py: warning: no registry matches for {ident.full}; the registry may be '
                  'unreadable, and the Own statements check of its matches did not run', file=sys.stderr)
        missing = unapplied_matches(entry, matches)
        if missing:
            raise ValueError('the entry develops ' + ident.full + ', beside which the registry matches '
                             + ', '.join(missing) + ' are printed, and no Own statements clause names them: apply '
                             'each to the entry\'s next attempt there, or say why it does not bear (AGENTS.md: a '
                             'listed record is read by applying it to the case in hand)')


def older_claim_lines(source, ident, claims=None):
    """Lines for the claims of entries older than a queued item that are nearest to its text, marked as earlier;
    the registry matches above them are of any date and do not say which."""
    import lead_queue
    found = lead_queue.claims_elsewhere(source, lead_queue.registered_claims() if claims is None else claims,
                                        getattr(ident, 'full', ident), 3, earlier=True)
    return [f'  Claim of an entry up to the one that queued it, nearest to its text [earlier]: {claim} in #{anchor}'
            for _score, claim, anchor in found]


def home_of(source):
    """The part of a record address that marks a side notebook's claims, or None for the main notebook."""
    found = re.search(r'branches/[^/]+/', str(source))
    return found.group(0) if found else None


def refuse_excluded_item(source, next_html):
    """A next step may not take only the item that the finisher will refuse for the next entry.

    After two research entries in a row on one queue item that declare no bearing, the finisher sends the next
    entry to a different item.  On 11 October 2026 two next steps named such an item; the first was noticed
    on opening the cycle and the second only when the finished entry was refused."""
    items = named_items(source, next_html)
    if not items:
        return
    tags = [t for t in re.findall(r'<article\b[^>]*>', source) if 'data-kind="research"' in t]
    if not tags:
        return
    # Each named item on its own route: on 16 October 2026 a next step written in an entry of another route
    # named an item whose route had just had two such entries, and the check, reading the route of the last
    # entry, passed it; the finisher refused the entry that developed it.
    import lead_queue
    blocked = lead_queue.no_bearing_excluded(source)    # sub-ideas resolved to their item (lead_queue.item_root)
    excluded = []
    for full in sorted({ident.full for ident, *_ in items}):
        kind, _, ident = full.partition(':')
        mine = [t for t in tags if lead_queue.tag_item(source, t) == ident]
        route = re.search(r'data-route="([^"]+)"', mine[-1]) if mine else None
        if route is not None and blocked.get(route.group(1)) == ident:
            excluded.append((full, ident))
    if not excluded:
        return
    if len(excluded) == len({ident.full for ident, *_ in items}):
        raise ValueError(f'the next step takes {excluded[0][1]}, whose last two entries declared no bearing: the '
                         'finisher will refuse a third in a row, so name the different item the next entry '
                         'develops (AGENTS.md, goal progress)')
    for _full, ident in excluded:
        print(f'Note: {ident} had two entries in a row without bearing; the next entry must develop '
              'another of the items this step names.', file=sys.stderr)


# What the plan must say of the entry it plans; "does not close" and "the other check is closed" do not match.
PLAN_CLOSES = re.compile(r'\b(?:the |this )?entry (?:then )?(?:closes|will close) (?:its|the|that|this) '
                         r'(?:queue |queued )?(?:item|check|lead|build)\b', re.I)
PLAN_BEST = re.compile(r'\bBest outcome\b(.*)', re.I | re.S)


def refuse_no_bearing_plan(source, next_html):
    """A next step may not plan, in a run of entries without bearing, an entry the finisher will refuse.

    After three research entries in a row on the route that declare no bearing, the finisher refuses an entry
    whose Best outcome says it gives nothing at the goal's parameters unless its follow-up closes its item.  On
    12 October 2026 a next step stated exactly that best outcome, was accepted, and the cycle made by it was
    refused at its end, when its reviewer had ruled the item open.  The run's length and the words for nothing
    are the finisher's own; like the finisher it reads only what follows "Best outcome", so a sentence about
    past work is not taken for the plan, and a next step that states no best outcome is not refused here.  A
    next step for the route review that is due is not a plan of a research entry."""
    import lead_queue
    if review_due(lead_queue.record_articles(source)):
        return
    checks = reporting_checks()
    tags = [t for t in re.findall(r'<article\b[^>]*>', source) if 'data-kind="research"' in t]
    if not tags:
        return
    route = re.search(r'data-route="([^"]+)"', tags[-1])
    run = 0
    for tag in reversed([t for t in tags if route and f'data-route="{route.group(1)}"' in t]):
        if 'data-bearing="none"' not in tag:
            break
        run += 1
    step = plain(next_html)
    best = PLAN_BEST.search(step)
    text = best.group(1) if best else ''                 # the closing may be said anywhere in the step
    if run >= checks.NO_BEARING_RUN and checks.NOTHING_BEST_RE.search(text) and not PLAN_CLOSES.search(step):
        raise ValueError(f'the last {run} research entries on the route declared no bearing, and this next step '
                         "says its best outcome is nothing at the goal's parameters without saying that the entry "
                         'closes its item: the finisher will refuse the entry it plans; plan an attempt whose '
                         'best outcome bears on the goal, or one that closes its item and says so (AGENTS.md, '
                         'goal progress)')


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


def append(source, entry, next_html=None, committed=None, reason=None, tools=None, *, checked=True):
    """The notebook `source` with `entry` appended and, with `next_html`, its next step replaced.
    `committed` is the notebook as of the last commit, for the Where we stand rule, and `reason`
    what --stand-unchanged gave."""
    entry = entry.strip()
    m = re.match(r'<article\b[^>]*?\sid="([^"]+)"', entry)
    if not m or not entry.endswith('</article>'):
        raise ValueError('entry must be one <article id="..."> ... </article> element')
    refuse_broken_text('entry', entry)
    refuse_early_review_credit(entry)
    refuse_unbuilt_obstacle(entry)
    refuse_unwitnessed_nonlinearity(entry)
    if next_html is not None:
        refuse_broken_text('next step', next_html)
        refuse_next_structure(next_html)
        parked = PARKING.search(strip_tags(next_html))
        # A branch's own module may name kinds of entry whose next step may wait.
        may_wait = '|'.join(map(re.escape, branch_extension.ask('PARKING_KINDS', (), tools)))
        waiting_kind = may_wait and re.match(rf'<article\b[^>]*\bdata-kind="(?:{may_wait})"', entry)
        if parked and goal_open(source) and not waiting_kind:
            raise ValueError(f'the next step parks the goal ("{parked.group(0)}"); while the goal is open '
                             'the next step is research: open a new line or test a new idea (AGENTS.md)')
    try:        # the finisher's rule, with the next step, which the finisher does not see
        reporting_checks().refuse_unverified_attempt(entry, next_html)
    except ValueError as error:
        raise ValueError(str(error)[0].lower() + str(error)[1:]) from None
    refuse_trivial_smallest_case(entry)
    refuse_uncomputed_smallest_case(entry)
    refuse_unmeasured_decline(entry)
    entry = with_stand_reason(source, entry, committed, reason)
    own = branch_checks(tools)
    if own:
        own(source, entry, next_html)
    if f'id="{m.group(1)}"' in source:
        raise ValueError(f'anchor already present: {m.group(1)}')
    source = insert_entry(source, entry)
    if next_html is not None:
        source = replace_next(source, next_html)
    living_sections(source)
    if checked:     # skeleton_check runs these checks itself, under their own names
        preflight(source, m.group(1))
    return source


def insert_entry(source, entry):
    """The notebook with `entry` after the last article of its research record."""
    start = source.find('<section id="research-record">')
    if start < 0:
        raise ValueError('research-record section missing')
    close = source.find('</section>', start)
    last = source.rfind('</article>', start, close)
    at = last + len('</article>') if last >= 0 else close
    return source[:at] + '\n' + entry.strip() + source[at:]


def refuse_record_findings(entry):
    """Refuse a draft with a finding of tools/check_records.py (commit hashes, environment literals, backticks,
    long status lines), which the checkpoint's --diff run would otherwise find only at the commit."""
    import check_records
    found = check_records.draft_findings(entry)
    if found:
        raise ValueError(f'{len(found)} record-check findings in the draft: '
                         + '; '.join(f'line {n}: {kind}: {text[:60]}' for n, kind, text in found))


def skeleton_check(source, entry, next_html=None, committed=None, reason=None, path=None, root=ROOT):
    """The entry checks that can run on a draft, run without writing anything: the (check, error) pairs that
    fail. They are the Where we stand rule, the append's other refusals (one at a time: its first refusal hides
    its later ones), the refusals main() makes around the append (item history, quoted closures, publication
    citations), the queue check, and the finisher's entry_checks with claim registration not required. An entry's skeleton, its
    headings and labelled paragraphs before the body, goes through it at the start of drafting (AGENTS.md), so
    that a paragraph a check requires is found then and not when the finished draft is appended or finished
    (16 October 2026: two drafts of one session lacked such a paragraph). Left out: main()'s check that every
    summing-up sentence is answered (refuse_unanswered), since those sentences are written after the work and
    their answers with them; and, left to the finisher, the checks that read the session's searches, the
    registered claims and the context budgets, and its printed reports."""
    failures = []

    def run(name, call):
        try:
            call()
        except ValueError as error:
            failures.append((name, str(error)))

    # The Where we stand rule is reported on its own, and the append then runs with a stand-in reason, so that
    # its refusal does not hide the append's later ones (16 October 2026: it hid the open sub-ideas refusal).
    run('where we stand', lambda: with_stand_reason(source, entry, committed, reason))
    proposed = []
    run('append', lambda: proposed.append(append(source, entry, next_html, committed, reason or 'a stand-in reason for the skeleton check',
                                                 checked=False)))
    try:
        body = proposed[0] if proposed else insert_entry(source, entry)
    except ValueError as error:
        return failures + [('record', str(error))]
    # The refusals main() makes around the append: the item's record, quoted closures, publication citations.
    run('item history', lambda: refuse_item_history(body))
    run('closures', lambda: refuse_unquoted_closures(source, entry))
    run('publication citation', lambda: refuse_uncited_publication(entry))
    run('record lines', lambda: refuse_record_findings(entry))
    run('plainest uniform bound', lambda: refuse_one_function_plainest(entry))
    ident = re.match(r'\s*<article\b[^>]*?\sid="([^"]+)"', entry)
    if not ident:
        return failures
    article = body.rfind('<article', 0, body.rindex(f'id="{ident.group(1)}"'))
    close = body.find('</article>', article)
    checks = reporting_checks()
    from lead_queue import check as queue_check, is_draining, SECTION_RE
    run('queue', lambda: queue_check(committed, body, path, Path(root)))
    section = SECTION_RE.search(body)
    draining = is_draining(committed, section.group(1) if section else None)
    for name, call in checks.entry_checks(body, article, close, draining, registered=False):
        run(name, call)
    marker = re.search(r'<!-- TIMING \S+ -->', entry)
    if marker:
        run('stand-in review answer', lambda: checks.validate_review_answer(Path(root), body, marker.group(0)))
    return failures


def replace_next(source, next_html):
    """The notebook with its Proposed next step replaced by `next_html`, after the next-step checks.
    Used with an entry, and alone (--next without an entry) when the last entry's next step must change
    after it was appended, so that the notebook need not be restored and the entry appended again."""
    a = source.find('<section id="proposed-next-step">')
    if a < 0:
        raise ValueError('proposed-next-step section missing')
    b = source.index('</section>', a)
    body = source[a:b]
    if HEADING not in body:
        raise ValueError('proposed-next-step heading missing')
    head = body[:body.index(HEADING) + len(HEADING)]
    source = source[:a] + head + '\n' + next_html.strip() + '\n' + source[b:]
    require_named_item(source, next_html)
    require_quoted_items(source, next_html)
    refuse_excluded_item(source, next_html)
    refuse_no_bearing_plan(source, next_html)
    return source


def refuse_next_structure(fragment):
    """The next-step file is section contents; its enclosing section and heading are retained."""
    book = excerpt.Notebook(fragment)
    for node in book.nodes:
        if node['tag'] == 'section' or (node['tag'] == 'h2' and
                excerpt.visible_text(fragment[node['start']:node['end']]).casefold() == 'proposed next step'):
            raise ValueError('next step must contain only the section contents, without a section wrapper '
                             'or the retained Proposed next step heading')


def refuse_item_history(result):
    """Refuse an entry developing a queue item that the finisher would refuse for its item's record (links to
    earlier developments, an owed attempt, open sub-ideas), before anything is written or registered."""
    import lead_queue
    problems = lead_queue.draft_item_problems(result)
    if problems:
        raise ValueError('; '.join(problems))


def committed_version(path):
    """The notebook as of HEAD, or None outside a repository or for a notebook not yet committed."""
    try:
        rel = Path(path).resolve().relative_to(Path(ROOT).resolve())
    except ValueError:
        return None
    shown = subprocess.run(['git', '-C', str(ROOT), 'show', f'HEAD:{rel.as_posix()}'], capture_output=True, text=True)
    return shown.stdout if shown.returncode == 0 else None


def result_files_line(body, ident):
    """The line listing the result files the entries on queue item `ident` link, or '' when there are none or the
    item is not found: what its entries computed, from which a test posed on the item or a control planned for it
    starts."""
    import lead_queue
    try:
        files = lead_queue.result_files(body, getattr(ident, 'full', ident))
    except (ValueError, KeyError):
        return ''
    return f'  Result files its entries link ({len(files)}): ' + ', '.join(files) if files else ''


def cadence_line(text):
    """One line on the review cadence after the last entry of the record, for a next step to be written against.

    Twice on 11 October 2026 a next step said which coming entry is the sixth since the last route review,
    counted from memory, and was wrong by one; the count is printed where the next step is written."""
    tags = re.findall(r'<article\b[^>]*>', text[text.find('<section id="research-record"'):])
    if not tags:
        return None
    checks = reporting_checks()
    kinds = (re.search(r'data-kind="([^"]*)"', tag) for tag in tags)
    streak, _ = checks.review_cadence(match.group(1) if match else None for match in kinds)
    left = checks.REVIEW_PERIOD - streak
    return (f'Review cadence: {streak} research entries since the last route review, this one included; '
            + (f'{left} more, then the review.' if left > 0 else 'the next entry is the review.'))


def closing_followups(source, entry, articles=None):
    """[(kind, identifier, the follow-up's text, the item's listed text)] for the follow-up list items of
    `entry` that close a listed item (Closed or Developed, a merge apart), the listed text read whole from
    the article of `source` that listed it, or '' when that article or the item is not found.  `articles`,
    {anchor: article}, spares a search of the whole notebook for each item when many entries are read."""
    import lead_queue
    found = []
    for kind, ident, item in lead_queue.FOLLOWUP_ITEM.findall(entry):
        outcome = lead_queue.OUTCOME_RE.search(item)
        if not outcome or outcome.group(1) not in ('Closed', 'Developed') or ':' not in ident:
            continue
        if re.search(r'Closed:\s*merged into\b', item):
            continue
        anchor = ident.rsplit(':', 1)[0]
        if articles is not None:
            art = articles.get(anchor)
        else:
            hit = re.search(r'<article\b[^>]*\bid="' + re.escape(anchor) + r'"[^>]*>.*?</article>', source, re.S)
            art = hit.group(0) if hit else None
        listed = lead_queue.listed_item(kind, art, ident) if art else None
        found.append((kind, ident, plain(item), plain(listed[1]) if listed else ''))
    return found


def refuse_unquoted_closures(source, entry):
    """Lines to print, the listed text of each item the entry closes beside its follow-up; a closing follow-up
    that quotes no QUOTED_WORDS consecutive words of that text is refused.  On 12 October 2026 two sub-ideas
    were closed by what a result resembled and not by what their texts ask, and a reviewer caught both: the
    quotation puts the item's own words into the closure, where the reviewer and the author read them."""
    lines, bad = [], []
    for kind, ident, follow, text in closing_followups(source, entry):
        lines.append(f'The entry closes {kind}:{ident}. Its listed text, to read beside the follow-up:')
        lines.append(f'  Listed text: {text or "(not found in the notebook)"}')
        lines.append(f'  Follow-up: {follow}')
        if text and not quotes(follow, text, min(QUOTED_WORDS, len(words(text)))):    # a short text, whole
            bad.append(f'{kind}:{ident}, whose text is: {text}')
    if bad:
        raise ValueError(f'A follow-up that closes a listed item quotes {QUOTED_WORDS} consecutive words of the '
                         'item\'s listed text, so that the closure answers what the item asks; none is quoted '
                         'for ' + '; '.join(bad))
    return lines


def closures_count(source):
    """A line for each entry with closing follow-ups (how many, how many quote their item, how many items were
    not found), and the totals."""
    rows, kinds = [], {}
    whole = {m.group(1): m.group(0)
             for m in re.finditer(r'<article\b[^>]*\bid="([^"]+)"[^>]*>.*?</article>', source, re.S)}
    for ident, article in whole.items():
        found = closing_followups(source, article, whole)
        for kind, _, _, _ in found:
            kinds[kind] = kinds.get(kind, 0) + 1
        if found:
            rows.append((ident, len(found),
                         sum(1 for _, _, follow, text in found
                             if text and quotes(follow, text, min(QUOTED_WORDS, len(words(text))))),
                         sum(1 for _, _, _, text in found if not text)))
    lines = [f'{n}\t{quoted}\t{missing}\t{ident}' for ident, n, quoted, missing in rows]
    return '\n'.join(lines + [f'{sum(r[1] for r in rows)} closing follow-ups in {len(rows)} entries; '
                              f'{sum(r[2] for r in rows)} quote {QUOTED_WORDS} consecutive words of their item\'s '
                              f'listed text; {sum(r[3] for r in rows)} name an item whose text was not found '
                              '(columns: closing, quoting, not found). By kind of item: '
                              + (', '.join(f'{n} {kind}' for kind, n in sorted(kinds.items())) or 'none')
                              + f'. The notebook has {len(source.encode())} bytes.'])


def refuse_unanswered(entry, answers):
    """Refuse an entry whose summing-up sentences with a universal, negative or exact word are not each
    answered in the file given by --answers.  In one review period of 12 October 2026 the draft tool printed,
    in five entries of six, sentences that a reviewer then corrected: a printed list that nothing answers is
    passed over.  The answer is a line saying what the sentence rests on; whether it does is for the reviewer,
    who is given the file."""
    import draft_claim_sentences
    rows = draft_claim_sentences.summing_up(entry)
    instance_rows = draft_claim_sentences.hypothesis_rows(entry)
    if instance_rows:           # a cited claim evaluated at an instance, its hypotheses checked there
        unchecked = draft_claim_sentences.unchecked_hypotheses(entry, answers or '')
        if unchecked:
            raise ValueError(draft_claim_sentences.unchecked_hypotheses_report(unchecked)
                             + ('\n(pass the answers with --answers FILE; tools/draft_claim_sentences.py DRAFT '
                                '--answers FILE writes the form)' if answers is None else ''))
    if draft_claim_sentences.source_rows(entry):      # a cited proof described, the passage it rests on named
        open_source = draft_claim_sentences.unsourced(entry, answers or '')
        if open_source:
            raise ValueError(draft_claim_sentences.unsourced_report(open_source)
                             + ('\n(pass the answers with --answers FILE; tools/draft_claim_sentences.py DRAFT '
                                '--answers FILE writes the form)' if answers is None else ''))
    if draft_claim_sentences.converse_rows(entry):     # a condition called exact, its other direction answered
        open_converse = draft_claim_sentences.unconversed(entry, answers or '')
        if open_converse:
            raise ValueError(draft_claim_sentences.unconversed_report(open_converse)
                             + ('\n(pass the answers with --answers FILE; tools/draft_claim_sentences.py DRAFT '
                                '--answers FILE writes the form)' if answers is None else ''))
    if not rows:
        refuse_unbounded(entry, answers)
        return
    if answers is None:
        raise ValueError(f'{len(rows)} summing-up sentences of the entry (its title and status line, and those '
                         'saying no, every, exactly and the like) are answered before the append; '
                         'answer each in a file and pass it with --answers FILE '
                         '(tools/draft_claim_sentences.py DRAFT --answers FILE writes the form)')
    left = draft_claim_sentences.unanswered(entry, answers)
    if left:
        # Each row says which condition failed: on 17 October 2026 three answers were present but cited nothing
        # grounded() accepts, and the message, "not answered", left their cause to be guessed.
        given = {key: answer for key, answer in draft_claim_sentences.ANSWER.findall(answers or '')}

        def why(key):
            answer = given.get(key)
            if answer is None:
                return 'no "rests on:" line under this key (a sentence changed since its answer has a new key)'
            if len(answer.split()) < draft_claim_sentences.ANSWER_WORDS:
                return f'its "rests on:" answer has fewer than {draft_claim_sentences.ANSWER_WORDS} words'
            return ('its "rests on:" answer cites no claim ID, #entry- anchor, research/ path or formula, and does '
                    'not begin "none:"')
        raise ValueError(f'{len(left)} of {len(rows)} summing-up sentences are not answered in the --answers '
                         'file:\n' + '\n'.join(f'  {key} [{where}] {sentence[:160]}\n    {why(key)}'
                                               for key, where, sentence in left))
    gaps = draft_claim_sentences.qualifier_gaps(entry, answers)
    if gaps:                    # the answer admits a limit that the sentence does not carry
        raise ValueError(draft_claim_sentences.qualifier_gaps_report(
            gaps, draft_claim_sentences.stated_in_reasons(entry, answers, gaps)))
    untried = draft_claim_sentences.unextreme(entry, answers)
    if untried:                 # a universal about the next attempt, not tried on its extreme member
        raise ValueError(draft_claim_sentences.unextreme_report(untried))
    refuse_unbounded(entry, answers)


def refuse_unbounded(entry, answers):
    """Refuse an entry whose summing-up sentences cite a claim with symbols their paragraph does not name and
    are not answered on a "within:" line (draft_claim_sentences.domain_rows)."""
    import json
    import draft_claim_sentences
    registry = Path(__file__).resolve().parents[1] / 'research' / 'claims' / 'index.json'
    if not registry.exists():
        return
    summaries = {c['id']: c['summary'] for c in json.loads(registry.read_text())['claims']}
    outside = draft_claim_sentences.unbounded(entry, answers or '', summaries)
    if outside:
        raise ValueError(draft_claim_sentences.unbounded_report(outside))
    repeated = draft_claim_sentences.repeated_within(entry, answers or '', summaries)
    if repeated:
        raise ValueError('"within:" answers repeated word for word for sentences citing different claims; each '
                         'says how its sentence\'s objects meet its own claim\'s hypotheses:\n'
                         + '\n'.join(f'  {", ".join(keys)}: {text[:120]}' for text, keys in repeated))


PUBLICATION_LINK = re.compile(r'href="(publications/[^"#]+\.tex)')


ONE_FUNCTION = re.compile(r'one function|fixed witness|one fixed', re.I)
UNIFORM_TRIED = re.compile(r'plainest uniform bound', re.I)


def refuse_one_function_plainest(entry):
    """Refuse a Plainest bound paragraph that settles a fixed witness by a bound for one function without naming
    the plainest uniform bound tried on the witness's family (a union over its members, or over the subsets of
    each cell the statement localizes to).  On 17 October 2026 a witness was decided by such a per-cell count,
    which the paragraph never tried; it had said only that the statement's content is its uniformity."""
    for body in re.findall(r'<strong>Plainest bound\.</strong>(.*?)</p>', entry, re.S):
        if ONE_FUNCTION.search(body) and not UNIFORM_TRIED.search(body):
            raise ValueError('a Plainest bound settles a fixed witness by a bound for one function: name also, in '
                             'the words "plainest uniform bound", the uniform bound tried on the witness\'s family '
                             '(a union over its members, or over the subsets of each cell the statement '
                             'localizes to) and what it gives there (AGENTS.md, Nonvacuity)')


def refuse_uncited_publication(entry):
    """Refuse an entry with a sentence that links a publication's source file but cites no registered claim.
    Every publication statement is derived from registered claims, reached through its Lean files
    (tools/publication_claims.py); on 16 October 2026 an entry cited Braun's corollary as unregistered."""
    import draft_claim_sentences
    import publication_claims
    # Any registry prefix, bare: a publication's statements are often audit: or imp: claims, which cited()
    # takes bare only for the kinds that name a statement.
    any_claim = re.compile(r'(?<![\w/#.:-])(?:' + draft_claim_sentences.PREFIXES + r'):[A-Za-z0-9]')
    bare = []
    for _tag, body in draft_claim_sentences.BLOCK.findall(entry):
        for sentence in draft_claim_sentences.sentences(body):
            links = PUBLICATION_LINK.findall(sentence)
            if links and not any_claim.search(strip_tags(sentence)):
                bare.append((links, draft_claim_sentences.text(sentence)))
    if bare:
        lines = []
        for links, sentence in bare:
            lines.append(f'  {sentence[:160]}')
            for (section, label), ids in publication_claims.lookup(links).items():
                lines.append(f'    {section} {label}: {" ".join(ids) or "no claim names its Lean files"}')
        raise ValueError(f'{len(bare)} sentences link a publication file and cite no registered claim; cite the '
                         'claim of the statement used (tools/publication_claims.py SECTION lists them):\n'
                         + '\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('entry', type=Path, nargs='?')
    parser.add_argument('--closures', action='store_true',
                        help='append nothing: count, over the notebook\'s entries, the follow-ups that close a '
                             'listed item and how many quote its listed text')
    parser.add_argument('--answers', type=Path,
                        help='the file answering the entry\'s summing-up sentences (see refuse_unanswered)')
    parser.add_argument('--next', type=Path, dest='next_file')
    parser.add_argument('--notebook')
    parser.add_argument('--stand-unchanged', metavar='REASON',
                        help='why Where we stand needs no change in this cycle; recorded in the entry')
    parser.add_argument('--check', action='store_true',
                        help='append nothing: run the entry checks of this tool and the finisher that apply to a '
                             'draft and list each that fails (for an entry\'s skeleton, at the start of drafting)')
    args = parser.parse_args()
    path = Path(ROOT) / selected(args.notebook)['source']
    if args.closures:
        print(closures_count(path.read_text()))
        return
    nxt = args.next_file.read_text() if args.next_file else None
    if args.check:
        if args.entry is None:
            parser.error('--check needs the draft entry')
        failures = skeleton_check(path.read_text(), args.entry.read_text(), nxt, committed_version(path),
                                  args.stand_unchanged, path)
        for name, error in failures:
            print(f'FAILS {name}: {error}')
        print(f'Skeleton check of {args.entry}: {len(failures)} failing check(s), against '
              f'{path.relative_to(ROOT)} ({path.stat().st_size / 1e6:.1f} MB); nothing was written.')
        sys.exit(1 if failures else 0)
    if args.entry is None:
        if nxt is None:
            parser.error('an entry file is required, or --next alone to replace the Proposed next step')
        try:
            refuse_next_structure(nxt)
            result = replace_next(path.read_text(), nxt)
            living_sections(result)
        except ValueError as err:
            sys.exit(f'notebook-append.py: {err}')
        path.write_text(result)
        print(f'Replaced the Proposed next step in {path.relative_to(ROOT)}')
        return
    try:
        refuse_unanswered(args.entry.read_text(), args.answers.read_text() if args.answers else None)
        refuse_uncited_publication(args.entry.read_text())
        refuse_one_function_plainest(args.entry.read_text())
        refuse_unapplied_matches(path.read_text(), args.entry.read_text(), home=home_of(path))
        closures = refuse_unquoted_closures(path.read_text(), args.entry.read_text())
        refuse_off_route(path.read_text(), args.entry.read_text())
        result = append(path.read_text(), args.entry.read_text(), nxt, committed_version(path),
                        args.stand_unchanged)
        refuse_item_history(result)
    except ValueError as err:
        sys.exit(f'notebook-append.py: {err}')
    path.write_text(result)
    print(f'Appended to {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)')
    for line in closures:
        print(line)
    if nxt and cadence_line(result):
        print(cadence_line(result))
    for ident, text, anchor, follow in (named_items(result, nxt) or []) if nxt else []:
        print(f'The next step names queue item {ident.label}. Check its description against the item\'s own '
              'words:')
        print(f'  Queued text: {text}')
        for claim, summary in registry_matches(f'{text} {follow or ""}',     # attempts are named in follow-ups
                                               home=home_of(path)):
            print(f'  Registry match for its text and latest follow-up, to read before planning: {claim} — {summary}')
        for line in older_claim_lines(result, ident):
            print(line)
        if anchor:
            print(f'  Latest development, #{anchor}. Follow-up: {follow}')
        earlier = [entry for entry in item_history(result, ident) if entry[0] != anchor]
        if earlier:
            print(f'  {len(earlier)} earlier entries developed it; read each before planning on it:')
            for entry_anchor, title in earlier:
                print(f'    #{entry_anchor}: {title[:140]}')
        line = result_files_line(result, ident)
        if line:
            print(line)


if __name__ == '__main__':
    main()
