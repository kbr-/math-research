"""End-to-end test of the session watchdog's wake on a throwaway background session.

Statement tested: tools/session_watchdog.py's wake_session (claude stop, then a flagless
`claude --bg --resume SESSION PROMPT` from the session's directory) delivers the prompt as a user
message in the same session ID, keeps its earlier context, and starts no copy.
Prediction: the woken session's transcript holds the watchdog prompt and a reply after it, its
first reply's word is still in the same file, and the agents list holds one session of the name.
Refuted by: the prompt missing from the transcript, a second session of the name, or no reply.
Possible because: a resume of a running session, or one with flags, starts a copy (2f27eb5d).
Baseline: none applies; the plainest check is that claude stop and resume exit 0, which says
nothing about where the prompt lands, so the script reads the transcript itself.
Record checked: no registered claim concerns sessions; the spec's verification on throwaway
sessions (17 October 2026) is the only earlier evidence, by another session.
Control: the first reply must hold "ready", the word asked before the wake.
Forced by counts: no count forces the transcript's content.
Positive control: the first reply itself, which must be seen before the wake is tried.
"""
import argparse
import glob
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, 'tools')
import session_watchdog as sw  # noqa: E402

NAME = 'watchdog wake test'


def wait(cond, timeout, step=3):
    end = time.time() + timeout
    while time.time() < end:
        got = cond()
        if got:
            return got
        time.sleep(step)
    return None


def transcript(sid):
    hits = glob.glob(str(Path.home() / '.claude' / 'projects' / '*' / (sid + '.jsonl')))
    return hits[0] if hits else None


def records(sid):
    p = transcript(sid)
    return [] if not p else [json.loads(l) for l in open(p) if l.strip()]


def replies(sid):
    out = []
    for r in records(sid):
        if r.get('type') == 'assistant' and not r.get('isSidechain'):
            for c in (r.get('message') or {}).get('content') or []:
                if isinstance(c, dict) and c.get('type') == 'text':
                    out.append((r['timestamp'], c['text']))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cwd', required=True, help='a trusted directory outside this repository')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    result = dict(cwd=a.cwd)
    before = {s.get('sessionId') for s in sw.list_sessions()}
    out = sw.claude('--bg', '-n', NAME, '--model', 'haiku', 'Reply with the single word ready, nothing else.',
                    cwd=a.cwd, timeout=120)
    result['create'] = dict(code=out.returncode, stdout=out.stdout.strip()[:300], stderr=out.stderr.strip()[:300])
    s = wait(lambda: next((x for x in sw.list_sessions() if x.get('name') == NAME and x.get('sessionId') not in before),
                          None), 60)
    try:
        assert s, 'throwaway session not listed'
        result['session'] = dict(id=s.get('id'), sessionId=s['sessionId'])
        first = wait(lambda: [t for t in replies(s['sessionId']) if 'ready' in t[1].lower()], 120)
        result['first_reply'] = first
        assert first, 'no first reply'
        s = next(x for x in sw.list_sessions() if x.get('sessionId') == s['sessionId'])
        prompt = sw.PROMPT_TAG + ' test wake: reply with the single word woken, nothing else.'
        ok, detail = sw.wake_session(s, prompt)
        result['wake'] = dict(ok=ok, detail=detail)
        woke = wait(lambda: [t for t in replies(s['sessionId']) if 'woken' in t[1].lower()], 180)
        result['second_reply'] = woke
        recs = records(s['sessionId'])
        result['prompt_in_transcript'] = any(
            r.get('type') == 'user' and sw.PROMPT_TAG in json.dumps(r.get('message'))
            for r in recs)
        result['first_reply_kept'] = bool([t for t in replies(s['sessionId']) if 'ready' in t[1].lower()])
        same = [x for x in sw.list_sessions() if x.get('name') == NAME]
        result['sessions_of_name'] = [(x.get('id'), x.get('sessionId')) for x in same]
        result['passed'] = bool(ok and woke and result['prompt_in_transcript'] and result['first_reply_kept']
                                and len(same) == 1 and same[0]['sessionId'] == s['sessionId'])
    finally:
        for x in sw.list_sessions():
            if x.get('name') == NAME and x.get('sessionId') not in before:
                result.setdefault('cleanup', []).append(dict(
                    id=x.get('id'), stop=sw.claude('stop', x['id']).returncode, rm=sw.claude('rm', x['id']).returncode))
        result['left_after_cleanup'] = [x.get('id') for x in sw.list_sessions() if x.get('name') == NAME]
        Path(a.out).write_text(json.dumps(result, indent=1))
        print(json.dumps(result, indent=1))


if __name__ == '__main__':
    main()
