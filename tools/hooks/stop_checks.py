#!/usr/bin/env python3
"""Claude Code Stop hook: the checks a turn's end must pass.

Requests waiting for the judge. In this clone's own sessions, the stop is blocked while a task
holds a request to others that `tools/task_index.py request judge` hasn't passed, so no such
request reaches the user unjudged (research/notes/TASK_PROTOCOL.md, A request for someone else's
action). It reads the task records only; the Codex adapter, codex_unchecked_claim.py, runs it too.

Promises. A turn that promises the assistant's behaviour beyond it ("from now on I'll ...", in
its text or its thinking) is blocked once, with the sentence: nothing said in a turn survives
compaction or a new session, so a promise holds only through a framework change. A pattern finds
them, without a model: first person and future tense with a marker such as "going forward".

Mistakes. A turn that admits a mistake of the assistant's own ("my mistake", "I was wrong", "I never
measured it") is blocked once, with the sentence, unless what the user is told has a paragraph that
starts "Prevention": the user must not have to ask how the class of mistake is prevented. A pattern
finds them, without a model.

Tool faults. A turn that reports one of this clone's tools misbehaving (a sentence naming it, as
`name`, name.py or tools/name, next to a word such as "nested", "refused" or "wrong", in its text or
its thinking) and doesn't edit the tool or its test is blocked once, with the sentence: a committed
tool that falls short is fixed, not worked around by hand. A pattern finds them, without a model.

Missing tools. A turn that says no tool does a job, or that a scratch script does it (in its text or
its thinking), and neither queues the tool (`tools/lead_queue.py add` or `append`) nor edits a file
under tools/ is blocked once, with the sentence: a helper the framework lacks is built or queued in
the same turn, so the need outlives the turn. A pattern finds them, without a model.

Deferrals. A turn that hands a step to someone else ("left to the owners", "up to their team"), in its
text, its thinking or what it writes (an edit's new text, a written file, a command such as a
commit message), is blocked once, with the sentence: the step is taken apart and settled as
TASK_PROTOCOL.md's request for someone else's action requires, so what is left to others holds only
what needs them. A pattern finds them, without a model; it reads across a wrapped line's break.

Gaps. A final reply that declares something unchecked, unverified or out of reach is blocked
once, with the sentence: the agent lists every route that could settle it, each tried, cheap (a
check of a few minutes, taken at once), expensive (its cost named, left to the user) or closed,
then settles the question or asks for the narrowest open route. A pattern finds them in the
reply's text outside quotes and code spans.

Loops. A final reply that proposes a loop (a word for repetition with its "until") and holds no
`/goal` prompt for it blocks once: the agent gives the prompt unasked, as TASK_PROTOCOL.md's "Loops"
section says.

Unchecked claims. It asks Haiku whether the turn's final reply proposes building around a tool, or calls something
impossible, missing or costly, without the turn having checked what the tool already offers.
If so, the hook blocks the stop once with Haiku's reason, so the agent checks before the turn
ends. Haiku classifies the reply's sentence closest to the failure and quotes it; only an
unchecked workaround or missing-feature claim whose quote is found in the reply blocks, and
not when the reply declares the gap with a reason or a way to check it. The rule it enforces is
the engineering-discipline skill's: before designing around a tool's limit, check whether the tool
already does the job.

The reply comes from the hook input's `last_assistant_message`; the turn's tool calls from the
transcript, read backwards from its end only as far as the turn's first prompt. Haiku runs
through tools/haiku_judge.py, with this hook switched off in it. A judge that fails (no answer
within JUDGE_TIMEOUT seconds, no `claude` to run, an answer without the verdict asked for, a model
the API refuses) lets the stop through with a warning to the user naming the cause.

When `stop_hook_active` is set the stop already follows a block, so no check runs. The
repository's `.claude/settings.json` runs it for sessions in this clone; a session elsewhere
runs it through an entry in the global settings, with `--global` (see README.md), which checks
promises and claims, not this clone's requests.
"""
import json
import os
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from haiku_judge import INSIDE_JUDGE, MODEL, Failed, Refused, ask

