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
statements and proofs that hold a universal or negative word, each to be read beside its source, and the
proof sentences that speak of a recorded construction (its compiler, transform, convention, "the lemma's")
without a claim identifier, an entry anchor or a quotation, each to be checked against that record.
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

MIN_WIDTH = 120  # the shortest cut at which a sentence can still be read beside its source

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


# A sentence using a part of the draft's own statement by its letter, outside the paragraphs that state and prove
# it: on 17 October 2026 five such sentences ("by (a) no fixed-kernel sandpile adds one") dropped the statement's
# hypothesis that the one rule is reversible, and none was listed beside the statement, as none names its ID.
OWN_PART = re.compile(r'(?<!its )(?<!that lemma\'s )\b[Pp]arts? \(([a-h])\)|\bby \(([a-h])\)|(?<!\'s )(?<!’s )(?<![\w-])\(([a-h])\) (?:shows|'
                      r'gives|covers|decides|identifies|removes|holds|applies|proves|implies)\b')
DEFINING = ('Statement', 'Proof')


def citations(draft):
    """(claim id, section label, sentence text) for every sentence of the draft that cites a claim, and for every
    sentence outside the Statement and Proof that uses a part of a claim the draft declares by its letter (each
    declared claim, as the letter does not say which)."""
    declared = [c for c in (re.search(r'data-claims="([^"]*)"', draft) or [None, ''])[1].split() if c != 'none']
    found, heading = [], ''
    for tag, body in BLOCK.findall(draft):
        if tag in ('h3', 'h4'):
            heading = text(body)
            continue
        label = LABEL.match(body)
        where = label.group(1) if label else heading
        for sentence in sentences(body):
            claims = cited(sentence)
            for claim in claims:
                found.append((claim, where, text(sentence)))
            # labelled paragraphs only: under a section heading the paragraphs are the statement's own proof steps
            if (declared and label and where not in DEFINING and not where.startswith(('Step', 'Part'))
                    and OWN_PART.search(text(sentence))):
                for claim in declared:
                    if claim not in claims:
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


# Nouns by which a proof sentence speaks of a recorded construction (a compiler's terms, a transform's lines, a
# segment's specialization) rather than of the draft's own objects; and what sources such a sentence: a claim
# identifier, an entry anchor or a quotation. On 16 October 2026 a draft's proof asserted that every compiler
# term carries one placeholder, and a review's argument read prefix products without the absorption terms, both
# written from the agent's picture of the construction; the reviewer found each.
# Only nouns that point outside the draft: "prefix", "translates" and "absorption" were dropped after a count of
# five past entries (dag composite, composite modulus, paid core pencils, exact implication capacity, the
# representation review), where 14 of 20 listings were the proofs' own derivations with those words.
# The narrowed list both dropped and added words, which is why it lists sentences the first did not: it adds
# phrases that refer to a recorded result without naming it ("the lemma's", "as in the lemma", "recorded").
# Dropping "prefix" and "absorption" loses the second 16 October case, a review argument that read a prefix
# product without its absorption terms: such a sentence is listed only if it also names the construction.
# "compiler", "initial segment" and "GP's" come from one goal's vocabulary; the rest are general, and
# --construction-words replaces the list. "specialization", a word of the queued item, was tried and dropped:
# on the representation review both its listings were the proof's own minors.
CONSTRUCTION = re.compile(r'\b(?:compiler|compiled|construction|transform(?:ed|s)?|initial segments?|'
                          r'the record|record\'s|recorded|convention|(?:the|its) (?:theorem|lemma|source)\'s|'
                          r'as in the (?:lemma|theorem|source|record)|GP\'s|its terms)\b',
                          re.I)
# A claim identifier or an entry anchor in the sentence's HTML; a quotation in its text, tags stripped, so an
# attribute's quotes (href="...", class="...") do not count.
SOURCED_HTML = re.compile(r'#entry-|' + CLAIM.pattern)
SOURCED_TEXT = re.compile(r'[“”]|"[^"]{8,}"')


def construction_steps(draft, words=None):
    """((section label, sentence text) for every sentence of a Proof paragraph that speaks of a recorded
    construction (CONSTRUCTION) without a claim identifier, an entry anchor or a quotation in it; the number of
    proof sentences read). A reading list: each such step is read against the construction's record, and quoted
    with its anchor, before the review (AGENTS.md)."""
    found, read = [], 0
    for tag, body in BLOCK.findall(STATUS_LINE.sub('', draft)):
        label = LABEL.match(body)
        if tag != 'p' or not label or not label.group(1).startswith('Proof'):
            continue
        for index, sentence in enumerate(sentences(body)):
            unlabelled = LABEL.sub('', sentence) if index == 0 else sentence
            bare = re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]', ' ', unlabelled, flags=re.S)
            read += 1
            if ((words or CONSTRUCTION).search(text(bare)) and not SOURCED_HTML.search(sentence)
                    and not SOURCED_TEXT.search(text(sentence))):
                found.append((label.group(1), text(unlabelled)))
    return found, read


def construction_report(draft, width, words=None):
    found, read = construction_steps(draft, words)
    lines = [f'  [{where}] {sentence if width <= 0 else sentence[:width]}' for where, sentence in found]
    return '\n'.join(['Proof sentences that speak of a recorded construction (its compiler, transform, segment, '
                      'translations, prefixes) without a claim identifier, an entry anchor or a quotation; check '
                      'each against the construction\'s record and quote it with its anchor (AGENTS.md):']
                     + lines + [f'{len(found)} such sentences of {read} proof sentences read.'])


# A proof step that makes a term vanish by a factor's value, and the words that say where the factor stands
# (16 October 2026: a factor inside a commutator certificate was used as if it stood outside).
VANISH = re.compile(r'\b(?:vanish(?:es|ing)?|(?:is|are|becomes?) zero|contributes? (?:zero|nothing)|translates? '
                    r'to (?:one|zero)|has the factor|kills? the term|drops? out)\b', re.I)
# Only a step that names a factor or multiplier: without it, 72 proof sentences of 235 entries from 10 October 2026
# were listed, mostly products or images vanishing with no factor involved.
FACTOR = re.compile(r'\b(?:factors?|multipliers?|multiplied)\b', re.I)
# General words of a factor's place; a notebook adds its own (its brackets, certificates) through the
# data-listing-words attribute (listing_words). Common words such as "left", "before" or "around" are not
# here: anywhere in a sentence they silenced the listing.
POSITION_WORDS = r'inside|outside|within|brackets?|sits|stands|outer|inner|placed'
# General restrictions a Hypotheses paragraph can copy from a source; a notebook adds the words of its own
# families and ranges through data-listing-words, so this tool holds no goal's vocabulary.
RESTRICTION_WORDS = (r'characteristic(?: two| three| zero| 2| 3| p)?|prime field|odd|acyclic|regular|bipartite|'
                     r'connected|simple graphs?|multigraphs?|monotone|multilinear')
