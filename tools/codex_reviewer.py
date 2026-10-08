#!/usr/bin/env python3
"""Archive owned legacy root reviewers; new reviews use native subagents (tools/CODEX.md)."""
import argparse
import asyncio
import fcntl
import hashlib
import json
from pathlib import Path
import re
import sys
import uuid

from codex_runtime import Client, NativeError

ROOT = Path(__file__).resolve().parents[1]


RETIRED = ('Root reviewer sessions are retired. Use collaboration.spawn_agent with fork_turns="none", '
           'model="gpt-6.1-sol", reasoning_effort="medium"; see tools/CODEX.md. '
           'Use --close only to archive an existing owned legacy reviewer.')


async def review(client, root, state, text, close=False, model=None):
    if not close:
        raise NativeError(RETIRED)
    if not state.exists():
        raise NativeError('No owned reviewer with this handle')
    saved = json.loads(state.read_text())
    if saved['root'] != str(root):
        raise NativeError('Reviewer handle belongs to another checkout')
    ident = str(uuid.UUID(saved['thread']))
    await client.call('thread/archive', {'threadId': ident})
    state.unlink()
    return 'Owned reviewer archived.'


async def run(args, root=ROOT):
    if not args.close:
        raise NativeError(RETIRED)
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
    parser.add_argument('--handle', required=True, help='Existing owned legacy reviewer handle')
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--brief', type=Path, help='Retired; refuses new root reviews')
    action.add_argument('--close', action='store_true')
    parser.add_argument('--model', help=argparse.SUPPRESS)
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
