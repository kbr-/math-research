def planned_test_texts(entry):
    """(label, text) for the tests an entry poses: a review's Decisive test, by its Operation and Prediction, and
    a research entry's next attempt, the Follow-up's words after "Next attempt" up to its Record search."""
    plain = lambda fragment: re.sub(r'\s+', ' ', html.unescape(strip_tags(fragment))).strip()
    found = []
    test = report_paragraph(entry + '</article>', 'Decisive test')
    parts = [re.search(r'<strong>' + label + r'\.</strong>(.*?)(?=<strong>[A-Z][\w ]*\.</strong>|$)', test, re.S)
             for label in ('Operation', 'Prediction')]
    if any(parts):
        found.append(('Decisive test', ' '.join(plain(part.group(1)) for part in parts if part)))
    follow = plain(report_paragraph(entry + '</article>', 'Follow-up'))
    attempt = re.search(r'Next attempt[:.]?\s*(.*?)(?:Record search\.|$)', follow, re.S)
    if attempt and attempt.group(1).strip():
        found.append(('next attempt', attempt.group(1).strip()))
    return found


def uncited_matches_report(entry, data=None, limit=4):
    """Lines for the finisher and the skeleton check to print: for each test the entry poses (planned_test_texts),
    the registered claims nearest to its words that the entry does not cite. It refuses nothing.

    On 16 October 2026 a review posed a union bound on label conjunctions, searched in union-bound words, and
    missed two claims that treat the same defects as affine flats; and a research entry named exact evaluation as
    the only alternative where the registry holds a branching lemma beside the theorem it read."""
    texts = planned_test_texts(entry)
    if not texts:
        return []
    spec = importlib.util.spec_from_file_location('search_claims', Path(__file__).with_name('search-claims.py'))
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        data = module.read_json(module.REGISTRY) if data is None else data
    except (OSError, ValueError, KeyError):
        return []
    cited = set(CLAIM_ID_RE.findall(html.unescape(strip_tags(entry))))
    lines = []
    for label, text in texts:
        found = [claim for _score, claim in module.search(data, [text]) if claim['id'] not in cited][:limit]
        if found:
            lines.append(f'Registered claims nearest to the words of its {label} that the entry does not cite; '
                         'read each before posing it (a test the record answers decides nothing):')
            lines += [f"  {claim['id']} — {' '.join(claim['summary'].split())[:160]}" for claim in found]
    return lines