# A proof sentence that names a restriction to deny it does not count as using it.
DENIED = re.compile(r'\b(?:not (?:used|needed|required)|unused|without|need not)\b', re.I)


def listing_words(notebook_text):
    """{kind: words} from the notebook's data-listing-words="restriction=a|b; position=c|d" attribute, the words a
    notebook adds to these listings for its own objects."""
    found = re.search(r'\bdata-listing-words="([^"]*)"', notebook_text or '')
    words = {}
    for part in (found.group(1).split(';') if found else []):
        kind, _, value = part.partition('=')
        if value.strip():
            words[kind.strip()] = value.strip()
    return words


def word_pattern(general, extra=None):
    return re.compile(r'\b(?:' + general + ('|' + extra if extra else '') + r')\b', re.I)


def proof_sentences(draft):
    """(label, sentence HTML, plain text without its mathematics) for every sentence of a Proof paragraph."""
    for tag, body in BLOCK.findall(STATUS_LINE.sub('', draft)):
        label = LABEL.match(body)
        if tag != 'p' or not label or not label.group(1).startswith('Proof'):
            continue
        for index, sentence in enumerate(sentences(body)):
            unlabelled = LABEL.sub('', sentence) if index == 0 else sentence
            yield label.group(1), unlabelled, text(re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]', ' ', unlabelled, flags=re.S))


def vanishing_steps(draft, words=None):
    """(label, sentence) for each proof sentence that makes a term vanish by a factor's value and does not say
    where the factor stands relative to the brackets or certificates around it (AGENTS.md: quoted from the
    construction's record). A reading list, not a verdict; `words` are the notebook's (listing_words)."""
    position = word_pattern(POSITION_WORDS, (words or {}).get('position'))
    return [(label, text(sentence)) for label, sentence, plain_words in proof_sentences(draft)
            if VANISH.search(plain_words) and FACTOR.search(plain_words) and not position.search(plain_words)]


def vanishing_report(draft, width, words=None):
    found = vanishing_steps(draft, words)
    lines = [f'  [{where}] {s if width <= 0 else s[:width]}' for where, s in found]
    return '\n'.join(['Proof sentences that make a term vanish by a factor\'s value without saying where the factor '
                      'stands (inside or outside a bracket, a certificate); quote its place from the '
                      'construction\'s record (AGENTS.md):'] + lines + [f'{len(found)} such sentences.'])


def hypothesis_restrictions(draft, words=None):
    """(restriction, sentence) for each restriction the Hypotheses paragraph names that no proof sentence names,
    other than to deny it: a restriction copied from a source and used by no step (16 October 2026:
    characteristic two stated where the proof needed only 0/1-valued definitions). A reading list: a proof may use
    a restriction in other words; `words` are the notebook's (listing_words)."""
    restriction = word_pattern(RESTRICTION_WORDS, (words or {}).get('restriction'))
    proof = ' '.join(plain_words for _, _, plain_words in proof_sentences(draft)
                     if not DENIED.search(plain_words)).lower()
    found = []
    for tag, body in BLOCK.findall(STATUS_LINE.sub('', draft)):
        label = LABEL.match(body)
        if tag != 'p' or not label or not label.group(1).startswith('Hypotheses'):
            continue
        for sentence in sentences(body):
            plain_words = text(re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]', ' ', sentence, flags=re.S))
            for m in dict.fromkeys(r.group(0).lower() for r in restriction.finditer(plain_words)):
                if m not in proof:
                    found.append((m, text(sentence)))
    return found


def hypothesis_report(draft, width, words=None):
    found = hypothesis_restrictions(draft, words)
    lines = [f'  "{r}": {s if width <= 0 else s[:width]}' for r, s in found]
    return '\n'.join(['Restrictions the Hypotheses paragraph names that no proof sentence names; read each off the '
                      'proof, and drop or justify one no step uses (AGENTS.md):'] + lines
                     + [f'{len(found)} such restrictions.'])


HYPOTHESIS_ITEM = re.compile(r'(?:</strong>|[.;])\s*\\\(((?:(?!\\\)).)+?)\\\):')   # one math span opening an item
INEQUALITY = re.compile(r'\\le|\\ge|\\leq|\\geq|<|>|&lt;|&gt;')


def step_forms(draft):
    """(hypothesis, [inequalities its step displays]) for each item "\\(H\\): step" of a Hypotheses, each with its
    step paragraph whose step displays inequalities none of which is H itself: the step may need only the form it
    displays (17 October 2026: "\\(K+\\tau\\le D\\): the cut has support at most \\(2K+\\tau\\le2D\\)", a hypothesis
    copied from the template, while its own step showed the weaker form the lemma needed). A reading list."""
    found = []
    squash = lambda tex: re.sub(r'\s+', '', tex)
    for tag, body in BLOCK.findall(STATUS_LINE.sub('', draft)):
        label = LABEL.match(body)
        if tag != 'p' or not label or not label.group(1).startswith('Hypotheses, each with its step'):
            continue
        items = list(HYPOTHESIS_ITEM.finditer(body))
        for item, following in zip(items, items[1:] + [None]):
            hypothesis = item.group(1)
            if not INEQUALITY.search(hypothesis):
                continue
            step = body[item.end():following.start() if following else len(body)]
            shown = [tex for tex in re.findall(r'\\\((.+?)\\\)', step, re.S) if INEQUALITY.search(tex)]
            if shown and squash(hypothesis) not in {squash(tex) for tex in shown}:
                found.append((text('\\(' + hypothesis + '\\)'), [text('\\(' + tex + '\\)') for tex in shown]))
    return found


def step_forms_report(draft, width):
    found = step_forms(draft)
    lines = [f'  {h}: its step displays ' + '; '.join(forms) for h, forms in found]
    return '\n'.join(['Hypotheses whose step displays other inequalities than the hypothesis; if the step needs only '
                      'a displayed form, state that form, the weakest the proof allows (AGENTS.md):']
                     + [line if width <= 0 else line[:width] for line in lines]
                     + [f'{len(found)} such hypotheses.'])


