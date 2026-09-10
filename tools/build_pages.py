#!/usr/bin/env python3
"""Build only the public notebook files for GitHub Pages; no external packages."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from server import snapshot

SOURCE_URL = 'https://github.com/kbr-/math-research'
OUTPUT_FILES = {'index.html', 'revision.json', '.nojekyll'}


def build(out, root=ROOT, source_url=SOURCE_URL):
    out, root = Path(out), Path(root)
    if urlsplit(source_url).scheme != 'https':
        raise ValueError('Source URL must use HTTPS')
    template, notebook, source_revision = snapshot(root)
    software_license = (root / 'LICENSES/MIT.txt').read_text(encoding='utf-8').strip()
    if '--' in software_license:
        raise ValueError('License text cannot be embedded in an HTML comment unchanged')
    settings = {'mode': 'published', 'revisionUrl': './revision.json', 'pollMs': 30000}
    configuration = json.dumps(settings, sort_keys=True)
    revision = hashlib.sha256(source_revision.encode() + configuration.encode()
                              + source_url.encode() + software_license.encode()
                              + Path(__file__).read_bytes()).hexdigest()
    begin, end = '// BEGIN NOTEBOOK SETTINGS', '// END NOTEBOOK SETTINGS'
    if template.count(begin) != 1 or template.count(end) != 1 or template.count('<!-- NOTEBOOK -->') != 1:
        raise ValueError('Expected one configuration block and one notebook placeholder')
    before, remainder = template.split(begin, 1)
    _, after = remainder.split(end, 1)
    page = before + begin + '\n    window.notebookSettings = ' + configuration + ';\n    ' + end + after
    footer = ('<footer id="notebook-footer">Kamil Braun · '
              f'<a href="{html.escape(source_url, quote=True)}">Source and citation</a> · '
              '<a href="https://creativecommons.org/licenses/by/4.0/">Research: CC BY 4.0</a>'
              '</footer>')
    page, count = re.subn(r'<footer id="notebook-footer">.*?</footer>',
                          lambda _: footer, page, flags=re.DOTALL)
    if count != 1:
        raise ValueError('Expected one notebook footer')
    if page.count('<head>') != 1:
        raise ValueError('Expected one page head for the software license notice')
    page = page.replace('<head>', '<head>\n<!--\n' + software_license + '\n-->', 1)
    page = page.replace('__REVISION__', revision).replace('<!-- NOTEBOOK -->', notebook)

    # Never package arbitrary contents from an existing output directory.
    if out.is_symlink():
        raise ValueError('Output directory must not be a symlink')
    if out.exists():
        for path in out.iterdir():
            if path.name not in OUTPUT_FILES or path.is_symlink() or not path.is_file():
                raise ValueError(f'Unexpected output-directory entry: {path.name}')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'index.html').write_text(page, encoding='utf-8')
    (out / 'revision.json').write_text(json.dumps({'revision': revision}) + '\n', encoding='utf-8')
    (out / '.nojekyll').write_text('', encoding='utf-8')
    return revision


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True, help='Dedicated site-output directory')
    parser.add_argument('--source-url', default=SOURCE_URL)
    args = parser.parse_args()
    build(args.out, source_url=args.source_url)
    print(f'Built the public notebook in {args.out}: index.html, revision.json, .nojekyll')


if __name__ == '__main__':
    main()
