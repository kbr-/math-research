#!/usr/bin/env python3
"""Prepare source-backed registry proposals; canonical writes are deliberately separate."""
import argparse
from copy import deepcopy
import json
from pathlib import Path

from claim_registry import ROOT, REGISTRY, load, read_json, validate, require, write_json, check_targets
from claim_reviews import FIELDS, Evidence, make_review, digest
from claim_maintenance import maintenance

REQUIRED = 'REQUIRED: '


def template(identifier, existing=None):
    """An intentionally non-importable questionnaire, never an all-null claim."""
    claim = deepcopy(existing) if existing else {
        'id': identifier, 'summary': REQUIRED + 'precise summary',
        'assessment': REQUIRED + 'status and exact qualifications',
        'record': REQUIRED + 'Markdown link to dated source',
        'mathematical_status': REQUIRED + 'schema status or null with pending review',
        'formalization': REQUIRED + 'status, scope, references, artifacts object',
        'topics': REQUIRED + 'list of existing or supplied topic IDs',
        'significance': REQUIRED + 'assessment object or null with pending review'}
    claim.pop('reviews', None)
    return {'claim': claim, 'dispositions': {field: {
        'state': REQUIRED + 'reviewed, pending or not_applicable',
        'note': REQUIRED + 'field-specific finding or precise unresolved question',
        'targets': [REQUIRED + 'source evidence locator'],
        'next_action': REQUIRED + 'specific action if pending; otherwise null'} for field in FIELDS}}


def questionnaire(data, identifier):
    existing = next((c for c in data['claims'] if c['id'] == identifier), None)
    return {'base_sha256': digest(data),
            'provenance': {'revision': REQUIRED + 'immutable source revision',
                           'date': REQUIRED + 'YYYY-MM-DD', 'reviewer': REQUIRED + 'reviewer'},
            'submissions': [template(identifier, existing)], 'relationships': [], 'topic_definitions': []}


def ensure_answered(value):
    if isinstance(value, str):
        require(not value.startswith(REQUIRED), 'Unanswered authoring questionnaire: ' + value)
    elif isinstance(value, dict):
        for item in value.values():
            ensure_answered(item)
    elif isinstance(value, list):
        for item in value:
            ensure_answered(item)


def prepare(before, request, root=ROOT):
    """Return a validated full proposal without mutating before or writing any files."""
    ensure_answered(request)
    require(set(request) == {'base_sha256', 'provenance', 'submissions', 'relationships', 'topic_definitions'},
            'Unexpected/missing authoring request keys')
    require(request['base_sha256'] == digest(before), 'Registry changed: refresh questionnaire against the current base')
    require(bool(request['submissions']), 'At least one explicit claim submission is required')
    meta = request['provenance']
    require(set(meta) == {'revision', 'date', 'reviewer'}, 'Supply revision, date and reviewer')
    after = deepcopy(before)
    for key in ('relationships', 'topic_definitions'):
        known = {item['id'] for item in after[key]}
        for item in request[key]:
            require(item['id'] not in known, 'Authoring proposals append ' + key + '; existing IDs require a separate reviewed edit')
            after[key].append(deepcopy(item)); known.add(item['id'])
    positions = {claim['id']: i for i, claim in enumerate(after['claims'])}
    submitted = set()
    for submission in request['submissions']:
        require(set(submission) == {'claim', 'dispositions'}, 'Submission requires claim and dispositions only')
        claim = deepcopy(submission['claim'])
        require('reviews' not in claim, 'Supply human dispositions; hashes are generated from actual evidence')
        require(claim['id'] not in submitted, 'Duplicate claim submission')
        submitted.add(claim['id'])
        claim['reviews'] = {}
        if claim['id'] in positions:
            after['claims'][positions[claim['id']]] = claim
        else:
            after['claims'].append(claim)
    validate(after)
    evidence = Evidence(root)
    claims = {claim['id']: claim for claim in after['claims']}
    for submission in request['submissions']:
        claim = claims[submission['claim']['id']]
        dispositions = submission['dispositions']
        require(set(dispositions) == set(FIELDS), 'Supply all five explicit field dispositions')
        for field, disposition in dispositions.items():
            require(set(disposition) == {'state', 'note', 'targets', 'next_action'}, 'Unexpected/missing disposition keys')
            require(bool(disposition['note'].strip()) and bool(disposition['targets']),
                    field + ': a reason and source evidence are required')
            require(disposition['state'] != 'pending' or bool(disposition['next_action']),
                    field + ': pending question requires a next action')
            value = claim.get(field)
            if field == 'formalization':
                value = value['status']
            if field != 'relationships' and (value is None or value == []):
                require(disposition['state'] in ('pending', 'not_applicable'),
                        field + ': missing metadata cannot be marked reviewed')
            claim['reviews'][field] = make_review(after, claim, field, disposition['targets'],
                **meta, state=disposition['state'], note=disposition['note'],
                next_action=disposition['next_action'], evidence=evidence)
    validate(after)
    report = maintenance(before, after, root)
    targets = check_targets(after, root)
    require(targets['passed'], 'Broken source targets: ' + json.dumps(targets['errors']))
    report['targets'] = targets
    require(report['passed'], 'Incomplete proposal: ' + '; '.join(report['errors']))
    return after, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path, default=REGISTRY)
    sub = parser.add_subparsers(dest='mode', required=True)
    form = sub.add_parser('template', help='Write an intentionally incomplete questionnaire')
    form.add_argument('claim')
    form.add_argument('--out', type=Path, required=True)
    proposal = sub.add_parser('prepare', help='Validate completed answers and emit a full proposal')
    proposal.add_argument('--request', type=Path, required=True)
    proposal.add_argument('--out', type=Path, required=True)
    proposal.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    destinations = [args.out] + ([args.report] if args.mode == 'prepare' else [])
    require(len({p.resolve() for p in destinations}) == len(destinations), 'Output paths must differ')
    for path in destinations:
        require(path.resolve() != args.registry.resolve(), 'Proposal must not overwrite canonical input')
        require(not path.exists(), 'Refusing to overwrite existing output: ' + str(path))
    data = load(args.registry)
    if args.mode == 'template':
        write_json(args.out, questionnaire(data, args.claim))
    else:
        proposed, report = prepare(data, read_json(args.request))
        write_json(args.out, proposed)
        write_json(args.report, report)
    print('Saved ' + str(args.out) + '; canonical registry unchanged.')


if __name__ == '__main__':
    main()