# A search the draft reports by its words, "QUERY" returned ...: on 17 October 2026 a review's draft reported two
# searches and their results before either was run; the finisher's search check fires only at the end.
REPORTED_SEARCH = re.compile(r'["“]([^"”]{12,400})["”]\s*(?:returned|found|gave)\b')
SEARCH_WINDOW_S = 12 * 3600


def search_words(query):
    """A query's words, without the tool's options (-n 5) and in lower case."""
    return [w for w in re.sub(r'(?:^|\s)-n\s+\d+', ' ', query).lower().split() if not w.startswith('-')]


def unrun_searches(draft, logged):
    """The searches the draft says returned something whose words no logged query (`logged`, query strings) has."""
    run = {tuple(search_words(q)) for q in logged}
    return [m.group(1) for m in REPORTED_SEARCH.finditer(text(draft))
            if tuple(search_words(m.group(1))) not in run]


def logged_queries(root, now=None):
    """The queries tools/search-claims.py logged in the last SEARCH_WINDOW_S seconds."""
    path = pathlib.Path(root) / 'research/logs/claim-searches.jsonl'
    now = now or __import__('time').time()
    found = []
    for line in path.read_text().splitlines() if path.exists() else ():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get('unix_s', 0) >= now - SEARCH_WINDOW_S:
            found.append(row.get('query', ''))
    return found


def unrun_searches_report(draft, logged, width):
    found = unrun_searches(draft, logged)
    lines = [f'  "{q}"' for q in found]
    return '\n'.join(['Searches the draft reports as returning results that tools/search-claims.py has not logged in '
                      'the last twelve hours; run each, then write what it returned (AGENTS.md):']
                     + [line if width <= 0 else line[:width] for line in lines]
                     + [f'{len(found)} such searches, of {len(logged)} logged queries compared.'])


def unread_named_claims(draft, root, now=None):
    """The claims the draft's Record search, Record comparison, Record, Own statements or Bearing paragraphs
    name whose statements no reading tool printed in the last SEARCH_WINDOW_S seconds, the draft's declared
    claims exempt: the finisher's validate_named_claims_read, run at the drafting stage.  On 17 October 2026 a
    review's Record search named six claims from search listings, whose summaries are shortened, and only the
    finisher, after the review, found that their statements had not been read; two descriptions were wrong."""
    import claim_reads
    now = now or __import__('time').time()
    declared = re.search(r'\bdata-claims="([^"]*)"', draft)
    return claim_reads.unread(draft, claim_reads.read_since(root, now - SEARCH_WINDOW_S),
                              declared.group(1).split() if declared else ())


def unread_named_claims_report(missing, width):
    lines = [f'  {ident}' for ident in missing]
    return '\n'.join(['Claims a Record search, Record comparison, Record, Own statements or Bearing paragraph names '
                      'whose statements no reading tool printed in the last twelve hours; read each with '
                      'tools/notebook-excerpt.py --claims, and write the paragraph from the statement (the '
                      'finisher refuses them; AGENTS.md):']
                     + [line if width <= 0 else line[:width] for line in lines]
                     + [f'{len(missing)} such claims.'])


PART = r'(?:Sections?|Theorems?|Lemmas?|Corollar(?:y|ies)|Propositions?|Definitions?|Appendix|Remarks?)'
NOT_READ = re.compile(r'(' + PART + r'\s+[\dA-Z][\w.]*(?:(?:\s*(?:,|and|to|–|-)\s*)[\dA-Z][\w.]*)*)'
                      r'(?:[^.;]|(?<=\d)\.(?=\d)){0,60}?\b(?:not read|unread|was not read|were not read)\b'
                      r'|\b(?:not read|unread)\b[^.;]{0,20}?(' + PART + r'\s+[\dA-Z][\w.]*)', re.I)


def unread_in(source, text_of):
    """(source, kind, number) for each numbered part `text_of` says was not read; a part whose proof alone was
    not read ("the proof of Proposition 24 was not read") is read for its statement and is skipped; "Sections
    2 to 4" gives 2, 3 and 4."""
    found = []
    for m in NOT_READ.finditer(text_of):
        if re.search(r'\bproofs? of\s*$', text_of[max(0, m.start() - 12):m.start()], re.I):
            continue
        whole = m.group(1) or m.group(2)
        kind = re.sub(r'(?:ies|s)$', lambda e: 'y' if e.group(0) == 'ies' else '', whole.split()[0]).lower()
        rest = whole[len(whole.split()[0]):]
        numbers = re.findall(r'[\dA-Z][\w.]*', rest)
        span = re.search(r'\b(\d+)\s*(?:to|–|-)\s*(\d+)\b', rest)
        if span and int(span.group(2)) - int(span.group(1)) < 20:
            numbers += [str(n) for n in range(int(span.group(1)), int(span.group(2)) + 1)]
        found += [(source, kind, n.rstrip('.')) for n in dict.fromkeys(numbers)]
    return found


def unread_parts(registry, ids, spec=None):
    """(source, kind, number) for each numbered part of a source that the assessment of a cited import, or any
    text of the draft's own spec, says was not read."""
    claims = {c['id']: c for c in registry['claims']}
    found = []
    for ident in ids:
        found += unread_in(ident, claims.get(ident, {}).get('assessment', ''))
    for claim in (spec or {}).get('claims', []):
        found += unread_in(f"the spec's {claim.get('id', '?')}",
                           ' '.join(str(v) for v in claim.values() if isinstance(v, str)))
    return found


def unread_citations(draft, registry, spec=None):
    """(source, part, sentence) for each draft sentence citing a numbered part of a source that a registered
    import cited by the draft, or the draft's own spec (--spec), says was not read (16 October 2026: a section
    cited that its own spec listed as not read). Parts are matched by kind and number, not by source, so a part
    of another source with the same number is listed too: a reading list."""
    ids = {i for i in CLAIM_ID.findall(text(draft)) if i.startswith('imp:')}
    parts = unread_parts(registry, ids, spec)
    found = []
    for _tag, body in BLOCK.findall(STATUS_LINE.sub('', draft)):
        for sentence in sentences(body):
            plain_text = text(sentence)
            for ident, kind, number in parts:
                if re.search(r'\b' + PART + r'\s+' + re.escape(number) + r'(?![\w.])', plain_text, re.I) and \
                        re.search(r'\b' + kind[:6], plain_text, re.I):
                    found.append((ident, f'{kind} {number}', plain_text))
    return found


def unread_report(draft, registry, width, spec=None):
    found = unread_citations(draft, registry, spec)
    lines = [f'  {ident}, {part} (not read): {s if width <= 0 else s[:width]}' for ident, part, s in found]
    return '\n'.join(['Sentences citing a part of a source that its registered import says was not read; read it '
                      'first or cite only what was read (AGENTS.md):'] + lines + [f'{len(found)} such sentences.'])


