#!/usr/bin/env python3
"""List each sentence of a draft entry that cites a claim, beside that claim's registered statement.

For the author to read before the reviewer's brief: a sentence that cites a claim for more than the claim
says is seen when the two stand side by side.  A claim declared by the draft itself (data-claims) is not in
the registry yet and is listed as declared; any other identifier the registry does not hold is listed as
unregistered.

Usage: draft_claim_sentences.py DRAFT.html [--registry INDEX.json] [--notebook NOTEBOOK.html] [--width N]
Prints, per cited claim in order of first citation, the registered summary and then each citing sentence
with the heading or paragraph label it stands under.  Ends with the counts: sentences, claims, unregistered.
With --notebook it then lists, per entry the draft links, that entry's title and status line and each
sentence linking it: a sentence about what an earlier entry said is read beside what that entry claims.
It then lists each sentence that denies (no, none, cannot, not) without citing a claim itself, beside the
claims and entries its paragraph cites, and each that describes a cited result's proof, remarks or scope,
beside that result; for both, the passage of the claim's record entry (with --notebook) nearest the
sentence's words is shown. It then lists the sentences outside the mathematics that hold a count, and the sentences outside the
statements and proofs that hold a universal or negative word, each to be read beside its source.
"""
import argparse
import hashlib
import html
import json
import pathlib
import re
import sys
from notebook_math import MATH, protect_math, strip_tags_tight
from notebooks import notebook_file

ROOT = pathlib.Path(__file__).resolve().parents[1]
# Every prefix the registry's identifiers had on 11 October 2026, and historical: until then eleven were listed
# and 352 registered identifiers, imported statements (imp:) among them, were passed over.
PREFIXES = ('lem|thm|prop|cor|conj|obs|ex|def|rem|local|historical|imp|check|audit|third-party|ctx|criterion|q|'
            'note|open|draft|proof')
# Bare, only the kinds that name a statement: "note:", "proof:", "q:" and the like begin ordinary phrases.
BARE_PREFIXES = 'lem|thm|prop|cor|conj|obs|criterion'
# An identifier in code tags, or bare with a hyphen in its name: a notebook that keeps code formatting for
# program names writes its claims bare, and until 12 October 2026 none of them was listed (0 citing sentences
# in every draft of the riemann notebook, 105 entries).
CLAIM = re.compile(r'<code>((?:' + PREFIXES + r'):[A-Za-z0-9-]+)</code>'
                   r'|(?<![\w/#.:-])((?:' + BARE_PREFIXES + r'):[a-z0-9]+(?:-[a-z0-9]+)+)(?![\w-])')


def cited(fragment):
    """The claim identifiers a fragment cites, in order, each once."""
    return list(dict.fromkeys(a or b for a, b in CLAIM.findall(fragment)))
BLOCK = re.compile(r'<(p|li|h3|h4)\b[^>]*>(.*?)</\1>', re.S)
LABEL = re.compile(r'^\s*<(?:strong|em)>([^<]{1,80}?)\.?</(?:strong|em)>')


def text(fragment):
    """Plain text of an HTML fragment, claim identifiers kept, TeX kept."""
    return re.sub(r'\s+', ' ', html.unescape(strip_tags_tight(fragment))).strip()


def sentences(fragment):
    """The fragment's sentences as HTML; a full stop inside TeX or an identifier does not end one."""
    held = []

    def hold(match):
        held.append(match.group(0))
        return f'\x00{len(held) - 1}\x00'

    masked = re.sub(MATH.pattern + r'|<code>.*?</code>', hold, fragment, flags=re.S)
    parts = re.split(r'(?<=[.?!])\s+(?=[A-Z<\x00(])', masked)
    return [re.sub(r'\x00(\d+)\x00', lambda m: held[int(m.group(1))], part) for part in parts]


def citations(draft):
    """(claim id, section label, sentence text) for every sentence of the draft that cites a claim."""
    found, heading = [], ''
    for tag, body in BLOCK.findall(draft):
        if tag in ('h3', 'h4'):
            heading = text(body)
            continue
        label = LABEL.match(body)
        where = label.group(1) if label else heading
        for sentence in sentences(body):
            for claim in cited(sentence):
                found.append((claim, where, text(sentence)))
    return found


# Names of Greek letters as a registered summary writes them in plain text, with an index: the symbols by which
# a statement's hypotheses are told from one another without reading its formulas.
SYMBOL = re.compile(r'\b((?:alpha|beta|gamma|delta|eps|epsilon|zeta|eta|theta|kappa|lam|lambda|mu|nu|xi|rho|sigma|'
                    r'tau|phi|chi|psi|omega)(?:_[A-Za-z0-9*]+|[0-9]+)?)\b', re.I)


# The same symbols as a paragraph's TeX or plain text writes them.
HELD = re.compile(r'(?<![A-Za-z])\\?(?:var)?(?:alpha|beta|gamma|delta|eps|epsilon|zeta|eta|theta|kappa|lam|lambda|mu|'
                  r'nu|xi|rho|sigma|tau|phi|chi|psi|omega)(?:_\{?\\?[A-Za-z0-9*]+\}?|[0-9]+)?(?![A-Za-z])', re.I)
# Paragraphs that name claims without applying them.
NAMING = re.compile(r'^(?:New mathematics|General statement|Verification gate|Process assessment|Review|'
                    r"Reviewer's suggestions.*|Suggestion check|The item's sub-ideas|Sub-ideas)$", re.I)


def bare(name):
    return re.sub(r'[\\_{}\s]|var', '', name).lower().replace('epsilon', 'eps').replace('lambda', 'lam')


