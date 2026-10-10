"""Word stems shared by the ranked searches (tools/search-claims.py, tools/search-record.py)."""
import math
import re

STOP = set('a an and are as at be by for from has have in is it its no not of on or over that the this to '
           'with without every each any all at most least than then under into only which whose'.split())


def stem(word):
    word = word.lower()
    for suffix in ('ations', 'ation', 'ings', 'ing', 'ies', 'ed', 'es', 's'):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[:len(word) - len(suffix)]
    return word


def stems(text):
    return {stem(w) for w in re.findall(r'[A-Za-z][A-Za-z0-9]+', text) if w.lower() not in STOP}


def matches(query_stem, token_set):
    """A query stem matches a document stem when they are equal, or when either is a prefix of the
    other and the shorter has at least four letters ("app" would otherwise match "appeal")."""
    return any(t == query_stem or (min(len(t), len(query_stem)) >= 4
                                   and (t.startswith(query_stem) or query_stem.startswith(t)))
               for t in token_set)


def rarity_weights(query, token_sets):
    """Inverse document frequency of each query stem over the documents' stem sets."""
    count = {q: sum(matches(q, s) for s in token_sets) for q in query}
    return {q: math.log((len(token_sets) + 1) / (count[q] + 1)) for q in query}