# The record's own form is "<strong>Statement.</strong> Corollary (...)"; 17 October 2026: such a draft was
# listed as having no statement, so its summaries were compared with nothing.
OWN_STATEMENT = re.compile(r'^(?:Lemma|Theorem|Proposition|Corollary|Statement)\b')
OWN_SUMMARY = re.compile(r'^(?:New mathematics|Goal progress|Architecture test)$')
LEDGER = re.compile(r'<h4\b[^>]*ledger[^>]*>.*?</h4>\s*<ul>(.*?)</ul>', re.S | re.I)


def own_summaries(draft):
    """([(label, text)] for each statement the draft proves itself, a paragraph opening Lemma, Theorem, Proposition
    or Corollary; [(where, sentence)] for each sentence that summarizes the draft's results: the title, the
    New mathematics, Goal progress (with its Bearing) and Architecture test paragraphs, and the items of a ledger).
    16 October 2026: a draft's ledger, Bearing, Architecture test and commit message said more than its lemma
    (a matched image where the lemma gave that image minus a sum, without the lemma's two qualifiers), having
    been written while the statement was still settling."""
    statements = [(label.group(1), text(body)) for tag, body in BLOCK.findall(draft)
                  if tag == 'p' and (label := LABEL.match(body)) and OWN_STATEMENT.match(label.group(1))]
    if not statements:
        return [], []
    summaries = [('title', text(title)) for title in TITLE.findall(draft)]
    for tag, body in BLOCK.findall(STATUS_LINE.sub('', draft)):
        label = LABEL.match(body)
        if tag == 'p' and label and OWN_SUMMARY.match(label.group(1)):
            summaries += [(label.group(1), text(LABEL.sub('', s) if i == 0 else s))
                          for i, s in enumerate(sentences(body))]
    for items in LEDGER.findall(draft):
        summaries += [('ledger', text(body)) for tag, body in BLOCK.findall(items) if tag == 'li']
    return statements, summaries


def own_summaries_report(draft, width):
    statements, summaries = own_summaries(draft)
    if not statements:
        return 'No statement of the draft\'s own (Lemma, Theorem, Proposition, Corollary paragraph) to set summaries beside.'
    cut = (lambda s: s) if width <= 0 else (lambda s: s[:width])
    return '\n'.join(['The draft\'s own statements, then each sentence that summarizes them: a summary says no more '
                      'than the statement and keeps its hypotheses and qualifiers (AGENTS.md):']
                     + [f'  STATEMENT [{label}] {body}' for label, body in statements]
                     + [f'  [{where}] {cut(sentence)}' for where, sentence in summaries]
                     + [f'{len(summaries)} summary sentences beside {len(statements)} statements.'])


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
# Words by which a sentence gives a decision its reason (17 October 2026: an attempt was dropped as "the same
# question in a sharper form" and a split as "decided by this entry's statements", neither shown; the reviewer
# found both).  Read also in bookkeeping paragraphs, where such decisions are written.
DECISION = re.compile(r'\b(?:decided by|the same question|sharper form|supersed(?:es|ed)|implies|'
                      r'(?:the )?conjectured order|the goal\'s order)\b', re.I)
# "conjectured order" from 17 October 2026: a Bearing said single-level functions meet the goal "at the conjectured
# order" while its constant, about 1.31 L, exceeded the goal's L/2 unless a cellwise sum was small.
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
        if STATEMENT.match(where):
            continue
        pattern = DECISION if BOOKKEEPING.match(where) else re.compile(EXACT.pattern + '|' + DECISION.pattern, re.I)
        shown = DISPLAY.findall(body) or [m for m in INLINE.findall(body) if RELATION.search(m)]
        conditions = [' '.join(html.unescape(m).split()) for m in shown[:3]]
        for index, sentence in enumerate(sentences(body)):
            unlabelled = LABEL.sub('', sentence) if index == 0 and label else sentence
            bare = re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]|<code>.*?</code>', ' ', unlabelled, flags=re.S)
            if pattern.search(text(bare)):
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


# Words by which a sentence outside the mathematics compares two orders.  17 October 2026: an Owed attempt
# dropped an attempt because a bound was "below its heuristic target", when the bound was the larger of the two;
# the reviewer found the comparison read the wrong way round.
COMPARE = re.compile(r'\b(?:below|above|beats?|beat by|smaller|larger|exceeds?|less than|more than|'
                     r'better than|worse than|stronger than|weaker than|within|negligible|keeps?(?: \w+)? small|'
                     r'not improved|outside the attempt)\b', re.I)
# The last four from 17 October 2026: a case was dismissed twice in a row, as kept small by the cost and as
# not improved, each wrong at the instance's parameters, before a third version computed both sides.


def comparisons(draft):
    """[(section label, sentence text, [conditions])] for the sentences, outside the statements, their proofs
    and bookkeeping, that compare two orders by a word of COMPARE, with the formulas of their paragraph as in
    exactness(), so that both sides are evaluated at the instance before the sentence stands."""
    found, heading = [], ''
    for tag, body in BLOCK.findall(STATUS_LINE.sub('', draft)):
        if tag in ('h3', 'h4'):
            heading = text(body) if tag == 'h4' else ''
            continue
        label = LABEL.match(body)
        where = label.group(1) if label else heading
        # Bookkeeping paragraphs are read too: the exposing sentence was in an Owed attempt, where a comparison
        # decided what was dropped, as one in an Architecture test decides its verdict.
        if STATEMENT.match(where) or where.lower() == 'statement':
            continue
        shown = DISPLAY.findall(body) or [m for m in INLINE.findall(body) if RELATION.search(m)]
        conditions = [' '.join(html.unescape(m).split()) for m in shown[:3]]
        for index, sentence in enumerate(sentences(body)):
            unlabelled = LABEL.sub('', sentence) if index == 0 and label else sentence
            bare = re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]|<code>.*?</code>', ' ', unlabelled, flags=re.S)
            if COMPARE.search(text(bare)) and INLINE.search(unlabelled):
                found.append((where, text(sentence), conditions))
    return found


def comparisons_report(draft, width):
    found = comparisons(draft)
    lines = []
    for where, sentence, conditions in found:
        lines.append(f'  [{where}] {sentence if width <= 0 else sentence[:width]}')
        lines += [f'      beside: {c if width <= 0 else c[:width]}' for c in conditions]
    return '\n'.join(['Sentences that compare two orders (below, above, beats, smaller, within and the like); '
                      'evaluate both sides at the instance, with numbers or exponents written out, and say which is '
                      'larger before the sentence stands:'] + lines + [f'{len(found)} such sentences.'])


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


