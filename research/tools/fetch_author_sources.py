#!/usr/bin/env python3
"""Resolve public author links and import two papers without editing the export."""
import concurrent.futures
import html.parser
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import import_references as importer

ROOT = Path(__file__).resolve().parents[1]


class Links(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.url = None
        self.label = ''
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.url = dict(attrs).get('href')
            self.label = ''

    def handle_data(self, data):
        if self.url:
            self.label += data

    def handle_endtag(self, tag):
        if tag == 'a' and self.url:
            self.links.append((self.url, self.label.strip()))
            self.url = None


def resolve_r():
    page = 'https://people.cs.uchicago.edu/~razborov/research.html'
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(page, timeout=20) as response:
            raw = response.read(2 * 1024 * 1024)
            final_url = response.url
        dest = ROOT / 'references/cache/Razborov-author-index.html'
        dest.write_bytes(raw)
        parser = Links()
        parser.feed(raw.decode('utf-8', errors='replace'))
        matches = [(urllib.parse.urljoin(final_url, u), t) for u, t in parser.links
                   if 'lower bounds for the polynomial calculus' in t.lower()]
        print('Razborov author links:', matches, flush=True)
        return matches, {'url': page, 'final_url': final_url, 'status': 'retrieved',
                         'elapsed_s': time.perf_counter() - start,
                         'sha256': importer.sha(dest), 'matches': matches}
    except Exception as e:
        return [], {'url': page, 'status': 'failed', 'error': str(e),
                    'elapsed_s': time.perf_counter() - start}


def main():
    refs = {r['id']: r for r in json.loads((ROOT / 'references/manifest.json').read_text())['references']}
    matches, resolution = resolve_r()
    requests = []
    b = dict(refs['BIKPRS'])
    b['pdf_candidates'] = ['https://mathweb.ucsd.edu/~sbuss/ResearchWeb/nullstellensatz/token.pdf']
    b['version'] = 'Author-hosted copy linked by Samuel Buss; printed version to be inspected'
    requests.append(b)
    if matches:
        r = dict(refs['Razborov'])
        r['pdf_candidates'] = [u for u, _ in matches if u.endswith('.pdf')]
        r['version'] = 'Author-hosted copy linked by Alexander Razborov; printed version to be inspected'
        if r['pdf_candidates']:
            requests.append(r)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda r: importer.acquire(r, True, True, 20), requests))
    report = {'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
              'resolution': resolution, 'sources': results}
    (ROOT / 'references/author_source_import.json').write_text(json.dumps(report, indent=2) + '\n')
    status_path = ROOT / 'references/import_status.json'
    status = json.loads(status_path.read_text())
    for result in results:
        key = result['id']
        result['prior_import_record'] = status['references'][key]
        status['references'][key] = result
        print(key, result['status'], result.get('extraction', {}).get('status'), flush=True)
    status['utc'] = report['utc']
    status_path.write_text(json.dumps(status, indent=2) + '\n')
    if not matches:
        print('Author-index lookup failed or found no matching PDF; see report.', flush=True)
    return 0 if len(results) == 2 and all(r['status'] in ('downloaded', 'cached') for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