def unmentioned(draft, summaries):
    """[(claim id, section label, sentence text, [symbols])] for the sentences citing a registered claim whose
    paragraph names none of some symbols of the claim's registered statement.  On 12 October 2026 a sentence
    applied a statement "with fewer than log tau zeros" where the statement has a constant kappa, and the
    reviewer found it; the listing prints the statement's symbols the paragraph does not hold.  A symbol the
    paragraph writes otherwise is printed too: it is a list to read, not a finding."""
    found, heading = [], ''
    own = set((re.search(r'data-claims="([^"]*)"', draft) or [None, ''])[1].split())
    for tag, body in BLOCK.findall(STATUS_LINE.sub('', draft)):
        if tag in ('h3', 'h4'):
            heading = text(body) if tag == 'h4' else ''
            continue
        label = LABEL.match(body)
        where = label.group(1) if label else heading
        if STATEMENT.match(where) or BOOKKEEPING.match(where) or NAMING.match(where):
            continue
        held = {bare(token) for token in HELD.findall(text(body))}      # whole symbols: "eta" is not in "zeta"
        for sentence in sentences(body):
            if re.match(r'\s*(?:<strong>)?Record(?: search)?\.', sentence):
                break                          # a search's results, to the paragraph's end, are named, not applied
            for claim in cited(sentence):
                if claim not in summaries or claim in own:      # the draft's own claim is stated beside it
                    continue
                symbols = list(dict.fromkeys(m for m in SYMBOL.findall(summaries[claim])))
                missing = [s for s in symbols if bare(s) not in held]
                if missing:
                    found.append((claim, where, text(sentence), missing))
    return found


def unmentioned_report(draft, summaries, width):
    articles = re.findall(r'<article\b.*?</article>', draft, re.S)     # each with its own declared claims
    found = [row for article in (articles if len(articles) > 1 else [draft])
             for row in unmentioned(article, summaries)]
    lines = []
    for claim, where, sentence, missing in found:
        lines.append(f'  [{where}] {sentence if width <= 0 else sentence[:width]}')
        lines.append(f'      {claim}: its statement names, and this paragraph does not: {", ".join(missing[:12])}'
                     + (f' and {len(missing) - 12} more' if len(missing) > 12 else ''))
    return '\n'.join(['Sentences citing a claim whose paragraph does not name some symbols of the claim\'s '
                      'registered statement; ask of each whether a hypothesis that symbol carries is used:']
                     + lines + [f'{len(found)} such sentences.'])


# Paragraphs of mathematics, where a number is part of a statement or an argument and not a count taken from
# somewhere: by their leading label or, without one, the heading they stand under.  Every other paragraph is
# listed: a first form that named the bookkeeping paragraphs missed a count under a heading it did not know.
MATHEMATICS = re.compile(r'^(?:New mathematics|General statement|Setting|Question|Degenerate cases|Nonvacuity|'
                         r'Sources read|.*\b(?:lemma|proposition|theorem|corollary|proof|formula|identity)\b.*)$', re.I)
NUMBER_WORDS = ('two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|'
                'seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|'
                'thousand|dozen')
COUNT = re.compile(r'(?<![\w.-])\d[\d,.]*(?!\w)|\b(?:' + NUMBER_WORDS + r')(?:-\w+)?\b', re.I)
MONTHS = 'January|February|March|April|May|June|July|August|September|October|November|December'
DATE = re.compile(r'\b\d{1,2} (?:' + MONTHS + r')(?: \d{4})?\b|\b(?:' + MONTHS + r') \d{4}\b')


def counts(draft):
    """(section label, sentence text) for every sentence, outside the paragraphs of mathematics, that holds a
    count: a number in digits or words outside TeX, identifiers, links' targets, dates and the paragraph's own
    label.  On 11 October 2026 three counts in
    one draft were quoted from memory and were wrong; listed, each is read beside the saved output it came
    from before the reviewer's brief."""
    found, heading = [], ''
    for tag, body in BLOCK.findall(draft):
        if tag in ('h3', 'h4'):
            heading = text(body) if tag == 'h4' else ''   # a title that names a lemma marks no paragraph
            continue
        label = LABEL.match(body)
        where = label.group(1) if label else heading
        if MATHEMATICS.match(where):
            continue
        for index, sentence in enumerate(sentences(body)):
            # Only the paragraph's own label is left out: bold at the start of a later sentence is its text.
            unlabelled = LABEL.sub('', sentence) if index == 0 and label else sentence
            bare = re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]|<code>.*?</code>', ' ', unlabelled, flags=re.S)
            if COUNT.search(DATE.sub(' ', text(bare))):
                found.append((where, text(sentence)))
    return found


# Paragraphs that are a statement or its proof, where a universal word is the mathematics itself: by their
# leading label or, without one, the heading they stand under.  A summary of the result, its bearing, its
# reading and its structural reason are not among them: those are where a draft says more than it proved.
STATEMENT = re.compile(r'^(?:General statement|Setting|Degenerate cases|Nonvacuity|Sources read|'
                       r'.*\b(?:lemma|proposition|theorem|corollary|proof)\b.*)$', re.I)
# Paragraphs about how the work was done, where such a word is not a conclusion about the mathematics.  A first
# form without this list, and with "only" and "neither" among the words, listed 203 of the 435 sentences of six
# entries, too many to read.
BOOKKEEPING = re.compile(r'^(?:Where we stand|Chosen|Returns|Picked|Best outcome|Architecture test|Earlier entries.*|Owed attempt|'
                         r'Question|Verification gate|Record search|Process assessment|Review|'
                         r'Specification decision|Reviewer\'s suggestions.*|Sub-idea.*|The computation|'
                         r'Against the expectations.*|What was built)$', re.I)
