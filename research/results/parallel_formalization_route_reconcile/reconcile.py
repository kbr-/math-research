import json,re,hashlib,sys,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'tools'))
from claim_registry import local_target
from claim_reviews import verified_declarations
reg=json.loads((root/'research/claims/index.json').read_text());old=json.loads((root/'research/results/index_formalization_metadata_20260919/inventory.json').read_text());oldfiles={f['path']:f for f in old['files']}
routepath='formalization/BIT_PHP_FORMALIZATION_ROUTE.md';rt=(root/routepath).read_text();route={}
for line in rt.splitlines():
 m=re.match(r'\| ([RH]\d+) \|',line)
 if m:route[m[1]]=line
mapping={}
def group(ids,names,note):
 for name in names.split():mapping[name]=([s for s in ids.split()],note)
group('H01','AugmentedChains','Finite augmented chain interface; boundary squared-zero and original-coordinate bridge are separate claims.')
group('H02','AugmentedBoundarySquared','Full binary insertion cancellation including augmentation.')
group('H03','AugmentedChainMaps AugmentedSubcomplexRelabeling','All-degree naturality/coordinate or subcomplex equivalence; helper scope does not claim later homology.')
group('H04','AugmentedCone','Actual cone vertex required; empty-face-only complex not silently a nonempty cone.')
group('H05','SimplexBoundary','Acyclic below top degree only, including small simplex boundary cases.')
group('H06','FiniteComplexCover CoverDoubleComplex','Finite cover interface and supported double complex; positive-vertex horizontal exactness distinguished from final cover theorem.')
group('H07','HomologicalCover','Binary augmented homological cover theorem, direct finite chain chase, exact intersection degree range.')
group('H08','ChessboardStarCover','Combinatorial star cover/cone closure only; cone acyclicity consumed separately.')
group('H09','ChessboardStarIntersections','Multiple-star intersections and actual filling transport, including zero remaining columns.')
group('H10','ChessboardStarNerve','Nerve is simplex boundary with below-top acyclicity; singleton stars use cone result.')
group('H11','ChessboardParameterArithmetic','Arithmetic only; no homology assertion.')
group('H12','ChessboardHomology','Full binary homological bound, no homotopy connectivity claim.')
group('H13','ChessboardFilling ChessboardFillingProof','Definition-only H interface and separate complete proof jointly cover full original filling statement including s=2 augmentation.')
group('R01','PolynomialCalculus','Ordinary PC/NS foundations and bases only; no equality PC=NS inferred.')
group('R02','PolynomialCalculusReuse','Completed-line multiplication and NS-to-PC inclusion, including zero cases.')
group('R03','PolynomialCalculusSubstitution','Degree-controlled and weighted replay; nonzero predecessor bound and degree-zero substitutions included.')
group('R04','PolynomialCalculusDuality LinearSeparation','Bounded-functional duality uses generic annihilator extension over any field; broader infinite-dimensional ambient separation is not an extra hypothesis.')
group('R05','BooleanReduction','Only binary Boolean reduction required; not historical full mixed-domain/all-prime theorem.')
group('R05 R09 R11','SquarefreePairDivisibility','Extracted forbidden-pair reduction helper, separately indexed and sufficient for row/column normal forms.')
group('R06','MpTelescoping','Original loose-degree equality remains refuted; only identity and upper bounds used. Actual fresh companion equality supplied separately by R07.')
group('R07','AffineForm AffineSystemLinearAlgebra AffineCoordinates FreshENSBlock FreshENSScalarCleanup FiniteAffineSpan','Separate affine-coordinate/scalar/exact-fresh-degree helpers; broader field/empty cases preserved without attributing full original learning theorem.')
group('R07 R18','FiniteAffinePolynomial','Finite-coordinate affine-map/polynomial bridge shared by normal forms and clause registry.')
group('R08','LowRankENS','Legitimate no-retained-core construction and certificates; no retained-core optimality claim.')
group('R09','MatchingNormalForm MatchingMomentCompleteness','Ordinary matching normal form and complete marginal characterization; arbitrary constant moment, not only normalized designs.')
group('R10','MatchingMomentCycles MatchingMomentRelabeling MatchingMomentExtension MatchingFiltration','Actual row-set cycles/fillings and arbitrary-row prescribed extension; removed m>=B assumption preserved; PC=NS only in stated stable range.')
group('R11','TwoRowInterpolation','Binary two-row interpolation with max(d,2) witnesses; not full column normalizer theorem.')
group('R12','CompactBitDecoder CompactBitDecoderTransfer','Coordinate injectivity/degree holds all ell; actual arbitrary-PC decoder requires ell>=2. No broader transported J_k package inferred.')
group('R13','RowLinearPolynomialSpace OrdinaryRestrictionDimension','Ordinary polynomial dimension/top coefficient/restriction dimensions; no quotient injection or separation inferred.')
group('R14','DisjointCoordinatePairs BinaryCubeDegreeDrop RowCubeCoefficientIsolation RowCubeRestriction CubeResidualDualSeparation','Separate pair packing, cube operator, exact coefficient isolation, actual restriction and final separator; final separator retains full board/degree hypotheses.')
group('R15','FiniteAffineCoordinates CoordinateRestrictionIdeal AffineRestrictionIdeal RestrictionKernelBounds AffineBlockRestriction CommonAffineRestrictionKernel','Literal ordinary restriction/ideal identities and final common-kernel assembly; no pointwise finite-field-zero substitution.')
group('R16','AffineFamilyRemoval AffineFamilyRemovalWithUnits','Weighted removal at k(D+1), with explicit unit-span alternative in later helper and literal-only compatibility wrapper retained.')
group('R17','AffineFamilyExclusion','Assembled exclusion uses actual kernel, removal, separator and explicit finite parameter conditions.')
group('R17 R25','AffineParameterBounds','Uniform eventual polynomial inventory/degree parameter room; not standalone proof-size theorem.')
group('R18','AffineClauseRegistry','Complete fixed registry with all companions/domains and empty value one; h>=1 needed only where stated.')
group('R19','BinaryAffineZeroCover','Opposite-fiber separator is ambient premise literal, no finite-dimension assumption.')
group('R20','AffineClauseCompression','Finite-width compression; shared module import does not make separator theorem a proof prerequisite.')
group('R21','BinarySemanticAffineCover','Semantic one/three-step reduction and restriction/compression only; concrete PC and shared DAG assembly are separate later claims.')
group('R22','AffineClauseResolution','Concrete resolution max(K,4h+1), overlapping contexts and empty conclusion included.')
group('R23','AffineClauseWeakening','Concrete weakening max(K,4h) and tautology2h+1; zero-flat affine witnesses rather than semantic separator alone.')
group('R24','AffineLiteralProduct BitPHPInitialBridge AffineDAGRegistry BitPHPClauseTransfer','Initial and DAG helpers split from full transfer; exact3S+initial slots and width v+2 auxiliary allowance retained.')
group('R25','BitPHPSuperpolynomial','Both usual-CNF rule conventions, arbitrary positive real exponent eventually, no proof-height bound.')
post={
'GenericAffineSubspaceConsequence':'research/results/lean_generic_subspace_20260917/dependency-scope-map.md',
'BitPHPExponential':'research/results/lean_bitphp_exponential_20260917/dependency-scope-map.md',
'GenericCNFSubspaceCriterion':'research/results/lean_generic_cnf_bridge_20260917/dependency-scope-map.md',
'GenericCNFDensityBound':'research/results/lean_generic_density_form_20260917/dependency-scope-map.md',
'ShortProofControl':'research/results/lean_generic_density_form_20260917/dependency-scope-map.md'}
rows=[];errors=[];summary={};changes=[]
for c in reg['claims']:
 f=c['formalization']
 if f['status'] not in {'complete','partial'}:continue
 entry={'id':c['id'],'overall_status':f['status'],'scope':f['scope'],'artifacts':[],'route_rows':[],'maps':[],'disposition':'consistent_source_relative_mapping'}
 for a in f['artifacts']:
  lean=[r for r in a['references'] if r.endswith('.lean')][0];path,anchor=local_target(lean,root);rel=str(path.relative_to(root));name=path.stem
  raw=path.read_text();header=raw.split('/-',1)[1].split('-/',1)[0].strip();sha=hashlib.sha256(path.read_bytes()).hexdigest()
  if rel in oldfiles and sha!=oldfiles[rel]['sha256']:errors.append(c['id']+': source changed since initial audited inventory')
  if name in mapping:
   ids,note=mapping[name];entry['route_rows']+=ids;entry['maps'].append(routepath);entry.setdefault('scope_reconciliation',[]).append(note)
  elif name in post:
   entry['maps'].append(post[name]);entry.setdefault('scope_reconciliation',[]).append('Post-publication-route separate target; exact dependency/scope map read, including outside-assignment boundaries.')
  elif name=='ModInterpolation':
   entry.setdefault('scope_reconciliation',[]).append('Explicitly outside bit-PHP publication route; independent existing MOD interpolation proof, joint total-degree bound only, not surrounding certificate.')
  else:errors.append(c['id']+': unmapped Lean artifact '+name)
  reportpath,_=local_target(a['verification'],root);report=reportpath.read_text();verified=verified_declarations(report);missing=[n for n in a['declarations'] if n not in verified]
  if missing:errors.append(c['id']+': declarations absent from successful named-axiom evidence '+repr(missing))
  declared=re.search(r'^Declarations:\s*(.*)$',header,re.M);hd=declared.group(1).split() if declared else []
  entry['artifacts'].append({'source':rel,'source_sha256':sha,'source_unchanged_since_initial_inventory':rel in oldfiles and sha==oldfiles[rel]['sha256'],'artifact_status':a['status'],'artifact_scope':a['scope'],'header':header,'declarations':a['declarations'],'header_declarations_not_claimed_by_this_artifact':[n for n in hd if n not in a['declarations']],'verification':str(reportpath.relative_to(root)),'verification_sha256':hashlib.sha256(reportpath.read_bytes()).hexdigest(),'named_axiom_evidence_complete':not missing})
 entry['route_rows']=list(dict.fromkeys(entry['route_rows']));entry['maps']=list(dict.fromkeys(entry['maps']));entry['route_target_rows']={r:route[r] for r in entry['route_rows']};rows.append(entry)
 if 'assembly remains R15' in f['scope']:
  changes.append({'id':c['id'],'field':'formalization.scope','before':f['scope'],'after':f['scope'].replace('actual common-kernel assembly remains R15','common-kernel assembly is separately verified under lem:common-affine-restriction-kernel (R15)'), 'reason':'Remove historically prospective wording now that route R15 is complete, without expanding helper coverage.'})
