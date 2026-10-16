"""Audits of the research record's open work: carried leads and open gaps.

Reviews carry Outside leads and Absurd bridges forward as follow-up items, and a later list says
"Continuing: no work on it this cycle" for an item worked on earlier, so the latest list alone
hides which items were never worked. Entries also end with a remaining gap that a later entry may
take up without linking back. A lead or bridge whose test was "Not run" is listed until an entry
claims it in data-lead or data-bridge or a later follow-up item closes it. The audits read the notebook's HTML; the reader
judges each row.
"""
import datetime
import html
import re

from record_search import entries, plain, rank
from notebook_math import strip_tags
from text_stems import stems

# An article of the record, whatever attributes stand before its id: the notebooks write
# <article class="research-entry" id=...> and <article id=... data-kind=...> alike.
ARTICLE = re.compile(r'<article\b([^>]*?)\sid="([^"]+)"([^>]*)>(.*?)</article>', re.S)
ITEM = re.compile(r'<li data-(lead|bridge)="([^"]+)">(.*?)</li>', re.S)
GAP = re.compile(r'<strong>Remaining gap\.</strong>(.*?)</p>', re.S)
NO_WORK = 'no work on it this cycle'


def records(text):
    """(anchor, the tag's other attributes, body) for each Research-record article."""
    for before, anchor, after, body in ARTICLE.findall(text):
        yield anchor, before + ' ' + after, body


def articles(text, kind=None):
    """(anchor, body) for each Research-record article, optionally of one data-kind."""
    for anchor, attrs, body in records(text):
        if kind is None or f'data-kind="{kind}"' in attrs:
            yield anchor, body


def carried_items(text):
    """Items in the latest review's follow-up lists, as (kind, key, name, last work).

    The last work is the most recent follow-up of that item, anywhere in the record, that did
    something; it is empty for an item no follow-up ever worked on."""
    items = ITEM.findall(text)
    if not items:
        return []
    reviews = [body for _, body in articles(text) if ITEM.search(body)]
    if not reviews:
        return []
    latest = {(k, key) for k, key, _ in ITEM.findall(reviews[-1])}
    names, last = {}, {}
    # Work is recorded two ways, read in record order: a review's follow-up item, and an entry
    # tagged data-lead or data-bridge with the item's key, which develops it in a cycle of its own.
    for anchor, attrs, body in records(text):
        for kind, key in claims(attrs):
            last[(kind, key)] = f'Developed in {anchor}.'
        for kind, key, item in ITEM.findall(body):
            name, _, follow = plain(item).partition('Follow-up.')
            names[(kind, key)] = ' '.join(name.split())
            follow = ' '.join(follow.split())
            if follow and NO_WORK not in follow:
                last[(kind, key)] = follow
    return [(k, key, names[(k, key)], last.get((k, key), '')) for k, key in sorted(latest)]


def open_gaps(text, kind=None):
    """Entries whose remaining gap is open and which no later entry links, as (anchor, gap,
    best later match). The match is the later entry the ranked record search puts first for the
    gap's words: work done without a link back shows up there."""
    found = list(articles(text, kind))
    # A link from an entry of any kind closes a gap: a cycle of one kind often does the next step of another.
    every = list(articles(text))
    position = {anchor: i for i, (anchor, _) in enumerate(every)}
    linked_later = {}
    for i, (_, body) in enumerate(every):
        for target in set(re.findall(r'href="#([^"]+)"', body)):
            linked_later[target] = max(linked_later.get(target, -1), i)
    # Parsed and stemmed once, as not_run does: building the later record anew for each gap and searching
    # it took 119 s for the 169 gaps of a notebook of 18 MB.
    parsed = list(entries(text))
    tokens = [stems(body) for _, _, body in parsed]
    place = {anchor: i for i, (anchor, _, _) in enumerate(parsed)}
    rows = []
    for anchor, body in found:
        match = GAP.search(body)
        if not match:
            continue
        gap = ' '.join(html.unescape(strip_tags(match.group(1))).split())
        if gap.startswith('None') or linked_later.get(anchor, -1) > position[anchor]:
            continue
        start = place[anchor] + 1
        hits = rank(parsed[start:], tokens[start:], gap.split()) if start < len(parsed) else []
        rows.append((anchor, gap, hits[0][1] if hits else ''))
    return rows


# Some reviews list their items in <ol>; route reviews (data-kind="review") in <ul>, which the finisher requires.
SECTION = re.compile(r'<h4>(Outside leads|Absurd bridges)</h4>\s*<[ou]l>(.*?)</[ou]l>', re.S)