JUDGE_TIMEOUT = 9.5
PROMPT = Path(__file__).with_name('unchecked-claim-prompt.txt')
# The noemesis clone this hook lives in; its own settings already run the hook there.
ROOT = Path(__file__).resolve().parents[2]
KINDS = {'workaround', 'missing-feature', 'other'}
BLOCKED_KINDS = {'workaround', 'missing-feature'}
# The newest calls are kept when a turn has more.
MAX_CALLS = 80
CALL_CHARS = 200
BLOCK = 1 << 20
# The input field that best says what each tool call did.
CALL_FIELDS = {'Bash': 'command', 'Read': 'file_path', 'Edit': 'file_path', 'Write': 'file_path',
               'WebSearch': 'query', 'WebFetch': 'url', 'Skill': 'skill', 'Grep': 'pattern',
               'Glob': 'pattern', 'ToolSearch': 'query'}


def is_prompt(entry):
    """A line that starts a turn: the user's own message, not a tool result or a meta line."""
    if entry.get('type') != 'user' or entry.get('isMeta') or entry.get('isSidechain'):
        return False
    content = (entry.get('message') or {}).get('content')
    if isinstance(content, str):
        return True
    return isinstance(content, list) and not any(b.get('type') == 'tool_result' for b in content)


def blocks_in(entry):
    """An assistant entry's tool calls, as (name, input), and its text and thinking blocks, in order."""
    content = (entry.get('message') or {}).get('content')
    if entry.get('type') != 'assistant' or not isinstance(content, list):
        return [], []
    calls = [(b.get('name'), b.get('input') or {}) for b in content if b.get('type') == 'tool_use']
    # A subagent's text is not the assistant's own.
    texts = [] if entry.get('isSidechain') else [b.get('text') or b.get('thinking') or '' for b in content
                                                 if b.get('type') in ('text', 'thinking')]
    return calls, texts


def read_turn(path):
    """The tool calls, and the text and thinking blocks, since the transcript's last prompt, each oldest
    first, reading backwards in blocks."""
    calls, texts, tail = [], [], b''
    with open(path, 'rb') as f:
        position = f.seek(0, 2)
        while position > 0:
            step = min(BLOCK, position)
            position -= step
            f.seek(position)
            lines = (f.read(step) + tail).split(b'\n')
            tail = lines.pop(0) if position > 0 else b''
            for line in reversed(lines):
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if is_prompt(entry):
                    return calls[::-1], texts[::-1]
                entry_calls, entry_texts = blocks_in(entry)
                calls.extend(reversed(entry_calls))
                texts.extend(reversed(entry_texts))
    return calls[::-1], texts[::-1]


# A promise about the assistant's own behaviour beyond the turn: first person and future tense, with a
# marker that it outlasts the turn, in either order within one sentence. Measured on one long session's
# 11,723 text and thinking blocks: 8 sentences matched, 6 of them such promises.
FIRST_PERSON = r"\bI(?:'ll| will| won't| will not| am going to|'m going to| shall)\b"
LASTING = (r"\b(?:going forward|from now on|from here on|henceforth|in (?:the )?future|next time|in future "
           r"sessions|every time|always|never again|from this point)\b")