# The paragraphs where a result is summed up, printed first: the others are prose under the entry's own headings.
SUMMARY = re.compile(r'^(?:New mathematics|Goal progress|Structural reason|Follow-up)$', re.I)
TITLE = re.compile(r'<h3>(.*?)</h3>', re.S)
STATUS_LINE = re.compile(r'<p class="entry-meta">(.*?)</p>', re.S)
UNIVERSAL = re.compile(r'\b(?:no|none|nothing|never|cannot|every|all|always|any|whatever)\b', re.I)


def universals(draft):
    """((section label, sentence text) for every sentence, outside the statements, their proofs and the
    paragraphs of bookkeeping, that holds a universal or a negative word; the number of sentences read).  The
    status line is not read here: the report prints it whole.  On 12 October 2026 four drafts of one block
    concluded more than they proved ("no witness of product form...", "it creates none"), each found by a
    reviewer; listed, each such sentence is read beside the statement it rests on before the reviewer's brief.
    The list is long, most sentences on it being sound: it is a reading list and not a finding."""
    found, read, heading = [], 0, ''
    for tag, body in BLOCK.findall(STATUS_LINE.sub('', draft)):
        if tag in ('h3', 'h4'):
            heading = text(body) if tag == 'h4' else ''
            continue
        label = LABEL.match(body)
        where = label.group(1) if label else heading
        if STATEMENT.match(where) or BOOKKEEPING.match(where):
            continue
        for index, sentence in enumerate(sentences(body)):
            unlabelled = LABEL.sub('', sentence) if index == 0 and label else sentence
            bare = re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]|<code>.*?</code>', ' ', unlabelled, flags=re.S)
            read += 1
            if UNIVERSAL.search(text(bare)):
                found.append((where, text(sentence)))
    return found, read


def universals_report(draft, width):
    found, read = universals(draft)
    found = [row for row in found if SUMMARY.match(row[0])] + [row for row in found if not SUMMARY.match(row[0])]
    lines = [f'  [{where}] {sentence if width <= 0 else sentence[:width]}' for where, sentence in found]
    header = article_header(draft)
    head = [] if header is None else [f'  [title] {header[0]}'] + (
        [f'  [status line] {header[1]}'] if header[1] is not None else [])
    return '\n'.join(['The title and the status line, whatever their words, then the sentences outside the '
                      'statements, proofs and bookkeeping that say no, none, cannot, every, all and the like, '
                      'the summing-up paragraphs first; read each beside the statement it rests on:']
                     + head + lines + [f'{len(found)} such sentences of {read} read.'])


# Words by which a sentence says more than a bound or a sufficient condition gives: equality and exactness, a
# quantifier over a parameter, and words that call an unwritten step done.  In one review period of 12 October
# 2026 five sentences of three entries were corrected by reviewers for one of these ("exactly when", "at every
# tilt" under a condition containing the tilt, "do not extend", "immediate", "the reach is the same"); the
# reviewers' records of three entries name four of them, the fifth is from the session's own drafts.
# "for every" and "for all" are left to the listing of universal sentences; "the same" is taken only as a
# predicate ("is the same"), 137 of the first form's 521 lines on one notebook being "the same reviewer" and
# the like, and "at all" is dropped for the same reason (a reviewer's count).
EXACT = re.compile(r'\b(?:exactly|precisely|(?:is|are|was|were|stays?|remains?) the same|'
                   r'(?:do(?:es)?|did|can)(?: ?not|n\'t) extend|cannot extend|no farther|no further|only when|'
                   r'immediate(?:ly)?|clear(?:ly)?|direct(?:ly)?|obviously|at every|if and only if|sharp|tight|'
                   r'equals?)\b', re.I)
DISPLAY = re.compile(r'\\\[(.*?)\\\]', re.S)
INLINE = re.compile(r'\\\((.*?)\\\)', re.S)
RELATION = re.compile(r'\\(?:ge|le|geq|leq|geqslant|leqslant|lesssim|gtrsim|lt|gt|gg|ll)(?![A-Za-z])|[<>]|&lt;|&gt;')


def exactness(draft):
    """[(section label, sentence text, [conditions]), ...] for the sentences, outside the statements, their
    proofs and the paragraphs of bookkeeping, that hold a word of EXACT; the conditions are the displayed
    formulas of the sentence's paragraph, or without any its inline formulas that hold a relation, at most
    three, so that a quantifier or an equality is read beside the condition it was drawn from."""
    found, heading = [], ''
    for tag, body in BLOCK.findall(STATUS_LINE.sub('', draft)):
        if tag in ('h3', 'h4'):
            heading = text(body) if tag == 'h4' else ''
            continue
        label = LABEL.match(body)
        where = label.group(1) if label else heading
        if STATEMENT.match(where) or BOOKKEEPING.match(where):
            continue
        shown = DISPLAY.findall(body) or [m for m in INLINE.findall(body) if RELATION.search(m)]
        conditions = [' '.join(html.unescape(m).split()) for m in shown[:3]]
        for index, sentence in enumerate(sentences(body)):
            unlabelled = LABEL.sub('', sentence) if index == 0 and label else sentence
            bare = re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]|<code>.*?</code>', ' ', unlabelled, flags=re.S)
            if EXACT.search(text(bare)):
                found.append((where, text(sentence), conditions))
    return found


