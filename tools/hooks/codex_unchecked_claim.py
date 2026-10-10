#!/usr/bin/env python3
"""Native Codex Stop adapter for the checks of stop_checks.py: requests waiting for the judge, promises,
and unchecked claims, through the shared predicate and prompt.

Its file name is the path main's tools/hooks/codex_dispatch.py loads it by.
"""
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
from urllib.parse import urlsplit, urlunsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stop_checks import (PROMPT, MAX_CALLS, CALL_CHARS, checks_off, gap_block, promise_block, validate_verdict,
                         waiting_block)

ROOT = Path(__file__).resolve().parents[2]
JUDGE_TIMEOUT = 6.5
MAX_TRANSCRIPT = 16 * 1024 * 1024
SCHEMA = {'type': 'object', 'properties': {
    'kind': {'type': 'string', 'enum': ['workaround', 'missing-feature', 'other']},
    'quote': {'type': 'string'}, 'tool': {'type': 'string'},
    'checked': {'type': 'boolean'}, 'declared': {'type': 'boolean'}, 'reason': {'type': 'string'}},
    'required': ['kind', 'quote', 'tool', 'checked', 'declared', 'reason'],
    'additionalProperties': False}
COMPACT = ('\nKeep the JSON compact. For kind other use empty quote, tool and reason. '
           'Otherwise use at most eight words for reason. Do not explain your reasoning. '
           'Evidence descriptions omit query text, URL paths and source contents; '
           'do not infer that no lookup occurred just because those details are omitted.\n')


def safe(value, limit=CALL_CHARS):
    text = ' '.join(str(value).split())
    text = re.sub(r'(?i)(?:bearer\s+|(?:password|token|api[_-]?key|secret)\s*[=:]\s*)\S+', '[redacted]', text)
    text = re.sub(r'\b(?:sk-[A-Za-z0-9_-]+|gh[pousr]_[A-Za-z0-9_]+)\b', '[redacted]', text)
    return text[:limit]


def url(value):
    parts = urlsplit(str(value))
    # No credentials, query parameters or fragments are evidence of a capability lookup.
    return safe(urlunsplit((parts.scheme, parts.hostname or '', '', '', '')))


def shell(command):
    if isinstance(command, list):
        if len(command) >= 3 and Path(command[0]).name in ('bash', 'sh', 'zsh'):
            command = command[-1]
        else:
            command = shlex.join(command)
    if not isinstance(command, str):
        raise ValueError('Unsupported shell event')
    # Never forward inline program bodies, arbitrary command arguments or command output.
    first = command.splitlines()[0] if command.splitlines() else ''
    try:
        words = shlex.split(first)
    except ValueError:
        if '\n' not in command:
            raise
        # A quoted argument may span lines. Read only the executable, avoiding
        # inline program/heredoc bodies and arbitrary argument contents.
        lexer = shlex.shlex(command, posix=True)
        lexer.whitespace_split = True
        words = [next(lexer)]
        first = ''
    names = []
    for word in words:
        if re.fullmatch(r'(?:\./)?(?:tools|research/tools|tests)/[A-Za-z0-9_./-]+', word):
            names.append(word)
    program = Path(words[0]).name if words else 'empty'
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', program):
        program = 'shell'
    help_requested = ' --help' in ' '+first or program in ('man', 'help')
    return safe('shell: '+program+(' help lookup' if help_requested else '')+' '+', '.join(names))


def item_description(item):
    kind = item.get('type')
    if kind == 'CommandExecution':
        parsed = item.get('parsed_cmd') or []
        descriptions = []
        for command in parsed:
            if command.get('type') == 'read':
                descriptions.append('read: file (path omitted)')
            elif command.get('type') == 'search':
                descriptions.append('search: repository text (query omitted)')
        return '; '.join(descriptions)[:CALL_CHARS] if descriptions else shell(item.get('command'))
    if kind == 'Extension' and item.get('kind') == 'web.search':
        action = item.get('action') or {}
        if action.get('type') == 'openPage':
            return 'web open: '+url(action.get('url', ''))
        return 'web search (query omitted)'
    if kind in ('McpToolCall', 'mcpToolCall'):
        description = 'MCP: '+safe(item.get('server', ''))+'/'+safe(item.get('tool', ''))
        arguments = item.get('arguments') or {}
        if isinstance(arguments, dict):
            if isinstance(arguments.get('url'), str):
                description += ' '+url(arguments['url'])
            elif isinstance(arguments.get('query'), str):
                description += ' query lookup (contents omitted)'
        return description[:CALL_CHARS]
    if kind == 'FileChange':
        return 'file edit (contents omitted)'
    # Like Claude Code's non-tool transcript blocks, lifecycle notifications
    # contain no lookup evidence. In particular, a reviewer finishing proves no claim.
    if kind in ('Reasoning', 'AgentMessage', 'UserMessage', 'ContextCompaction', 'Plan', 'HookPrompt',
                'SubAgentActivity', 'subAgentActivity'):
        return None
    raise ValueError('Unsupported completed tool event: type='+event_tag(kind)
                     +'; kind='+event_tag(item.get('kind')))


