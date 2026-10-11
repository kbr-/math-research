#!/usr/bin/env python3
"""Claude Code Stop hook: the checks a turn's end must pass.

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

Gaps. A final reply that declares something unchecked, unverified or out of reach is blocked
once, with the sentence: the agent lists every route that could settle it, each tried, cheap (a
check of a few minutes, taken at once), expensive (its cost named, left to the user) or closed,
then settles the question or asks for the narrowest open route. A pattern finds them in the
reply's text outside quotes and code spans.

A branch's own checks. Where the branch has a module of its own (tools/branch_extension.py), the hook
asks it for a block that comes before every other check and for further checks of the turn, which run
after the ones above and are turned off by the names the module gives.

Unchecked claims. It asks Haiku whether the turn's final reply proposes building around a tool, or calls something
impossible, missing or costly, without the turn having checked what the tool already offers.
If so, the hook blocks the stop once with Haiku's reason, so the agent checks before the turn
ends. Haiku classifies the reply's sentence closest to the failure and quotes it; only an
unchecked workaround or missing-feature claim whose quote is found in the reply blocks, and
not when the reply declares the gap with a reason or a way to check it. The rule it enforces:
before designing around a tool's limit, check whether the tool already does the job.

The reply comes from the hook input's `last_assistant_message`; the turn's tool calls from the
transcript, read backwards from its end only as far as the turn's first prompt. Haiku runs
through tools/haiku_judge.py, with this hook switched off in it. A judge that fails (no answer
within JUDGE_TIMEOUT seconds, no `claude` to run, an answer without the verdict asked for, a model
the API refuses) lets the stop through with a warning to the user naming the cause.

When `stop_hook_active` is set the stop already follows a block, so no check runs. The
repository's `.claude/settings.json` runs it for sessions in this clone; a session elsewhere
runs it through an entry in the global settings, with `--global`, which leaves out the
block the branch's own module puts first.
"""
import json
import os
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import branch_extension
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
# A fenced block is text handed over (a prompt for the user to paste, a command, a file's lines), not the
# reply's own account: a goal prompt's condition that named a tool beside the word "merged" was taken three
# times for a tool's fault worked around.
FENCED = r'(?s:^[ \t]*```.*?^[ \t]*```)'
QUOTED = re.compile(rf'{FENCED}|"[^"\n]*"|“[^”\n]*”|`[^`\n]*`|{BLOCKQUOTE}', re.M)
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
DOUBLE_QUOTED = re.compile(rf'{FENCED}|"[^"\n]*"|“[^”\n]*”|{BLOCKQUOTE}', re.M)


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





# The gap's words used for something else: the outcome a tool gives a case ("reports such a scenario as
# unverified", "leaves the scenario unverified"), a thing so described ("an unverified signer"), a past
# omission told ("I had not checked it"), or what a tool cannot do ("this can't verify that"). Read on the
# 39 replies of one long session that the pattern blocked: 11 were of these kinds.
NOT_A_GAP = re.compile(
    r"\b(?:report(?:s|ed|ing)?|show[ns]?|mark(?:s|ed)?|list(?:s|ed)?|flag(?:s|ged)?|count(?:s|ed)?)\b[^.!?\n]{0,60}?"
    r"\bas (?:an? )?[\"“]?(?:unverified|unchecked|not checked)\b"
    r"|\bleav(?:e|es|ing) (?:the |a |that |such a )?(?:scenario|test|case|claim|row|finding)s? unverified\b"
    r"|\b(?:an?|loses|keeps) (?:unverified|unchecked) [a-z]+"
    r"|\bwhen unchecked\b|\bhad(?: not|n't) (?:been )?(?:checked|verified)\b"
    r"|\b(?:this|it|that|the (?:tool|check|hook|script|judge)) (?:can't|cannot) (?:check|verify|confirm)\b"
    # What a tool or a reply says, in the third person: "prints a warning that the names weren't checked".
    r"|\b(?:prints|warns|says|tells|reports|states|printed|warned)\b[^.!?\n]{0,80}?\b(?:wasn't|weren't|was not|were not|went) "
    r"(?:un)?checked\b"
    r"|\b(?:go|goes|went|going) unchecked\b"
    # A gap denied: "not something unverified", "nothing in them was unverified".
    r"|\b(?:not|nothing|none|no)\b(?: \w+){0,4} (?:unverified|unchecked)\b", re.I)


def gap_block(reply):
    """The block for a final reply that declares something unchecked, or None."""
    found = [sentence for sentence in sentences(GAP, [reply]) if GAP.search(NOT_A_GAP.sub(' ', sentence))]
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





