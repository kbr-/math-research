#!/usr/bin/env python3
import argparse,json,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,write_json
from claim_reviews import Evidence,claim_digest
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();d=load();cs=d['claims'];ids={c['id'] for c in cs};packets=json.loads((ROOT/'research/results/parallel_index_classify_360_520/packets.json').read_text())['packets'];REV='dc1d95b4cb6a463436256b830afd69029c1dc3ed';WEB='https://kbr.is-a.dev/math-research/#';e=Evidence();edges=[]
def add(pos,target,kind,scope,anchor=None):
 source=cs[pos]['id'];target=cs[target]['id'] if isinstance(target,int) else target;assert target in ids
 loc=WEB+anchor if anchor else packets[pos-360]['passages'][0]['target']
 edges.append({'id':source+'::'+kind+'::'+target,'source':{'namespace':'current','id':source,'locator':None},'target':{'namespace':'current','id':target,'locator':None},'type':kind,'scope':scope,'evidence':[loc],'review_status':'reviewed','review':{'revision':REV,'date':'2026-09-19','reviewer':'Codex parallel dependency worker 360-520','note':'Resolved the recorded local proof role; no new mathematical or computation verification.'}})
add(360,'thm:proper-comparison-grid-separator','depends_on','The m=6 minimum separator is justified by the analytic theorem; only m=2,3 were exhaustively enumerated.')
add(360,'ex:proper-OR-source-interface-certificates','depends_on','The factored polynomial registry reuses the previously verified local source template with checked variable maps.')
add(360,'prop:proper-comparison-collected-grid-support','applies','The finite family checks isolate the predicted distinct collected supports.')
add(360,'prop:proper-comparison-fixed-target-necessity','applies','Complete block-deletion models instantiate the fixed-target necessity construction.')
add(362,361,'depends_on','Ordinary weighted reflection identifies the actual degrees of the remaining genuine products.')
add(362,'lem:constructor-selector-only-dependencies','refines','Specializes the earlier structural argument to the direct binary NS constructor before optional packing.')
add(362,'prop:php-final-boundary-pruning','depends_on','The standard boundary/clause map supplies the removed products and their old-degree bounds.')
add(363,'thm:shallow-source-cofactor-formulas','depends_on','The local OR proof uses its source prefix comparison, not its global cofactor-width conclusion.','selector-valued-NS-gate-modules')
add(363,'lem:virtual-MOD-scalar-relation','depends_on','The binary MOD frame uses the literal common-prefix interpolation relation.','selector-valued-NS-source-composition')
add(363,'cor:recorded-schema-value-compiler','cites','The ten-leaf MOD frame is reused as syntax; the NS witness accounting is re-proved, rather than importing the PC compiler conclusion.','selector-valued-NS-source-composition')
add(363,361,'depends_on','The formal weighted degree ledger uses reflection for genuine selectors.','selector-valued-NS-source-composition')
add(363,362,'depends_on','The binary values and input presentations supply selector-valued external coefficients.','selector-valued-NS-source-composition')
add(364,363,'depends_on','Specializes the constructed modular source identity and carries its supplied witness ceilings.')
add(364,361,'depends_on','Reflection identifies surviving formal coefficient and target degrees after the commuting substitution.')
add(364,362,'depends_on','The binary profile bounds old degree and selector degree in the target relations.')
add(364,'lem:ns-target-image-transfer','depends_on','Original-degree NS axiom images justify the boundary/clause substitution.')
add(364,'thm:proper-OR-union-NS-degree-six','applies','The degree-six witness example demonstrates that weighted target degree is not witness cost.')
add(365,361,'applies','Finite field and accuracy cases test weighted degree reflection and its scope controls.')
add(365,363,'applies','Two nested gate fixtures instantiate complete ordinary NS witnesses, not minimum-degree proofs.')
add(366,362,'depends_on','The specific binary source stage bounds inputs and limits an OR witness to three companion families.')
add(366,363,'depends_on','The source local witnesses give the initial NS ceiling and companion-family count.')
add(366,'lem:old-consequence-transfer','depends_on','Successive arbitrary-old-target elimination supplies the 6L old PC ceiling.')
add(366,'thm:functional-PHP-stable-filtration','depends_on','Old filtration reduces the resulting old PC target to its own-degree NS space.')
add(367,'thm:assignment-tree-ens-refutation','refines','Branches by pigeon-hole assignments and uses current module witnesses; the new 4h+2 ceiling is not an improvement over 4h+1.')
add(367,363,'cites','Uses the source-module viewpoint, but the local edge, collision and telescoping witnesses are supplied explicitly.')
add(368,367,'depends_on','The complete module identity for one forbids a normalized joint annihilator.')
add(368,'thm:functional-PHP-stable-filtration','depends_on','Supplies a normalized old design at D=4h+2 in the stated old-board range.')
add(368,'thm:literal-family-matching-restriction','cites','Explicitly excludes polynomial literal-family restriction from what the factorial counterexample refutes.')
add(369,367,'applies','The saved complete identities instantiate the matching-tree module construction with satisfiable frontier controls.')
add(370,'thm:global-PHP-row-projection','depends_on','Reuses the affine pivot map and degree-two Booleanity certificates, adding functional exclusions explicitly.')
add(370,'thm:functional-PHP-stable-filtration','depends_on','Transports old PC=NS and stable restrictions through the projected functional base.')
add(371,370,'depends_on','The preceding compatible row projection establishes the functional quotient used for affine spans.')
add(371,'cor:binary-source-domain-and-copy-cleanup','depends_on','Equal-span sharing and rank-at-most-2h packing provide canonical source values with certified maps.')
add(371,363,'depends_on','The three-value NS bound supplies uniform OR witness cost 6h.')
add(372,371,'depends_on','Canonical shared flat relations define the exact module system and avoid conflicting pair prescriptions.')
add(372,370,'depends_on','Old projected filtration supplies the assumed extension property in the stated PHP range; the abstract reduction needs that property as a hypothesis.')
add(373,372,'depends_on','Constructed singleton restrictions satisfy FLAT-singletons, then the reduction supplies the full design.')
add(373,370,'depends_on','Old filtration extends the weighted singleton restrictions to their required degrees.')
add(373,'thm:optimal-linear-core-factor-packing','cites','Comparison shows rank O(h) already had constant-factor transfer; packing is not used to construct this design.')
add(374,372,'depends_on','Uses the specified zero-triple construction to exhibit failure of moment-preserving extension at 8h.')
add(374,367,'applies','The matching-tree example illustrates incompatible singleton networks; the local triple control is separate.')
add(374,363,'cites','The full compiler has no proved ceiling below this narrow band; it is excluded from the extension claim.')
add(375,372,'applies','Complete free-Boolean moment arrays instantiate the singleton/pair/triple construction.')
add(375,374,'applies','The finite checker includes the nonextension and inconsistent-parent-mean controls.')
add(376,371,'cites','The affine-flat source values give the local clause dictionary; the audit does not extract a full clause proof.')
add(377,376,'obstructs','Fails the proper-point and rank premises of the proposed unary extensibility import, not all affine-DAG extraction.')
add(377,370,'cites','Uses the nonpivot row-coordinate setup; the rank and no-proper-point arguments are given directly.')
add(378,'lem:ns-target-image-transfer','depends_on','The original-cofactor argument transfers all certified images at factor ell; PC replay is separately supplied.')
for name,url,scope in [('GOR-2024-v2','https://arxiv.org/html/2404.08370v2','Recorded audit of unary tree-like size and space, with functionality caveat.'),('Byramji-Impagliazzo-2025-v1','https://arxiv.org/html/2511.20023v1','Recorded audit of bit-PHP size-depth and affine-DAG conventions.'),('Alekseev-Gaevoy-TR26-007','https://eccc.weizmann.ac.il/report/2026/007/','Abstract screen only, not a proof audit.'),('Itsykson-Podolskii-Shekhovtsov-TR26-018','https://eccc.weizmann.ac.il/report/2026/018/','Abstract screen only, not a proof audit.')]:
 source=cs[376]['id'];edges.append({'id':source+'::cites::external:'+name,'source':{'namespace':'current','id':source,'locator':None},'target':{'namespace':'external','id':name,'locator':url},'type':'cites','scope':scope,'evidence':[WEB+'affine-clause-source-theorem-audit'],'review_status':'reviewed','review':{'revision':REV,'date':'2026-09-19','reviewer':'Codex parallel dependency worker 360-520','note':'Records earlier source provenance; no fresh retrieval or literature audit.'}})
