#!/usr/bin/env python3
"""Externally bind persistent Codex sessions in persistent Git worktrees."""
import argparse
import asyncio
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

from codex_runtime import Client, NativeError
from codex_state import atomic_json
from register_codex import register

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ('Restore this repository context. Run python3 tools/resume.py with default output '
             'allowances, including enclosing wrappers, and read every listed part in full. '
             'Retry missing parts without preparing a new bundle. Follow its restart guide. '
             'Summarize readiness without beginning a new research attempt.')


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def worktree(root, name=None, base=None):
    root = Path(git(root, 'rev-parse', '--show-toplevel')).resolve()
    common = Path(git(root, 'rev-parse', '--git-common-dir'))
    main = (root/common).resolve().parent
    if root != main and name is None:
        upstream = git(root, 'rev-parse', '--abbrev-ref', '@{upstream}')
        upstream_ref = git(root, 'rev-parse', '--symbolic-full-name', '@{upstream}')
        git(root, 'show-ref', '--verify', upstream_ref)
        if base is not None and upstream != base:
            raise ValueError('Existing worktree has a different upstream')
        return root
    base = base or git(root, 'symbolic-ref', '--short', 'HEAD')
    name = name or 'codex-' + base.replace('/', '-')
    if '/' in name or name.startswith('.') or not name or name.startswith('-'):
        raise ValueError('Use a plain persistent worktree name')
    subprocess.run(['git', 'check-ref-format', '--branch', name], check=True, capture_output=True)
    directory = main/'.codex/worktrees'/name
    directory.parent.mkdir(parents=True, exist_ok=True)
    with (directory.parent/'.creation.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not directory.exists():
            subprocess.run(['git', '-C', str(main), 'worktree', 'add', '--track', '-b', name,
                            str(directory), base], check=True)
        if git(directory, 'symbolic-ref', '--short', 'HEAD') != name:
            raise ValueError('Existing worktree is on a different branch')
        upstream = git(directory, 'rev-parse', '--abbrev-ref', '@{upstream}')
        if upstream != base:
            raise ValueError('Existing worktree has a different base; select its actual base explicitly')
    return directory


def bind(root, ident):
    ident = str(uuid.UUID(ident))
    fd, temporary = tempfile.mkstemp(dir=root, prefix='.codex-session-id.')
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(ident + '\n');stream.flush();os.fsync(stream.fileno())
        os.replace(temporary, root/'.codex-session-id')
    finally:
        Path(temporary).unlink(missing_ok=True)


async def trusted(client, root):
    response = await client.call('hooks/list', {'cwds': [str(root)]})
    entries = response['data']
    definitions = json.loads((root/'.codex/hooks.json').read_text())['hooks']
    expected = {event[0].lower() + event[1:]: [hook['command'] for group in groups
                for hook in group['hooks'] if hook.get('type') == 'command']
                for event, groups in definitions.items()}
    if not expected or any(len(commands) != 1 for commands in expected.values()):
        raise NativeError('No framework hooks are registered in this checkout')
    entries = [e for e in entries if Path(e['cwd']).resolve() == root]
    if len(entries) != 1 or entries[0].get('errors') or entries[0].get('warnings'):
        raise NativeError('Hook discovery is incomplete; review Codex hooks before startup')
    hooks = [h for h in entries[0]['hooks'] if 'tools/hooks/codex_dispatch.py' in (h.get('command') or '')]
    if any([h.get('command') for h in hooks if h['eventName'] == event] != commands
           for event, commands in expected.items()) or any(
            not h['enabled'] or h['trustStatus'] != 'trusted' for h in hooks):
        raise NativeError('Framework hooks need normal Codex trust review in ' + str(root)
                          + '; open codex --remote unix:// there and review /hooks, then retry.')


async def session(client, root, mode, context, compact):
    await trusted(client, root)
    binding = root/'.codex-session-id'
    bootstrap = root/'.codex/framework/bootstrap.json'
    previous = json.loads(bootstrap.read_text()) if bootstrap.exists() else {}
    recovered = None
    if not binding.exists() and previous.get('thread') and previous.get('bound') is False and mode != 'new':
        ident = previous['thread']
        response = await client.call('thread/resume', {'threadId': ident, 'excludeTurns': True})
        if response['thread']['id'] != ident or Path(response['cwd']).resolve() != root:
            raise NativeError('Incomplete session belongs to a different worktree')
        bind(root, ident)
        recovered = response
    if binding.exists() and mode != 'new':
        ident = str(uuid.UUID(binding.read_text().strip()))
        # No permission overrides on resume; preserve the exact thread's saved policy.
        response = recovered or await client.call('thread/resume', {'threadId': ident, 'excludeTurns': True})
        if response['thread']['id'] != ident or Path(response['cwd']).resolve() != root:
            raise NativeError('Recorded session belongs to a different worktree')
    else:
        if mode == 'resume':
            raise NativeError('No session ID is recorded; start without --resume')
        response = await client.call('thread/start', {
            'cwd': str(root), 'runtimeWorkspaceRoots': [str(root)], 'ephemeral': False,
            'approvalPolicy': 'on-request', 'approvalsReviewer': 'auto_review',
            'permissions': ':workspace', 'config': {
                'model_context_window': context, 'model_auto_compact_token_limit': compact}})
        ident = str(uuid.UUID(response['thread']['id']))
        if Path(response['cwd']).resolve() != root:
            raise NativeError('Created session belongs to a different worktree')
        atomic_json(bootstrap, {'thread': ident, 'accepted': False, 'bound': False})
        await client.call('thread/inject_items', {'threadId': ident, 'items': [{
            'type': 'message', 'role': 'user', 'content': [{'type': 'input_text',
            'text': 'External launcher initialized this session. Await the restoration request.'}]}]})
        bind(root, ident)
        atomic_json(bootstrap, {'thread': ident, 'accepted': False, 'bound': True})
    pending = json.loads(bootstrap.read_text()) if bootstrap.exists() else {}
    if pending.get('thread') == ident and not pending.get('accepted'):
        # A transport failure leaves the exact binding and pending bootstrap for explicit retry.
        await client.call('turn/start', {'threadId': ident, 'input': [{'type': 'text', 'text': BOOTSTRAP}]})
        atomic_json(bootstrap, {'thread': ident, 'accepted': True})
    return ident


async def launch(args):
    root = worktree(ROOT, args.worktree, args.base)
    register(root)
    with (root/'.codex/framework/launcher.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        client = await Client.connect()
        try:
            ident = await asyncio.wait_for(session(client, root, args.mode, args.context, args.compact), 10)
        finally:
            await client.close()
    return root, ident


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--new', dest='mode', action='store_const', const='new')
    modes.add_argument('--resume', dest='mode', action='store_const', const='resume')
    parser.set_defaults(mode='auto')
    parser.add_argument('--detached', action='store_true')
    parser.add_argument('--worktree')
    parser.add_argument('--base')
    parser.add_argument('--context', type=int, required=True)
    parser.add_argument('--compact', type=int, required=True)
    args = parser.parse_args()
    if os.environ.get('CODEX_THREAD_ID'):
        parser.error('Run the launcher outside an agent; workers cannot replace bindings')
    try:
        root, ident = asyncio.run(launch(args))
    except (OSError, ValueError, NativeError, asyncio.TimeoutError, subprocess.CalledProcessError) as error:
        print('Codex startup incomplete: ' + (str(error) or type(error).__name__), file=sys.stderr)
        return 1
    if args.detached:
        print(f'Persistent session bound in {root}; attach with ./start-session.sh --resume there.')
    else:
        os.chdir(root)
        os.execvp('codex', ['codex', 'resume', ident, '--remote', 'unix://'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
