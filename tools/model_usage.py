#!/usr/bin/env python3
"""A research cycle's model use: its tokens by model and reasoning effort, their cost at API list prices,
and its share of the subscription's weekly usage limit.

The cycle is a timing session's interval, from its `start` to its `stop` event. Its tokens are those of the
harness session that runs the finisher, named by CLAUDE_CODE_SESSION_ID (Claude Code) or CODEX_THREAD_ID
(Codex), whichever belongs to the agent the session's `start` event records; the id is used, never written:

- Claude Code: the `assistant` records of `<config>/projects/*/ID.jsonl` and of the session's subagent
  transcripts (`<config>/projects/*/ID/subagents/*.jsonl`), each message id counted once per file, with the
  effort of the latest `api-request` before it in the same file (`params.output_config.effort`). `<config>`
  is CLAUDE_CONFIG_DIR or ~/.claude.
- Codex: the `token_count` events of the thread's rollouts and of its subagents' (whose `session_meta` names
  the thread), each event's tokens being the change of the cumulative totals since the event before it, with
  the model and effort of the latest `turn_context`. `<home>` is CODEX_HOME or ~/.codex.
- The framework's own `claude -p` calls (tools/haiku_judge.py), from the main checkout's
  research/logs/model-usage.jsonl.

Costs use tools/model_prices.json; a model it doesn't list is reported unpriced, with its tokens.

The share of the weekly limit is the limit's movement over the interval, times the cycle's API-price cost
over the API-price cost of every session on this machine billed to the same plan in the interval: parallel
sessions split the movement by their use. Use elsewhere (the web or phone apps, another machine) moves the
limit unseen and is counted against the sessions here. Claude's readings come from the status-line log
`$USAGE_LOG_DIR/claude.jsonl`; Codex's from the rate limits every rollout records. A session on an API key
doesn't use a plan: its API-price cost is its bill. `$USAGE_LOG_DIR/plans.json` ({"claude": {"plan": NAME,
"usd_per_month": N}, "codex": {...}}) turns the share into dollars.

    python3 tools/model_usage.py TURN    # the model use of timing session TURN so far, as JSON
"""
from datetime import datetime, timezone
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PRICES = ROOT / 'tools' / 'model_prices.json'
MARGIN_S = 900          # records this long before the start are read for the effort and model in force
LATE_S = 120            # records may land slightly out of order: read this far past the stop
RESET_JITTER_S = 60     # a reset time that moves by more is a new window
WEEK_MINUTES = 10080
SEARCH_STOP = 1 << 16   # binary search stops at this span of bytes
KINDS = ('input', 'cache_write_5m', 'cache_write_1h', 'cache_read', 'output')
STAMP = re.compile(rb'(?<!\\)"timestamp":\s*"(\d{4}-\d\d-\d\dT[^"]+)"')
CLAUDE_OAUTH = 'oauth-2025-04-20'
API_BILLING = ('ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN', 'CLAUDE_CODE_USE_BEDROCK', 'CLAUDE_CODE_USE_VERTEX')
AGENT_ID = {'Claude Code': 'CLAUDE_CODE_SESSION_ID', 'Codex': 'CODEX_THREAD_ID'}
PROVIDER = {'Claude Code': 'claude', 'Codex': 'codex'}