def answers_template(draft, summaries=None):
    domain = {row[0]: row for row in domain_rows(draft, summaries or {})}
    extreme = {row[0] for row in extreme_rows(draft)}
    hypothesis = {row[0] for row in hypothesis_rows(draft)}
    form = ''.join(f'{key} [{where}] {sentence}\n  rests on: \n' + ('  within: \n' if key in domain else '')
                   + ('  extreme: \n' if key in extreme else '') + ('  hypotheses: \n' if key in hypothesis else '')
                   for key, where, sentence in summing_up(draft))
    asked = {key for key, _, _ in summing_up(draft)}
    form += ''.join(f'{key} [{where}] {sentence}\n  within: \n'
                    for key, (_, where, sentence, _, _) in domain.items() if key not in asked)
    asked |= set(domain)
    return form + ''.join(f'{key} [{where}] {sentence}\n  hypotheses: \n'
                          for key, where, sentence in hypothesis_rows(draft) if key not in asked)


# A summing-up sentence that cites a registered claim while its paragraph leaves some of the claim's symbols
# unnamed is answered also on a line "within:": how the sentence's objects meet that claim's hypotheses.  On
# 17 October 2026 a Bearing applied a conversion lemma to a family of grid functions that are not in the lemma's
# image; the listing had printed the sentence among those naming fewer symbols than the claim, and its "rests
# on:" answer, the lemma, was true.
WITHIN = re.compile(r'^([0-9a-f]{8})\b[^\n]*\n(?:[ \t]*rests on:[^\n]*\n)?[ \t]*within:[ \t]*([^\n]*)$', re.M)


# A Follow-up sentence with a universal word ("every", "all", "only", "no") states a property of the next
# attempt's construction: it is answered also on a line "extreme:", the extreme member of the construction it was
# tried on (layers that coincide, a member that covers another, the largest family).  On 17 October 2026 two such
# sentences ("lie on every boundary", "only in the family of all unions") were answered by their sources and were
# false at an extreme member.
EXTREME = re.compile(r'^([0-9a-f]{8})\b[^\n]*\n(?:[ \t]*(?:rests on|within):[^\n]*\n)*[ \t]*extreme:[ \t]*([^\n]*)$',
                     re.M)


def extreme_rows(draft):
    """[(key, section label, sentence)] for the summing-up sentences of Follow-up paragraphs with a universal
    word."""
    return [row for row in summing_up(draft) if row[1].lower() == 'follow-up' and UNIVERSAL.search(text(row[2]))]


def unextreme(draft, answers):
    """The rows of extreme_rows(draft) whose answer has no "extreme:" line of at least ANSWER_WORDS words."""
    given = {key: answer for key, answer in EXTREME.findall(answers or '')}
    return [row for row in extreme_rows(draft) if len(given.get(row[0], '').split()) < ANSWER_WORDS]


def unextreme_report(rows):
    return '\n'.join([f'{len(rows)} Follow-up sentences state a universal about the next attempt and have no '
                      '"extreme:" answer: name the extreme member of the construction the sentence was tried on '
                      '(members that coincide, one that covers another, the largest family) and what it gave:']
                     + [f'{key} [{where}] {sentence[:160]}\n  extreme: ' for key, where, sentence in rows])


# A sentence that evaluates a cited claim at an instance (a Falsification attempt, an Instance check, a Power or
# Trivial cases paragraph, a Nonvacuity) is answered on a line "hypotheses:", the claim's hypotheses checked at
# that instance with its numbers.  On 17 October 2026 a review evaluated four lemmas at N = 10^12, y = 763, while
# each needs y >= 2e^16 (and a grid side its instance did not have), copying the previous review's instance; the
# listing had set each sentence beside the lemma's statement.
HYPOTHESES = re.compile(r'^([0-9a-f]{8})\b[^\n]*\n(?:[ \t]*(?:rests on|within|extreme):[^\n]*\n)*'
                        r'[ \t]*hypotheses:[ \t]*([^\n]*)$', re.M)
INSTANCE_LABELS = re.compile(r'^(?:Falsification attempt|Instance check|Power|Trivial cases|Nonvacuity)$', re.I)


def hypothesis_rows(draft):
    """[(key, section label, sentence)] for the sentences under an instance label that cite a claim, each once.
    The label is the latest bold label before the sentence within its paragraph: a review's Instance check, Power
    and Trivial cases stand inside its Decisive test paragraph (the exposing case of 17 October 2026 did)."""
    found = {}
    for tag, body in BLOCK.findall(draft):
        if tag in ('h3', 'h4'):
            continue
        where = ''
        for sentence in sentences(body):
            inline = LABEL.match(sentence)
            if inline:
                where = inline.group(1)
            if INSTANCE_LABELS.match(where) and cited(sentence):
                plain = text(sentence)
                found.setdefault(hashlib.sha1(plain.encode()).hexdigest()[:8], (where, plain))
    return [(key, where, sentence) for key, (where, sentence) in found.items()]


def unchecked_hypotheses(draft, answers):
    """The rows of hypothesis_rows(draft) whose answer has no "hypotheses:" line of at least ANSWER_WORDS words."""
    given = {key: answer for key, answer in HYPOTHESES.findall(answers or '')}
    return [row for row in hypothesis_rows(draft) if len(given.get(row[0], '').split()) < ANSWER_WORDS]


def unchecked_hypotheses_report(rows):
    return '\n'.join([f'{len(rows)} sentences evaluate a cited claim at an instance and have no "hypotheses:" '
                      'answer: name each hypothesis of the claim (levels, grid sides, ranges) and its value at the '
                      'instance, with numbers:']
                     + [f'{key} [{where}] {sentence[:160]}\n  hypotheses: ' for key, where, sentence in rows])


def domain_rows(draft, summaries):
    """[(key, section label, sentence, claim, [symbols])] for the summing-up sentences (SUMMARY paragraphs) that
    cite a registered claim whose statement has symbols their paragraph does not name (unmentioned)."""
    articles = re.findall(r'<article\b.*?</article>', draft, re.S)
    found = {}
    for article in (articles if len(articles) > 1 else [draft]):
        for claim, where, sentence, missing in unmentioned(article, summaries):
            if SUMMARY.match(where):
                found.setdefault(hashlib.sha1(sentence.encode()).hexdigest()[:8], (where, sentence, claim, missing))
    return [(key, *row) for key, row in found.items()]


