#!/usr/bin/env python3
"""A judge of whether a research entry takes the shortest route to its notebook's goal.

The user, 17 October 2026: "When you identify a direct shortest route above all else, you prioritize it above all
else. You do not keep orbiting around the goal and producing math just for the sake of producing math." Nine
cycles in a row had proved exclusions after the record's own obstructions named the construction a proof needs.

The judge (Sonnet, through tools/haiku_judge.py; Haiku passed the prompting case, the linear-flow entry, as on
route because its review had scheduled it, research/provenance/framework/route-judge-replay-20261017.txt) is given the notebook's living sections that state the goal and
the route (Where we stand, Open statements, The remaining route, Proposed next step), the latest review's Obstacle
and Decision, and the draft's Question, Shortest route and New mathematics paragraphs, and answers whether the
draft takes the most direct step the record names toward the goal. tools/notebook-append.py calls it on every
research entry: a verdict "detour" is refused unless the draft's Shortest route paragraph says "Not taken" with a
reason of at least eight words; a failed call lets the append through with a printed notice, so the judge never
blocks work on its own outage.

Usage: python3 tools/route_judge.py DRAFT --notebook NOTEBOOK.html   (prints the verdict as JSON)
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import haiku_judge
import notebook_math
import notebooks

TIMEOUT = 90
MODEL = 'claude-sonnet-5-5'
LIVING = ('where-we-stand', 'open-statements', 'remaining-route', 'proposed-next-step')
PARAGRAPHS = ('Question', 'Shortest route', 'New mathematics')

PROMPT = '''A research notebook pursues one goal. Its living sections state the goal, what is proved, what remains, and
the next step; its latest route review names the obstacle and decides the next work. A new entry is drafted.

Decide one thing: does the new entry take the shortest, most direct route to the goal that the record itself names
(the construction, proof or test whose success would most directly advance the goal), or is it a detour (work
around the goal: excluding one more class, a side lemma, bookkeeping) while a more direct step is named and untaken?
Judge only from the text below. A review's Decision that schedules the entry does not make it on route: reviews
can schedule detours too, so judge against the goal and the named obstacle, not the schedule. Excluding one more
class of candidates is a detour while a candidate construction the record names is still unbuilt; proving that
some construction cannot work is not building one. While the record names no direct step at all (no construction
or proof route toward the goal is identified), exploring the field, obstructions included, is on route. An entry whose
step the direct step concretely needs first (a lemma the construction uses) is on route.

Answer with JSON only: {{"verdict": "on-route" or "detour", "shortest": "<the most direct step the record names, one
sentence>", "reason": "<one sentence>"}}

THE RECORD:
{record}

THE NEW ENTRY:
{entry}
'''


def strip_tags(text):
    return re.sub(r'\s+', ' ', notebook_math.strip_tags(text)).strip()


def record_text(notebook):
    """The living sections and the latest review's Obstacle and Decision, as plain text."""
    parts = []
    for name in LIVING:
        start = notebook.find(f'<section id="{name}"')
        if start >= 0:
            parts.append(strip_tags(notebook[start:notebook.index('</section>', start)])[:4000])
    reviews = list(re.finditer(r'<article id="[^"]+"[^>]*data-kind="review"[^>]*>.*?</article>', notebook, re.S))
    if reviews:
        last = reviews[-1].group(0)
        for label in ('Obstacle', 'Decision'):
            found = (re.search(r'<h4>Obstacle</h4>(.*?)<h4>', last, re.S) if label == 'Obstacle'
                     else re.search(r'<strong>Decision\.</strong>(.*?)</p>', last, re.S))
            if found:
                parts.append(f'Latest review, {label}: ' + strip_tags(found.group(1))[:2000])
    return '\n\n'.join(parts)


def entry_text(draft):
    """The draft's title and its Question, Shortest route and New mathematics paragraphs."""
    title = re.search(r'<h3>(.*?)</h3>', draft, re.S)
    parts = [f'Title: {strip_tags(title.group(1))}'] if title else []
    for label in PARAGRAPHS:
        found = re.search(rf'<p><strong>{label}\.</strong>(.*?)</p>', draft, re.S)
        if found:
            parts.append(f'{label}: ' + strip_tags(found.group(1))[:1500])
    return '\n'.join(parts)


SHORTEST = re.compile(r'<p><strong>Shortest route\.</strong>(.*?)</p>', re.S)
NOT_TAKEN = re.compile(r'\bNot taken\b[:,]?\s+((?:\S+\s+){7,}\S+)', re.I)


def shortest_paragraph(draft):
    found = SHORTEST.search(draft)
    return strip_tags(found.group(1)) if found else ''


def sonnet(prompt, timeout):
    return haiku_judge.ask(prompt, timeout, model=MODEL)


def judge(draft, notebook, ask=sonnet):
    """The judge's answer, a dict with verdict, shortest and reason; raises haiku_judge.Failed on failure."""
    answer = ask(PROMPT.format(record=record_text(notebook), entry=entry_text(draft)), TIMEOUT)
    verdict = str(answer.get('verdict', '')).strip().lower()
    if verdict not in ('on-route', 'detour'):
        raise haiku_judge.Failed(f'the judge answered no verdict: {answer!r}')
    return {'verdict': verdict, 'shortest': str(answer.get('shortest', '')), 'reason': str(answer.get('reason', ''))}


def refusal(draft, notebook, ask=sonnet, notice=sys.stderr):
    """The reason to refuse a research draft on route grounds, or None. A draft without a Shortest route paragraph
    is refused without asking; a detour is refused unless that paragraph says "Not taken" with a reason."""
    said = shortest_paragraph(draft)
    if len(said) < 40:
        return ('a research entry states, in a <p><strong>Shortest route.</strong> paragraph of at least 40 '
                'characters, the most direct step toward the goal that the record names and whether this entry '
                'takes it, or "Not taken" with the concrete reason (AGENTS.md, order of work: shortest route first)')
    try:
        verdict = judge(draft, notebook, ask)
    except haiku_judge.Failed as error:
        print(f'route judge not consulted ({error}); the append goes on', file=notice)
        return None
    print(f'route judge: {verdict["verdict"]}; shortest named: {verdict["shortest"]}; {verdict["reason"]}',
          file=notice)
    if verdict['verdict'] == 'detour' and not NOT_TAKEN.search(said):
        return (f'the route judge reads this entry as a detour ({verdict["reason"]}); its shortest step: '
                f'{verdict["shortest"]}. Take that step, or say in the Shortest route paragraph "Not taken" and the '
                'concrete reason, in at least eight words (AGENTS.md, order of work: shortest route first)')
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('draft')
    parser.add_argument('--notebook', required=True)
    args = parser.parse_args()
    print(json.dumps(judge(Path(args.draft).read_text(), notebooks.notebook_file(args.notebook).read_text()), indent=1))


if __name__ == '__main__':
    main()
