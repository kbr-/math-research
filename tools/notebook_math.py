"""Protect notebook TeX from HTML parsing without changing stored mathematics."""
# SPDX-License-Identifier: MIT
import re


# An opener preceded by a backslash is an escaped backslash and a bracket, not an opener: prose quoting the TeX
# line break "\\[2pt]" opened a display match there that ran 14230 characters to the next closer and hid the next
# entry's article tag from every tool that masks with this pattern (17 October 2026; over the nine notebooks the
# lookbehind changes two of 403,298 matches, that one and a double-escaped \\(\square\\),
# research/results/rank_floor_20261017/math-regex-lookbehind.txt).  Inside display math the lazy match has
# already started, so a line break there is unaffected.
MATH = re.compile(r'(?<!\\)\\\([\s\S]*?\\\)|(?<!\\)\\\[[\s\S]*?\\\]|\$\$[\s\S]*?\$\$')


def protect_math(source):
    """Escape raw angle brackets in math; leave existing entities and HTML alone."""
    return MATH.sub(lambda match: match.group().replace('<', '&lt;').replace('>', '&gt;'), source)


TAG = re.compile(r'<[^>]*>')


def strip_tags(fragment, replacement=' '):
    """The fragment with its HTML tags replaced, its mathematics kept: a raw < inside TeX is escaped first, so
    the tag pattern cannot run from it to the next tag's >.  Measured on the main notebook of 16 October 2026,
    269 of its 74,060 math spans hold a raw < that the bare pattern runs past, and stripping the whole notebook
    without protection loses 72,253 characters.  Brackets come back as &lt; and &gt;, which html.unescape
    restores."""
    return TAG.sub(replacement, protect_math(fragment))


def strip_tags_tight(fragment):
    """strip_tags with tags removed rather than replaced by a space."""
    return strip_tags(fragment, '')