def unbounded(draft, answers, summaries):
    """The rows of domain_rows(draft) whose answer has no "within:" line of at least ANSWER_WORDS words."""
    given = {key: answer for key, answer in WITHIN.findall(answers or '')}
    return [row for row in domain_rows(draft, summaries) if len(given.get(row[0], '').split()) < ANSWER_WORDS]


def repeated_within(draft, answers, summaries):
    """[(answer text, keys)] for each "within:" answer given word for word to sentences citing different claims.
    A "within:" line says how one sentence's objects meet one claim's hypotheses, so one text for several claims
    is a form filled before it was read: on 17 October 2026 three such lines got one generic sentence, caught
    only when the author went back to read what the line asks."""
    claim_of = {row[0]: row[3] for row in domain_rows(draft, summaries)}
    by_text = {}
    for key, answer in WITHIN.findall(answers or ''):
        if key in claim_of and answer.split():
            by_text.setdefault(' '.join(answer.split()).lower(), []).append(key)
    return [(text, keys) for text, keys in by_text.items() if len({claim_of[k] for k in keys}) > 1]


def unbounded_report(rows):
    return '\n'.join([f'{len(rows)} summing-up sentences cite a claim whose symbols their paragraph does not '
                      'name and have no "within:" answer: say how the sentence\'s objects meet that claim\'s '
                      'hypotheses (or which they do not, and the sentence\'s limit):']
                     + [f'{key} [{where}] {sentence[:160]}\n  within:   ({claim}: {", ".join(missing[:8])})'
                        for key, where, sentence, claim, missing in rows])


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


def stated_in_reasons(draft, answers, gaps):
    """{key: why its "stated in:" passage did not count}, for the gaps qualifier_gaps returned: no passage, too
    few words, not a run of the entry's words outside the sentence, or lacking a missing word.  On 17 October
    2026 a second answers file added "stated in:" passages that quoted the entry but held none of the missing
    words, and the refusal, unchanged, did not say which condition the passages failed."""
    given = {key: answer for key, answer in ANSWER.findall(answers or '')}
    words = ' ' + ' '.join(plain(draft)) + ' '
    reasons = {}
    for key, _, sentence, missing in gaps:
        stated = STATED.search(given.get(key, ''))
        if not stated:
            reasons[key] = 'no "stated in:" passage'
            continue
        quote = ' '.join(plain(stated.group(1)))
        elsewhere = words.replace(f' {" ".join(plain(sentence))} ', ' | ')
        lacks = sorted(set(missing) - {m.lower() for m in QUALIFIER.findall(quote)})
        if len(quote.split()) < STATED_WORDS:
            reasons[key] = f'the passage has {len(quote.split())} words, fewer than {STATED_WORDS}'
        elif f' {quote} ' not in elsewhere:
            reasons[key] = 'the passage is not a run of the entry\'s words outside this sentence'
        elif lacks:
            reasons[key] = f'the passage does not hold {", ".join(lacks)}'
    return reasons


