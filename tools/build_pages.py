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
from notebooks import catalogue
from notebook_site import manifest
from notebook_math import strip_tags_tight

SOURCE_URL = 'https://github.com/kbr-/math-research'
OUTPUT_FILES = {'index.html', 'revision.json', '.nojekyll', 'notebooks.json', 'notebook-source.html'}
COLLECTION = 'Noemesis research notebooks'
RESEARCH_LICENSE = ('CC BY 4.0', 'https://creativecommons.org/licenses/by/4.0/')
# An attribute value may hold '>', as in data-claim-note="... = 2, so no claim ...".
ARTICLE = r'<article\b(?:[^>"\']|"[^"]*"|\'[^\']*\')*>'
ENTRY = re.compile(ARTICLE.replace(r'<article\b', r'<article\b(?=(?:[^>"\']|"[^"]*"|\'[^\']*\')*?\bid="entry-)')
                   + r'(\s*<h3[^>]*>(.*?)</h3>)?(\s*<p class="entry-meta">.*?</p>)?', re.DOTALL)
ENTRY_ID = re.compile(r'\bid="(entry-(?:(\d{4})-(\d\d)-(\d\d))?[^"]*)"')
MONTHS = ('January February March April May June July August September October November '
          'December').split()


def authors(root):
    """The author names CITATION.cff gives, as 'Given Family', in order: the one place they are written."""
    text = (Path(root) / 'CITATION.cff').read_text(encoding='utf-8')
    names = [' '.join(part.strip().strip('"\'') for part in (given, family))
             for family, given in re.findall(r'-\s*family-names:\s*(.+)\n\s*given-names:\s*(.+)', text)]
    if not names:
        raise ValueError('CITATION.cff names no author (family-names, then given-names)')
    return ', '.join(names)


def site_page(site_url, route):
    """The absolute public URL of a notebook route under the site's base URL."""
    parts = urlsplit(site_url)
    if parts.scheme != 'https' or not parts.netloc:
        raise ValueError(f'Site URL must be an HTTPS URL with a host, not {site_url!r}')
    return site_url.rstrip('/') + '/' + route


def plain(fragment):
    return ' '.join(html.unescape(strip_tags_tight(fragment)).split())


def cite_entries(notebook, author, title, url):
    """The notebook with a citation line after each entry's heading and status line, so that a reader who
    lands on an entry deep in a long page finds who wrote it and how to cite it there."""
    def line(match):
        ident, year, month, day = ENTRY_ID.search(match.group(0)).groups()
        heading = plain(match.group(2) or '')
        name = heading.split(' — ', 1)[1] if ' — ' in heading else heading
        date = f'{int(day)} {MONTHS[int(month) - 1]} {year}, ' if year else ''
        anchor = html.escape(f'{url}#{ident}', quote=True)
        named = f'“{html.escape(name, quote=False)}”, ' if name else ''
        return (match.group(0) + f'\n<p class="entry-cite">Cite as: {html.escape(author, quote=False)}, {named}'
                f'{html.escape(title, quote=False)}, {COLLECTION}, {date}<a href="{anchor}">{anchor}</a>.</p>')
    return ENTRY.sub(line, notebook)


def citation_block(author, title, url):
    name, deed = RESEARCH_LICENSE
    author, title, link = (html.escape(author, quote=False), html.escape(title, quote=False),
                           html.escape(url, quote=True))
    return (f'<aside class="citation" id="cite-this-notebook"><p><strong>Author:</strong> {author}. '
            f'<strong>Cite as:</strong> {author}, <cite>{title}</cite>, {COLLECTION}, <a href="{link}">{link}</a>, '
            'with the dated entry used: each entry gives its own citation and link below its heading. '
            f'<strong>License:</strong> the research text is under <a href="{deed}">{name}</a>, which requires '
            'attribution. If you build on a result here, please cite its entry and tell your readers where it '
            'came from.</p></aside>')


def attribute(notebook, author, title, url):
    """The notebook with the citation block after its introduction (or its title) and every entry cited."""
    block = citation_block(author, title, url)
    for anchor in (r'<p class="intro">.*?</p>', r'</h1>'):
        found = re.search(anchor, notebook, re.DOTALL)
        if found:
            notebook = notebook[:found.end()] + '\n' + block + notebook[found.end():]
            break
    else:
        notebook = block + '\n' + notebook
    return cite_entries(notebook, author, title, url)


