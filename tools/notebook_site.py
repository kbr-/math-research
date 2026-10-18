"""Shared navigation and public source payloads; never expose arbitrary repository files."""
# SPDX-License-Identifier: MIT
import hashlib
import html
import json
import posixpath
import re
from pathlib import Path

from notebooks import ROOT, catalogue, selected, PUBLIC
from notebook_math import protect_math


def relative(route, current):
    return posixpath.relpath(route or '.', current or '.') + ('/' if not route or route.endswith('/') else '')


def navigation(root, name):
    items=catalogue(root);item=items[name]
    links=' · '.join(f'<a href="{html.escape(relative(i["route"],item["route"]),quote=True)}">{html.escape(i["title"])}</a> ({i["status"]})' for i in items.values())
    return ('<nav class="thread-navigation" aria-label="Research notebooks">'
            f'<strong>{html.escape(item["title"])}</strong> · {item["status"]}'
            f'<details><summary>Research notebooks ({len(items)})</summary>{links}</details></nav>')


def source(root, name):
    item=selected(name,root)
    body=(root/item['source']).read_text()
    # Public notebook hyperlinks also work when served locally and below a project prefix.
    for other in catalogue(root).values():
        for host in ('https://kbr.is-a.dev/math-research/','https://kbr-.github.io/math-research/'):
            body=body.replace('href="'+host+other['route']+'#','href="'+relative(other['route'],item['route'])+'#')
    return protect_math(body)


def manifest(root):
    return [dict(name=i['name'],title=i['title'],status=i['status'],url=i['route'],
                 source=i['route']+'notebook-source.html') for i in catalogue(root).values()]


def decorate(template,root,name):
    item=selected(name,root)
    template=template.replace('<!-- THREAD NAVIGATION -->',navigation(root,name))
    # Root-level data is fetched only when all-notebooks search is requested.
    return template.replace('<!-- THREAD SETTINGS -->',
        '<script>window.notebookThread = '+__import__('json').dumps(dict(name=name,title=item['title'],
         catalogue=relative('notebooks.json',item['route'])),ensure_ascii=True).replace('<','\\u003c')+';</script>')


def snapshot(root=ROOT, notebook_name="main"):
    """Return the decorated template, public notebook source, and their raw-source revision."""
    root = Path(root)
    template = (root / "index.html").read_text(encoding="utf-8")
    template = decorate(template, root, notebook_name)
    notebook = source(root, notebook_name)
    revision = hashlib.sha256(json.dumps([template, notebook]).encode()).hexdigest()
    return template, notebook, revision