def qualifier_gaps_report(gaps, reasons=None):
    lines = [f'{len(gaps)} summing-up sentences whose answer limits them by a word the sentence lacks; put the '
             f'limit into the sentence, or end the answer "stated in:" with {STATED_WORDS} or more consecutive '
             'words of the entry that state it, holding each word the answer adds:']
    reasons = reasons or {}
    return '\n'.join(lines + [f'{key} [{where}] {sentence}\n  the answer says: {", ".join(missing)}'
                              + (f'\n  stated in: {reasons[key]}' if key in reasons else '')
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
    # 16 October 2026: "at least two twists", derived from inequalities, was false at its boundary t = 1 and was
    # repeated in four summaries before anyone tried that case.
    return '\n'.join(['Sentences outside the mathematics that hold a count; read each beside its saved source, '
                      'and a count derived from inequalities beside its boundary case, worked out:']
                     + lines + [f'{len(found)} sentences with a count.'])


UNNAMED_RESULT = re.compile(r'\b(?:the|a) (?:recorded|registered)\s+(?:[\w-]+\s+){0,3}(?:lemma|statement|bound|theorem|'
                            r'result|proposition|corollary)\b', re.I)
CLAIM_ID = re.compile(r'\b(?:lem|thm|prop|cor|conj|ex|def|imp):[\w-]+')


def unnamed_results(draft):
    """(section label, sentence) for each sentence naming a recorded result in words without its claim ID.

    Such a sentence escapes the listing of claims beside their statements: on 16 October 2026 "the recorded block
    lower-tail statement" was applied to summands it does not cover (it assumes i.i.d. summands), and no listing
    set it beside its hypotheses.  Of the record's 499 sentences naming a recorded result in words, 417 carry no
    ID, so this lists for reading and refuses nothing."""
    found, heading = [], ''
    for tag, body in BLOCK.findall(draft):
        if tag in ('h3', 'h4'):
            heading = text(body)
            continue
        label = re.match(r'\s*<strong>([^<]+?)\.?</strong>', body)
        where = label.group(1) if label else heading
        for sentence in sentences(body):
            said = text(sentence)
            if UNNAMED_RESULT.search(said) and not CLAIM_ID.search(said):
                found.append((where, said))
    return found


def unnamed_results_report(draft, width):
    found = unnamed_results(draft)
    lines = [f'  [{where}] {sentence if width <= 0 else sentence[:width]}' for where, sentence in found]
    return '\n'.join(['Sentences naming a recorded result without its claim ID; give the ID and read each beside the '
                      "result's statement and hypotheses:"] + lines + [f'{len(found)} such sentences.'])


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


# Words by which a sentence says which way a condition runs.
DIRECTION = re.compile(r'\b(?:necessary|sufficient|suffices?|only if|if and only if|exactly when|converse(?:ly)?|'
                       r'one direction|one-way)\b', re.I)


def direction_sentences(body):
    """The sentences of an entry's body that say which way a condition runs (necessary, sufficient, only if)."""
    found = []
    for tag, block in BLOCK.findall(body.split('</article>', 1)[0]):
        if tag in ('h3', 'h4'):
            continue
        found += [text(s) for s in sentences(block) if DIRECTION.search(text(s))]
    return found


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
    bodies = dict(ARTICLE.findall(notebook))
    heads = {entry: header for entry, body in bodies.items()
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
        # 17 October 2026: a draft read a linked entry's "necessary, not sufficient" as sufficient.  The entry's
        # own sentences that say which way a condition runs are set beside the draft's sentences that cite it.
        for sentence in direction_sentences(bodies.get(entry, '')):
            lines.append(f'  DIRECTION: {cut(sentence)}')
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


# A cited claim used in the converse direction: on 16 October 2026 a draft cited part (i) of a corollary that
# assumes c_E(K) > 0 to conclude c(K) > 0, and the side-by-side listing above was read past.  The relations a
# registered statement assumes are those of its "If ..."/"assume ..." clauses; a citing sentence whose chain of
# relations derives one of them is flagged.
# An If clause ends at "then", or, without one, at its first comma; "if and only if" and "only if" state
# equivalences or necessary conditions, not assumptions.
ASSUMING = re.compile(r'(?<!\bonly )(?<!\band )\b(?:[Ii]f(?! and only if)|[Aa]ssum(?:e|es|ed|ing)|'
                      r'[Pp]rovided(?: that)?|[Ww]henever|[Gg]iven that|[Ll]et|[Ss]uppose)\b'
                      r'((?:(?!\bthen\b)[^,;])*?)(?:,\s*then\b|\bthen\b|,|;|\.(?:\s|$)|$)', re.S)
REL_OPS = [(r'\\geqslant|\\geq|\\ge(?![a-z])|>=|≥', '>='), (r'\\leqslant|\\leq|\\le(?![a-z])|<=|≤', '<='),
           (r'\\neq|\\ne(?![a-z])|!=|≠', '!='), (r'\\gt(?![a-z])|>', '>'), (r'\\lt(?![a-z])|<', '<')]
REL_SPLIT = re.compile('(' + '|'.join(p for p, _ in REL_OPS) + ')')


def _term(raw):
    """A relation's side, normalized: no TeX delimiters, spacing or subscripts (c_E(K) and c(K) are one term)."""
    raw = re.sub(r'\\[(),;! ]|\\left|\\right|\\mathrm|\\operatorname|[{}\s]', '', raw)
    raw = re.sub(r'_(?:\{[^}]*\}|\\?[A-Za-z0-9]+)', '', raw)
    return raw.strip('.,:;')


def _chains(fragment, positions=False):
    """Chains of relations, [(terms, ops)], in the formulas and words of a fragment; with positions, also the
    offset at which each starts."""
    chains = []
    for found in re.finditer(r'\\\((.*?)\\\)|\\\[(.*?)\\\]', fragment, re.S):
        parts = REL_SPLIT.split(found.group(1) or found.group(2) or '')
        if len(parts) >= 3:
            ops = [next(norm for pattern, norm in REL_OPS if re.fullmatch(pattern, op)) for op in parts[1::2]]
            terms = [_term(t.split(',')[-1] if i == 0 else t.split(',')[0]) for i, t in enumerate(parts[::2])]
            chains.append((terms, ops, found.start()))
    plain = re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]', lambda m: ' ' * len(m.group(0)), fragment, flags=re.S)
    plain_op = {'>=': '>=', '≥': '>=', '<=': '<=', '≤': '<=', '!=': '!=', '≠': '!=', '>': '>', '<': '<'}
    for found in re.finditer(r'(?<![\w(])([A-Za-z]\w*(?:\([^()]*\))?)\s*(>=|<=|!=|≥|≤|≠|>|<)\s*'
                             r'([\w.]+(?:\([^()]*\))?)', plain):
        chains.append(([_term(found.group(1)), _term(found.group(3))], [plain_op[found.group(2)]], found.start()))
    return chains if positions else [(terms, ops) for terms, ops, _ in chains]


# A relation the sentence introduces as already known ("since c(K) > 0, ...", "for \(c(K)>0\)") is assumed
# there, not derived: the marker must stand at most one word before the formula ("assume that", "for every"),
# so that "applied with T as label set gives c(K) > 0" is still read as a derivation.
KNOWN = re.compile(r'\b(?:since|given(?: that)?|assum\w*|if|because|when(?:ever)?|hypothes[ei]s|provided(?: that)?|'
                   r'for|let|at|suppose|where|as|with|including)\b(?:\s+\w+)?\s*$', re.I)
FLIPPED = {'>': '<', '>=': '<=', '<': '>', '<=': '>=', '!=': '!='}


def assumed_relations(summary):
    """(left, op, right) relations that a registered statement assumes."""
    found = []
    for clause in ASSUMING.findall(summary):
        for terms, ops in _chains(clause):
            found.extend((terms[i], ops[i], terms[i + 1]) for i in range(len(ops)))
    return found


def _derives(terms, ops, relation):
    """Whether a chain states the relation, directly or by transitivity (c >= q > 0 states c > 0), in either
    orientation (0 < q <= c states it too)."""
    return (_derives_forward(terms, ops, relation)
            or _derives_forward(terms[::-1], [FLIPPED[op] for op in ops[::-1]], relation))


def _derives_forward(terms, ops, relation):
    left, op, right = relation
    up, down = {'>', '>='}, {'<', '<='}
    for i, term in enumerate(terms):
        if term != left:
            continue
        for j in range(i + 1, len(terms)):
            if terms[j] != right:
                continue
            between = set(ops[i:j])
            if op in up and between <= up and (op == '>=' or '>' in between):
                return True
            if op in down and between <= down and (op == '<=' or '<' in between):
                return True
            if op == '!=' and between == {'!='} and j == i + 1:
                return True
    return False


def converse_uses(draft, summaries):
    """(claim, section, sentence, relation) for each citing sentence that derives a relation the claim assumes."""
    flagged = []
    for claim, where, sentence in citations(draft):
        assumed = assumed_relations(summaries.get(claim, ''))
        chains = [(terms, ops) for terms, ops, start in _chains(sentence, positions=True)
                  if not KNOWN.search(sentence[:start])]
        for relation in assumed:
            if any(_derives(terms, ops, relation) for terms, ops in chains):
                flagged.append((claim, where, sentence, relation))
                break
    return flagged


def converse_report(draft, summaries, width):
    flagged = converse_uses(draft, summaries)
    if not flagged:
        return 'No citing sentence derives a relation that its cited claim assumes.'
    lines = ['CONVERSE USE? Each sentence below states, in one formula or a plain-text relation, a relation that '
             'the claim it cites assumes in an If, Let, Suppose or assume clause of its registered statement '
             '(subscripts ignored, either orientation): check that it does not use the claim in the converse '
             'direction. Conclusions in words or split across formulas are not seen, and plain-text relations are '
             'read one pair at a time.']
    for claim, where, sentence, (left, op, right) in flagged:
        lines.append(f'  {claim} assumes {left} {op} {right}\n    [{where}] '
                     f'{sentence if width <= 0 else sentence[:width]}')
    lines.append(f'{len(flagged)} such sentences.')
    return '\n'.join(lines)


def spec_summary(claim):
    """The summary a compact claim spec under research/results gives the claim, newest spec first, or None.

    A draft's own claim is registered only after its review, so without this its sentences (New mathematics, a
    Bearing, a commit message) were never set beside its statement before the review: on 16 October 2026 three
    entries in a row had their summaries of their own claim narrowed by the reviewer."""
    for path in sorted((ROOT / 'research' / 'results').glob('*/claim-spec.json'),
                       key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            spec = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        for item in spec.get('claims', []):
            if item.get('id') == claim and item.get('summary'):
                return f"(declared by this draft; spec {path.relative_to(ROOT)}) {item['summary']}"
    return None


def report(draft, registry, width):
    summaries = {claim['id']: claim['summary'] for claim in registry['claims']}
    rests_on = {}
    for edge in registry.get('relationships', []):
        if edge.get('type') == 'depends_on':
            rests_on.setdefault(edge['source']['id'], set()).add(edge['target']['id'])
    declared = set((re.search(r'data-claims="([^"]*)"', draft) or [None, ''])[1].split())
    found = citations(draft)
    lines, unregistered = [], set()
    for claim in dict.fromkeys(c for c, _, _ in found):
        if claim in summaries:
            statement = summaries[claim]
        elif claim in declared:
            statement = spec_summary(claim) or '(declared by this draft; not yet registered, and no spec found)'
        elif f'<code>{claim}</code>' in draft:
            statement = '(NOT IN THE REGISTRY)'
            unregistered.add(claim)
        else:                   # written bare: it may be a phrase and not a claim, so it fails nothing
            statement = '(not in the registry; written without code tags, perhaps not a claim)'
        lines.append(f'{claim}\n  REGISTERED: {statement if width <= 0 else statement[:width]}')
        if rests_on.get(claim):
            # 16 October 2026: a draft citing a theorem repeated, as new, a step of the proof of the lemma that
            # theorem rests on; the listing showed the theorem but not what it rests on.
            lines.append('  RESTS ON (read their proofs for steps the draft may repeat): '
                         + ', '.join(sorted(rests_on[claim])))
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
    parser.add_argument('--construction', action='store_true', help='print only the listing of unsourced proof '
                        'sentences about recorded constructions; for a file of several articles, their count in each')
    parser.add_argument('--construction-words', help='a regular expression of the nouns that mark a recorded '
                        'construction, in place of the default list (a notebook with its own vocabulary)')
    parser.add_argument('--exactness', action='store_true', help='print only the listing of words of exactness; '
                        'for a file of several articles, the count of such sentences in each')
    parser.add_argument('--spec', help='the draft\'s claim spec, whose texts saying a part of a source was not '
                        'read are read for the unread-section listing')
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
    # 16 October 2026: a listing run at --width 1 passed the brief hook while cutting every sentence to one
    # character, so no citing sentence was read beside its source, and an unsupported citation reached review.
    if 0 < args.width < MIN_WIDTH:
        parser.error(f'--width {args.width} cuts sentences below {MIN_WIDTH} characters, too short to read them '
                     'beside their sources; omit it or give at least {MIN_WIDTH}'.replace('{MIN_WIDTH}',
                                                                                         str(MIN_WIDTH)))
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
    words = re.compile(r'\b(?:' + args.construction_words + r')\b', re.I) if args.construction_words else None
    if args.construction:
        articles = re.findall(r'<article id="([^"]+)"(.*?)</article>', draft, re.S)
        if len(articles) > 1:
            rows = [(ident, *construction_steps(body, words)) for ident, body in articles]
            print('\n'.join(f'{len(found)}\t{read}\t{ident}' for ident, found, read in rows if found))
            print(f'{sum(len(found) for _, found, _ in rows)} such sentences of '
                  f'{sum(read for _, _, read in rows)} proof sentences in {len(rows)} articles.')
        else:
            print(construction_report(draft, args.width, words))
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
    print('\n' + converse_report(draft, {c['id']: c['summary'] for c in registry['claims']}, args.width))
    missing = set()
    notebook_text = notebook_file(args.notebook).read_text() if args.notebook else ''
    if args.notebook:
        linked, missing = entry_report(draft, notebook_text, args.width)
        print('\n' + linked)
    print('\n' + pairings_report(draft, registry['claims'], notebook_text,
                                 args.width))
    print('\n' + counts_report(draft, args.width))
    print('\n' + unnamed_results_report(draft, args.width))
    print('\n' + universals_report(draft, args.width))
    print('\n' + construction_report(draft, args.width, words))
    listing = listing_words(notebook_text)
    print('\n' + vanishing_report(draft, args.width, listing))
    print('\n' + hypothesis_report(draft, args.width, listing))
    print('\n' + step_forms_report(draft, args.width))
    print('\n' + unrun_searches_report(draft, logged_queries(ROOT), args.width))
    print('\n' + unread_named_claims_report(unread_named_claims(draft, ROOT), args.width))
    spec =json.loads(pathlib.Path(args.spec).read_text()) if args.spec else None
    print('\n' + unread_report(draft, registry, args.width, spec))
    print('\n' + own_summaries_report(draft, args.width))
    print('\n' + exactness_report(draft, args.width))
    print('\n' + comparisons_report(draft, args.width))
    print('\n' + unmentioned_report(draft, {c['id']: c['summary'] for c in registry['claims']}, args.width))
    if naming_lines(draft):
        print('\n' + naming_lines_report(draft, args.width))
    for line in readings(draft=draft):
        print(line)
    log_run(draft)
    open_rows = []
    if args.answers:
        answers = pathlib.Path(args.answers)
        summaries = {c['id']: c['summary'] for c in registry['claims']}
        if not answers.exists():
            answers.write_text(answers_template(draft, summaries))
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
                print(qualifier_gaps_report(gaps, stated_in_reasons(draft, answers.read_text(), gaps)))
                open_rows = open_rows + gaps
            outside = unbounded(draft, answers.read_text(), summaries)
            if outside:
                print(unbounded_report(outside))
                open_rows = open_rows + outside
            untried = unextreme(draft, answers.read_text())
            if untried:
                print(unextreme_report(untried))
                open_rows = open_rows + untried
            unchecked = unchecked_hypotheses(draft, answers.read_text())
            if unchecked:
                print(unchecked_hypotheses_report(unchecked))
                open_rows = open_rows + unchecked
    return 1 if unregistered or missing or open_rows else 0


if __name__ == '__main__':
    sys.exit(main())
