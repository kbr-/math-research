"""Ask Haiku for a JSON verdict through `claude -p`: the framework's judges share this call.

The prompt goes on stdin: Linux limits one command-line argument to 128 KB, and a judge's prompt
can carry a whole plan.

Haiku runs without extended thinking, CLAUDE.md, MCP servers, skills or tools, from an empty
directory, with INSIDE_JUDGE set in its environment, so the Stop hook (tools/hooks/stop_checks.py)
doesn't check the judge's own session.

Each answered call appends its token usage, with the calling harness session's id, to model-usage.jsonl
in the main checkout's research/logs, shared by all worktrees: `claude -p --no-session-persistence`
leaves no transcript, and tools/model_usage.py adds these calls to a research cycle's model use.
"""
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

MODEL = 'claude-haiku-4-5-20251001'
SYSTEM = 'You evaluate a hook condition and answer with the JSON the instructions ask for.'
INSIDE_JUDGE = 'INSIDE_HAIKU_JUDGE'
USAGE_LOG = 'model-usage.jsonl'


class Failed(Exception):
    """The call gave no verdict, for the cause its message names."""


class Refused(Failed):
    """The API refused the call, as for a retired model."""


def usage_log(root=Path(__file__).resolve().parents[1]):
    """The shared usage log: research/logs/model-usage.jsonl of the main checkout of `root`'s repository."""
    common = subprocess.run(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'], cwd=root,
                            capture_output=True, text=True)
    main = Path(common.stdout.strip()).parent if common.returncode == 0 else Path(root)
    return main / 'research' / 'logs' / USAGE_LOG


def record_usage(result, session, log=None):
    """Append the call's usage from `claude -p`'s JSON `result`, under the harness `session` that asked."""
    models = result.get('modelUsage')
    if not isinstance(models, dict) or not models:
        return
    line = {'at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z', 'unix_s': time.time(),
            'session': session, 'usage': result.get('usage'), 'models': models}
    try:
        path = log or usage_log()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            stream.write(json.dumps(line) + '\n')
    except OSError:
        pass  # A lost usage line costs one cycle's accuracy, never the judge's verdict.


def ask(prompt, timeout, model=MODEL, thinking=False, session=None):
    """The JSON object in Haiku's answer; raises Refused when the API refuses the call, and Failed,
    naming the cause, when it fails otherwise, a timeout included. A caller that needs a stronger reader
    names its `model`, and with `thinking` leaves the model its own thinking. `session` is the harness
    session that asks (a hook's input names it), else the one in the environment; the call's usage is
    recorded under it."""
    env = {**os.environ, INSIDE_JUDGE: '1', 'CLAUDE_CODE_DISABLE_CLAUDE_MDS': '1', **({} if thinking else {'MAX_THINKING_TOKENS': '0'})}
    try:
        with tempfile.TemporaryDirectory() as cwd:
            run = subprocess.run(
                ['claude', '-p', '--model', model, '--tools', '', '--strict-mcp-config',
                 '--disable-slash-commands', '--no-chrome', '--no-session-persistence',
                 '--output-format', 'json', '--system-prompt', SYSTEM],
                input=prompt, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise Failed(f'no answer within {timeout} s') from None
    except OSError as error:
        raise Failed(f'claude could not run: {error}') from error
    try:
        result = json.loads(run.stdout)
    except ValueError:
        output = ' '.join((run.stderr or run.stdout).split())[-200:]
        raise Failed(f'claude exited {run.returncode} without its JSON output: {output!r}') from None
    if not isinstance(result, dict):
        raise Failed(f'claude printed JSON that is not an object: {run.stdout[:200]!r}')
    record_usage(result, session or os.environ.get('CLAUDE_CODE_SESSION_ID') or os.environ.get('CODEX_THREAD_ID'))
    if result.get('is_error'):
        raise Refused(f"{result.get('api_error_status', 'error')}: {result.get('result', '')}")
    answer = str(result.get('result', ''))
    try:
        return json.loads(answer[answer.index('{'):answer.rindex('}') + 1])
    except ValueError:
        raise Failed(f'the answer held no JSON object: {answer[:200]!r}') from None