def exactness_report(draft, width):
    found = exactness(draft)
    found = [row for row in found if SUMMARY.match(row[0])] + [row for row in found if not SUMMARY.match(row[0])]
    lines = []
    for where, sentence, conditions in found:
        lines.append(f'  [{where}] {sentence if width <= 0 else sentence[:width]}')
        lines += [f'      beside: {c if width <= 0 else c[:width]}' for c in conditions] or [
            '      beside: no displayed or inline condition in its paragraph']
    return '\n'.join(['Sentences that say exactly, the same, at every, immediate and the like, each beside the '
                      'conditions displayed in its paragraph; ask of each whether the condition is sufficient only, '
                      'contains the quantified parameter, or leaves a step unwritten:']
                     + lines + [f'{len(found)} such sentences.'])


def summing_up(draft):
    """[(key, section label, sentence text)] for the sentences of the summing-up paragraphs (SUMMARY) that either
    listing above prints, each once: the sentences an entry answers before it is appended.  The key is of the
    sentence's text, so a sentence changed after its answer is unanswered again."""
    rows = [(where, sentence) for where, sentence in universals(draft)[0]]
    rows += [(where, sentence) for where, sentence, _ in exactness(draft)]
    found = {}
    for where, sentence in rows:
        if SUMMARY.match(where):
            found.setdefault(hashlib.sha1(sentence.encode()).hexdigest()[:8], (where, sentence))
    return [(key, where, sentence) for key, (where, sentence) in found.items()]


ANSWER = re.compile(r'^([0-9a-f]{8})\b[^\n]*\n[ \t]*rests on:[ \t]*([^\n]*)$', re.M)
ANSWER_WORDS = 4


def answers_template(draft):
    return ''.join(f'{key} [{where}] {sentence}\n  rests on: \n' for key, where, sentence in summing_up(draft))


def unanswered(draft, answers):
    """The rows of summing_up(draft) that the answers text does not answer: a line beginning with the row's key
    followed by a line "rests on:" with at least ANSWER_WORDS words, naming the statement, condition or source
    the sentence rests on."""
    given = {key: answer for key, answer in ANSWER.findall(answers or '')}
    return [row for row in summing_up(draft) if not grounded(given.get(row[0], ''))]


# What an answer points at: a claim, an entry, a saved file, a formula; or "none:" and why the sentence rests on
# nothing of the kind.  Four words of anything passed the first form (a reviewer's test, 12 October 2026).
GROUND = re.compile(r'#entry-|\bresearch/|\\\(|\\\[|^\s*none:', re.I)


def grounded(answer):
    return len(answer.split()) >= ANSWER_WORDS and bool(GROUND.search(answer) or cited(answer))


# Words by which an answer limits what its sentence rests on.  In three of four entries in a row of 12 October
# 2026 a summing-up sentence was wider than its statement, and in those three the answer written for that sentence
# already carried the limit the sentence lacked ("one direction only", "as read and not checked", "omits").
QUALIFIER = re.compile(r'\b(one direction|only|conditional(?:ly)?|given|under|provided|not checked|unverified|'
                       r'unread|omits?|up to|heuristic(?:ally)?|assum\w+|as read)\b', re.I)
STATED = re.compile(r'\bstated in:\s*(.+)$', re.I)
STATED_WORDS = 5


def plain(fragment):
    return re.sub(r'[^a-z0-9 ]+', ' ', text(fragment).lower()).split()


def qualifier_gaps(draft, answers):
    """[(key, section label, sentence, [qualifiers])] for the answered summing-up sentences whose answer limits
    the sentence by a word of QUALIFIER, outside quotation marks, that the sentence does not hold, unless the
    answer ends "stated in:" with at least STATED_WORDS consecutive words of the draft, outside that sentence
    and holding each missing word: the place where the entry itself states the limit.  An answer beginning
    "none:" limits nothing.  A word match: an answer reworded without the word passes, and a reviewer of the
    first form found any five words of the draft accepted (12 October 2026)."""
    given = {key: answer for key, answer in ANSWER.findall(answers or '')}
    words = ' ' + ' '.join(plain(draft)) + ' '
    found = []
    for key, where, sentence in summing_up(draft):
        answer = given.get(key, '')
        if not grounded(answer) or re.match(r'\s*none:', answer, re.I):
            continue
        stated = STATED.search(answer)
        own = STATED.sub('', answer)
        limits = {m.lower() for m in QUALIFIER.findall(re.sub(r'"[^"]*"|“[^”]*”', ' ', own))}
        missing = sorted(limits - {m.lower() for m in QUALIFIER.findall(text(sentence))})
        quote = ' '.join(plain(stated.group(1))) if stated else ''
        # the passage quoted is the entry's, lies outside the sentence asked about, and holds each missing word
        elsewhere = words.replace(f' {" ".join(plain(sentence))} ', ' | ')
        holds = {m.lower() for m in QUALIFIER.findall(quote)}
        if missing and not (len(quote.split()) >= STATED_WORDS and f' {quote} ' in elsewhere
                            and set(missing) <= holds):
            found.append((key, where, sentence, missing))
    return found


