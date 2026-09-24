#!/usr/bin/env python3
"""Create/select a research notebook. Context JSON is agent-reviewed HTML, not generated mathematics."""
# SPDX-License-Identifier: MIT
import argparse
import html
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from notebooks import ROOT, PUBLIC, catalogue, selected, select, valid_name
from notebook_context import budgets

SECTIONS = {'before-this-notebook':'Starting point', 'where-we-stand':'Where we stand',
            'open-statements':'Open statements', 'remaining-route':'The remaining route', 'proposed-next-step':'Proposed next step',
            'working-context':'Working mathematical context', 'formalization-gaps':'Gaps identified by formalization'}

OPEN_STATEMENTS_WORDS = 300


def create(name,title,context,root=ROOT,parent='main',origin=None):
    valid_name(name); items=catalogue(root)
    if name in items: raise ValueError('Notebook already exists; use select to resume it')
    selected(parent,root)
    if set(context) != {'goal',*SECTIONS} or not all(isinstance(v,str) and v.strip() for v in context.values()):
        raise ValueError('Context JSON needs nonempty goal and all seven living-section HTML values')
    if origin:
        from claim_registry import local_target,file_anchors
        target=local_target(origin,root)
        if not target or not target[0].is_file() or not target[1] or target[1] not in file_anchors(target[0]):
            raise ValueError('Origin must be an existing notebook entry/claim source URL with anchor')
        if target[0].resolve() not in {(root/i['source']).resolve() for i in items.values()}:
            raise ValueError('Origin must resolve to a registered notebook')
    for value in context.values():
        if any(token in value.lower() for token in ('<script','<article','<section','</section','<!-- timing')):
            raise ValueError('Context must contain only living-section contents, no scripts, articles or sections')
    source = f'<h1>{html.escape(title)}</h1>\n<p class="intro">{context["goal"]}</p>\n'
    if origin:
        source += f'<p>Origin: <a href="{html.escape(origin,quote=True)}">starting research record</a>.</p>\n'
    for key,label in SECTIONS.items():
        source += f'<section id="{key}">\n<h2>{label}</h2>\n{context[key]}\n</section>\n'
    source += '<section id="research-record">\n<h2>Research record</h2>\n</section>\n'
    config=json.loads((root/'research/context-budgets.json').read_text())
    # Every thread keeps its open statements; older configs predate the section.
    config['regions'].setdefault('open-statements',OPEN_STATEMENTS_WORDS)
    report=budgets(source,config)
    if not report['passed']:raise ValueError('Initial context exceeds hard budgets')
    if 'data-route-item=' not in context['remaining-route']:
        raise ValueError('Remaining route must declare at least one data-route-item')
    directory=root/'research/branches';directory.mkdir(parents=True,exist_ok=True)
    if directory.is_symlink():raise ValueError('Unsafe branch directory')
    destination=directory/name
    if destination.exists():raise ValueError('Branch directory already exists; inspect interrupted setup')
    temporary=Path(tempfile.mkdtemp(prefix='.creating-',dir=directory))
    try:
        (temporary/'notebook.html').write_text(source)
        (temporary/'context-budgets.json').write_text(json.dumps(config,indent=2)+'\n')
        (temporary/'notebook.json').write_text(json.dumps(dict(version=1,name=name,title=title,status='active',parent=parent,origin=origin),indent=2)+'\n')
        # Rename makes registration/source/budget appear together. Never overwrite a thread.
        if destination.exists():raise ValueError('Thread appeared during setup; retry with another name')
        temporary.rename(destination)
    finally:
        if temporary.exists():shutil.rmtree(temporary)
    return selected(name,root)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('list')
    pick=sub.add_parser('select');pick.add_argument('name')
    status=sub.add_parser('status');status.add_argument('name');status.add_argument('state',choices=['active','completed','abandoned'])
    new=sub.add_parser('create');new.add_argument('name');new.add_argument('--title',required=True)
    new.add_argument('--context',type=Path,required=True);new.add_argument('--parent',default='main');new.add_argument('--origin')
    new.add_argument('--git-branch',help='Optionally create and switch to a Git branch in this worktree')
    new.add_argument('--select',action='store_true')
    args=parser.parse_args()
    try:
        if args.command=='list':
            print(json.dumps(list(catalogue().values()),indent=2));return
        if args.command=='select':item=select(args.name)
        elif args.command=='status':
            item=selected(args.name)
            if args.name=='main':raise ValueError('Main lifecycle is not managed here')
            p=ROOT/item['source'];meta=p.with_name('notebook.json');d=json.loads(meta.read_text());d['status']=args.state
            meta.write_text(json.dumps(d,indent=2)+'\n');item=selected(args.name)
        else:
            if args.git_branch:
                subprocess.run(['git','check-ref-format','--branch',args.git_branch],cwd=ROOT,check=True,capture_output=True)
                if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():
                    raise ValueError('Use a clean worktree for --git-branch; unrelated edits are not stashed')
                if subprocess.run(['git','show-ref','--verify','--quiet','refs/heads/'+args.git_branch],cwd=ROOT).returncode==0:
                    raise ValueError('Git branch already exists')
            item=create(args.name,args.title,json.loads(args.context.read_text()),parent=args.parent,origin=args.origin)
            if args.git_branch:
                subprocess.run(['git','switch','-c',args.git_branch],cwd=ROOT,check=True)
            if args.select:item=select(args.name)
        print(json.dumps(dict(notebook=item['name'],source=item['source'],public_url=PUBLIC+item['route'],
                             publication='URL becomes public only after an authorized deployment'),indent=2))
    except (OSError,ValueError,subprocess.CalledProcessError) as error:parser.exit(2,f'branch: {error}\n')

if __name__=='__main__':main()
