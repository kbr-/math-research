"""Ranked search of a notebook's Research-record entries by content words.

A grep for one phrase misses an entry that names the same thing in other words: "rank bound"
misses the entry titled "a lower bound on the dimension of the span".
Entries are ranked by the rarity-weighted number of distinct word stems they share with the
query, so an entry sharing several uncommon words comes first whatever the phrasing. The
command-line front end is tools/search-record.py.
"""
import html
import math
import re

from text_stems import STOP, matches, stems

ARTICLE = re.compile(r'<article\b[^>]*\bid="([^"]+)"[^>]*>(.*?)</article>', re.S)
TITLE = re.compile(r'<h3[^>]*>(.*?)</h3>', re.S)
# A stem found in at most this share of the record's entries counts as distinctive.
RARE_SHARE = 0.03


def plain(fragment):
    return html.unescape(re.sub(r'<[^>]+>', ' ', fragment))


def entries(text):
    """(anchor, title, plain text) for each article in the notebook's HTML."""
    for anchor, body in ARTICLE.findall(text):
        title = TITLE.search(body)
        yield anchor, ' '.join(plain(title.group(1)).split()) if title else '', plain(body)


def search(text, words):
    """Entries sharing at least one query stem, best first, as (score, anchor, title, matched).

    Entries rank first by the rarity-weighted words their title shares with the query, then by
    those their whole text shares: long entries mention many words in passing, while the title
    names what the entry screened. The score returned is the whole-text one."""
    found = list(entries(text))
    return rank(found, [stems(body) for _, _, body in found], words)


def rank(found, tokens, words):
    """search() over entries already parsed, with each entry's stems, so a caller ranking many
    queries against one record parses and stems it once."""
    query = stems(' '.join(words))
    # Each query stem is expanded once into the record's stems it matches, so testing an entry is a
    # set intersection rather than a prefix scan of its stems: the Not run audit's 69 queries took
    # 11.8 s with the scan.
    vocabulary = set().union(*tokens) if tokens else set()
    expanded = {q: {v for v in vocabulary if matches(q, (v,))} for q in query}
    count = {q: sum(1 for s in tokens if s & expanded[q]) for q in query}
    weights = {q: math.log((len(tokens) + 1) / (count[q] + 1)) for q in query}
    ranked = []
    for (anchor, title, _), token_set in zip(found, tokens):
        hits = sorted(q for q in query if token_set & expanded[q])
        if hits:
            title_set = stems(title)
            title_score = sum(weights[q] for q in hits if title_set & expanded[q])
            ranked.append((title_score, sum(weights[q] for q in hits), anchor, title, hits))
    ranked.sort(key=lambda item: (-item[0], -item[1]))
    return [(score, anchor, title, hits) for _, score, anchor, title, hits in ranked]



def phrase_hits(text, phrase):
    """Entries whose text holds the exact phrase, as (anchor, title, count), in record order.

    The phrase matches whatever the case and spacing, so a lead, bridge or name already used is
    found with each place it was used: the check before calling a lead new, which a ranked search
    by stems cannot make, since it also returns entries that share only the words."""
    pattern = re.compile(re.escape(' '.join(phrase.split())), re.I)
    return [(anchor, title, len(found)) for anchor, title, body in entries(text)
            if (found := pattern.findall(' '.join(body.split())))]


def rare_phrase_hits(text, query, most=3):
    """Entries holding a two-word phrase of `query` that at most `most` entries hold, as
    {anchor: (title, [phrases])}. A step proposing "boarding schools and residential family
    centres" as untried missed the one entry that had counted both; a ranked search weighs single
    words, while a rare exact phrase names the object itself."""
    words = re.findall(r"[a-z][a-z'-]+", ' '.join(query.lower().split()))
    pairs = {f'{a} {b}' for a, b in zip(words, words[1:])
             if a not in STOP and b not in STOP and len(a) > 2 and len(b) > 2}
    bodies = [(anchor, title, ' '.join(body.lower().split())) for anchor, title, body in entries(text)]
    found = {}
    for phrase in pairs:
        pattern = re.compile(r'\b' + re.escape(phrase) + r'\b')
        holders = [(anchor, title) for anchor, title, body in bodies if pattern.search(body)]
        if 0 < len(holders) <= most:
            for anchor, title in holders:
                found.setdefault(anchor, (title, []))[1].append(phrase)
    return found


def coverage(text, rows, n=2):
    """For each (name, words) row of a catalogue, the record's best entries and how much of the
    row's query their titles share, as (name, [(anchor, title, shared, total)]). A row whose best
    title shares little of its query is likely unscreened ground; the reader decides."""
    # The record is parsed and stemmed once: per row, a 332-row catalogue took over 170 s.
    found = list(entries(text))
    tokens = [stems(body) for _, _, body in found]
    out = []
    for name, words in rows:
        query = stems(' '.join(words))
        best = []
        for _, anchor, title, _ in rank(found, tokens, words)[:n]:
            title_set = stems(title)
            best.append((anchor, title, sum(1 for q in query if matches(q, title_set)), len(query)))
        out.append((name, best))
    return out

FOLLOW_UPS = re.compile(r'<h4>(?:Lead|Bridge) follow-up</h4>\s*<ul>.*?</ul>', re.S)
QUOTE = re.compile(r'"([^"]+)"|\u201c([^\u201d]+)\u201d')