# A mistake of the assistant's own, admitted. Measured on one machine's 7,766 text and thinking blocks with
# a wider pattern, which also took "I didn't run it": 27 sentences, about 15 of a sample of 24 such
# admissions and 5 a gap declared, which the gap check has; that branch is left out here.
MISTAKE = re.compile(r"[^.!?\n]*(?:\bmy (?:own )?(?:mistake|error|fault|oversight)\b|\bI (?:was|had been) wrong\b|"
                     r"\bI got (?:it|that|this) wrong\b|\bI never (?:measured|checked|tested|verified|read|looked|"
                     r"timed|ran|tried)\b|\bI (?:missed|overlooked|misjudged|misread)\b|"
                     r"\bI (?:phrased|put) (?:it|that) badly\b|\bwas avoidable\b|"
                     # A claim of one's own taken back is a mistake admitted in other words.
                     r"\bI (?:had )?(?:overstated|misstated|misquoted)\b|\bI (?:withdraw|withdrew|retract(?:ed)?) "
                     r"(?:my|the|that|this)\b|\bmy (?:own )?(?:\w+ )?(?:claim|statement|reading|draft|conclusion) "
                     r"(?:was|is) (?:wrong|overstated|withdrawn|mistaken)\b)[^.!?\n]*", re.I)
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
    # The check is about a third-party tool: a verdict that names none, or names one of this repository's own,
    # is about something else. Of 24 blocks read on 10 October 2026, 6 were so, none of them a right block.
    tool = re.sub(r'^(?:\./)?(?:tools/(?:hooks/)?)?|\.(?:py|sh)$', '', str(verdict.get('tool') or '').strip().strip('`'))
    third_party = bool(tool) and tool.replace('-', '_') not in {name.replace('-', '_') for name in TOOL_NAMES}
    failed = (verdict['kind'] in BLOCKED_KINDS and not verdict['checked'] and not verdict['declared'] and quoted
              and third_party)
    return {'ok': not failed, 'kind': verdict['kind'], 'quote': quote, 'reason': str(verdict.get('reason', ''))}


CHECKS_OFF = 'tools/hooks/checks_off'
# The checks a branch can turn off, by name: this hook's own, then those of the branch's own module.
# 'review' is no check of a stop: it turns off the stand-in review (tools/stand_in_review.py).
CHECK_NAMES = (('promise', 'mistake', 'workaround', 'missing tool', 'gap', 'judge', 'review')
               + tuple(branch_extension.ask('STOP_CHECK_NAMES', ())))


def branch_block(root):
    """The block the branch's own module puts before every other check of a stop, or None."""
    first = branch_extension.ask('stop_first_block')
    return first(root) if first else None


def branch_checks(texts, calls, reply, root):
    """The branch's own further checks of a turn's end, in its order, each as (name, check)."""
    further = branch_extension.ask('stop_checks')
    return tuple(further(texts, calls, reply, root)) if further else ()




def checks_off(root):
    """The checks the branch at `root` turns off: one name of CHECK_NAMES a line of its
    tools/hooks/checks_off, the name taken whole. No file turns nothing off, and a line that names no
    check turns nothing off (the hooks' test fails on such a line in this branch's own file)."""
    try:
        lines = (Path(root) / CHECKS_OFF).read_text().splitlines()
    except OSError:
        return frozenset()
    return frozenset(line.strip() for line in lines)





def turn_block(texts, calls, said, off):
    """The first block among the checks that run at a stop and at a commit alike (a promise, an admitted
    mistake, a tool's fault worked around, a declared gap), those named in `off` left out; or None.
    `said` is what the gap check reads: the final reply, or what was said since the last commit."""
    checks = (('promise', lambda: promise_block(texts)), ('mistake', lambda: mistake_block(texts, '\n'.join(texts))),
              ('workaround', lambda: workaround_block(texts, calls)), ('gap', lambda: gap_block(said)))
    return next(filter(None, (check() for name, check in checks if name not in off)), None)





def emit_block(decision):
    """Print the decision that blocks the stop, and log it with what it said."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import block_log
    block_log.record('stop_checks', what=decision.get('reason', ''))
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
    blocked = None if global_entry else branch_block(ROOT)
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
    off = checks_off(ROOT)
    blocked = turn_block(turn_texts, calls, reply, off) or next(filter(None, (
        check() for name, check in ((('missing tool', lambda: missing_tool_block(turn_texts, calls)),)
                                    + branch_checks(turn_texts, calls, reply, ROOT))
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
    # The branch's own module asks for this one by name; it gets this copy, not a second one.
    sys.modules.setdefault('stop_checks', sys.modules['__main__'])
    sys.exit(main(sys.argv[1:]))
