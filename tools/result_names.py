"""Letter-code result labels ("Lemma K", "Theorem NDX'", "Conjecture H1"), which the naming rule forbids in
new text (CLAUDE.md and AGENTS.md, Naming results): cite results by descriptive names instead. Shared by the
finisher (new notebook entries) and claim authoring (new claim text)."""
import re

KEPT_LABELS = {'Corollary SL', 'Conjecture SR', 'Remark A.4'}
LABEL_NOUNS = 'Lemma|Theorem|Corollary|Conjecture|Proposition|Observation|Question|Remark|Criterion'


def letter_code_labels(html_text):
    """Letter-code result labels in prose; tables (name maps) and HTML tags are ignored."""
    text = re.sub(r'<table\b.*?</table>', ' ', html_text, flags=re.S)   # name maps live in tables
    text = re.sub(r'<[^>]*>', ' ', text)
    found = []
    for m in re.finditer(r'\b(' + LABEL_NOUNS + r')\s+([A-Z][A-Za-z0-9.]*[\u2032\u2033]*)', text):
        code = m.group(2).rstrip('.')
        if re.fullmatch(r'[A-Z][a-z]{2,}', code):          # an ordinary capitalized word
            continue
        label = f'{m.group(1)} {code}'
        if label not in KEPT_LABELS and label not in found:
            found.append(label)
    return found