def gaps_count(draft, answers, files):
    """For a file of several articles: per article, its answered summing-up sentences and the gaps among them;
    the totals count a key once, since a sentence repeated in many articles has one answer."""
    lines, keys, flagged = [], set(), set()
    for ident, body in re.findall(r'<article id="([^"]+)"(.*?)</article>', draft, re.S):
        open_keys = {key for key, _, _ in unanswered(body, answers)}
        answered = [key for key, _, _ in summing_up(body) if key not in open_keys]
        gaps = qualifier_gaps(body, answers)
        if answered:
            keys.update(answered)
            flagged.update(key for key, _, _, _ in gaps)
            lines.append(f'{len(answered)}\t{len(gaps)}\t{ident}')
            lines += [f'    {key} [{where}] {sentence[:150]} | the answer says: {", ".join(missing)}'
                      for key, where, sentence, missing in gaps]
    lines.append(f'{len(keys)} distinct answered summing-up sentences in {sum(1 for l in lines if not l.startswith(" "))} '
                 f'articles; {len(flagged)} of them have an answer that limits the sentence by a word it lacks '
                 f'(second column), from {files} answers files.')
    return '\n'.join(lines)


def qualifier_gaps_report(gaps):
    lines = [f'{len(gaps)} summing-up sentences whose answer limits them by a word the sentence lacks; put the '
             f'limit into the sentence, or end the answer "stated in:" with {STATED_WORDS} or more consecutive '
             'words of the entry that state it:']
    return '\n'.join(lines + [f'{key} [{where}] {sentence}\n  the answer says: {", ".join(missing)}'
                              for key, where, sentence, missing in gaps])


RUN_LOG = ROOT / 'research' / 'logs' / 'claim-searches.jsonl'


def log_run(draft, path=None):
    """Append this run, with the draft's article id and its number of count sentences, to the ignored log the
    finisher reads, so that an entry whose listing was never printed is reported.  A log that cannot be written
    is not an error.  The log is the registry searches' own and is not created here: in a checkout that has never
    searched, the finisher skips the checks that read it.  A draft without an article is logged as "-", which
    matches no entry."""
    import time
    ident = re.search(r'<article\b[^>]*\bid="([^"]+)"', draft)
    try:
        path = path or RUN_LOG
        if not path.exists():
            return
        with path.open('a') as handle:
            handle.write(json.dumps({'unix_s': time.time(), 'query': 'draft_counts '
                                     + (ident.group(1) if ident else '-') + f' {len(counts(draft))}'}) + '\n')
    except OSError:
        pass


def counts_report(draft, width):
    found = counts(draft)
    lines = [f'  [{where}] {sentence if width <= 0 else sentence[:width]}' for where, sentence in found]
    return '\n'.join(['Sentences outside the mathematics that hold a count; read each beside its saved source:']
                     + lines + [f'{len(found)} sentences with a count.'])


LINK = re.compile(r'<a href="#(entry-[A-Za-z0-9-]+)"')
ARTICLE = re.compile(r'<article id="(entry-[A-Za-z0-9-]+)"[^>]*>(.*?)</article>', re.S)


def article_header(fragment):
    """Read title and status independently, without borrowing from a later article."""
    body = fragment.split('</article>', 1)[0]
    title = TITLE.search(body)
    if title is None:
        return None
    status = STATUS_LINE.search(body, title.end())
    return text(title.group(1)), text(status.group(1)) if status is not None else None


def entry_links(draft):
    """(entry id, section label, sentence text) for every sentence of the draft that links an entry."""
    found, heading = [], ''
    for tag, body in BLOCK.findall(draft):
        if tag in ('h3', 'h4'):
            heading = text(body)
            continue
        label = LABEL.match(body)
        where = label.group(1) if label else heading
        for sentence in sentences(body):
            for entry in dict.fromkeys(LINK.findall(sentence)):
                found.append((entry, where, text(sentence)))
    return found


def entry_report(draft, notebook, width):
    """Per linked entry, its title and status line from the notebook, then each sentence linking it."""
    heads = {entry: header for entry, body in ARTICLE.findall(notebook)
             if (header := article_header(body)) is not None}
    found = entry_links(draft)
    lines = [f'Notebook input: {len(notebook.encode("utf-8"))} bytes; {len(heads)} entry headers.', '']
    missing = set()
    cut = (lambda s: s) if width <= 0 else (lambda s: s[:width])
    for entry in dict.fromkeys(e for e, _, _ in found):
        if entry in heads:
            status = heads[entry][1]
            lines.append(f'{entry}\n  TITLE: {cut(heads[entry][0])}\n  STATUS: '
                         f'{cut(status) if status is not None else "(NO STATUS LINE)"}')
        else:
            lines.append(f'{entry}\n  TITLE: (NOT IN THE NOTEBOOK)')
            missing.add(entry)
        for linked, where, sentence in found:
            if linked == entry:
                lines.append(f'  [{where}] {cut(sentence)}')
        lines.append('')
    entries = len({e for e, _, _ in found})
    lines.append(f'{len(found)} linking sentences, {entries} entries, {len(missing)} not in the notebook.')
    return '\n'.join(lines), missing


NEGATIVE = re.compile(r'\b(?:no|none|nothing|never|cannot|not)\b', re.I)
DESCRIBES = re.compile(r'\b(?:proofs?|remarks?|conditional(?:ly)?|scope|applies|apply|says|states|uses|requires|'
                       r'assumes|covers)\b', re.I)
KEY_STOP = set('which their there these those where while about after before other under every claim entry '
               'lemma theorem corollary proof remark statement since given gives needs holds'.split())
WINDOW = 400        # characters of a linked entry shown around a sentence's key words


def _keys(sentence):
    bare = re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]', ' ', sentence, flags=re.S)
    return {w for w in re.findall(r'[a-z]{5,}', bare.lower()) if w not in KEY_STOP}


