"""Math delimiters protect comparisons without escaping notebook markup twice."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from notebook_math import protect_math


class MathMarkup(unittest.TestCase):
    def test_math_angles_and_existing_entities(self):
        source = r'<p title="keep">\(a<b>c\), \[P_{<a}\n>0\], $$u<v>w$$; \(x&lt;y&gt;z\). $5 to $6.</p>'
        expected = r'<p title="keep">\(a&lt;b&gt;c\), \[P_{&lt;a}\n&gt;0\], $$u&lt;v&gt;w$$; \(x&lt;y&gt;z\). $5 to $6.</p>'
        self.assertEqual(protect_math(source), expected)
        self.assertEqual(protect_math(expected), expected)


if __name__ == '__main__':
    unittest.main()
