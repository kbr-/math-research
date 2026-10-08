# Generic normality exception inventory

An empty set is recorded only when a cited working proof covers every degree. Unresolved entries are **not** empty sets. This inventory does not supply a stopping algorithm.

Scope: dimensions 1–10; odd primes through 97.

| Dimension | Complete empty sets | Unresolved pairs |
|---:|---:|---:|
| 1 | 24 | 0 |
| 2 | 24 | 0 |
| 3 | 24 | 0 |
| 4 | 24 | 0 |
| 5 | 24 | 0 |
| 6 | 24 | 0 |
| 7 | 24 | 0 |
| 8 | 24 | 0 |
| 9 | 0 | 24 |
| 10 | 0 | 24 |

Total: **192 complete**, **48 unresolved**.

Evidence:

- `thm:cube-eight-all-odd-normality`: [Complete dimension-eight normality](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-10-06-cube-eight-all-degrees) (working_proof).
- `cor:cube-nine-ternary-filter`: [Exception coefficient filter](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-10-07-cube-exception-coefficient-filter) (working_proof).
- `cor:cube-nine-torsion-families`: [Frobenius cup certificate](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-10-07-cube-frobenius-cup-certificate) (working_proof).
- `cor:nine-first-bulk-progression`: [First bulk progression](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-10-08-cube-first-bulk-progression) (working_proof).
- `cor:short-period-normality`: [Nonordinary Cartier return](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-10-08-cube-nonordinary-return) (working_proof).
- `cor:nine-periodic-cup-cover`: [Periodic cup cover](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-10-08-cube-periodic-cup-cover) (working_proof).
- `cor:nine-unit-digit-normality`: [Unit digit lifting](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-10-08-cube-unit-digit-lifting) (working_proof).

For n=9, p=3, certified normal degrees: {"intervals": [[2, 6]], "residue_classes": {"minimum_degree": 7, "modulus": 729, "residues": [50, 68, 124, 181, 218, 349, 367, 368, 386, 517, 554, 611, 667, 685]}}. The complete exception set remains unresolved.

For n=9, p=3, certified normal degrees: {"first_degree": 1120878158380954709673208311740178314035203, "frobenius_families": {"e_min": 1, "e_not_divisible_by": 3, "exponent_offset": 5, "exponent_period": 10862102160, "formula": "d = offset + multiplier * prime^(exponent_offset + exponent_period*j) * e", "j_min": 0, "multiplier": 4612667318440142838161351077120075366400, "offset": 3, "prime": 3}}. The complete exception set remains unresolved.

For n=9, p=3, certified normal degrees: {"intervals": [[2, 7]], "residue_classes": {"minimum_degree": 7, "modulus": 373626052793651569891069437246726104678400, "residues": [7]}}. The complete exception set remains unresolved.

For n=9, p=3, certified normal degrees: {"constants_path": "research/results/bmd-exception-stable-projection-20261008/constants.json", "families": [{"centres": [0, 1, 2, 3, 4, 5, 6], "e_min": 1, "e_not_divisible_by": 3, "exponent_offset": [0, 3, 4, 5, 4, 3, 0], "exponent_period": 74880, "formula": "d = centre + multiplier * 3^(exponent_offset[centre] + exponent_period*j) * e", "j_min": 1, "multiplier": 78462395094571490005399192653094427321702994152290946798262775780231714502561058837601971965956818137473908527641231440922111257456692676471319959725345589018386839326404898230494599576863764829928027575656407934389778834759781502440718328877452909055515546098920376717227725898951560550995474925147018161246949386581502524975865630347221745486417698304764616287781437225880970745578448448001441024161137112897132602796306833039943770016452909695605510107955684387215125642718510481828390083785677933404987813257292288295560726391359972201428776564879751030721767217083248173265348989102317843381294956182525582560057969309092495206782217159875825225694785515049026136818050221098399373059548612986123513180374288528231958610121749860055043434913117728855914531636326595067069057202820787916778935857608283969956489407952569359043274098982750255116275785640194607353230667885708425107503739950727159443266734644312904722871933309221774431264463453140494845894003323849329401483141567845473782632761183865533914480015494135901613047694048332837635521576791917262300239746250182195292283504988395402013704119900593682571225328373400533397012862124290194419066226808000167420309356784896359780672256081920000}, {"centres": [1, 2, 3, 4, 5], "e_min": 1, "e_not_divisible_by": 3, "exponent_period": 28080, "formula": "d = centre + multiplier * 3^(exponent_period*j) * e", "j_min": 1, "multiplier": 4612667318440142838161351077120075366400}]}. The complete exception set remains unresolved.

For n=9, p=3, certified normal degrees: {"cover_path": "research/results/bmd-exception-period-cover-20261008/cover-summary.json", "scope_note": "Excluded exponents are uncertified by these tests, not proved exceptions.", "valuation_family": {"centres": [0, 1, 2, 3, 4, 5, 6], "e_min": 1, "e_not_divisible_by": 3, "excluded_exponent_residues_by_centre": [[], [1, 2], [1, 2, 3], [1, 2, 3, 4, 3649, 4224, 7489, 7872, 7873, 10944, 14593, 14977, 15744, 17089, 19008, 20160, 21121, 22465, 25152, 30336, 30337, 33409, 34368], [1, 2, 3], [1, 2], []], "exponent_modulus": 37440, "formula": "d = centre + multiplier * e * 3^s", "minimum_exponent": 20, "multiplier": 12393517966288443071509558811418833936985035871856835769733140562045079495751148233683182456840157396216060312192821812379384850251887224538828138266061916295891843944221048552195292125327768019468207514565416109538361585901684611764898863429483622323156144255642797937163369225358608175790542469358181460576528056982706681807752283610022878100032412706352203479688713519897249950758442118454908512794126440847801693927380501867083854279865107327261475789624396848833385543435148268780414090792386452332599041229554572750773834183177918271800101626566063593848279961997016763968602887935730955366197708904531217942627301655087480062010374677275475308798117085570950572410880294053420477868498114839743742231213899558439390049730871954169761598991359016547955330567128576055647699680977521608437903049579406008655548979784950914941649197982106141668609962418875305460542845698514924345719465020957094530420585548934083615013955312610328346012123279211802127102321250056211992143753243922618966342482528967854794001019366334330560573050108538045423779781493013345760811106189458739884982620079570882152440186573291527357514940482505091324459558804260216371769692310311769060854371752907419966903833186732175523840000}}. The complete exception set remains unresolved.

For n=9, p=3, certified normal degrees: {"scope_note": "Sufficient original normality certificate; other multipliers remain unresolved.", "unit_valuation_family": {"M": 373626052793651569891069437246726104678400, "condition": "For N=256*(M/81)*h and epsilon in {-1,1} congruent to N mod3, v3(N-epsilon)=1+28080*j, j>=0", "formula": "d = 3 + M*h", "h_min": 1, "h_not_divisible_by": 3, "included_h_residues_mod9": [1, 4, 5, 8]}}. The complete exception set remains unresolved.

The pairwise machine-readable inventory is in `inventory.json`. Bounds may be reduced according to measured cost, as requested by the user.
