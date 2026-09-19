"""Versioned evidence normalization for explicitly generated article decorations.

Existing evidence defaults to raw bytes. This module never rewrites old hashes.
"""
from html.parser import HTMLParser
import re

ARTICLE_NORMALIZATION = 'notebook-article-v1'
FRAGMENT_NORMALIZATION = 'notebook-fragment-v1'

def normalize_evidence(source, version):
    if version == ARTICLE_NORMALIZATION:
        return normalize_article(source, version)
    if version == FRAGMENT_NORMALIZATION:
        # Notebook heading excerpts omit their enclosing article. Restore only
        # that parsing scope, then remove the synthetic wrapper byte-for-byte.
        result = normalize_article('<article>' + source + '</article>', ARTICLE_NORMALIZATION)
        return result[len('<article>'):-len('</article>')]
    raise ValueError('Unknown evidence normalization: ' + str(version))



def normalize_article(source, version):
    if version != ARTICLE_NORMALIZATION:
        raise ValueError('Unknown evidence normalization: ' + str(version))
    if not re.match(r'\s*<article\b', source):
        raise ValueError('Article evidence normalization requires an article excerpt')
    parser = _Decorations(source)
    masked = re.sub(r'\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]',
                    lambda m: m.group().replace('<', ' ').replace('>', ' '), source)
    parser.feed(masked); parser.close()
    if parser.stack:
        raise ValueError('Unclosed markup in article evidence')
    for start, end in sorted(parser.remove, reverse=True):
        source = source[:start] + source[end:]
    return source


class _Decorations(HTMLParser):
    VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source, self.stack, self.remove = source, [], []
        self.offsets = [0]
        for line in source.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))

    def position(self):
        line, col = self.getpos()
        return self.offsets[line - 1] + col

    def handle_starttag(self, tag, attributes):
        if tag in self.VOID:
            return
        attrs = dict(attributes)
        parent = self.stack[-1] if self.stack else None
        generated = None
        if (tag == 'div' and attrs.get('data-generated') == 'finish-turn-timing-v1'
                and attrs.get('class') == 'timing-report' and attrs.get('data-session')
                and parent and parent['tag'] == 'article'):
            generated = 'timing'
        if (tag == 'span' and attrs.get('data-generated') == 'finish-turn-producer-v1'
                and parent and parent['tag'] == 'p'
                and parent['attrs'].get('class') == 'entry-meta'
                and len(self.stack) >= 2 and self.stack[-2]['tag'] == 'article'):
            generated = 'producer'
        self.stack.append({'tag':tag,'attrs':attrs,'start':self.position(),
                           'body':self.position()+len(self.get_starttag_text()),'generated':generated})

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if not self.stack or self.stack[-1]['tag'] != tag:
            raise ValueError('Unbalanced markup in article evidence: ' + tag)
        item = self.stack.pop()
        start, end = item['start'], self.source.index('>', self.position())+1
        if item['generated'] == 'timing':
            self.remove.append((start,end))
        elif item['generated'] == 'producer':
            body = self.source[item['body']:self.position()]
            if not re.fullmatch(r'Produced by [^<>\n]+ \([^<>\n]+\)\.', body):
                return  # A differently shaped span is substantive evidence.
            if not re.match(r'\s*</p>', self.source[end:]):
                return  # Ignore only the generated terminal credit, never interior prose.
            if start and self.source[start-1] == ' ':
                start -= 1  # Exactly the one space inserted by credit_producer.
            self.remove.append((start,end))

    def handle_comment(self, data):
        if (re.fullmatch(r' TIMING [A-Za-z0-9_.-]+ ', data) and self.stack
                and self.stack[-1]['tag'] == 'article'):
            start=self.position();self.remove.append((start,self.source.index('-->',start)+3))
