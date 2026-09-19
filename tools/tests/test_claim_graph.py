import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from claim_graph import query, audit, components


def edge(a,b,kind='depends_on',state='reviewed',identifier=None):
    return {'id':identifier or a+'-'+kind+'-'+b,
            'source':{'namespace':'current','id':a,'locator':None},
            'target':{'namespace':'current','id':b,'locator':None},
            'type':kind,'review_status':state,'scope':'full'}


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.data={'claims':[{'id':x} for x in 'abcde'],
                   'relationships':[edge('a','b'),edge('b','c'),edge('d','b','cites'),
                                    edge('e','b',state='unreviewed')]}

    def test_direction_type_and_review_filter(self):
        self.assertEqual([r['id'] for r in query(self.data,'a','descendants')['nodes']],['b','c'])
        self.assertEqual([r['id'] for r in query(self.data,'c','ancestors')['nodes']],['b','a'])
        self.assertEqual([r['id'] for r in query(self.data,'b','cites')['nodes']],['d'])
        self.assertEqual([r['id'] for r in query(self.data,'b','predecessors')['nodes']],['a'])
        self.assertEqual([r['id'] for r in query(self.data,'a','successors')['nodes']],['b'])
        self.assertEqual({r['id'] for r in query(self.data,'b','impact',include_unreviewed=True)['nodes']},{'a','e'})

    def test_shortest_witness_and_cycle_termination(self):
        self.data['relationships'] += [edge('a','c'),edge('c','a')]
        rows=query(self.data,'a','descendants')['nodes']
        self.assertEqual(len(rows),2)
        self.assertEqual(next(r for r in rows if r['id']=='c')['path'],['a-depends_on-c'])
        self.assertEqual(audit(self.data)['reviewed_dependency_cycles'],[[('current',x) for x in 'abc']])

    def test_citation_cycle_is_separate_from_proof_cycle(self):
        self.data['relationships'] += [edge('b','d','cites')]
        report=audit(self.data)
        self.assertEqual(report['reviewed_dependency_cycles'],[])
        self.assertEqual(report['citation_cycles'],[[('current','b'),('current','d')]])

    def test_duplicates_conflicts_and_scope(self):
        duplicate=copy.deepcopy(self.data['relationships'][0]);duplicate['id']='duplicate'
        duplicate['review_status']='unreviewed';self.data['relationships'].append(duplicate)
        other=copy.deepcopy(duplicate);other['id']='other-proof';other['scope']='different proof'
        self.data['relationships'].append(other)
        report=audit(self.data)
        self.assertEqual(report['duplicate_semantic_edges'],[['a-depends_on-b','duplicate']])
        self.assertEqual(len(report['conflicting_review_states']),1)

    def test_external_identity_and_missing_claim(self):
        e=edge('a','a');e['target']['namespace']='historical';e['target']['locator']='old.md#a'
        self.data['relationships'].append(e)
        rows=query(self.data,'a','successors')['nodes']
        self.assertIn(('historical','a'),[(r['namespace'],r['id']) for r in rows])
        self.assertEqual(audit(self.data)['self_links'],[])
        with self.assertRaises(ValueError):query(self.data,'missing','impact')

    def test_long_chain_no_recursion_and_self_link(self):
        edges=[edge(str(i),str(i+1)) for i in range(2000)]
        self.assertEqual(components(edges),[])
        edges.append(edge('2000','0'))
        self.assertEqual(len(components(edges)[0]),2001)
        self.data['relationships'].append(edge('a','a'))
        self.assertEqual(audit(self.data)['self_links'],['a-depends_on-a'])

if __name__=='__main__':unittest.main()