NOT_AGAIN = r"\bI (?:won't|will not)\b[^.!?\n]*\bagain\b"
# A turning point that lasts, which promises with no first person at all: "from now on, runs go through it",
# "from the suite on, runs went through it". A named turning point ends its phrase at the "on", so "from this
# machine on the VPN" is not one. Measured on every local session's 21,230 text and thinking blocks: 12
# sentences matched only this, 5 of them promises, 2 a tool's new behaviour announced, 4 a design's future
# state, 1 a promise under discussion.
ONWARD = r"\bfrom (?:now|here|this point) on\b|\bfrom (?:the|this|that|my|our) [\w-]+(?: [\w-]+)? on\b(?![ \t]*\w)"
# A rule announced in the present as the assistant's own standing practice, with no future tense: "the rule I'm
# following now: never batch a commit with its edit". Measured on this machine's 9,322 text and thinking blocks:
# the one sentence it matches is that promise; describing a rule ("the rule I'm supposed to follow") and a
# present activity ("I'm now following the logs") are not matched.
RULE_NOW = r"\b(?:rule|practice|habit)s? (?:that )?I(?:'m| am| now) (?:now )?(?:following|applying|keeping|using)\b"
# An admission of what the assistant should have done, which promises to do it the next time without
# saying so: "I should have timed it before committing". Measured on one long session's 3,295 text and
# thinking blocks: 9 sentences matched, 7 of them such admissions and 2 the phrase quoted in discussion,
# which the quote filter drops.
REGRET = r"\bI (?:should|ought to)(?: not|n't)? have\b"
PROMISE = re.compile(rf"[^.!?\n]*(?:{FIRST_PERSON}[^.!?\n]*{LASTING}|{LASTING}[^.!?\n]*{FIRST_PERSON}|{NOT_AGAIN}|"
                     rf"{ONWARD}|{RULE_NOW}|{REGRET})[^.!?\n]*", re.I)


# Quoted text, such as an earlier promise under discussion or a document's sentence in a Markdown
# blockquote, and code spans, such as a hook's name, say nothing about this turn.
BLOCKQUOTE = r'^[ \t]*>[^\n]*'
QUOTED = re.compile(rf'"[^"\n]*"|“[^”\n]*”|`[^`\n]*`|{BLOCKQUOTE}', re.M)
# A declared gap: something left unchecked, unverified or out of reach, in the present (a past "didn't
# check" is usually narration). Measured on one long session's 3,831 text blocks: 130 matched, about two
# thirds of a sample real open questions, several with a cheap route not taken.
# "An unchecked claim" is the name of one of this hook's own checks, not a gap.
GAP = re.compile(r"[^.!?\n]*\b(?:unchecked(?! claims?\b)|unverified|not verified|not been verified|haven't (?:checked|"
                 r"verified|tested)|hasn't been (?:checked|verified)|couldn't (?:check|verify|read|confirm)|can't "
                 r"(?:check|verify|confirm|be read|be checked)|cannot (?:check|verify|confirm)|outside our access|"
                 r"needs your (?:access|login|credentials|session)|wasn't checked|weren't checked|not checked)"
                 r"(?![\w-])[^.!?\n]*", re.I)


def sentences(pattern, texts):
    """The sentences of `texts` that `pattern` matches outside quotes and code spans."""
    found = []
    for text in texts:
        # Quotes blanked to their length, so a match's span still points into the original text.
        unquoted = QUOTED.sub(lambda m: ' ' * len(m.group(0)), text)
        found += [' '.join(text[m.start():m.end()].split()) for m in pattern.finditer(unquoted)]
    return found


def promises(texts):
    """The sentences of `texts` that promise the assistant's behaviour beyond this turn."""
    return sentences(PROMISE, texts)


# A repository tool reported misbehaving: a sentence naming one of this clone's tools, written as a tool
# (`name`, name.py, tools/name), next to a word for what it got wrong. Measured on one long session's
# 12,943 text and thinking blocks: 22 sentences matched, about ten of them a tool's fault reported.
TOOLS_DIR = Path(__file__).resolve().parents[1]
TOOL_NAMES = sorted({p.stem for p in TOOLS_DIR.glob('*.py')} | {p.stem for p in TOOLS_DIR.glob('*.sh')}
                    | {p.stem for p in (TOOLS_DIR / 'hooks').glob('*.py')} | {'compute'}, key=len, reverse=True)
_NAMES = '|'.join(map(re.escape, TOOL_NAMES))
TOOL_REF = (rf"`(?:tools/(?:hooks/)?)?(?P<a>{_NAMES})(?:\.py|\.sh)?`|\btools/(?:hooks/)?(?P<b>{_NAMES})\b"
            rf"|\b(?P<c>{_NAMES})\.(?:py|sh)\b")