def quote_hits(text, entry, words=4):
    """Earlier entries holding a quotation of `entry` of at least `words` words, as
    [(quotation, [anchors])], each holder listed whether or not the entry links it. A review offered
    a police force's sharing rule as surfaced by its search, when two entries had quoted the same
    words (notebook entry-2026-10-02-force-routes); a quotation repeated word for word is the
    plainest sign that the record already holds a source, and neither the ranked listing nor the
    lead names compare quotations."""
    own = re.search(r'\bid="([^"]+)"', entry)
    own = own.group(1) if own else None
    # A review's follow-up lists carry earlier items' titles forward by design.
    entry = FOLLOW_UPS.sub(' ', entry)
    quotes = []
    for m in QUOTE.finditer(' '.join(plain(entry).split())):
        quote = (m.group(1) or m.group(2)).strip()
        if len(quote.split()) >= words and quote.lower() not in (q.lower() for q in quotes):
            quotes.append(quote)
    if not quotes:
        return []
    bodies = [(anchor, ' '.join(body.lower().split())) for anchor, _, body in entries(text) if anchor != own]
    hits = []
    for quote in quotes:
        # Quoting the same source, an entry may start or stop one word apart ("that could not ...").
        cut = quote.lower().split()
        forms = {' '.join(cut)} | ({' '.join(cut[1:]), ' '.join(cut[:-1])} if len(cut) > words else set())
        holders = [anchor for anchor, body in bodies if any(f in body for f in forms)]
        if holders:
            hits.append((quote, holders))
    return hits


def nearest_unlinked(text, entry, n=3):
    """The `n` earlier entries closest to `entry` that it does not link, as (anchor, title, score,
    shared stems), closest first.

    Closeness is the summed rarity of the distinctive stems (in at most RARE_SHARE of entries) the
    two texts share. Two entries of 1 October 2026 repeated earlier entries' figures without citing
    them; on that day's last 25 entries the repeated entry ranked first for one and third for the
    other, so the list is a prompt to look, not a verdict."""
    new = next(entries(entry), None)
    if new is None:
        return []
    found = [(a, t, stems(body)) for a, t, body in entries(text) if a != new[0]]
    df = {}
    for _, _, token_set in found:
        for w in token_set:
            df[w] = df.get(w, 0) + 1
    total = len(found)
    rare = {w for w in stems(new[2]) if 0 < df.get(w, 0) <= max(1, RARE_SHARE * total)}
    scored = []
    for anchor, title, token_set in found:
        shared = rare & token_set
        if shared and f'#{anchor}"' not in entry:
            score = sum(math.log(total / df[w]) for w in shared)
            scored.append((anchor, title, score, sorted(shared, key=lambda w: (df[w], w))))
    scored.sort(key=lambda item: -item[2])
    return scored[:n]


ITEM_LISTS = re.compile(r'<h4>(?:Outside leads|Absurd bridges)</h4>\s*<ol>(.*?)</ol>', re.S)
ITEM = re.compile(r'<li\b[^>]*>(.*?)</li>', re.S)
# A run of capitalised words, joined by lower-case particles ("Theory of Constraints").
NAME = re.compile(r"\b[A-Z][\w'’-]+(?:\s+(?:of|the|and|on|for|de|van|von)?\s*[A-Z][\w'’-]+)*")
GENERIC = {'The', 'A', 'An', 'In', 'On', 'For', 'Translate', 'Answers', 'Test', 'Passed', 'Falsified',
           'Not', 'This', 'That', 'Its', 'Our', 'Your', 'When', 'Where', 'What', 'How', 'Which', 'UK',
           'US', 'USD', 'GBP', 'EUR', 'England'}


def lead_names(entry):
    """Proper names in the head of each new Outside lead and Absurd bridge of a review entry: the
    text before its first colon or Answers. The follow-up lists, which repeat earlier reviews'
    items by design, are left out."""
    names = []
    for block in ITEM_LISTS.findall(entry):
        for item in ITEM.findall(block):
            head = re.split(r':|<strong>Answers', item, maxsplit=1)[0]
            # Titles of books and papers ("<em>Innovation and Entrepreneurship</em>", "&quot;A
            # Mathematical Theory of Communication&quot;") are not names; their words flagged unrelated
            # entries in the check's first review.
            head = re.sub(r'<em>.*?</em>|&quot;.*?&quot;|"[^"]*"|“[^”]*”', ' ', head)
            for run in NAME.findall(' '.join(plain(head).split())):
                # "Open Contracting Data Standard on Contracts Finder" names two things; the run
                # and each part between particles are searched.
                parts = re.split(r'\s+(?:of|the|and|on|for|de|van|von)\s+', run)
                for name in [run] + (parts if len(parts) > 1 else []):
                    name = re.sub(r"^(?:The|A|An)\s+|['’]s$", '', name)
                    if name not in GENERIC and (' ' in name or len(name) >= 4) and name not in names:
                        names.append(name)
    return names


def lead_name_hits(text, entry, most=20):
    """For each name lead_names() finds, the earlier entries using it, as [(name, [(anchor,
    title)])], leaving out names more than `most` entries use (a regulator's name, say), which say
    nothing about the lead. A review of 1 October 2026 offered a Contracts Finder search as new
    that a review of 30 September had run, and the phrase search the protocol asks for before
    calling a lead new was not run."""
    new = next(entries(entry), None)
    bodies = [(a, t, ' '.join(body.split())) for a, t, body in entries(text)
              if new is None or a != new[0]]
    out = []
    for name in lead_names(entry):
        pattern = re.compile(r'\b' + re.escape(name) + r'\b', re.I)
        holders = [(a, t) for a, t, body in bodies if pattern.search(body)]
        if 0 < len(holders) <= most:
            out.append((name, holders))
    return out
