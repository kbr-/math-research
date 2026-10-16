"""No statement tested: BM25 over exact stems on the two motivating cases."""
import importlib.util, sys, time, math, collections, re
sys.path.insert(0, 'tools')
spec = importlib.util.spec_from_file_location('sc', 'tools/search-claims.py'); sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
data = sc.read_json(sc.REGISTRY); claims = data['claims']
t = time.monotonic()
docs = [sc.stems(c['id'] + ' ' + c['summary']) for c in claims]
lens = [len(d) for d in docs]; avg = sum(lens) / len(lens)
index = collections.defaultdict(list)
for i, d in enumerate(docs):
    for w, k in collections.Counter(d).items(): index[w].append((i, k))
print(f'index {time.monotonic()-t:.2f} s')
def bm25(text, k1=1.2, b=0.75):
    text = re.sub(r'\\\(.*?\\\)', ' ', text)
    q = set(sc.stems(text)); n = len(docs); score = collections.Counter()
    for w in q:
        post = index.get(w, ())
        idf = math.log(1 + (n - len(post) + 0.5) / (len(post) + 0.5))
        for i, k in post:
            score[i] += idf * k * (k1 + 1) / (k + k1 * (1 - b + b * lens[i] / avg))
    return [claims[i]['id'] for i, _ in score.most_common()]
cases = {
 'union bound (paraphrase of the item)': ("Bound the error of Pang's second-layer inputs by a union bound over label conjunctions: "
     "each conjunction of labels is a defect, and the weight must kill every defect of the inputs of the second layer.",
     ['cor:growing-expansion-flat-removal', 'thm:growing-rank-gap-exclusion']),
 'spread next attempt': ("first check whether full coset families are expressible as bottoms of the rank-gap exclusion's sources, on which "
     "the split rests; then extend the exact evaluation of low-rank bottoms from rho <= q to rho <= log2 M",
     ['lem:weighted-chain-cells', 'thm:growing-rank-gap-exclusion', 'thm:core-star-source-exclusion']),
}
for name, (text, wants) in cases.items():
    order = bm25(text)
    print(name, {w: order.index(w) + 1 if w in order else None for w in wants}, order[:6])
t = time.monotonic(); bm25(cases['spread next attempt'][0]); print(f'query {time.monotonic()-t:.3f} s')