TOOL_PATTERN = re.compile(TOOL_REF)
FAULT = re.compile(r"\b(?:nested|merged|mangled|garbled|broke|breaks|split|dropped|lost|swallowed|indented|"
                   r"misplaced|misread|misreads|choked|wrongly|wrong|instead of|refused|refuses|has no way|"
                   r"didn't (?:handle|keep|match)|doesn't (?:handle|keep|match)|can't handle)\b", re.I)
SENTENCE_END = re.compile(r'[.!?\n]')
# Double quotes and blockquotes only: a tool's name is usually a code span, which the other checks blank.
DOUBLE_QUOTED = re.compile(rf'"[^"\n]*"|“[^”\n]*”|{BLOCKQUOTE}', re.M)


def tool_faults(texts):
    """(sentence, tool name) for each sentence of `texts` reporting a repository tool's fault.

    The tool references are found first and only their sentences searched for a fault word: a single
    pattern spanning the sentence backtracks at every position over the many tool names."""
    found = []
    for text in texts:
        unquoted = DOUBLE_QUOTED.sub(lambda m: ' ' * len(m.group(0)), text)
        seen = set()
        for ref in TOOL_PATTERN.finditer(unquoted):
            start = max(unquoted.rfind(mark, 0, ref.start()) for mark in '.!?\n') + 1
            end_match = SENTENCE_END.search(unquoted, ref.end())
            end = end_match.start() if end_match else len(unquoted)
            if start in seen or not FAULT.search(unquoted, start, end):
                continue
            seen.add(start)
            tool = ref.group('a') or ref.group('b') or ref.group('c')
            found.append((' '.join(text[start:end].split()), tool))
    return found


def edited(calls, tool):
    """Whether the turn's calls changed the tool or its test."""
    names = {f'{tool}.py', f'{tool}.sh', f'test_{tool}.py'}
    for name, tool_input in calls:
        if name in ('Edit', 'Write', 'NotebookEdit') and Path(str(tool_input.get('file_path', ''))).name in names:
            return True
    return False


def workaround_block(texts, calls):
    """The block for a turn that reports a repository tool's fault without changing the tool, or None."""
    for sentence, tool in tool_faults(texts):
        if not edited(calls, tool):
            return {'decision': 'block', 'reason': (
                f'A tool\'s fault, worked around: "{sentence}". Where a committed tool falls short, fix it with a '
                f'test in the same turn (AGENTS.md: "improve it until it does the job"), rather than correcting '
                f'its output by hand; if the fault was in how it was used, or the sentence reports no fault of '
                f'`{tool}`\'s, say so.')}
    return None


# A loop proposed or described as the way forward: a word for repetition with its "until" condition, in
# either order within one sentence. A numbered round ("round 4's reviewer") reports on a loop already running.
REPEATS = r"\b(?:loop|loops|looping|rounds?(?! \d)|iterate|iterating|iterations?|repeat|repeating|repeated)\b"
LOOP = re.compile(rf"[^.!?\n]*(?:{REPEATS}[^.!?\n]*\buntil\b|\buntil\b[^.!?\n]*{REPEATS})[^.!?\n]*", re.I)


def loop_block(reply):
    """The block for a final reply that proposes a loop and gives no /goal prompt for it, or None."""
    found = sentences(LOOP, [reply])
    if not found or '/goal' in reply:
        return None
    return {'decision': 'block', 'reason': (
        f'A loop with no /goal prompt: "{found[0]}". Give the prompt in this reply, unasked, written as '
        'research/notes/TASK_PROTOCOL.md\'s "Loops" section says: every way out inside the goal\'s condition '
        '(success, a round cap, non-convergence), and each round costed, with no run a later round repeats '
        'anyway. If the sentence proposes no loop to run, say so.')}


def gap_block(reply):
    """The block for a final reply that declares something unchecked, or None."""
    found = sentences(GAP, [reply])
    if not found:
        return None
    return {'decision': 'block', 'reason': (
        f'A declared gap: "{found[0]}". List every route that could settle it (the system\'s own API, CLI or '
        'UI, through the user\'s sessions; a credential or clone on this machine; a person who holds the '
        'access, found also from who owns and changes its configuration: CODEOWNERS, commit history, '
        'project members; documentation), each marked tried, with its result; cheap, a check of a few minutes, then '
        'take it now; expensive, with its cost, left to the user to decide; or closed, with why. Then settle '
        'the question, or ask for the narrowest open route. If the sentence leaves no question open, say so.')}


