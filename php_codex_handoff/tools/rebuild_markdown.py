#!/usr/bin/env python3
"""Regenerate the reading copy from immutable LaTeX; requires Pandoc.
No theorem is verified by this conversion. Equations are kept as raw LaTeX.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, re, shutil, subprocess, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
KINDS = {'lemma':'Lemma','theorem':'Theorem','corollary':'Corollary',
         'imported':'Imported input','example':'Example','definition':'Definition','problem':'Open target'}
ENV = r'\\begin\{('+'|'.join(KINDS)+r')\}(?:\[([^\]]*)\])?(?:\s*\\label\{([^}]+)\})?'
EVENT = re.compile(r'\\chapter\{([^}]+)\}(?:\\label\{([^}]+)\})?|'+ENV)

def digest(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def anchor(s: str) -> str: return s.replace(':','-').replace('_','-')

def main() -> None:
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'manuscript');args=ap.parse_args()
    if not shutil.which('pandoc'): raise SystemExit('Pandoc is required only to regenerate; the Markdown files are already included.')
    st=time.perf_counter();out=args.out;chdir=out/'chapters';chdir.mkdir(parents=True,exist_ok=True)
    src=ROOT/'manuscript/latex';paths=sorted(src.glob('[0-9]*.tex'));sources={p.name:p.read_text() for p in paths}
    maintex=(src/'main.tex').read_text()
    macros='\n'.join(l for l in maintex.splitlines() if l.startswith(('\\newcommand','\\DeclareMathOperator')) and not l.startswith('\\newcommand{\\chapterintro}'))
    macros+='\n\\newcommand{\\chapterintro}[1]{\\begin{quote}#1\\end{quote}}\n'
    (out/'macros.tex').write_text(macros)
    labelmap={};records=[];chapter_no=0;counter=0;chapter='';chapter_title=''
    positions={}
    for name,s in sources.items():
        positions[name]={}
        for m in EVENT.finditer(s):
            if m.group(1) is not None:
                chapter_no+=1;chapter=str(chapter_no) if chapter_no<=10 else chr(65+chapter_no-11);counter=0
                chapter_title=m.group(1);lab=m.group(2) or f'chapter-{chapter}'
                rec={'kind':'chapter','number':chapter,'title':chapter_title,'label':lab,'anchor':anchor(lab),'source':name,'line':s.count('\n',0,m.start())+1}
            else:
                counter+=1;kind,title,lab=m.group(3),m.group(4),m.group(5)
                lab=lab or f'{kind}-{chapter}-{counter}'
                start=m.end();end=s.find('\\end{'+kind+'}',start)
                statement=s[start:end].strip()
                proof='';endline=s.count('\n',0,max(end,start))+1
                following=s[end+len('\\end{'+kind+'}'):]
                pm=re.match(r'\s*\\begin\{proof\}(.*?)\\end\{proof\}',following,re.S)
                if pm: proof=pm.group(1).strip();endline=s.count('\n',0,end+len('\\end{'+kind+'}')+pm.end())+1
                refs=sorted(set(r.strip() for g in re.findall(r'\\(?:[cC]ref|eqref|ref)\{([^}]+)\}',statement+'\n'+proof) for r in g.split(',')))
                status='imported' if kind=='imported' else 'example' if kind=='example' else 'open' if kind=='problem' else 'working-proof'
                if lab in ('thm:rigidity','thm:conditionalpayoff'):status='conditional-working-proof'
                rec={'kind':kind,'number':chapter+'.'+str(counter),'title':title or '', 'label':lab,'anchor':anchor(lab),
                     'chapter':chapter,'chapter_title':chapter_title,'source':name,'line':s.count('\n',0,m.start())+1,'end_line':endline,
                     'status':status,'statement_latex':statement,'proof_latex':proof,'references':refs}
                records.append(rec)
            rec['markdown']='chapters/'+name.replace('.tex','.md')
            labelmap[rec['label']]=rec;positions[name][m.start()]=rec
        for lab in re.findall(r'\\label\{([^}]+)\}',s):
            if lab not in labelmap:labelmap[lab]={'kind':'equation','label':lab,'anchor':anchor(lab),'markdown':'chapters/'+name.replace('.tex','.md'),'source':name}
    warnings=[];generated=[]
    def refrepl(m):
        refs=m.group(2).split(',');links=[]
        for label in refs:
            label=label.strip();r=labelmap.get(label)
            if not r: warnings.append('Unresolved '+label);links.append('\\texttt{'+label+'}');continue
            text=('Chapter '+r['number']) if r['kind']=='chapter' else ('Equation '+label) if r['kind']=='equation' else KINDS[r['kind']]+' '+r['number']
            links.append('\\href{'+Path(r['markdown']).name+'#'+r['anchor']+'}{'+text+'}')
        return ', '.join(links)
    for name,s in sources.items():
        # Replace headings and environments without touching their mathematical bodies.
        def evt(m):
            r=positions[name][m.start()]
            if r['kind']=='chapter':return '\\chapter{'+r['number']+'. '+r['title']+'}\\label{'+r['label']+'}'
            return '\\subsection*{'+KINDS[r['kind']]+' '+r['number']+': '+r['title']+'}\\label{'+r['label']+'}'
        text=EVENT.sub(evt,s)
        text=re.sub(r'\\end\{(?:'+'|'.join(KINDS)+r')\}','',text)
        text=text.replace('\\begin{proof}','\\textbf{Proof.}').replace('\\end{proof}','\\emph{End of proof.}')
        for typ,title in [('remark','Scope'),('editorial','Editorial clarification'),('statusbox','Status')]:
            text=text.replace('\\begin{'+typ+'}','\\paragraph*{'+title+'}').replace('\\end{'+typ+'}','')
        text=re.sub(r'\\(cref|Cref|ref|eqref)\{([^}]+)\}',refrepl,text)
        # Tables use layout-only custom L{width} columns. Pandoc needs ordinary columns.
        text=re.sub(r'\\begin\{(longtable|tabular)\}\{@\{\}(.*?)@\{\}\}',lambda m:'\\begin{'+m.group(1)+'}{'+'l'*max(1,len(re.findall(r'L\{',m.group(2))))+'}',text)
        text=text.replace('\\endhead','')
        text=re.sub(r'\\path\{([^}]+)\}',lambda m:r'\verb|'+m.group(1)+'|',text)
        result=subprocess.run(['pandoc','-f','latex','-t','markdown+tex_math_dollars+raw_tex','--wrap=none'],input=macros+'\n\\begin{document}\n'+text+'\n\\end{document}',text=True,capture_output=True,check=True)
        if result.stderr.strip():warnings.append(name+': '+result.stderr.strip())
        md=result.stdout
        # Stable anchors work in both rendered Markdown and a text-only agent.
        md=re.sub(r'^(#+) (.*?) \{#([^ }]+)[^}]*\}$',lambda m:'<a id="'+anchor(m.group(3))+'"></a>\n\n'+m.group(1)+' '+m.group(2),md,flags=re.M)
        # Equation labels are kept in the math and also exposed as navigable anchors.
        for lab in re.findall(r'\\label\{([^}]+)\}',md):
            marker='<a id="'+anchor(lab)+'"></a>\n\n'
            pos=md.find('\\label{'+lab+'}');start=md.rfind('$$',0,pos)
            if start<0:start=pos
            md=md[:start]+marker+md[start:]
        # Explicit bibliography links rather than unresolved citation tokens.
        md=re.sub(r'\[@([A-Za-z]+)([^\]]*)\]',lambda m:'['+m.group(1)+m.group(2)+'](../../references/README.md#'+m.group(1).lower()+')',md)
        md=re.sub(r'\[@([^\]]+)\]',lambda m:'['+m.group(1).replace('@','')+'](../../references/README.md)',md)
        header='<!-- Generated from ../latex/'+name+'. Do not silently edit this reading copy. -->\n\n'
        md=header+md
        dest=chdir/name.replace('.tex','.md');dest.write_text(md);generated.append(dest)
    # Front matter is retained independently of the mathematical chapters.
    intro=maintex.split('\\chapter*{How to read this record}',1)[1].split('\\tableofcontents',1)[0]
    intro=re.sub(r'\\addcontentsline\{toc\}\{chapter\}\{[^}]*\}','',intro)
    intro=re.sub(r'\\(cref|Cref|ref|eqref)\{([^}]+)\}',refrepl,intro)
    intro=re.sub(r'\\begin\{(longtable|tabular)\}\{@\{\}(.*?)@\{\}\}',lambda m:'\\begin{'+m.group(1)+'}{'+'l'*max(1,len(re.findall(r'L\{',m.group(2))))+'}',intro)
    r=subprocess.run(['pandoc','-f','latex','-t','markdown+tex_math_dollars+raw_tex','--wrap=none'],input=macros+'\n\\begin{document}\n'+intro+'\n\\end{document}',text=True,capture_output=True,check=True)
    front='# How to read this record\n\n'+r.stdout
    front=re.sub(r'\]\((\d\d_[^)]*\.md#[^)]*)\)',r'](chapters/\1)',front)
    (out/'00_reading_guide.md').write_text(front)
    # Full reading copy links to the split chapters, whose anchors are canonical.
    full='# Pigeonhole Designs and Extension Elimination\n\nFull raw-LaTeX Markdown reading copy. Source snapshot: 10 September 2026.\n\n'
    full+='This conversion preserves the working status of the manuscript; it is not a new proof audit. The exact original source is in `latex/`.\n\n'+front+'\n\n'
    for p in generated:
        md=p.read_text();md=re.sub(r'\]\((\d\d_[^)]*\.md#[^)]*)\)',r'](chapters/\1)',md);md=md.replace('../../references/','../references/')
        full+='\n\n---\n\n'+md
    (out/'FULL_RESEARCH.md').write_text(full)
    (out/'claims.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    (out/'labels.json').write_text(json.dumps(labelmap,ensure_ascii=False,indent=2)+'\n')
    idx=['# Claim index','', 'Source numbering and labels are stable. **Working proof** means an argument is present in the conversation compendium, not independent verification. Imported and conditional statements are marked separately.','', '| Claim | Title | Status | Exact source |','|---|---|---|---|']
    for r in records:
        title=r['title'].replace('|','\\|')
        idx.append(f"| [{KINDS[r['kind']]} {r['number']}]({r['markdown']}#{r['anchor']}) | {title} | {r['status']} | [`{r['label']}`](latex/{r['source']}#L{r['line']}) |")
    (out/'CLAIM_INDEX.md').write_text('\n'.join(idx)+'\n')
    # Compare structural coverage, not theorem truth.
    expected=sum(s.count('\\begin{proof}') for s in sources.values());actual=sum(p.read_text().count('End of proof.') for p in generated)
    expected_eq=sum(len(re.findall(r'\\label\{eq:[^}]+\}',s)) for s in sources.values())
    got_eq=sum(len(re.findall(r'<a id="eq-[^"]+"',p.read_text())) for p in generated)
    report={'source_files':len(paths),'source_proofs':expected,'markdown_proofs':actual,'claims':len(records),
      'working_results':sum(r['kind'] in ['lemma','theorem','corollary'] for r in records),
      'equation_anchors_expected':expected_eq,'equation_anchors_actual':got_eq,'warnings':warnings,
      'source_sha256':{p.name:digest(p) for p in paths},'elapsed_s':time.perf_counter()-st,
      'scope':'Structural conversion checks only. Not a mathematical audit.'}
    (ROOT/'provenance/markdown_conversion.json').write_text(json.dumps(report,indent=2)+'\n')
    if expected!=actual or expected_eq!=got_eq:raise SystemExit('Structural coverage mismatch; inspect provenance/markdown_conversion.json')
    print(json.dumps({k:v for k,v in report.items() if k!='source_sha256'},indent=2))
if __name__=='__main__':main()