def page(root, source_url, notebook_name, site_url):
    root = Path(root)
    if urlsplit(source_url).scheme != 'https':
        raise ValueError('Source URL must use HTTPS')
    template, notebook, source_revision = snapshot(root, notebook_name)
    item = catalogue(root)[notebook_name]
    author = authors(root)
    notebook = attribute(notebook, author, item['title'], site_page(site_url, item['route']))
    software_license = (root / 'LICENSES/MIT.txt').read_text(encoding='utf-8').strip()
    if '--' in software_license:
        raise ValueError('License text cannot be embedded in an HTML comment unchanged')
    settings = {'mode': 'published', 'revisionUrl': './revision.json', 'pollMs': 30000}
    configuration = json.dumps(settings, sort_keys=True)
    revision = hashlib.sha256(source_revision.encode() + configuration.encode()
                              + source_url.encode() + site_url.encode() + author.encode()
                              + software_license.encode() + Path(__file__).read_bytes()).hexdigest()
    begin, end = '// BEGIN NOTEBOOK SETTINGS', '// END NOTEBOOK SETTINGS'
    if template.count(begin) != 1 or template.count(end) != 1 or template.count('<!-- NOTEBOOK -->') != 1:
        raise ValueError('Expected one configuration block and one notebook placeholder')
    before, remainder = template.split(begin, 1)
    _, after = remainder.split(end, 1)
    page = before + begin + '\n    window.notebookSettings = ' + configuration + ';\n    ' + end + after
    footer = (f'<footer id="notebook-footer">{html.escape(author, quote=False)} · '
              f'<a href="{html.escape(source_url, quote=True)}">Source and citation</a> · '
              f'<a href="{RESEARCH_LICENSE[1]}">Research: {RESEARCH_LICENSE[0]}</a>'
              '</footer>')
    page, count = re.subn(r'<footer id="notebook-footer">.*?</footer>',
                          lambda _: footer, page, flags=re.DOTALL)
    if count != 1:
        raise ValueError('Expected one notebook footer')
    if page.count('<head>') != 1:
        raise ValueError('Expected one page head for the software license notice')
    page = page.replace('<head>', '<head>\n<!--\n' + software_license + '\n-->', 1)
    page = page.replace('__REVISION__', revision).replace('<!-- NOTEBOOK -->', notebook)

    return page,notebook,revision


def build(out, site_url, root=ROOT, source_url=SOURCE_URL):
    out,root=Path(out),Path(root)
    items=catalogue(root)
    payload={'.nojekyll':'','notebooks.json':json.dumps(manifest(root))+'\n'}
    main_revision=None
    for name,item in items.items():
        rendered,notebook,revision=page(root,source_url,name,site_url)
        if name=='main':main_revision=revision
        prefix=item['route']
        payload[prefix+'index.html']=rendered
        payload[prefix+'revision.json']=json.dumps({'revision':revision})+'\n'
        payload[prefix+'notebook-source.html']=notebook
    allowed_dirs={p.as_posix() for name in payload for p in Path(name).parents if p.as_posix()!='.'}
    if out.is_symlink():raise ValueError('Output directory must not be a symlink')
    if out.exists():
        for existing in out.rglob('*'):
            rel=existing.relative_to(out).as_posix()
            if existing.is_symlink() or (existing.is_dir() and rel not in allowed_dirs) or (existing.is_file() and rel not in payload):
                raise ValueError('Unexpected output-directory entry: '+rel)
    out.mkdir(parents=True,exist_ok=True)
    for name,body in payload.items():
        target=out/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(body)
    return main_revision


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True, help='Dedicated site-output directory')
    parser.add_argument('--source-url', default=SOURCE_URL)
    parser.add_argument('--site-url', required=True,
                        help='The public HTTPS base URL of the site, for the citations on its pages')
    args = parser.parse_args()
    build(args.out, args.site_url, source_url=args.source_url)
    print(f'Built registered public notebooks in {args.out}; no private or runtime files copied')


if __name__ == '__main__':
    main()