# A tool the framework lacks: no tool, helper or script does a job, or a scratch script stands in for one.
# Measured on one long session's 14,647 text and thinking blocks: 6 sentences matched, 5 of them a job
# done without a tool, the sixth this check's own description.
_THING = r"(?:helper|tool|script|utility)s?"
MISSING_TOOL = re.compile(
    rf"[^.!?\n]*(?:\bno (?:existing |committed |reusable )?{_THING} (?:exists|for|does|handles|covers|that)\b"
    rf"|\bthere(?:'s| is) no {_THING}\b|\b{_THING} (?:doesn't|does not) exist\b"
    rf"|\b(?:write|wrote|writing|written|use|using|used|with|via) (?:a|an|the|these|this) "
    rf"(?:scratch|throwaway|one-off|ad hoc|ad-hoc) {_THING}\b"
    rf"|\bnothing (?:in (?:the framework|the workspace|tools/) )?(?:does|handles|covers) (?:this|that|it)\b)"
    rf"[^.!?\n]*", re.I)
QUEUED = re.compile(r"\blead_queue\.py\s+(?:add|append)\b")


def followed_up(calls):
    """Whether the turn's calls queued an item or changed a file under tools/."""
    for name, tool_input in calls:
        if name == 'Bash' and QUEUED.search(str(tool_input.get('command', ''))):
            return True
        if name in ('Edit', 'Write', 'NotebookEdit') and 'tools' in Path(str(tool_input.get('file_path', ''))).parts:
            return True
    return False


def missing_tool_block(texts, calls):
    """The block for a turn that names a missing tool without building or queuing it, or None."""
    found = sentences(MISSING_TOOL, texts)
    if not found or followed_up(calls):
        return None
    return {'decision': 'block', 'reason': (
        f'A missing tool: "{found[0]}". A job without a tool recurs; build the tool, with its test, or queue it '
        '(tools/lead_queue.py add notebook.html --build ID SOURCE TEXT) in this turn, so the need outlives it '
        '(AGENTS.md: "Extend committed, tested tools for recurring helpers"). If the job is a genuine one-off, '
        'or the sentence names no missing tool, say so.')}


# A step handed to someone else. Measured on one long session's 14,847 text and thinking blocks and
# 13,411 tool calls' written content (edits' new text, written files, commands), in 0.39 s: 8 sentences
# matched, 3 of them a step left to others (a reply, a plan edit, a commit message), one a runbook's
# instruction to hand a token to its owners, and 4 this check's own test fixtures.
_GAP = r"[ \t]*\n?[ \t]*(?:#[ \t]*)?"  # a word gap, a wrapped line's break (and a comment's #) included
_WHO = rf"(?:owners?|team|maintainers?|code{_GAP}?owners?|admins?|platform{_GAP}team|other{_GAP}team)"
# The phrase alone: its sentence is found around it by deferrals(), since a pattern spanning a sentence
# across wrapped lines backtracks over every start position (54 s over the session above).
DEFERRAL = re.compile(
    rf"(?:\b(?:left|leave|leaving|hand(?:ed|ing)?|defer(?:red|ring)?|pass(?:ed|ing)?){_GAP}"
    rf"(?:(?:it|this|that|them|these|those){_GAP})?(?:to|for){_GAP}(?:the|their|its){_GAP}{_WHO}\b"
    rf"|\bfor{_GAP}(?:the|their|its){_GAP}{_WHO}{_GAP}to{_GAP}(?:decide|confirm|check|fix|remove|clean)\b"
    rf"|\bup{_GAP}to{_GAP}(?:the|their|its){_GAP}{_WHO}\b"
    rf"|\b(?:the|their|its){_GAP}owners'?{_GAP}(?:call|decision|job|problem)\b"
    rf"|\bnot{_GAP}(?:this{_GAP}task's|ours){_GAP}to{_GAP}(?:decide|fix|change|remove)\b)", re.I)