def event_tag(value):
    """Diagnostic discriminator only, never arbitrary event contents or identifiers."""
    if value is None:
        return '<missing>'
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]{0,79}', value):
        return '<invalid>'
    return safe(value)


def said(path):
    """What the assistant wrote in the newest turn, oldest first, from the same bounded read as evidence():
    the text of each completed AgentMessage item and each Reasoning item's summary. A rollout that cannot be
    read gives none: the final reply is checked whatever this finds."""
    if not path:
        return []
    try:
        with open(path, 'rb') as file:
            size = file.seek(0, 2)
            file.seek(max(0, size-MAX_TRANSCRIPT))
            lines = file.read().splitlines()
    except OSError:
        return []
    texts = []
    for line in reversed(lines):
        try:
            entry = json.loads(line)
            payload = entry.get('payload') or {}
            item = payload.get('item') or {}
            if entry.get('type') == 'event_msg' and (payload.get('type') in ('user_message', 'task_started')
                                                     or item.get('type') == 'UserMessage'):
                break
            if entry.get('type') == 'response_item' and payload.get('type') == 'message' and payload.get('role') == 'user':
                break
            if entry.get('type') != 'event_msg' or payload.get('type') != 'item_completed':
                continue
            if item.get('type') == 'AgentMessage':
                parts = [part.get('text') for part in item.get('content') or [] if isinstance(part, dict)]
            elif item.get('type') == 'Reasoning':
                parts = item.get('summary_text') or []
            else:
                continue
            text = '\n'.join(part for part in parts if isinstance(part, str))
            if text.strip():
                texts.append(text)
        except (ValueError, TypeError, AttributeError):
            continue
    return texts[::-1]


def evidence(path):
    """Bounded newest-turn reader. Gaps are explicit, never represented as no calls."""
    if not path:
        return [], 'transcript unavailable'
    with open(path, 'rb') as file:
        size = file.seek(0, 2)
        start = max(0, size-MAX_TRANSCRIPT)
        file.seek(start)
        lines = file.read().splitlines()
    if start:
        lines = lines[1:]
    calls, gap, boundary = [], None, False
    for line in reversed(lines):
        try:
            entry = json.loads(line)
            payload = entry.get('payload') or {}
            if entry.get('type') == 'event_msg' and payload.get('type') in ('user_message', 'task_started'):
                boundary = True
                break
            if entry.get('type') == 'response_item' and payload.get('type') == 'message' and payload.get('role') == 'user':
                boundary = True
                break
            if entry.get('type') == 'event_msg' and payload.get('type') == 'item_completed':
                item = payload.get('item') or {}
                if item.get('type') == 'UserMessage':
                    boundary = True
                    break
                description = item_description(item)
                if description:
                    calls.append(description)
            elif entry.get('type') == 'response_item' and payload.get('type') == 'function_call':
                name = payload.get('name', '')
                # Completed native items carry shell/web details; keep other names, never raw arguments.
                if not name.endswith(('exec_command', 'write_stdin')):
                    calls.append(safe('tool: '+name))
            elif entry.get('type') == 'response_item' and payload.get('type') == 'custom_tool_call':
                if payload.get('name') not in ('exec', 'functions.exec', 'apply_patch'):
                    gap = 'unsupported custom tool'
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            gap = 'tool evidence failed: '+type(error).__name__+': '+safe(str(error))
    if not boundary:
        gap = 'turn boundary missing from bounded transcript'
    return list(reversed(calls[:MAX_CALLS])), gap


