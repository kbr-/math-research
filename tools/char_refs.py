"""HTML character references that have lost their ampersand.

A sed replacement whose text held a reference such as the apostrophe's put the matched text in place
of each "&", and three committed notebook entries carried the result (budget#39;s, (quot;spend).
check_records.py flags such lines before a commit and notebook-append.py refuses such an entry.
"""
import re

# A numeric reference right after a character other than "&" (prose writes "issue #12;" after a
# space), or a named one the notebook uses, not after a letter (so "while;" is not a broken "le;").
BROKEN_ENTITY = re.compile(r'(?<=[^&\s])#(?:\d+|x[0-9a-fA-F]+);'
                           r'|(?<![&A-Za-z])(?:quot|amp|nbsp|ndash|mdash|rsquo|lsquo|ldquo|rdquo|hellip);')


def broken_entities(text):
    """The character references in `text` that have lost their ampersand."""
    return [m.group(0) for m in BROKEN_ENTITY.finditer(text)]