notes={360:'The finite support/deletion assertions use saved certificates; the m=6 separator minimum imports the analytic bound and polynomial templates reuse earlier exact evidence.',361:'Self-contained induction and coefficient extraction prove reflection. Earlier Boolean-diagonal methods are contrasted, not invoked; scope controls impose hypotheses.',362:'Binary source syntax, boundary replacement and genuine-selector reflection are the explicit prerequisites; the earlier structural result is a scoped refinement.',363:'Local OR prefix identities and literal binary MOD interpolation feed a freshly proved NS frame/MP recurrence. The older PC frame conclusion is not used as an NS theorem.',364:'The preceding source identity, profile/reflection and target-image lemma give the interface. The degree-six relation is an explanatory application separating target degree from certificate cost.',365:'Complete direct polynomial checks instantiate reflection and two gates. No minimum-degree or full-PHP conclusion relies on these finite cases.',366:'Three source-local companion families are removed by the old-target theorem, then old functional filtration lowers the target to its own degree.',367:'The local edge/collision identities and tree telescoping are proved explicitly; the older assignment-tree bound is refined rather than used to establish the new ceiling.',368:'Old design existence and the explicit refutation identity give the contradiction; the count-sensitive literal theorem is a scope comparison only.',369:'Complete mapped local polynomials and final target identities certify the finite instances and frontier controls; the universal degree separation is not inferred from their sizes.',370:'The row projection and its Boolean certificates are reused, functional exclusion images are supplied locally, and base filtration is transported.',371:'Canonical sharing/packing and the three-value source bound follow compatible row projection; all later inputs are actually substituted.',372:'The assumed old extension property and canonical module definitions suffice; the pair/triple assembly and necessity are shown locally.',373:'Old filtration extends chi-weighted singleton restrictions; the singleton reduction then gives the design. Prior packing is only a comparison.',374:'Nonextension uses the exact constructed moments at degree below 8h, not nonexistence of every higher design. Matching-tree and full-compiler scope roles are separate.',375:'The full saved 94198 checks instantiate the explicit moment construction and its two controls on a satisfiable Boolean base.',376:'Recorded primary-source audits and abstract-only screens are distinguished. The local clause dictionary is direct, and its reverse proof extraction is explicitly absent.',377:'Pivot independence, pigeon/column counting and a displayed three-evaluation functional prove the controls directly; the obstructed import is the earlier audited premise.',378:'Base indicator images are proved locally, original-cofactor transfer supplies NS, and line-by-line PC replay is supplied explicitly.',379:'Self-contained distributive collision sum and all-zero separating point prove filtration failure; finite saved cases are checks, not prerequisites.'}
invs=[]
for pos in range(360,380):
 c=cs[pos];targets=[p['target'] for p in packets[pos-360]['passages']]
 invs.append({'id':c['id'],'position':pos,'baseline_claim_sha256':claim_digest(c),'state':'reviewed','note':notes[pos],'next_action':None,'evidence':[{'target':t,'sha256':e.sha256(t)} for t in targets]})
write_json(a.out,{'schema_version':1,'baseline_revision':REV,'claims':invs,'relationships':edges,'scope':'Direct source-relative relationship inventories; no canonical mutation. Root must merge edges and regenerate incident-field hashes.','counts':{'closed_inventories':20,'relationships':len(edges)}})
print(len(invs),'closed inventories;',len(edges),'reviewed scoped edges')