WRITTEN_FIELDS = ('new_string', 'content', 'new_source', 'command')
_SENTENCE_BREAK = re.compile(r'[.!?]|\n[ \t]*\n')


def deferrals(texts):
    """The sentences of `texts` handing a step to someone else, outside quotes and code spans, each read
    across a wrapped line's breaks up to a sentence's end or a blank line."""
    found = []
    for text in texts:
        unquoted = QUOTED.sub(lambda m: ' ' * len(m.group(0)), text)
        seen = set()
        for phrase in DEFERRAL.finditer(unquoted):
            start = max([0] + [m.end() for m in _SENTENCE_BREAK.finditer(unquoted, 0, phrase.start())][-1:])
            end_match = _SENTENCE_BREAK.search(unquoted, phrase.end())
            end = end_match.start() if end_match else len(unquoted)
            if start not in seen:
                seen.add(start)
                found.append(' '.join(text[start:end].split()))
    return found


# Where the patterns' own examples are written: the checks' code and their tests. A sentence there is a
# fixture of a check, not something the turn says; an edit adding a deferral example to a test was blocked
# as a step handed to others (9 October 2026).
OWN_FIXTURES = re.compile(r"(?:^|/)tools/(?:hooks/[^/]+|measure_stop_checks\.py|tests/test_(?:stop_checks|during_run|"
                          r"codex_unchecked_claim|measure_stop_checks|unlisted_work)\.py)$")


def written(calls):
    """What the turn's calls write: edits' new text, written files and commands; not what they write into
    the checks' own code and tests."""
    return [str(tool_input[field]) for _, tool_input in calls for field in WRITTEN_FIELDS
            if isinstance(tool_input.get(field), str)
            and not OWN_FIXTURES.search(str(tool_input.get('file_path') or tool_input.get('notebook_path') or ''))]


def deferral_block(texts, calls):
    """The block for a turn that hands a step to someone else, or None."""
    found = deferrals(texts + written(calls))
    if not found:
        return None
    return {'decision': 'block', 'reason': (
        f'A step handed to others: "{found[0]}". Take it apart and settle each part yourself '
        '(TASK_PROTOCOL.md, A request for someone else\'s action): what access it needs; whether we lack '
        'it, checked; who holds it, from the role lists, CODEOWNERS or commit history; how the system does '
        'it today; and a route around it. Do what needs no access we lack, and record what is left as a '
        'request (tools/task_index.py request add --to-others), naming who acts. If the sentence hands '
        'no step to anyone, say so.')}


# A mistake of the assistant's own, admitted. Measured on one machine's 7,766 text and thinking blocks with
# a wider pattern, which also took "I didn't run it": 27 sentences, about 15 of a sample of 24 such
# admissions and 5 a gap declared, which the gap check has; that branch is left out here.
MISTAKE = re.compile(r"[^.!?\n]*(?:\bmy (?:own )?(?:mistake|error|fault|oversight)\b|\bI (?:was|had been) wrong\b|"
                     r"\bI got (?:it|that|this) wrong\b|\bI never (?:measured|checked|tested|verified|read|looked|"
                     r"timed|ran|tried)\b|\bI (?:missed|overlooked|misjudged|misread)\b|"
                     r"\bI (?:phrased|put) (?:it|that) badly\b|\bwas avoidable\b)[^.!?\n]*", re.I)
# The paragraph that answers it, in what the user is told.
PREVENTION = re.compile(r'^[\s>*#-]*Prevention\b', re.M)


