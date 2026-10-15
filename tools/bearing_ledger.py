"""Check explicit budget references, not the mathematics of a claimed application."""
from html.parser import HTMLParser
import re


class _Paragraphs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.bearing = None
        self.paragraphs = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article':
            self.bearing = attrs.get('data-bearing')
        elif tag == 'p':
            self.current = {'text': '', 'links': []}
        elif tag == 'a' and self.current is not None:
            self.current['links'].append((len(self.current['text']),
                                          attrs.get('data-ledger'), attrs.get('href', '')))

    def handle_data(self, data):
        if self.current is not None:
            self.current['text'] += data

    def handle_endtag(self, tag):
        if tag == 'p' and self.current is not None:
            self.paragraphs.append(self.current)
            self.current = None


def _references(paragraph, start=0, end=None):
    refs = set()
    for position, name, href in paragraph['links']:
        if name is None:
            continue
        if not re.fullmatch(r'[a-z][a-z0-9-]*', name) or not href.strip() or href.strip() == '#':
            raise ValueError('A data-ledger link needs a descriptive budget name and a nonempty target')
        if position < start or (end is not None and position >= end):
            continue
        refs.add((name, href.strip()))
    return refs


def _check_multiple(text, refs):
    if re.search(r'\b(?:both|all) (?:the )?(?:ledgers|budgets)\b', text, re.I):
        if len({name for name, _ in refs}) < 2:
            raise ValueError('A both/all-ledgers assertion needs separately named data-ledger references')


def validate(article):
    """Validate only the supplied new article; do not retrofit historical records.

    Bearing links use data-ledger="selection" (or another budget name). Each
    Nonvacuity paragraph identifies the budget it verifies with a matching link.
    Link existence and mathematical adequacy remain the normal link/review duties.
    """
    parsed = _Paragraphs()
    parsed.feed(article)
    if parsed.bearing != 'some':
        return
    progress = next((p for p in parsed.paragraphs
                     if p['text'].lstrip().startswith('Goal progress.')), None)
    if progress is None or 'Bearing.' not in progress['text']:
        raise ValueError('A bearing-some application needs its Bearing statement and a data-ledger link')
    start = progress['text'].index('Bearing.') + len('Bearing.')
    end = progress['text'].find('Not covered.', start)
    end = len(progress['text']) if end < 0 else end
    refs = _references(progress, start, end)
    if not refs:
        raise ValueError('A bearing-some application must link its matched parameter ledger with data-ledger')
    _check_multiple(progress['text'][start:end], refs)
    for paragraph in parsed.paragraphs:
        if not paragraph['text'].lstrip().startswith('Nonvacuity.'):
            continue
        witness = _references(paragraph)
        if not witness or not witness <= refs:
            raise ValueError('Each Nonvacuity paragraph must link the particular data-ledger budget it '
                             'verifies, using a name and target from Bearing')
        _check_multiple(paragraph['text'], witness)