def degraded(reason):
    return {'systemMessage': 'unchecked-claim hook: degraded coverage ('+reason+'); this stop passes unchecked.'}


def failure_type(value):
    # Accept exception class names without flattening unfamiliar errors into one class.
    return (value if isinstance(value, str) and (value in ('ConnectionClosedOK', 'TimeoutExpired')
            or re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,79}(?:Error|Exception)', value))
            else 'unknown error type')


def failure_details(response, key):
    details = response.get(key)
    if not isinstance(details, dict):
        return ''
    fields = []
    for name in ('stage', 'message', 'elapsed_seconds', 'deadline_seconds', 'stage_seconds'):
        if name in details and details[name] != '':
            fields.append(name+'='+safe(details[name],
                limit=600 if name in ('message', 'stage_seconds') else CALL_CHARS))
    return ' ['+', '.join(fields)+']' if fields else ''


def check(event):
    if event.get('stop_hook_active'):
        return {}
    blocked = waiting_block(ROOT)
    if blocked:
        return blocked
    reply = event.get('last_assistant_message') or ''
    if not isinstance(reply, str):
        return degraded('invalid final reply')
    # A promise is looked for in everything the turn wrote, as in Claude Code; a gap in the final reply.
    off = checks_off(ROOT)
    blocked = (('promise' not in off and promise_block(said(event.get('transcript_path')) + [reply]))
               or ('gap' not in off and gap_block(reply)))
    if blocked:
        return blocked
    if not reply.strip() or 'judge' in off:
        return {}
    stage = 'read transcript evidence'
    try:
        calls, gap = evidence(event.get('transcript_path'))
        if gap:
            return degraded(gap)
        description = '\n'.join('- '+call for call in calls) or '(none)'
        stage = 'read judge prompt'
        prompt = PROMPT.read_text().replace('$TOOL_CALLS', description).replace('$REPLY', reply)+COMPACT
        stage = 'run judge subprocess'
        result = subprocess.run([sys.executable, str(ROOT/'tools/codex_judge.py')],
            input=json.dumps({'prompt': prompt, 'schema': SCHEMA}), capture_output=True, text=True,
            timeout=JUDGE_TIMEOUT)
        if result.returncode:
            return degraded('native judge process failed: exit='+str(result.returncode)
                            +'; stderr='+safe(result.stderr))
        stage = 'decode judge response JSON'
        response = json.loads(result.stdout)
        if not isinstance(response, dict):
            return degraded('invalid judge response: expected JSON object, got '+type(response).__name__)
        if response.get('error') or response.get('warning'):
            failures = []
            if response.get('error'):
                failures.append('native inference failed: '+failure_type(response['error'])
                                +failure_details(response, 'error_details'))
            if response.get('warning'):
                failures.append('native cleanup failed: '+failure_type(response.get('cleanup_error'))
                                +failure_details(response, 'cleanup_details'))
            return degraded('; '.join(failures))
        raw = response.get('result')
        if not isinstance(raw, dict):
            return degraded('invalid native verdict schema: expected object, got '+type(raw).__name__)
        required = set(SCHEMA['properties'])
        missing = sorted(required - set(raw))
        extra = sorted(set(raw) - required)
        wrong = [k for k in ('kind', 'quote', 'tool', 'reason') if k in raw and not isinstance(raw[k], str)]
        wrong += [k for k in ('checked', 'declared') if k in raw and not isinstance(raw[k], bool)]
        if missing or extra or wrong:
            return degraded('invalid native verdict schema: missing='+','.join(missing)
                            +'; extra_count='+str(len(extra))+'; wrong_types='+','.join(wrong))
        verdict = validate_verdict(reply, raw)
        if verdict is None:
            return degraded('invalid native verdict')
        if not verdict['ok']:
            return {'decision': 'block', 'reason': (
                f'Unchecked claim: "{verdict["quote"]}" {verdict["reason"]} '
                'Check what the tool already offers (documentation, --help or a scratch test), '
                'then answer again; if this turn already checked, say what it found.')}
        return {}
    except subprocess.TimeoutExpired:
        return degraded('judge subprocess deadline exceeded: '+str(JUDGE_TIMEOUT)+'s')
    except (OSError, ValueError, TypeError, AttributeError) as error:
        return degraded(stage+': '+type(error).__name__+': '+safe(str(error)))