def mistake_block(texts, told):
    """The block for a turn that admits a mistake while what the user is told (`told`) has no
    Prevention paragraph, or None."""
    found = sentences(MISTAKE, texts)
    if not found or PREVENTION.search(told):
        return None
    return {'decision': 'block', 'reason': (
        f'A mistake admitted with no prevention: "{found[0]}". The user must not have to ask how it is prevented. '
        'Give, unasked, a paragraph that starts "Prevention": the class of the mistake in general terms (not this '
        'instance), why the existing rules and checks let it through, and the framework change made in this turn '
        'that stops the class (a check, a hook, a test, a tool that reports or refuses; a written rule only where '
        'nothing mechanical can), or the build item queued for it with tools/lead_queue.py. A fix of the one '
        'instance is not a prevention. If the sentence admits no mistake of yours, say so.')}


def promise_block(texts):
    """The block for a turn that promises future behaviour, or None."""
    found = promises(texts)
    if not found:
        return None
    return {'decision': 'block', 'reason': (
        f'A promise about future behaviour, or an admission that implies one: "{found[0]}". Nothing said in a '
        'turn, its thinking included, survives compaction or a new session; only the framework does. Name the '
        'change this turn made that enforces it (a rule in its durable home, a check, a hook, a tool), make one, '
        'or propose one; if the sentence promises nothing beyond this turn, say so.')}


def describe(calls):
    """One line per tool call, its name and what it did."""
    lines = []
    for name, tool_input in calls[-MAX_CALLS:]:
        if name == 'Agent':
            detail = f"{tool_input.get('subagent_type', '')}: {tool_input.get('description', '')}"
        else:
            detail = str(tool_input.get(CALL_FIELDS.get(name), ''))
        lines.append(f"- {name}: {' '.join(detail.split())[:CALL_CHARS]}".rstrip(': '))
    if len(calls) > MAX_CALLS:
        lines.insert(0, f'({len(calls) - MAX_CALLS} earlier calls left out)')
    return '\n'.join(lines) or '(none)'


def judge(reply, calls):
    """Haiku's verdict as {'ok': bool, ...}; {'error': str, 'refused': bool} when the call fails,
    refused being whether the API refused it, such as for a retired model."""
    prompt = PROMPT.read_text().replace('$TOOL_CALLS', describe(calls)).replace('$REPLY', reply)
    try:
        verdict = ask(prompt, JUDGE_TIMEOUT)
    except Failed as error:
        return {'error': str(error), 'refused': isinstance(error, Refused)}
    checked = validate_verdict(reply, verdict)
    if checked is None:
        return {'error': f'the answer lacked the verdict asked for: {json.dumps(verdict)[:200]}', 'refused': False}
    return checked


def validate_verdict(reply, verdict):
    """Shared host-side predicate; a fabricated quote never blocks either agent."""
    if not isinstance(verdict, dict) or verdict.get('kind') not in KINDS or not isinstance(verdict.get('checked'), bool) \
            or not isinstance(verdict.get('declared'), bool):
        return None
    quote = str(verdict.get('quote', ''))
    # A block must quote the reply; one that doesn't is the judge's invention, and passes.
    quoted = bool(quote.strip()) and ' '.join(quote.split()) in ' '.join(reply.split())
    failed = verdict['kind'] in BLOCKED_KINDS and not verdict['checked'] and not verdict['declared'] and quoted
    return {'ok': not failed, 'kind': verdict['kind'], 'quote': quote, 'reason': str(verdict.get('reason', ''))}


PROTOCOL = 'research/notes/TASK_PROTOCOL.md'
CHECKS_OFF = 'tools/hooks/checks_off'
# The checks a branch can turn off, by the names tools/measure_stop_checks.py prints.
CHECK_NAMES = ('promise', 'mistake', 'workaround', 'missing tool', 'deferral', 'gap', 'loop', 'judge')


def has_protocol(root):
    """Whether the branch at `root` works under the task protocol. The checks that send the agent to it
    (requests waiting for the judge, a step handed to others, a loop proposed without its prompt) run
    only there."""
    return (Path(root) / PROTOCOL).is_file()


def checks_off(root):
    """The checks the branch at `root` turns off: one name of CHECK_NAMES a line of its
    tools/hooks/checks_off, the name taken whole. No file turns nothing off, and a line that names no
    check turns nothing off (the hooks' test fails on such a line in this branch's own file)."""
    try:
        lines = (Path(root) / CHECKS_OFF).read_text().splitlines()
    except OSError:
        return frozenset()
    return frozenset(line.strip() for line in lines)


