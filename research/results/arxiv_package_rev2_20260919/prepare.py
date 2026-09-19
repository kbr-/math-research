#!/usr/bin/env python3
"""Reproduce the source-only arXiv upload and check its isolated compilation."""
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[3]
PAPER = 'publications/bit-php-resolution-over-parities'
PIN = '652e6172f5237d1e5ee768a853d3c1bb78f7c6f4'
TAG = 'bit-php-preprint-2026-09-19'
OUT = Path(__file__).resolve().parent
ARCHIVE = Path('/tmp/bit-php-arxiv-revision-2.tar.gz')

def git_file(path):
    return subprocess.check_output(['git', 'show', f'{PIN}:{path}'], cwd=ROOT)

def sha(data):
    return hashlib.sha256(data).hexdigest()

main = git_file(f'{PAPER}/whitepaper.tex')
names = ['whitepaper.tex'] + [name+'.tex' for name in re.findall(r'\\input\{([^}]+)\}', main.decode())]
assert len(names) == len(set(names)) == 12
files = {name:git_file(f'{PAPER}/{name}') for name in names}
for name, data in files.items():
    assert re.fullmatch(r'[A-Za-z0-9_+.,=/\-]+',name)
    assert not name.startswith('/') and '..' not in Path(name).parts
    assert (ROOT/PAPER/name).read_bytes() == data, name
files['LICENSE.txt'] = git_file('LICENSES/CC-BY-4.0.txt')
with ARCHIVE.open('wb') as raw:
    with gzip.GzipFile(fileobj=raw,filename='',mode='wb',mtime=0) as gz:
        with tarfile.open(fileobj=gz,mode='w',format=tarfile.USTAR_FORMAT) as tar:
            for name,data in sorted(files.items()):
                member=tarfile.TarInfo(name)
                member.size=len(data); member.mode=0o644; member.mtime=0
                tar.addfile(member,io.BytesIO(data))
work=Path(tempfile.mkdtemp(prefix='bit-php-arxiv-rev2-'))
with tarfile.open(ARCHIVE,'r:gz') as tar:
    members=tar.getmembers()
    assert sorted(m.name for m in members)==sorted(files)
    for member in members:
        assert member.isfile() and member.name in files
        data=tar.extractfile(member).read()
        assert data==files[member.name]
        path=work/member.name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
env=dict(os.environ,TEXINPUTS='')
for number in range(1,4):
    result=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',
        '-file-line-error','-no-shell-escape','-recorder','whitepaper.tex'],cwd=work,
        env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (OUT/f'pdflatex-pass-{number}.txt').write_bytes(result.stdout)
    if result.returncode:
        raise RuntimeError(f'LaTeX pass {number} failed; see saved full output')
log=(work/'whitepaper.log').read_text()
(OUT/'latex-log.txt').write_text(log)
assert not re.search(r'Warning|Overfull|Underfull|Undefined control|Fatal error',log)
info=subprocess.check_output(['pdfinfo',str(work/'whitepaper.pdf')],text=True)
(OUT/'pdfinfo.txt').write_text(info)
assert re.search(r'Pages:\s+37\b',info)
reference=work/'reference.pdf'; reference.write_bytes(git_file(f'{PAPER}/whitepaper.pdf'))
texts=[subprocess.check_output(['pdftotext','-layout',str(path),'-']) for path in (reference,work/'whitepaper.pdf')]
assert texts[0]==texts[1], 'PDF text differs from reviewed tagged PDF'
for name in ('reference','whitepaper'):
    subprocess.run(['pdftoppm','-scale-to','700','-png',str(work/f'{name}.pdf'),str(work/name)],check=True)
reference_pages=sorted(work.glob('reference-*.png'))
new_pages=sorted(work.glob('whitepaper-*.png'))
assert len(reference_pages)==len(new_pages)==37
assert all(a.read_bytes()==b.read_bytes() for a,b in zip(reference_pages,new_pages)), 'Rendered pages differ'
report={'archive':str(ARCHIVE),'sha256':sha(ARCHIVE.read_bytes()),'bytes':ARCHIVE.stat().st_size,
    'source_tag':TAG,'source_commit':PIN,'main_file':'whitepaper.tex','processor':'pdflatex',
    'entries':[{'path':name,'sha256':sha(data)} for name,data in sorted(files.items())],
    'validation':{'isolated_compile_passes':3,'pages':37,'latex_warnings':0,
    'text_matches_tagged_pdf':True,'all_rendered_pages_match_tagged_pdf':True,
    'render_comparison':'pdftoppm -scale-to 700 -png; byte-identical PNGs'},
    'note':'Source-only revision-2 archive. No upload or submission. Local TeX Live build; review arXiv-produced PDF too.'}
(OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/PAPER/'submission-package.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
