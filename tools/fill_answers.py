#!/usr/bin/env python3
"""Fill the rests-on lines of an answers file written by tools/draft_claim_sentences.py --answers, by sentence ID.

Usage: tools/fill_answers.py FILE ID ANSWER [ID ANSWER ...]

Each ID is the eight-hex identifier that opens a sentence's line in the file. An ID not in the file is refused,
nothing being written, and the IDs still unanswered after the fill are printed. On 16 October 2026 a scratch helper
filled the lines in file order; a sentence added to a draft shifted the order and two answers landed on the wrong
sentences, which the append caught only by their words.
"""
import re
import sys
from pathlib import Path

LINE = re.compile(r'^([0-9a-f]{8})\b')


def fill(text, answers):
    """(new text, unanswered IDs); raises ValueError naming any ID of `answers` not in the text, or an answer
    holding a line break. "Unanswered" means an empty rests-on line only: tools/notebook-append.py also refuses
    an answer of fewer than four words or with no ground (draft_claim_sentences.grounded)."""
    broken = [ident for ident, answer in answers.items() if '\n' in answer]
    if broken:
        raise ValueError('an answer holds a line break: ' + ', '.join(broken))
    lines = text.split('\n')
    known = [m.group(1) for line in lines if (m := LINE.match(line))]
    missing = [ident for ident in answers if ident not in known]
    if missing:
        raise ValueError('not in the answers file: ' + ', '.join(missing))
    current = None
    for i, line in enumerate(lines):
        found = LINE.match(line)
        if found:
            current = found.group(1)
        elif line.strip().startswith('rests on:') and current in answers:
            lines[i] = '  rests on: ' + answers[current]
    unanswered, current = [], None
    for line in lines:
        found = LINE.match(line)
        if found:
            current = found.group(1)
        elif line.strip() == 'rests on:' and current:
            unanswered.append(current)
    return '\n'.join(lines), unanswered


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) < 3 or len(argv) % 2 == 0:
        print(__doc__.split('\n\n')[1], file=sys.stderr)
        return 2
    path = Path(argv[0])
    repeated = sorted({ident for ident in argv[1::2] if argv[1::2].count(ident) > 1})
    if repeated:
        print('fill_answers: an ID is given twice: ' + ', '.join(repeated) + '; nothing written', file=sys.stderr)
        return 1
    answers = dict(zip(argv[1::2], argv[2::2]))
    try:
        text, unanswered = fill(path.read_text(), answers)
    except ValueError as error:
        print(f'fill_answers: {error}; nothing written', file=sys.stderr)
        return 1
    path.write_text(text)
    print(f'Filled {len(answers)} answers in {path}; unanswered: {", ".join(unanswered) or "none"}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