def waiting_block(root):
    """The block for requests in `root`'s tasks that wait for the judge, or None when none wait."""
    if not has_protocol(root):
        return None
    import task_index
    try:
        waiting = task_index.waiting(root)
    except (task_index.TaskError, ValueError, OSError):
        return None
    if not waiting:
        return None
    listed = ', '.join(f'{slug} request {label}' for slug, label in waiting)
    return {'decision': 'block', 'reason': (
        f'Requests for others wait for the judge: {listed}. Once all of a task\'s requests are ready, '
        'run tools/task_index.py request judge SLUG, fix any it refuses, then answer again: a request '
        'reaches the user only judged (TASK_PROTOCOL.md, A request for someone else\'s action).')}


def turn_block(texts, calls, said, off):
    """The first block among the checks that run at a stop and at a commit alike (a promise, an admitted
    mistake, a tool's fault worked around, a declared gap), those named in `off` left out; or None.
    `said` is what the gap check reads: the final reply, or what was said since the last commit."""
    checks = (('promise', lambda: promise_block(texts)), ('mistake', lambda: mistake_block(texts, '\n'.join(texts))),
              ('workaround', lambda: workaround_block(texts, calls)), ('gap', lambda: gap_block(said)))
    return next(filter(None, (check() for name, check in checks if name not in off)), None)


def emit_block(decision):
    """Print the decision that blocks the stop, and count it for the cycle (tools/cycle_numbers.py)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import block_log
    block_log.record('stop_checks')
    print(json.dumps(decision))


def main(argv):
    if os.environ.get(INSIDE_JUDGE):
        return 0
    # The global entry leaves noemesis's own sessions to the project entry, so a stop is checked once.
    global_entry = '--global' in argv
    project = os.environ.get('CLAUDE_PROJECT_DIR')
    if global_entry and project and Path(project).resolve() == ROOT:
        return 0
    data = json.load(sys.stdin)
    if data.get('stop_hook_active'):
        return 0
    blocked = None if global_entry else waiting_block(ROOT)
    if blocked:
        emit_block(blocked)
        return 0
    reply = data.get('last_assistant_message') or ''
    path = data.get('transcript_path')
    try:
        calls, texts = read_turn(path) if path else ([], [])
    except OSError:
        calls, texts = [], []
    # The final reply may not be in the transcript yet when the hook runs.
    turn_texts = texts + ([reply] if reply not in texts else [])
    off, protocol = checks_off(ROOT), has_protocol(ROOT)
    blocked = turn_block(turn_texts, calls, reply, off) or next(filter(None, (
        check() for name, check in (('missing tool', lambda: missing_tool_block(turn_texts, calls)),
                                    ('deferral', lambda: protocol and deferral_block(turn_texts, calls)),
                                    ('loop', lambda: protocol and loop_block(reply)))
        if name not in off)), None)
    if blocked:
        emit_block(blocked)
        return 0
    if not reply.strip() or 'judge' in off:
        return 0
    verdict = judge(reply, calls)
    if verdict and verdict.get('refused'):
        # A refused call would let every stop through unseen; warn on each one until the hook is fixed.
        print(json.dumps({'systemMessage': (
            f"stop-checks hook: the judge model {MODEL} failed ({verdict['error']}), so every stop "
            'passes unchecked. Switch MODEL in tools/haiku_judge.py to an available model.')}))
    elif verdict and 'error' in verdict:
        print(json.dumps({'systemMessage': (
            f"stop-checks hook: the judge failed ({verdict['error']}), so this stop passed unchecked.")}))
    elif verdict and not verdict['ok']:
        emit_block({'decision': 'block', 'reason': (
            f"Unchecked claim: \"{verdict['quote']}\" {verdict['reason']} Check what the tool already offers (its "
            'documentation, --help, a scratch test), then answer again; if this turn already '
            'checked, say what it found.')})
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