def best_window(body, keys, size=WINDOW):
    """The passage of `size` characters of an entry's plain text holding the most of `keys`, by word starts, or
    None when no passage holds any."""
    plain = text(TITLE.sub('', STATUS_LINE.sub('', body)))
    starts = [m.start() for m in re.finditer(r'\b\w', plain)]
    best, where = 0, None
    for start in starts[::8]:
        hits = len(keys & set(re.findall(r'[a-z]{5,}', plain[start:start + size].lower())))
        if hits > best:
            best, where = hits, start
    return None if where is None else plain[where:where + size]


def pairings(draft):
    """[(section label, sentence text, [claim ids], [entry ids]), ...]: each sentence, outside the statements and
    bookkeeping, that either says no, none, cannot or not without citing a claim itself, paired with the claims
    and entries its paragraph cites, or describes what a cited result's proof, remarks or scope say, paired with
    the claims and entries it cites itself.

    In the error cube floor draft of 16 October 2026 a sentence denying a level-wise floor cited no claim and so
    was not set beside the weighted cube statement, cited in its paragraph, that gives one; the same day the goal
    review's draft said a lemma's conditional-use paragraph applied to error kernels, when that paragraph applies
    to the surviving weight.  Both are read beside their sources here."""
    found, heading = [], ''
    for tag, body in BLOCK.findall(STATUS_LINE.sub('', draft)):
        if tag in ('h3', 'h4'):
            heading = text(body) if tag == 'h4' else ''
            continue
        label = LABEL.match(body)
        where = label.group(1) if label else heading
        if STATEMENT.match(where) or BOOKKEEPING.match(where):
            continue
        block_claims, block_entries = cited(body), list(dict.fromkeys(LINK.findall(body)))
        for sentence in sentences(body):
            own_claims, own_entries = cited(sentence), list(dict.fromkeys(LINK.findall(sentence)))
            bare = text(re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]|<code>.*?</code>', ' ', sentence, flags=re.S))
            if NEGATIVE.search(bare) and not own_claims and (block_claims or block_entries):
                found.append((where, text(sentence), block_claims, block_entries))
            elif DESCRIBES.search(bare) and (own_claims or own_entries):
                found.append((where, text(sentence), own_claims, own_entries))
    return found


def pairings_report(draft, claims_list, notebook, width):
    """The listing of pairings: each claim's registered statement and, where its record is an entry of the
    notebook, the passage of that entry nearest the sentence's words; each linked entry's nearest passage."""
    rows = pairings(draft)
    summaries = {c['id']: c.get('summary', '') for c in claims_list}
    records = {c['id']: m.group(1) for c in claims_list if (m := re.search(r'#(entry-[A-Za-z0-9-]+)',
                                                                           c.get('record', '')))}
    bodies = dict(ARTICLE.findall(notebook)) if notebook else {}
    cut = (lambda s: s) if width <= 0 else (lambda s: s[:width])
    lines = ['Sentences that deny without citing, or describe a cited result\'s proof, remarks or scope, beside the '
             'claims and entries their paragraph cites, with the passage of each record nearest the sentence\'s '
             'words; read each sentence against its source:']
    for where, sentence, claims, entries in rows:
        lines.append(f'  [{where}] {cut(sentence)}')
        keys = _keys(sentence)
        shown = set()
        for claim in claims:
            lines.append(f'    {claim}: {cut(summaries.get(claim, "(not in the registry)"))}')
            entry = records.get(claim)
            if entry in bodies and entry not in shown:
                shown.add(entry)
                passage = best_window(bodies[entry], keys)
                if passage:
                    lines.append(f'      its record #{entry}: …{passage}…')
        for entry in entries:
            if entry in bodies and entry not in shown:
                shown.add(entry)
                passage = best_window(bodies[entry], keys)
                lines.append(f'    #{entry}: ' + (f'…{passage}…' if passage else '(none of its words found)'))
    lines.append(f'{len(rows)} such sentences.')
    return '\n'.join(lines)


def report(draft, registry, width):
    summaries = {claim['id']: claim['summary'] for claim in registry['claims']}
    declared = set((re.search(r'data-claims="([^"]*)"', draft) or [None, ''])[1].split())
    found = citations(draft)
    lines, unregistered = [], set()
    for claim in dict.fromkeys(c for c, _, _ in found):
        if claim in summaries:
            statement = summaries[claim]
        elif claim in declared:
            statement = '(declared by this draft; not yet registered)'
        elif f'<code>{claim}</code>' in draft:
            statement = '(NOT IN THE REGISTRY)'
            unregistered.add(claim)
        else:                   # written bare: it may be a phrase and not a claim, so it fails nothing
            statement = '(not in the registry; written without code tags, perhaps not a claim)'
        lines.append(f'{claim}\n  REGISTERED: {statement if width <= 0 else statement[:width]}')
        for cited, where, sentence in found:
            if cited == claim:
                lines.append(f'  [{where}] {sentence if width <= 0 else sentence[:width]}')
        lines.append('')
    claims = len({c for c, _, _ in found})
    unknown = sorted({ident.split(':', 1)[0] for ident in summaries} - set(PREFIXES.split('|')))
    if unknown:                 # a kind of identifier added to the registry since the list was written
        lines.append('WARNING: the registry holds identifiers with prefixes this tool does not look for, so '
                     'sentences citing them are not listed: ' + ', '.join(unknown) + '. Add them to PREFIXES.')
    silent = sorted(c for c in declared - {'none'} if c not in {cited_claim for cited_claim, _, _ in found})
    if silent:                  # a listing that is empty where the draft declares claims has not read them
        lines.append('WARNING: the draft declares claims that no listed sentence cites, so the listing has not '
                     'seen them (written in a form this tool does not read?): ' + ', '.join(silent))
    lines.append(f'{len(found)} citing sentences, {claims} claims, {len(unregistered)} unregistered.')
    return '\n'.join(lines), unregistered


