#!/usr/bin/env python3
"""Silent, best-effort recovery proxies; never reads transcripts or stores source text."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
WORK_PHASES = {'mathematics', 'coding', 'formalization', 'reasoning_writing'}
SCOPE = ('An explicit resume command marks restoration, not necessarily compaction. Elapsed time '
         'includes idle time and excludes reading before the trigger. Repeat reads/commands '
         'are proxies, not wasted work or proof of lost reasoning. Shell reads, internal '
         'reconstruction and actual token usage are unobserved. Emitted payload bytes may be captured or truncated '
         'downstream. Unidentified streams have no attributed recovery duration.')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def stream():
    # Only the local routing key sees a session identity. Neither raw IDs nor this
    # digest enter portable reports. An inherited opaque key crosses systemd jobs.
    inherited = os.environ.get('MATH_RECOVERY_STREAM')
    if inherited:
        return (inherited if len(inherited)==64 and all(c in '0123456789abcdef' for c in inherited)
                else digest(['provided-stream',inherited]))
    for name in ('CODEX_THREAD_ID', 'CLAUDE_SESSION_ID'):
        if os.environ.get(name):
            return digest([name, os.environ[name]])
    return None


class Store:
    def __init__(self, root=ROOT, owner=None, clock=None):
        self.root = Path(root)
        self.owner = owner if owner is not None else stream()
        self.clock = clock or (lambda: (time.time(), time.monotonic(),
                                      Path('/proc/sys/kernel/random/boot_id').read_text().strip()))
        directory = self.root/'research/logs'
        directory.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(directory/'recovery.sqlite', timeout=.2)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS actors(owner TEXT PRIMARY KEY, turn TEXT, active TEXT, latest TEXT);
          CREATE TABLE IF NOT EXISTS turns(name TEXT PRIMARY KEY);
          CREATE TABLE IF NOT EXISTS episodes(id TEXT PRIMARY KEY, owner TEXT, turn TEXT,
            start REAL, mono REAL, boot TEXT, end REAL, elapsed REAL, outcome TEXT);
          CREATE TABLE IF NOT EXISTS reads(id INTEGER PRIMARY KEY, owner TEXT, episode TEXT,
            at REAL, tool TEXT, selector TEXT, content TEXT, bytes INTEGER, shown INTEGER,
            repeated INTEGER, repeated_before INTEGER);
          CREATE INDEX IF NOT EXISTS read_match ON reads(owner,tool,selector,content,shown);
          CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, owner TEXT, turn TEXT, episode TEXT,
            at REAL, end REAL, command TEXT, repeated INTEGER, rc INTEGER, during_recovery INTEGER);
          CREATE INDEX IF NOT EXISTS job_match ON jobs(owner,command,rc,end);
        ''')

    def state(self):
        if not self.owner:
            return {'turn':None,'active':None,'latest':None}
        self.db.execute('INSERT OR IGNORE INTO actors(owner) VALUES (?)',(self.owner,))
        return self.db.execute('SELECT * FROM actors WHERE owner=?',(self.owner,)).fetchone()

    def close_episode(self, reason, turn=None, at=None, work=False):
        state=self.state()
        if not state['active']:
            return
        wall,mono,boot=self.clock();wall=wall if at is None else at
        episode=self.db.execute('SELECT * FROM episodes WHERE id=?',(state['active'],)).fetchone()
        elapsed=mono-episode['mono'] if work and boot==episode['boot'] and mono>=episode['mono'] else None
        if boot!=episode['boot']:reason='reboot_censored'
        self.db.execute('UPDATE episodes SET end=?,elapsed=?,outcome=?,turn=COALESCE(turn,?) WHERE id=?',
                        (wall,elapsed,reason,turn,episode['id']))
        self.db.execute('UPDATE actors SET active=NULL WHERE owner=?',(self.owner,))

    def begin(self):
        if not self.owner:
            return
        self.close_episode('superseded_by_resume')
        wall,mono,boot=self.clock();state=self.state();key=uuid.uuid4().hex
        self.db.execute('INSERT INTO episodes VALUES (?,?,?,?,?,?,NULL,NULL,?)',
                        (key,self.owner,state['turn'],wall,mono,boot,'open'))
        self.db.execute('UPDATE actors SET active=?,latest=? WHERE owner=?',(key,key,self.owner))

    def resume(self, turn=None):
        if not self.owner:
            wall,mono,boot=self.clock()
            self.db.execute('INSERT INTO episodes VALUES(?,NULL,?,?,?,?,?,NULL,?)',
                            (uuid.uuid4().hex,turn,wall,mono,boot,wall,'unattributed_resume'))
            if turn:self.db.execute('INSERT OR IGNORE INTO turns VALUES (?)',(turn,))
            return
        self.state()
        self.close_episode('superseded_by_resume')
        if self.owner:self.db.execute('UPDATE actors SET turn=? WHERE owner=?',(turn,self.owner))
        if turn:self.bind(turn)
        self.begin()

    def bind(self, turn):
        self.db.execute('INSERT OR IGNORE INTO turns VALUES (?)',(turn,))
        state=self.state()
        if not self.owner:return
        if state['active']:
            bound=self.db.execute('SELECT turn FROM episodes WHERE id=?',(state['active'],)).fetchone()[0]
            if bound is not None and bound != turn:
                self.close_episode('timing_session_changed')
                state=self.state()
        self.db.execute('UPDATE actors SET turn=? WHERE owner=?',(turn,self.owner))
        if state['active']:
            self.db.execute('UPDATE episodes SET turn=? WHERE id=?',(turn,state['active']))

    def phase(self, turn, category):
        self.bind(turn)
        if category in WORK_PHASES:self.close_episode('work_phase:'+category,turn,work=True)

    def stop(self, turn, at):
        state=self.state()
        if state['turn']==turn:
            self.close_episode('checkpoint_without_work_phase',turn,at=at)
            self.db.execute('UPDATE actors SET turn=NULL,latest=NULL WHERE owner=?',(self.owner,))

    def read(self, tool, selector, text, shown=True):
        state=self.state();wall,_,_=self.clock();key=digest(selector);content=digest(text)
        previous=(0,0)
        if self.owner and shown:
            previous=self.db.execute('SELECT count(*),sum(CASE WHEN episode IS NOT ? THEN 1 ELSE 0 END) '
                                     'FROM reads WHERE owner=? AND tool=? AND selector=? AND content=? AND shown=1',
                                     (state['active'],self.owner,tool,key,content)).fetchone()
        start=None
        if state['active']:
            start=self.db.execute('SELECT start FROM episodes WHERE id=?',(state['active'],)).fetchone()[0]
        self.db.execute('INSERT INTO reads VALUES(NULL,?,?,?,?,?,?,?,?,?,?)',
                        (self.owner,state['active'],wall,tool,key,content,len(text.encode()),int(shown),
                         int(previous[0]>0),int(start is not None and (previous[1] or 0)>0)))

    def job_start(self, turn, job, command, category):
        self.db.execute('INSERT OR IGNORE INTO turns VALUES (?)',(turn,))
        if category in {'computation','formal_verification'}:
            self.close_episode('work_job:'+category,turn,work=True)
        state=self.state();wall,_,_=self.clock();key=digest(command)
        previous=self.db.execute('SELECT count(*) FROM jobs WHERE owner=? AND command=? AND rc=0 AND end<=?',
                                 (self.owner,key,wall)).fetchone()[0] if self.owner else 0
        self.db.execute('INSERT INTO jobs VALUES(?,?,?,?,?,NULL,?,?,NULL,?)',
                        (turn+':'+job,self.owner,turn,state['active'] or state['latest'],wall,key,int(previous>0),int(bool(state['active']))))

    def job_end(self, turn, job, rc):
        wall,_,_=self.clock()
        self.db.execute('UPDATE jobs SET end=?,rc=? WHERE id=?',(wall,rc,turn+':'+job))

    def report(self, turn=None, cutoff=None):
        cutoff=cutoff if cutoff is not None else self.clock()[0]
        query='SELECT * FROM episodes WHERE start<=?';params=[cutoff]
        if turn is not None:query+=' AND turn=?';params.append(turn)
        episodes=[]
        for e in self.db.execute(query+' ORDER BY start',params).fetchall():
            reads=self.db.execute('SELECT * FROM reads WHERE episode=? AND at<=?',(e['id'],cutoff)).fetchall()
            jobs=self.db.execute('SELECT * FROM jobs WHERE episode=? AND at<=?',(e['id'],cutoff)).fetchall()
            completed=e['end'] is not None and e['end']<=cutoff
            times=[e['start']]+[r['at'] for r in reads]+[j['at'] for j in jobs if j['during_recovery']]
            if completed:times.append(e['end'])
            times.sort()
            episodes.append({'episode':e['id'],'timing_session':e['turn'],'started_unix_s':e['start'],
                'outcome':e['outcome'] if completed else 'open_at_snapshot',
                'elapsed_to_work_s':e['elapsed'] if completed else None,
                'largest_observation_gap_s':max((b-a for a,b in zip(times,times[1:])),default=0),
                'emitted_reads':sum(r['shown'] for r in reads),
                'emitted_bytes':sum(r['bytes'] for r in reads if r['shown']),
                'unchanged_repeat_reads':sum(r['repeated'] for r in reads if r['shown']),
                'reads_seen_before_resume':sum(r['repeated_before'] for r in reads if r['shown']),
                'saved_only_operations':sum(not r['shown'] for r in reads),
                'read_observations':[{'at_unix_s':r['at'],'tool':r['tool'],'selector_fingerprint':r['selector'],
                    'content_fingerprint':r['content'],'bytes':r['bytes'],'emitted':bool(r['shown']),
                    'unchanged_repeat':bool(r['repeated']),'seen_before_resume':bool(r['repeated_before'])} for r in reads],
                'jobs_after_resume':[{'job':j['id'].rsplit(':',1)[-1],'timing_session':j['turn'],'during_recovery':bool(j['during_recovery']),
                    'same_command_previously_succeeded':bool(j['repeated']),
                    'returncode':j['rc'] if j['end'] is not None and j['end']<=cutoff else None} for j in jobs]})
        errors=self.root/'research/logs/recovery-errors.jsonl'
        error_count=sum(1 for _ in errors.open()) if errors.exists() else 0
        return {'version':1,'snapshot_unix_s':cutoff,'collection':'available','episodes':episodes,
                'session_tracked':turn is None or bool(self.db.execute('SELECT 1 FROM turns WHERE name=?',(turn,)).fetchone()),
                'unattributed_reads':self.db.execute('SELECT count(*) FROM reads WHERE owner IS NULL AND at<=?',(cutoff,)).fetchone()[0],
                'known_collection_failures':error_count,'scope':SCOPE}


def observe(action, root=ROOT, **kwargs):
    if os.environ.get('MATH_RECOVERY_DISABLED')=='1':return
    store=None
    try:
        store=Store(root)
        with store.db:getattr(store,action)(**kwargs)
    except (OSError,ValueError,sqlite3.Error) as error:
        try:
            path=Path(root)/'research/logs/recovery-errors.jsonl';path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('a') as output:output.write(json.dumps({'at':time.time(),'operation':action,'error_type':type(error).__name__})+'\n')
        except OSError:pass
    finally:
        if store:store.db.close()


def snapshot(root=ROOT, turn=None, cutoff=None):
    if os.environ.get('MATH_RECOVERY_DISABLED')=='1':
        return {'version':1,'collection':'disabled','scope':SCOPE}
    store=None
    try:
        store=Store(root)
        return store.report(turn,cutoff)
    except (OSError,ValueError,sqlite3.Error) as error:
        return {'version':1,'collection':'unavailable','error_type':type(error).__name__,'scope':SCOPE}
    finally:
        if store:store.db.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--session')
    args=parser.parse_args()
    with args.out.open('x') as output:json.dump(snapshot(turn=args.session),output,indent=2);output.write('\n')


if __name__=='__main__':main()
