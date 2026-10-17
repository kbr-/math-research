"""No statement tested: counts the notebook's math delimiters and lists each display opener met while another is
open, to see whether notebook_math.protect_math, now applied before the ledger and claim-inventory parsers as it
is by the site's builder, can pair an opener with the wrong closer (a reviewer's question, 17 October 2026).
"""
import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text()
print(f'inline openers {text.count(chr(92) + "(")}, closers {text.count(chr(92) + ")")}; '
      f'display openers {text.count(chr(92) + "[")}, closers {text.count(chr(92) + "]")}')
opened = None
for match in re.finditer(r'\\\[|\\\]', text):
    if match.group() == '\\[':
        if opened is not None:
            print('opener while open:', repr(text[opened:opened + 30]), 'then', repr(text[match.start() - 2:match.start() + 8]))
        opened = match.start()
    else:
        opened = None
print('display openers preceded by a backslash (TeX line breaks such as \\\\[2pt]):',
      len(re.findall(r'\\\\\[', text)))