def iso(unix_s):
    """The transcripts' timestamp form, which orders as text in time order."""
    return datetime.fromtimestamp(unix_s, timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def unix(stamp):
    return datetime.fromisoformat(stamp.replace('Z', '+00:00')).timestamp()


def stamp_of(line):
    found = STAMP.search(line)
    return found.group(1).decode() if found else None


def first_stamp_after(stream, offset):
    """The timestamp of the first whole line at or after `offset` that has one, and that line's offset."""
    stream.seek(offset)
    if offset:
        stream.readline()
    while True:
        at = stream.tell()
        line = stream.readline()
        if not line:
            return None, at
        stamp = stamp_of(line)
        if stamp:
            return stamp, at


def seek_time(stream, size, target):
    """An offset at or before the first line stamped at `target` or later, in a file whose lines are stamped
    in time order: binary search down to SEARCH_STOP bytes."""
    low, high = 0, size
    while high - low > SEARCH_STOP:
        middle = (low + high) // 2
        stamp, _ = first_stamp_after(stream, middle)
        if stamp is None or stamp >= target:
            high = middle
        else:
            low = middle
    stream.seek(low)
    if low:
        stream.readline()  # to a line's start: the search before it then sees only whole lines
    return stream.tell()


def kind(name):
    """A pattern matching a record whose "type" is `name`, with or without a space after the colon."""
    return re.compile(rb'"type":\s*"' + re.escape(name.encode()) + rb'"')


def last_line_before(stream, offset, marker, limit=64 << 20):
    """The last whole line before `offset` matching the pattern `marker`, searched backwards over at most
    `limit` bytes."""
    end, tail = offset, b''
    while end > 0 and offset - end < limit:
        start = max(0, end - (1 << 20))
        stream.seek(start)
        block = stream.read(end - start) + tail
        lines = block.split(b'\n')
        tail = lines[0] if start else b''
        for line in reversed(lines[1:] if start else lines):
            if marker.search(line):
                return line
        end = start
    return None


ASSISTANT, API_REQUEST, TURN_CONTEXT, TOKEN_COUNT = (kind(name) for name in
                                                    ('assistant', 'api-request', 'turn_context', 'token_count'))


def records(path, low, high, markers, before=()):
    """The JSON records of `path` matching one of the patterns `markers`, up to LATE_S after `high` (ISO stamps),
    in file order. Records stamped earlier than MARGIN_S before `low` carry the key '_before': they give the
    settings in force (an effort, a model, cumulative totals), never use; so does, first, for each pattern in
    `before`, the last matching line before the part of the file read."""
    with open(path, 'rb') as stream:
        size = os.fstat(stream.fileno()).st_size
        early = iso(unix(low) - MARGIN_S)
        offset = seek_time(stream, size, early) if size > SEARCH_STOP else 0
        for marker in before:
            line = last_line_before(stream, offset, marker)
            if line:
                try:
                    yield {'_before': True, **json.loads(line)}
                except ValueError:
                    pass
        stream.seek(offset)
        late = iso(unix(high) + LATE_S)
        for line in stream:
            if not any(marker.search(line) for marker in markers):
                continue  # other lines can be out of order (a resumed transcript's leading snapshots)
            stamp = stamp_of(line)
            if stamp and stamp > late:
                return
            try:
                record = json.loads(line)
            except ValueError:
                continue  # an active transcript may end in a partly written line
            yield {'_before': True, **record} if stamp and stamp < early else record


def load_prices(path=PRICES):
    return json.loads(Path(path).read_text())


def model_key(model, prices):
    """The price table's key for `model`, ignoring a date suffix (claude-haiku-4-5-20251001), or None."""
    if not model:
        return None
    if model in prices['models']:
        return model
    bare = re.sub(r'-\d{8}$', '', model)
    return bare if bare in prices['models'] else None


def cost(model, tokens, prompt, prices, fast=False):
    """The API-price cost of `tokens` ({kind: count}) of one request with `prompt` prompt tokens, or None."""
    key = model_key(model, prices)
    if key is None:
        return None
    rates = prices['models'][key]
    tier = rates.get('long_context')
    if tier and prompt > tier['above_prompt_tokens']:
        rates = tier
    if any(count and kind not in rates for kind, count in tokens.items()):
        return None
    total = sum(count * rates.get(kind, 0) for kind, count in tokens.items()) / 1e6
    return total * (prices['models'][key].get('fast_multiplier', 1) if fast else 1)


class Tally:
    """Tokens and costs by (model, effort)."""

    def __init__(self, prices):
        self.prices, self.rows = prices, {}

    def add(self, model, effort, tokens, prompt, fast=False):
        row = self.rows.setdefault((model or 'unrecorded', effort or 'unrecorded'),
                                   {'tokens': dict.fromkeys(KINDS, 0), 'usd': 0.0, 'unpriced_tokens': 0})
        for kind, count in tokens.items():
            row['tokens'][kind] += count
        price = cost(model, tokens, prompt, self.prices, fast)
        if price is None:
            row['unpriced_tokens'] += sum(tokens.values())
        else:
            row['usd'] += price

    def usd(self):
        return sum(row['usd'] for row in self.rows.values())

    def merge(self, other):
        for (model, effort), row in other.rows.items():
            mine = self.rows.setdefault((model, effort), {'tokens': dict.fromkeys(KINDS, 0), 'usd': 0.0,
                                                          'unpriced_tokens': 0})
            for kind in KINDS:
                mine['tokens'][kind] += row['tokens'][kind]
            mine['usd'] += row['usd']
            mine['unpriced_tokens'] += row['unpriced_tokens']


def claude_tokens(usage):
    created = usage.get('cache_creation') or {}
    hour = created.get('ephemeral_1h_input_tokens')
    minutes = created.get('ephemeral_5m_input_tokens')
    if hour is None and minutes is None:
        minutes = usage.get('cache_creation_input_tokens', 0)  # without the split, the API's default TTL
    return {'input': usage.get('input_tokens', 0) or 0, 'cache_write_5m': minutes or 0,
            'cache_write_1h': hour or 0, 'cache_read': usage.get('cache_read_input_tokens', 0) or 0,
            'output': usage.get('output_tokens', 0) or 0}


def claude_file(path, low, high, effort=None):
    """(messages, whether the session is billed to a plan, or None when no request record says) of one Claude
    Code transcript, its messages stamped in [low, high] as (id, model, effort, tokens, prompt, fast). A message's
    effort is the one its record states; else the latest `api-request` record's; else `effort`, the session's
    setting, if given."""
    messages, oauth = [], None
    for record in records(path, low, high, (ASSISTANT, API_REQUEST), before=(API_REQUEST,)):
        if record.get('type') == 'api-request':
            params = record.get('params') or {}
            effort = (params.get('output_config') or {}).get('effort') or 'none'
            oauth = CLAUDE_OAUTH in (params.get('betas') or [])
            continue
        if record.get('_before') or record.get('type') != 'assistant':
            continue
        stamp, message = record.get('timestamp'), record.get('message') or {}
        usage = message.get('usage')
        if not stamp or not usage or not (low <= stamp <= high):
            continue
        tokens = claude_tokens(usage)
        prompt = tokens['input'] + tokens['cache_write_5m'] + tokens['cache_write_1h'] + tokens['cache_read']
        messages.append((message.get('id'), message.get('model'), record.get('effort') or effort, tokens, prompt,
                         usage.get('speed') == 'fast'))
    return messages, oauth


def claude_home():
    return Path(os.environ.get('CLAUDE_CONFIG_DIR') or Path.home() / '.claude')


def claude_session_files(home, session):
    projects = home / 'projects'
    return sorted(set(projects.glob(f'*/{session}.jsonl')) | set(projects.glob(f'*/{session}/subagents/*.jsonl')))


def recent(paths, low):
    since = unix(low)
    for path in paths:
        try:
            if path.stat().st_mtime >= since:
                yield path
        except OSError:
            continue


def judge_calls(log, low, high, prices, session=None):
    """The tally of framework judge calls in [low, high], of `session` or of every session."""
    tally = Tally(prices)
    try:
        lines = log.read_text().splitlines()
    except OSError:
        return tally
    for line in lines:
        try:
            call = json.loads(line)
        except ValueError:
            continue
        if not (low <= call.get('at', '') <= high) or (session and call.get('session') != session):
            continue
        models, usage = call.get('models') or {}, call.get('usage') or {}
        if len(models) == 1 and usage:
            tokens = claude_tokens(usage)
            prompt = tokens['input'] + tokens['cache_write_5m'] + tokens['cache_write_1h'] + tokens['cache_read']
            tally.add(next(iter(models)), 'judge', tokens, prompt, usage.get('speed') == 'fast')
            continue
        for model, part in models.items():  # several models: their split of cache writes isn't recorded
            tokens = {'input': part.get('inputTokens', 0), 'cache_write_5m': part.get('cacheCreationInputTokens', 0),
                      'cache_write_1h': 0, 'cache_read': part.get('cacheReadInputTokens', 0),
                      'output': part.get('outputTokens', 0)}
            tally.add(model, 'judge', tokens, tokens['input'] + tokens['cache_write_5m'] + tokens['cache_read'])
    return tally


def codex_tokens(usage):
    total, cached = usage.get('input_tokens', 0) or 0, usage.get('cached_input_tokens', 0) or 0
    return {'input': max(0, total - cached), 'cache_read': cached, 'output': usage.get('output_tokens', 0) or 0}


def codex_file(path, low, high, prices, readings=None):
    """(tally, billed to a plan) of one rollout's token_count events stamped in [low, high]; appends the week's
    limit readings, (unix_s, percent, resets_at), to `readings`."""
    tally, model, effort, plan, previous = Tally(prices), None, None, None, None
    for record in records(path, low, high, (TURN_CONTEXT, TOKEN_COUNT), before=(TURN_CONTEXT,)):
        payload = record.get('payload') or {}
        if record.get('type') == 'turn_context':
            model, effort = payload.get('model'), payload.get('effort') or 'none'
            continue
        if payload.get('type') != 'token_count':
            continue
        stamp, info = record.get('timestamp') or '', payload.get('info') or {}
        limits = payload.get('rate_limits') or {}
        if limits.get('plan_type'):
            plan = True
        if readings is not None:
            for slot in ('primary', 'secondary'):
                window = limits.get(slot) or {}
                if window.get('window_minutes') == WEEK_MINUTES and window.get('used_percent') is not None:
                    readings.append((unix(stamp), float(window['used_percent']), window.get('resets_at')))
        total, last = info.get('total_token_usage'), info.get('last_token_usage')
        if not total:
            continue
        now = codex_tokens(total)
        if previous and all(now[kind] >= previous[kind] for kind in now):
            tokens = {kind: now[kind] - previous[kind] for kind in now}
        else:
            tokens = codex_tokens(last or {})
        previous = now
        if not (low <= stamp <= high):
            continue
        prompt = (last or {}).get('input_tokens', 0) or 0
        tally.add(model, effort, tokens, prompt)
    return tally, bool(plan)


def codex_home():
    return Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex')


def codex_rollouts(home, low):
    return list(recent((home / 'sessions').rglob('rollout-*.jsonl'), low))


def codex_thread_files(paths, thread):
    """The thread's own rollout and its subagents' (their session_meta names the thread)."""
    own = []
    for path in paths:
        if path.name.endswith(f'-{thread}.jsonl'):
            own.append(path)
            continue
        try:
            with open(path, 'rb') as stream:
                meta = json.loads(stream.readline())
        except (OSError, ValueError):
            continue
        payload = meta.get('payload') or {}
        if meta.get('type') == 'session_meta' and thread in (payload.get('session_id'), payload.get('parent_thread_id')):
            own.append(path)
    return own


def claude_readings(log_dir):
    """The week's limit readings of the status-line log, (unix_s, percent, resets_at)."""
    readings = []
    try:
        lines = (Path(log_dir) / 'claude.jsonl').read_text().splitlines()
    except OSError:
        return None
    for line in lines:
        try:
            reading = json.loads(line)
            if reading.get('week') is not None:
                readings.append((datetime.fromisoformat(reading['at']).timestamp(), float(reading['week']),
                                 reading.get('week_resets_at')))
        except (ValueError, KeyError, TypeError):
            continue
    return readings


def same_window(a, b):
    return a is not None and b is not None and abs(a - b) <= RESET_JITTER_S


def window_at(readings, t):
    """The reset time of the newest window read by time t, or None."""
    seen = [r[2] or 0 for r in readings if r[0] <= t]
    return max(seen) if seen else None


def reading_at(readings, t, window=None):
    """The limit at time t in `window` (by default the newest read by then): the highest reading of that window
    made by t. Use within a window only grows, so a lower reading is stale, from a session idle since; a session
    still in an earlier window after a reset is stale too."""
    window = window_at(readings, t) if window is None else window
    if window is None:
        return None
    values = [r[1] for r in readings if r[0] <= t and same_window(r[2] or 0, window)]
    return max(values) if values else None


def movement(readings, low_s, high_s):
    """The limit's movement in percentage points over [low_s, high_s], and a note when its start is read late,
    or (None, reason)."""
    note, start_window = None, window_at(readings, low_s)
    if start_window is None:
        inside = sorted(r for r in readings if low_s <= r[0] <= high_s)
        if not inside:
            return None, 'no limit reading before the cycle ended'
        low_s, start_window, note = inside[0][0], inside[0][2] or 0, 'its first limit reading came after the cycle began'
    start, end_window = reading_at(readings, low_s, start_window), window_at(readings, high_s)
    end = reading_at(readings, high_s, end_window)
    if same_window(start_window, end_window):
        return max(0.0, end - start), note
    # a reset inside the cycle: the old window's rise to its last reading, then the new window's level
    return max(0.0, reading_at(readings, high_s, start_window) - start) + end, note


def plan_price(log_dir, provider):
    try:
        plan = json.loads((Path(log_dir) / 'plans.json').read_text())[provider]
        return plan.get('plan'), float(plan['usd_per_month'])
    except (OSError, ValueError, KeyError, TypeError):
        return None, None


def main_checkout(root):
    try:
        common = subprocess.run(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'], cwd=root,
                                capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return Path(root)
    return Path(common.stdout.strip()).parent if common.returncode == 0 else Path(root)


def cycle(events, root=ROOT, env=None, prices=None, claude=None, codex=None, now=None):
    """The model use of the timing session whose journal `events` are given, as a JSON-ready dict."""
    env = os.environ if env is None else env
    prices = prices or load_prices()
    first = events[0] if events else {}
    stop = next((e for e in events if e.get('event') == 'stop'), None)
    agent = first.get('agent')
    if agent not in AGENT_ID:
        return {'measured': False, 'reason': f'the cycle\'s agent ({agent or "unrecorded"}) keeps no transcript '
                                             'this tool reads'}
    session = env.get(AGENT_ID[agent])
    if not session:
        return {'measured': False, 'reason': f'{AGENT_ID[agent]} is not set: the finisher ran outside the '
                                             f'{agent} session'}
    low = iso(first['unix_s'])
    high = iso(stop['unix_s'] if stop else (now if now is not None else datetime.now(timezone.utc).timestamp()))
    judges = main_checkout(root) / 'research' / 'logs' / 'model-usage.jsonl'
    own, everyone, billed, readings = Tally(prices), Tally(prices), None, None
    if agent == 'Claude Code':
        home = claude or claude_home()
        mine = set(claude_session_files(home, session))
        if not mine:
            return {'measured': False, 'reason': 'no transcript of the Claude Code session was found'}
        setting = env.get('CLAUDE_EFFORT')
        keyed = any(env.get(name) for name in API_BILLING)
        counted, unread = {'own': set(), 'everyone': set()}, 0
        for path in recent((home / 'projects').rglob('*.jsonl'), low):
            ours = path in mine
            try:
                fallback = f'{setting} (session setting)' if ours and setting else None
                messages, plan = claude_file(path, low, high, fallback)
            except OSError:
                unread += ours  # another session's file may vanish or be unreadable: it is left out
                continue
            if plan is None:  # no request record: this session by its environment, another one by the default
                plan = not keyed if ours else True
            if ours:
                billed = plan if billed is None else billed or plan
            for ident, model, effort, tokens, prompt, fast in messages:
                # a resumed or forked transcript copies earlier messages under their ids: count each once
                for name, tally, wanted in (('own', own, ours), ('everyone', everyone, plan)):
                    if wanted and (ident is None or ident not in counted[name]):
                        counted[name].add(ident)
                        tally.add(model, effort, tokens, prompt, fast)
        own.merge(judge_calls(judges, low, high, prices, session))
        everyone.merge(judge_calls(judges, low, high, prices))
        log_dir = env.get('USAGE_LOG_DIR')
        readings = claude_readings(log_dir) if log_dir else None
    else:
        home = codex or codex_home()
        paths = codex_rollouts(home, low)
        mine = set(codex_thread_files(paths, session))
        if not mine:
            return {'measured': False, 'reason': 'no rollout of the Codex thread was found'}
        readings, unread = [], 0
        for path in paths:
            try:
                tally, plan = codex_file(path, low, high, prices, readings)
            except OSError:
                unread += path in mine
                continue
            if path in mine:
                own.merge(tally)
                billed = plan if billed is None else billed or plan
            if plan:
                everyone.merge(tally)
        log_dir = env.get('USAGE_LOG_DIR')
    # The share is the harness's own use against its plan's; a Codex cycle's judge calls bill Claude's plan,
    # so they are listed but kept out of its share.
    weight = own.usd()
    if agent == 'Codex':
        own.merge(judge_calls(judges, low, high, prices, session))
    result = {'measured': True, 'agent': agent, 'price_table': prices['date'],
              'billing': 'plan' if billed else 'API key',
              'rows': [{'model': model, 'effort': effort, 'tokens': row['tokens'],
                        'total_tokens': sum(row['tokens'].values()), 'usd': round(row['usd'], 6),
                        'unpriced_tokens': row['unpriced_tokens']}
                       for (model, effort), row in sorted(own.rows.items(), key=lambda kv: -kv[1]['usd'])],
              'usd': round(own.usd(), 6)}
    result['unpriced_models'] = sorted({row['model'] for row in result['rows'] if row['unpriced_tokens']})
    if unread:
        result['unread_files'] = unread
    if not billed:
        result['limit'] = {'measured': False, 'reason': 'billed to an API key: the API-price cost is the bill'}
        return result
    provider = PROVIDER[agent]
    if readings is None:
        result['limit'] = {'measured': False, 'reason': 'USAGE_LOG_DIR is not set, so the status-line limit log '
                                                        'is not found'}
        return result
    moved, note = movement(readings, unix(low), unix(high))
    if moved is None:
        result['limit'] = {'measured': False, 'reason': note}
        return result
    fraction = weight / everyone.usd() if everyone.usd() > 0 else None
    limit = {'measured': fraction is not None, 'window': 'week', 'moved_percent': round(moved, 3),
             'fraction_of_machine_use': None if fraction is None else round(min(1.0, fraction), 6)}
    if fraction is None:
        limit['reason'] = 'no priced use on this machine during the cycle'
    else:
        limit['share_percent'] = round(moved * min(1.0, fraction), 4)
        plan, monthly = plan_price(log_dir, provider) if log_dir else (None, None)
        if monthly is not None:
            weekly = monthly * 12 / 52
            limit.update(plan=plan, usd_per_month=monthly, usd=round(limit['share_percent'] / 100 * weekly, 4))
            # each row's part of it, by its API-price cost; a Codex cycle's judge calls bill Claude's plan instead
            for row in result['rows']:
                other = (agent == 'Codex' and row['effort'] == 'judge') or (row['unpriced_tokens'] and not row['usd'])
                row['plan_usd'] = None if other or not weight else round(
                    limit['share_percent'] / 100 * weekly * row['usd'] / weight, 6)
    if note:
        limit['note'] = note
    result['limit'] = limit
    return result


def tokens_text(count):
    if count >= 1e6:
        return f'{count / 1e6:.1f} M'
    if count >= 1e3:
        return f'{count / 1e3:.0f} k'
    return str(count)


def usd_text(value):
    return f'${value:,.2f}' if value >= 0.01 or value == 0 else '<$0.01'


COLUMNS = (('input', 'Input'), ('cache_write_5m', 'Cache writes, 5 min'), ('cache_write_1h', 'Cache writes, 1 h'),
           ('cache_read', 'Cache reads'), ('output', 'Output'))


def table_html(use):
    """The model-use table of a measured `use`, for the timing fragment: each kind of token in its own column."""
    from html import escape
    cell = lambda text, strong=False: (f'<td class="elapsed"><strong>{escape(text)}</strong></td>' if strong
                                       else f'<td class="elapsed">{escape(text)}</td>')
    rows = [f'<tr><td>{escape(row["model"])}, {escape(row["effort"])}</td>'
            + ''.join(cell(tokens_text(row['tokens'][kind])) for kind, _ in COLUMNS)
            + cell(tokens_text(row['total_tokens']))
            + cell('unpriced' if row['unpriced_tokens'] and not row['usd'] else usd_text(row['usd'])) + '</tr>'
            for row in use['rows']]
    totals = {kind: sum(row['tokens'][kind] for row in use['rows']) for kind, _ in COLUMNS}
    head = ''.join(f'<th scope="col">{label}</th>' for _, label in COLUMNS)
    limit, plan_head = use.get('limit') or {}, ''
    if 'usd' in limit:  # the plan's price of each row: its part of the cycle's share of the weekly limit
        plan_head = '<th scope="col">On the plan</th>'
        rows = [line[:-len('</tr>')] + cell('—' if row.get('plan_usd') is None else usd_text(row['plan_usd']))
                + '</tr>' for line, row in zip(rows, use['rows'])]
    return '\n'.join(['<table class="timing-table model-use-table">', '<caption>Model use (tokens)</caption>',
                      f'<thead><tr><th scope="col">Model and effort</th>{head}<th scope="col">All tokens</th>'
                      f'<th scope="col">At API prices</th>{plan_head}</tr></thead>', '<tbody>',
                      '<tr><th scope="row">Total</th>'
                      + ''.join(cell(tokens_text(totals[kind]), True) for kind, _ in COLUMNS)
                      + cell(tokens_text(sum(totals.values())), True) + cell(usd_text(use['usd']), True)
                      + (cell(usd_text(limit['usd']), True) if 'usd' in limit else '') + '</tr>',
                      *rows, '</tbody></table>'])


def note_text(use):
    """The one sentence the timing note gains for a measured `use`."""
    limit = use.get('limit') or {}
    if use.get('billing') == 'API key':
        return f'Model use billed to an API key at {usd_text(use["usd"])}.'
    if not limit.get('measured'):
        return f'Share of the weekly limit not measured: {limit.get("reason", "unknown")}.'
    if not limit['moved_percent']:
        return f'Model use: the weekly {use["agent"]} limit, read in whole points, did not move during the cycle.'
    share = f'{limit["share_percent"]:.2f}% of the weekly {use["agent"]} limit'
    if 'usd' in limit:
        share += f' (≈ {usd_text(limit["usd"])} of {limit["plan"] or "the plan"} at ${limit["usd_per_month"]:g} a month)'
    moved = limit['moved_percent']
    priceless = '' if 'usd' in limit else ' No plan price is set, so no dollars (USAGE_LOG_DIR/plans.json).'
    return (f'Model use: {share}, its part by API prices of the limit\'s {moved:g}-point movement, read in whole '
            'points.' + priceless)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('session', help='timing session name, as in research/logs/SESSION.jsonl')
    args = parser.parse_args(argv)
    journal = ROOT / 'research' / 'logs' / f'{args.session}.jsonl'
    events = [json.loads(line) for line in journal.read_text().splitlines() if line.strip()]
    print(json.dumps(cycle(events), indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