SECTION_KIND = {'Outside leads': 'lead', 'Absurd bridges': 'bridge'}


def claims(attrs):
    """(kind, key) for each item an entry's data-lead and data-bridge attributes name; an attribute
    may name several keys, separated by spaces, when one entry settles several items."""
    return [(kind, key) for kind, keys in re.findall(r'data-(lead|bridge)="([^"]+)"', attrs)
            for key in keys.split()]


NOUN = re.compile(r'\b[A-Z][A-Za-z]{2,}\b')
# A capitalised word in more entries than this is a common word or a field's name, not a mark of
# one item's subject.
RARE_NOUN = 20


def later_naming(found, start, item_text, frequency, nouns_of, limit=3):
    """Later entries naming the rare proper nouns of the item's text, its name included (a bridge
    run as "Christaller's lead" stayed listed when only nouns after the name counted; notebook
    entry-2026-10-02-christaller-developed), most nouns first: a run that never linked
    back still names what the item named (an adaptive-radiation bridge run on Pocket's shutdown was
    listed as not run until one entry linked it; notebook entry-2026-10-02-radiation-run-earlier)."""
    nouns = {n for n in NOUN.findall(item_text) if 0 < frequency.get(n, 0) <= RARE_NOUN}
    scored = []
    for (anchor, _, _), present in zip(found[start:], nouns_of[start:]):
        hits = len(nouns & present)
        if hits:
            scored.append((-hits, anchor))
    return [anchor for _, anchor in sorted(scored)[:limit]]


MONTHS = ('January February March April May June July August September October November December').split()
DATE = re.compile(r'\b(?:(\d{1,2}) )?(' + '|'.join(MONTHS) + r') (\d{4})\b')


def reason_date(reason):
    """The first date a not-run reason names, as a datetime.date (the month's first day when only a
    month is named), or None: items waiting on a date ("comments are due on 9 October 2026") surface
    on their day instead of being found by reading every reason. A reason may name a date that gates
    nothing; the reader judges."""
    match = DATE.search(reason)
    if not match:
        return None
    day, month, year = match.groups()
    return datetime.date(int(year), MONTHS.index(month) + 1, int(day or 1))


def not_run(text, kind=None):
    """Each review's Outside leads and Absurd bridges whose test was not run, as (key, section,
    name, reason, best later match, later entries naming it). The key is REVIEW:N as follow-up lists
    use it; the match is the later entry the ranked record search puts first for the item's name,
    where its work may be; the naming entries share the item's rare proper nouns."""
    # Parsed and stemmed once: ranking each item against the later record by rebuilding it took 21 s.
    found = list(entries(text))
    tokens = [stems(body) for _, _, body in found]
    position = {anchor: i for i, (anchor, _, _) in enumerate(found)}
    # Each entry's capitalised words, found once: searching every entry per item took 5 s.
    nouns_of = [set(NOUN.findall(body)) for _, _, body in found]
    frequency = {}
    for present in nouns_of:
        for noun in present:
            frequency[noun] = frequency.get(noun, 0) + 1
    # An entry that names the item in data-lead or data-bridge ran or closed it in a cycle of its own.
    claimed = {c for _, attrs, _ in records(text) for c in claims(attrs)}
    # So does a later review's follow-up item that closed it.
    claimed |= {(k, key) for k, key, item in ITEM.findall(text)
                if 'Closed' in plain(item).partition('Follow-up.')[2]}
    rows = []
    for anchor, body in articles(text, kind):
        for section, items in SECTION.findall(body):
            for number, item in enumerate(re.findall(r'<li>(.*?)</li>', items, re.S), 1):
                words = ' '.join(plain(item).split())
                test = words.rpartition('Test.')[2].strip()
                if not test.startswith('Not run') or (SECTION_KIND[section], f'{anchor}:{number}') in claimed:
                    continue
                name = re.split(r'[.:(]', words, maxsplit=1)[0].strip()
                start = position[anchor] + 1
                hits = rank(found[start:], tokens[start:], name.split())
                # A bridge's name opens with its field ("Geography, ..."), which names no subject.
                subject = words.partition(', ')[2] if section == 'Absurd bridges' else words
                rows.append((f'{anchor}:{number}', section, name, test, hits[0][1] if hits else '',
                             later_naming(found, start, subject, frequency, nouns_of)))
    return rows
