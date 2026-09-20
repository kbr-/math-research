#!/usr/bin/env python3
"""Check the short note's final build, extracted layout and local page renders."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[3]
NOTE = ROOT / 'publications/binary-polynomial-multiplicity'
OUT = Path(__file__).resolve().parent
pdf = NOTE / 'whitepaper.pdf'
log = (NOTE / 'pdflatex-pass-3.log').read_text()
problems = re.findall(r'.*(?:Warning|Overfull|Underfull|Missing character|undefined).*', log)
assert not problems, problems
with tempfile.TemporaryDirectory(prefix='multiplicity-note-qa-') as tmp:
    tmp = Path(tmp)
    subprocess.run(['pdftoppm', '-r', '110', '-png', str(pdf), str(tmp/'page')], check=True)
    subprocess.run(['pdftotext', '-bbox', str(pdf), str(tmp/'bbox.html')], check=True)
    subprocess.run(['pdftotext', '-layout', str(pdf), str(tmp/'text.txt')], check=True)
    text = (tmp/'text.txt').read_text()
    assert 'Proposition 1.' in text and 'Multiplicity Schwartz' in text
    assert 'Definition 2.2 and Lemma 2.7' in text
    assert 'doi:10.1137/100783704' in text and 'doi:10.1017/S0963548323000123' in text
    assert '??' not in text
    assert 'Preprint, version 1' in text
    assert 'revision 1' not in text.lower()
    # Poppler can emit XML-forbidden control codes for legacy TeX math glyphs.
    # Sanitize only the parser input; keep the raw extracted text as evidence.
    bbox = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', (tmp/'bbox.html').read_text())
    pages = ET.fromstring(bbox).findall('.//{*}page')
    assert len(pages) == 2
    layout = []
    for number, page in enumerate(pages, 1):
        width, height = float(page.attrib['width']), float(page.attrib['height'])
        words = page.findall('.//{*}word')
        assert words
        boxes = [{k: float(w.attrib[k]) for k in ('xMin','yMin','xMax','yMax')} for w in words]
        # Combining math accents may legitimately have zero advance width.
        assert all(0 <= b['xMin'] <= b['xMax'] <= width and 0 <= b['yMin'] < b['yMax'] <= height for b in boxes)
        img = Image.open(tmp/f'page-{number}.png').convert('RGB')
        ink = ImageChops.difference(img, Image.new('RGB', img.size, 'white')).convert('L')
        bounds = ink.point(lambda value: 255 if value > 20 else 0).getbbox()
        assert bounds and bounds[0] > 40 and bounds[1] > 40
        assert bounds[2] < img.width-40 and bounds[3] < img.height-40
        layout.append({'page':number,'words':len(words),'page_points':[width,height],
                       'text_bounds_points':[min(b['xMin'] for b in boxes),min(b['yMin'] for b in boxes),
                                             max(b['xMax'] for b in boxes),max(b['yMax'] for b in boxes)],
                       'render_pixels':list(img.size),'ink_bounds_pixels':list(bounds)})
    fonts = subprocess.check_output(['pdffonts',str(pdf)],text=True)
    assert all(re.search(r'\byes\s+yes\s+(?:yes|no)\s+\d+\s+\d+\s*$', line) for line in fonts.splitlines()[2:])
    (OUT/'extracted-text.txt').write_text(text)
    (OUT/'fonts.txt').write_text(fonts)
    urls = subprocess.check_output(['pdfinfo', '-url', str(pdf)], text=True)
    for target in ('https://doi.org/10.1112/jlms.12637', 'https://doi.org/10.1137/100783704', 'https://doi.org/10.1017/S0963548323000123', 'https://arxiv.org/abs/2101.11947v1', 'https://github.com/kbr-/math-research/blob/main/publications/binary-polynomial-multiplicity/DEVELOPMENT_HISTORY.md'):
        assert target in urls, target
    (OUT/'pdf-links.txt').write_text(urls)
    (OUT/'pdfinfo.txt').write_text(subprocess.check_output(['pdfinfo',str(pdf)],text=True))
    report={'pages':layout,'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
            'final_build_warnings':problems,'fonts_embedded':True,
            'review_scope':'Extracted content, word bounding boxes and rendered pixel margins checked; no human visual review or formal verification claimed.'}
    (OUT/'pdf-check.json').write_text(json.dumps(report,indent=2)+'\n')
for number in range(1,4):
    shutil.copyfile(NOTE/f'pdflatex-pass-{number}.log',OUT/f'pdflatex-pass-{number}.txt')
print(json.dumps({'pages':len(layout),'warnings':len(problems),'fonts_embedded':True,'geometry_and_raster_margins':'passed'}))
