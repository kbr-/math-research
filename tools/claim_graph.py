"""Typed claim graph queries. Reachability describes audit scope, not validity."""
from collections import defaultdict, deque


def node(endpoint):
    return (endpoint['namespace'], endpoint['id'])


def selected(data, types=('depends_on',), include_unreviewed=False):
    return [e for e in data['relationships'] if (not types or e['type'] in types)
            and (include_unreviewed or e['review_status']=='reviewed')]


def traverse(edges, start, reverse=False, transitive=True):
    adjacent=defaultdict(list)
    for edge in edges:
        a,b=node(edge['source']),node(edge['target'])
        if reverse:a,b=b,a
        adjacent[a].append((b,edge['id']))
    seen={start};queue=deque([(start,[]) ]);rows=[]
    while queue:
        a,path=queue.popleft()
        for b,identifier in sorted(adjacent[a]):
            if b in seen:continue
            seen.add(b);witness=path+[identifier]
            rows.append({'namespace':b[0],'id':b[1],'distance':len(witness),'path':witness})
            if transitive:queue.append((b,witness))
    return rows


def query(data, claim, mode, types=('depends_on',), include_unreviewed=False, namespace='current'):
    start=(namespace,claim)
    nodes={('current',c['id']) for c in data['claims']}
    nodes.update(node(e[k]) for e in data['relationships'] for k in ('source','target'))
    if start not in nodes:raise ValueError('Unknown graph endpoint: '+namespace+':'+claim)
    if mode=='cites':types=('cites',)
    if mode=='impact':types=('depends_on',)
    reverse=mode in ('predecessors','ancestors','cites','impact')
    rows=traverse(selected(data,types,include_unreviewed),start,reverse,
                  mode in ('ancestors','descendants','impact'))
    return {'claim':claim,'namespace':namespace,'mode':mode,'types':list(types),
            'include_unreviewed':include_unreviewed,'nodes':rows,
            'scope':'Reachability in the recorded graph only; missing edges do not imply independence. '
                    'Impact is a review scope, not a verdict that a dependent claim is invalid.'}


def components(edges):
    """Iterative Kosaraju: no recursion limit for long proof chains."""
    forward=defaultdict(set);backward=defaultdict(set);nodes=set()
    for e in edges:
        a,b=node(e['source']),node(e['target']);nodes.update((a,b))
        forward[a].add(b);backward[b].add(a)
    seen=set();order=[]
    for start in sorted(nodes):
        if start in seen:continue
        stack=[(start,False)]
        while stack:
            a,finished=stack.pop()
            if finished:order.append(a);continue
            if a in seen:continue
            seen.add(a);stack.append((a,True))
            stack.extend((b,False) for b in sorted(forward[a],reverse=True) if b not in seen)
    seen=set();result=[]
    for start in reversed(order):
        if start in seen:continue
        group=[];stack=[start];seen.add(start)
        while stack:
            a=stack.pop();group.append(a)
            for b in sorted(backward[a]):
                if b not in seen:seen.add(b);stack.append(b)
        if len(group)>1 or start in forward[start]:result.append(sorted(group))
    return sorted(result)


def audit(data):
    groups=defaultdict(list);self_links=[];locators=defaultdict(set);pairs=defaultdict(list)
    for e in data['relationships']:
        a,b=node(e['source']),node(e['target'])
        groups[(a,b,e['type'],e['scope'])].append(e['id'])
        pairs[(a,b)].append(e)
        if a==b:self_links.append(e['id'])
        for k in ('source','target'):
            endpoint=e[k]
            if endpoint['namespace']!='current':locators[node(endpoint)].add(endpoint['locator'])
    conflicts=[]
    for pair,edges in pairs.items():
        by_type=defaultdict(set)
        for e in edges:by_type[(e['type'],e['scope'])].add(e['review_status'])
        for key,statuses in by_type.items():
            if len(statuses)>1:conflicts.append({'endpoints':pair,'type':key[0],'scope':key[1],
                                                'review_states':sorted(statuses)})
    dependencies=selected(data)
    cycles=components(dependencies)
    return {'relationships':len(data['relationships']),
            'duplicate_semantic_edges':[v for v in groups.values() if len(v)>1],
            'self_links':self_links,'conflicting_review_states':conflicts,
            'inconsistent_endpoint_locators':[{'endpoint':k,'locators':sorted(v)}
                                               for k,v in locators.items() if len(v)>1],
            'reviewed_dependency_cycles':cycles,
            'all_candidate_dependency_cycles':components(selected(data,include_unreviewed=True)),
            'citation_cycles':components(selected(data,('cites',))),
            'scope':'Dependency cycles require proof/scope review; alternative proofs may explain them. '
                    'Citation cycles are reported separately and are not circular proof certificates. '
                    'Structural checks cannot decide semantic contradictions between claims.'}
