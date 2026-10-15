"""Protect notebook TeX from HTML parsing without changing stored mathematics."""
# SPDX-License-Identifier: MIT
import re


MATH = re.compile(r'\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]|\$\$[\s\S]*?\$\$')


def protect_math(source):
    """Escape raw angle brackets in math; leave existing entities and HTML alone."""
    return MATH.sub(lambda match: match.group().replace('<', '&lt;').replace('>', '&gt;'), source)
