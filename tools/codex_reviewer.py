#!/usr/bin/env python3
"""Run a fresh medium/read-only native reviewer; reuse its own handle for concrete follow-ups."""
import argparse
import asyncio
import fcntl
import hashlib
import json
from pathlib import Path
import re
import sys

from codex_runtime import Client, NativeError, isolated_config, verify_isolation
from codex_state import atomic_json

ROOT = Path(__file__).resolve().parents[1]


def reviewer_brief(root):
    source = (root/'.claude/agents/medium-reviewer.md').read_text()
    # The committed body is the single source for both agents; YAML is Claude's descriptor.
    return source.split('---', 2)[2].strip()


async def review(client, root, state, text, close=False, model=None):
    saved = json.loads(state.read_text()) if state.exists() else None
    if close:
        if not saved:
            raise NativeError('No owned reviewer with this handle')
        await client.call('thread/archive', {'threadId': saved['thread']})
        state.unlink()
        return 'Owned reviewer archived.'
    if saved:
        if saved['root'] != str(root):
            raise NativeError('Reviewer handle belongs to another checkout')
        response = await client.call('thread/resume', {'threadId': saved['thread']})
    else:
        params = {'cwd': str(root), 'approvalPolicy': 'never', 'sandbox': 'read-only',
                  'ephemeral': False, 'baseInstructions': reviewer_brief(root),
                  'developerInstructions': 'Use only the supplied brief and excerpts. Edit no files.',
                  'config': isolated_config('medium')}
        if model:
            params['model'] = model
        response = await client.call('thread/start', params)
        # Persist before inference, so an interrupted controller never loses its owned session.
        atomic_json(state, {'thread': response['thread']['id'], 'root': str(root)})
    verify_isolation(response, 'medium')
    return await client.turn(response['thread']['id'], text, 'medium')


async def run(args, root=ROOT):
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.handle):
        raise ValueError('Use a plain name for the reviewer handle')
    directory = root/'.codex/framework/reviewers'
    directory.mkdir(parents=True, exist_ok=True)
    state = directory/(hashlib.sha256(args.handle.encode()).hexdigest() + '.json')
    with state.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        client = await asyncio.wait_for(Client.connect(), min(args.timeout, 5))
        try:
            text = args.brief.read_text() if args.brief else ''
            return await asyncio.wait_for(review(client, root, state, text, args.close, args.model),
                                          args.timeout)
        finally:
            await client.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--handle', required=True, help='Owned name; reuse only for a concrete correction')
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--brief', type=Path)
    action.add_argument('--close', action='store_true')
    parser.add_argument('--model', help='Optional available native model; effort remains medium')
    parser.add_argument('--timeout', type=float, default=120)
    args = parser.parse_args()
    try:
        print(asyncio.run(run(args)))
    except (OSError, ValueError, NativeError, asyncio.TimeoutError) as error:
        print('Reviewer incomplete: ' + (str(error) or type(error).__name__), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