report={'baseline_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'registry_sha256':hashlib.sha256((root/'research/claims/index.json').read_bytes()).hexdigest(),'route_rows_covered':sorted({i for row in rows for i in row['route_rows']}),'unmapped_import_only_aggregate':{'path':'formalization/claims/BitPHPPreprintRevision1.lean','reason':'Import-only verification aggregate with no new claim; not a missing mathematical mapping.','sha256':hashlib.sha256((root/'formalization/claims/BitPHPPreprintRevision1.lean').read_bytes()).hexdigest()},'scope':'Exhaustive reconciliation of 75 existing mapped claims against all discovered formalization route/dependency-scope maps, source headers, and existing successful named-axiom reports; no fresh kernel replay or global literature audit.','claims':rows,'counts':{'claims':len(rows),'artifacts':sum(len(r['artifacts']) for r in rows),'publication_route_claims':sum(bool(r['route_rows']) for r in rows),'post_route_map_claims':sum(not r['route_rows'] and bool(r['maps']) for r in rows),'independent_outside_route':sum(not r['maps'] for r in rows)},'maps':[{'path':p,'sha256':hashlib.sha256((root/p).read_bytes()).hexdigest()} for p in [routepath]+sorted(set(post.values()))],'proposed_corrections':changes,'errors':errors}
folder=root/'research/results/parallel_formalization_route_reconcile';(folder/'report.json').write_text(json.dumps(report,indent=2)+'\n');(folder/'proposed-corrections.json').write_text(json.dumps(changes,indent=2)+'\n');print(report['counts']);print('proposed scope wording corrections',len(changes));print('errors',errors)