LINE_RUN = re.compile(r'\blines?\s+(\d{1,6}(?:\s*(?:to|through|–|—|--?|,|and)\s*\d{1,6})*)', re.I)
LINE_TOKEN = re.compile(r'\d+|to|through|–|—|--?', re.I)


def line_ranges(plain):
    """[(first, last), ...] named in a sentence: "lines 3, 7 and 10 to 20" gives three; a range written
    backwards is kept as written, for the report to say so."""
    ranges = []
    for run in LINE_RUN.findall(plain):
        tokens = LINE_TOKEN.findall(run)
        index = 0
        while index < len(tokens):
            first = int(tokens[index])
            if index + 2 < len(tokens) and not tokens[index + 1].isdigit():
                ranges.append((first, int(tokens[index + 2])))
                index += 3
            else:
                ranges.append((first, first))
                index += 1
    return ranges


def naming_lines(draft):
    """[(section label, sentence text, [(first, last), ...])] for the sentences that name line numbers
    ("line 412", "lines 1883 to 2214").  On 12 October 2026 a reading's summary gave a passage about one
    variable as the answer to a question about another and wrote "needs" where the lines "use"; each such
    sentence is read beside the lines it names before the brief."""
    found, heading = [], ''
    for tag, body in BLOCK.findall(STATUS_LINE.sub('', draft)):
        if tag in ('h3', 'h4'):
            heading = text(body) if tag == 'h4' else ''
            continue
        label = LABEL.match(body)
        where = label.group(1) if label else heading
        for sentence in sentences(body):
            plain = text(sentence)
            ranges = line_ranges(plain)
            if ranges:
                found.append((where, plain, ranges))
    return found


def unanchored(draft):
    """[(heading, first sentence)] for the body paragraphs of a draft that names lines somewhere, which stand
    under a heading, are not statements, bookkeeping or naming paragraphs, and name no line themselves: what a
    reading says its source does, with nothing to set it beside.  In the reading that prompted the listing
    above, the three paragraphs a reviewer corrected were of this kind and the listing above printed none."""
    if not naming_lines(draft):
        return []
    found, heading = [], ''
    for tag, body in BLOCK.findall(STATUS_LINE.sub('', draft)):
        if tag in ('h3', 'h4'):
            heading = text(body) if tag == 'h4' else ''
            continue
        if tag != 'p' or LABEL.match(body) or not heading:
            continue
        if STATEMENT.match(heading) or BOOKKEEPING.match(heading) or NAMING.match(heading):
            continue
        if not line_ranges(text(body)):
            found.append((heading, text(sentences(body)[0])))
    return found


def naming_lines_report(draft, width, source=None, shown=4):
    """The listing; with the source's lines, each range's first `shown` lines and its last, cut at `width`.
    The source's text is printed for reading and is not for a tracked file when the source is not ours."""
    found = naming_lines(draft)
    lines = []
    for where, sentence, ranges in found:
        lines.append(f'  [{where}] {sentence if width <= 0 else sentence[:width]}')
        for first, last in ranges:
            if first > last:
                lines.append(f'      lines {first}-{last}: WRITTEN BACKWARDS')
                continue
            if source is None:
                continue
            if first < 1 or last > len(source):
                lines.append(f'      lines {first}-{last}: OUTSIDE THE FILE, which has {len(source)} lines')
                continue
            picked = list(range(first, min(last, first + shown - 1) + 1))
            if last > picked[-1]:
                picked += ['...', last] if last > picked[-1] + 1 else [last]
            for n in picked:
                lines.append('      ...' if n == '...' else
                             f'      {n}: {source[n - 1] if width <= 0 else source[n - 1][:width]}')
    loose = unanchored(draft)
    tail = ['Body paragraphs of this draft that name no line, though the draft names lines elsewhere; say of '
            'each which lines it speaks of, or that it is the draft\'s own inference:'] if loose else []
    tail += [f'  [{heading}] {first if width <= 0 else first[:width]}' for heading, first in loose]
    return '\n'.join(['Sentences that name line numbers' + (', each beside the lines it names' if source is not None
                                                           else '; pass --source FILE to print the lines') + ':']
                     + lines + [f'{len(found)} such sentences, {sum(len(r) for _, _, r in found)} ranges.']
                     + tail + ([f'{len(loose)} such paragraphs.'] if loose else []))


