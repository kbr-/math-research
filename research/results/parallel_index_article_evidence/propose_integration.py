"""Generate/test exact minimal shared-file changes without editing shared files."""
import difflib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]

def proposed_sources(root=ROOT):
    changes={}
    path='tools/claim_reviews.py';old=(root/path).read_text();new=old
    if 'from claim_evidence import' not in new:
        new=new.replace('from claim_registry import ROOT, TEXT_FIELDS, local_target, require',
            'from claim_registry import ROOT, TEXT_FIELDS, local_target, require\nfrom claim_evidence import ARTICLE_NORMALIZATION, normalize_article')
        new=new.replace('def sha256(self, target):\n        if target in self.cache:\n            return self.cache[target]',
            'def sha256(self, target, normalization=None):\n        key = (target, normalization)\n        if key in self.cache:\n            return self.cache[key]')
        new=new.replace("        self.cache[target] = hashlib.sha256(content).hexdigest()\n        return self.cache[target]", "        if normalization is not None:\n            if not (path.suffix == '.html' and anchor):\n                raise ValueError('Article normalization requires an anchored HTML target')\n            content = normalize_article(content.decode(), normalization).encode()\n        self.cache[key] = hashlib.sha256(content).hexdigest()\n        return self.cache[key]\n\n    def snapshot(self, target):\n        normalization = None\n        local = local_target(target, self.root)\n        if local is not None:\n            path, anchor = local\n            if path.suffix == '.html' and anchor:\n                self.sha256(target)  # Load and validate the raw excerpt first.\n                if self.notebooks[path].anchor(anchor)['tag'] == 'article':\n                    normalization = ARTICLE_NORMALIZATION\n        item = {'target': target, 'sha256': self.sha256(target, normalization)}\n        if normalization is not None:\n            item['normalization'] = normalization\n        return item")
        new=new.replace("'evidence': [{'target': target, 'sha256': evidence.sha256(target)} for target in targets]", "'evidence': [evidence.snapshot(target) for target in targets]")
        new=new.replace("current = evidence.sha256(item['target'])", "current = evidence.sha256(item['target'], item.get('normalization'))")
        assert new!=old
    changes[path]=(old,new)
    path='research/claims/schema.json';old=(root/path).read_text();schema=json.loads(old)
    schema['$defs']['snapshot']['properties']['normalization']={'enum':['notebook-article-v1']}
    changes[path]=(old,json.dumps(schema,indent=2)+'\n')
    path='tools/finish-turn.py';old=(root/path).read_text();new=old
    if 'finish-turn-producer-v1' not in new:
        new=new.replace("return body[:close] + ' ' + producer + body[close:]", "return (body[:close] + ' <span data-generated=\"finish-turn-producer-v1\">'\n            + producer + '</span>' + body[close:])")
        new=new.replace("updated = credit_producer(current, marker, producer).replace(marker, fragment.read_text().strip())", "timing = fragment.read_text().strip()\n    timing = timing.replace('<div class=\"timing-report\"',\n                            '<div data-generated=\"finish-turn-timing-v1\" class=\"timing-report\"', 1)\n    updated = credit_producer(current, marker, producer).replace(marker, timing)")
        assert new!=old
    changes[path]=(old,new)
    path='tools/tests/test_finish_turn.py';old=(root/path).read_text();new=old
    if "'tools/claim_evidence.py'" not in new:
        new=new.replace("'tools/claim_reviews.py',", "'tools/claim_reviews.py', 'tools/claim_evidence.py', 'tools/notebook-excerpt.py',")
        new=new.replace("expected = content.replace('<!-- TIMING test_turn -->', table).replace(", "table = table.replace('<div class=\"timing-report\"', '<div data-generated=\"finish-turn-timing-v1\" class=\"timing-report\"', 1)\n        expected = content.replace('<!-- TIMING test_turn -->', table).replace(")
        new=new.replace("'Status: test. Produced by Test agent (Test model, high).</p>'", "'Status: test. <span data-generated=\"finish-turn-producer-v1\">Produced by Test agent (Test model, high).</span></p>'")
    changes[path]=(old,new)
    return changes

if __name__=='__main__':
    changes=proposed_sources();out=Path(__file__).parent/'integration.patch'
    out.write_text(''.join(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+p,tofile='b/'+p)) for p,(a,b) in changes.items()))
    print(out)