def readings(transcript=None, draft=None):
    """Lines to print before a brief, or none: theorem-like statements of TeX and Lean sources that begin,
    unread, just past a range the session read since its last checkpoint (tools/session_reads.py).  A reading
    of 11 October 2026 stopped fifty lines short of the proposition that decided its test, and its reviewer
    found it.  Nothing here fails the listing; an agent without a Claude Code transcript gets no lines."""
    try:
        sys.path.insert(0, str(ROOT / 'tools'))
        import session_reads
        import stand_in_review
        transcript = transcript or stand_in_review.session_transcript(ROOT)
        lines = session_reads.current_lines(pathlib.Path(transcript).read_text(errors='replace').splitlines(),
                                            draft)
    except Exception:
        return []
    return (['', 'Readings since the last checkpoint: statements that begin just past a range of a source that '
             'was read, sources that could not be checked, the unread parts of files the draft names, and its '
             'sentences on what a partly read file says; say in the draft whether '
             'each was read or why it does not matter:'] + lines) if lines else []


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('draft')
    parser.add_argument('--registry', default=str(ROOT / 'research' / 'claims' / 'index.json'))
    parser.add_argument('--width', type=int, default=0, help='cut statements and sentences at N characters')
    parser.add_argument('--notebook', help='also list sentences that link an entry of this notebook file, '
                        'beside the entry\'s title and status line')
    parser.add_argument('--exactness', action='store_true', help='print only the listing of words of exactness; '
                        'for a file of several articles, the count of such sentences in each')
    parser.add_argument('--answers', help='a file answering the summing-up sentences the listings print: written '
                        'as a form if it does not exist, else read, and the unanswered sentences printed')
    parser.add_argument('--summing-up', action='store_true', help='print only, for each article of the file, the '
                        'number of summing-up sentences an entry answers before it is appended')
    parser.add_argument('--source', help='print only the sentences that name line numbers, each beside those lines '
                        'of this file; for a file of several articles without a source, their number in each')
    parser.add_argument('--lines', action='store_true', help='print only the sentences that name line numbers and '
                        'the body paragraphs that name none; for a file of several articles, the two counts in each')
    parser.add_argument('--gaps', nargs='+', metavar='ANSWERS', help='print only, for each article of the file, '
                        'its summing-up sentences answered in these answers files and how many of the answers '
                        'limit their sentence by a word it lacks, with those sentences')
    args = parser.parse_args()
    draft = pathlib.Path(args.draft).read_text()
    if args.gaps:
        answers = '\n'.join(pathlib.Path(name).read_text() for name in args.gaps)
        print(gaps_count(draft, answers, len(args.gaps)))
        return 0
    if args.source or args.lines:
        articles = re.findall(r'<article id="([^"]+)"(.*?)</article>', draft, re.S)
        if len(articles) > 1 and not args.source:
            rows = [(ident, len(naming_lines(body)), len(unanchored(body))) for ident, body in articles]
            print('\n'.join(f'{count}\t{loose}\t{ident}' for ident, count, loose in rows if count))
            print(f'{sum(count for _, count, _ in rows)} such sentences in {sum(1 for _, c, _ in rows if c)} of '
                  f'{len(rows)} articles; {sum(loose for _, _, loose in rows)} body paragraphs naming no line in '
                  'those articles (second column).')
        else:
            source = pathlib.Path(args.source).read_text(errors='replace').splitlines() if args.source else None
            print(naming_lines_report(draft, args.width, source))
        return 0
    if args.summing_up:
        rows = [(ident, len(summing_up(body))) for ident, body in
                re.findall(r'<article id="([^"]+)"(.*?)</article>', draft, re.S)]
        print('\n'.join(f'{count}\t{ident}' for ident, count in rows))
        print(f'{sum(count for _, count in rows)} such sentences in {len(rows)} articles; '
              f'most in one article {max([count for _, count in rows] or [0])}.')
        return 0
    if args.exactness:
        articles = re.findall(r'<article id="([^"]+)".*?</article>', draft, re.S)
        if len(articles) > 1:
            rows = [(ident, len(exactness(body))) for ident, body in
                    re.findall(r'<article id="([^"]+)"(.*?)</article>', draft, re.S)]
            print('\n'.join(f'{count}\t{ident}' for ident, count in rows))
            print(f'{sum(count for _, count in rows)} such sentences in {len(rows)} articles; '
                  f'{sum(1 for _, count in rows if count == 0)} articles with none.')
        else:
            print(exactness_report(draft, args.width))
        return 0
    registry = json.loads(pathlib.Path(args.registry).read_text())
    out, unregistered = report(draft, registry, args.width)
    print(out)
    missing = set()
    notebook_text = notebook_file(args.notebook).read_text() if args.notebook else ''
    if args.notebook:
        linked, missing = entry_report(draft, notebook_text, args.width)
        print('\n' + linked)
    print('\n' + pairings_report(draft, registry['claims'], notebook_text,
                                 args.width))
    print('\n' + counts_report(draft, args.width))
    print('\n' + universals_report(draft, args.width))
    print('\n' + exactness_report(draft, args.width))
    print('\n' + unmentioned_report(draft, {c['id']: c['summary'] for c in registry['claims']}, args.width))
    if naming_lines(draft):
        print('\n' + naming_lines_report(draft, args.width))
    for line in readings(draft=draft):
        print(line)
    log_run(draft)
    open_rows = []
    if args.answers:
        answers = pathlib.Path(args.answers)
        if not answers.exists():
            answers.write_text(answers_template(draft))
            print(f'\nWrote {answers} with {len(summing_up(draft))} summing-up sentences to answer: after each, '
                  'say on its "rests on:" line what it rests on, pointing at a claim identifier, an #entry- '
                  'anchor, a file under research/ or a formula, or "none:" and why.')
        else:
            open_rows = unanswered(draft, answers.read_text())
            print(f'\n{len(open_rows)} of {len(summing_up(draft))} summing-up sentences unanswered in {answers}'
                  + (':' if open_rows else '.'))
            for key, where, sentence in open_rows:
                print(f'{key} [{where}] {sentence}\n  rests on: ')
            gaps = qualifier_gaps(draft, answers.read_text())
            if gaps:
                print(qualifier_gaps_report(gaps))
                open_rows = open_rows + gaps
    return 1 if unregistered or missing or open_rows else 0


if __name__ == '__main__':
    sys.exit(main())
