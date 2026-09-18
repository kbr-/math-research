#!/usr/bin/env python3
"""Exact round-trip test of the pair-space encoding of the restricted slack tree.

Labels are 0..n-1 with n = 2^L; Q is a random affine subspace of dimension L2 (N = 2^L2 points).
A pair (rho, rho'') consists of rho = (R, mu) in Phi_e (R residual of size N+1+e, mu an injection of the other
rows into O = [n] \\ Q leaving e free labels E) and a filling rho'', an injection of e rows of R onto E; the
compact restriction is rho' = rho u rho''.  Every rho' in Phi_0 arises from the same number of pairs.

The slack tree T(F, rho) is the complete-term tree (matched-first preference under mu; at a node the current
term's round comes first, then every uncovered tail row): a round at a pin (i, x) with x in Q queries the
pigeon i over the unused holes of Q u E, and queries the hole x only when the pigeon answer lies in Q \\ {x};
a pin (i, x) with x in E (a free hole) is resolved by the pigeon query alone.  The restricted tree T' follows
the filling at every query of a filled row (the answer rho''(i) in E is not a query of T') and keeps only
the branches into Q at other pigeon queries and the branches of unfilled rows at hole queries.  Heights count
the real queries of T'.

For every pair whose restricted tree has a path with at least h real queries, the lexicographically first such
path is encoded: moved light rows go to code labels in E n C(p) (real answers, holes of Q, and filling answers,
labels of E, are recorded in delta); a round whose pigeon is filled is recorded by one mark, the pinned row
staying residual in the code and treated by the decoder as assigned to an unknown outside label; pigeon answers
in Q and hole answers are recorded.  The filling is recorded as sigma, each filled row's label given as a label
of E(rho*) or as the index of the moved row whose code label it is.  The decoder rebuilds the path from the
code and must return the pair.  On the event G that no free label is pinned by any term (E n X = empty) the
decoder is expected to succeed for role-separated readers; off G it may fail (pins at free holes are
indistinguishable from pins at occupied labels), and failures are reported separately.
"""
import argparse, itertools, json, math, random, sys

HOLE_ALWAYS = False   # query the hole after every pigeon answer other than the pin (both-endpoints rule)
PIN_TEST = False   # a pin at a free outside label is resolved by a pin test (no query in T'); code labels avoid X
X_PINS = set()
SKIP_KILLED = False   # after a pigeon answer other than the pin (and the hole query, if any) the node is left: no tail queries
CODE_RULE = 'avoid-X'   # 'avoid-X': code labels outside X; 'own': code labels whose own filling row is not pinned to them; 'current': code labels outside the pin labels of the path's current terms so far (cycle 210)
REVEAL_SLOTS = False    # cycle 210: the decoder learns a slot row's label when the corresponding move is decoded
WIDE_W = None           # cycle 211: tail rows with more than WIDE_W literals are wide: moved without a code label (answer in delta)
LAST_XCUR_HIT = False   # cycle 210 diagnostic: the last compact code used a label that was a current term's pin label at the time
PINS = set()   # all (row, label) pins
PINS_BY_ROW = {}   # row -> labels it is pinned to (X_j)

OUT = 'OUT'   # a filled pinned row assigned to an unknown outside label

def bit(label, t): return (label >> t) & 1

def consistent(lits, label):
    if label == OUT: return False
    return all(bit(label, t) == v for t, v in lits)


def status(term, assign, emptied):
    """('false',None,None) | ('true',None,None) | ('free', uncovered_tail_rows, pin_alive)."""
    free = []
    for row, lits in term['tail']:
        if row in assign:
            if not consistent(lits, assign[row]): return 'false', None, None
        else:
            free.append(row)
    pin = term['pin']; pin_alive = False
    if pin is not None:
        i, x = pin
        if i in assign:
            if assign[i] != x: return 'false', None, None
        else:
            if x in emptied or x in set(assign.values()): return 'false', None, None
            pin_alive = True
    if not free and not pin_alive: return 'true', None, None
    return 'free', free, pin_alive

def pick_term(F, assign, emptied, base, killed=frozenset()):
    """Matched-first preference; base gives the matching used for the preference."""
    first = None
    for idx, term in enumerate(F):
        if idx in killed: continue
        st, rows, pa = status(term, assign, emptied)
        if st == 'false': continue
        pin = term['pin']
        if pin is not None and base.get(pin[0]) == pin[1]:
            return idx, st, rows, pa
        if first is None: first = (idx, st, rows, pa)
    return first if first is not None else (None, None, None, None)


def first_long_path(F, mu, R, Q, E, fill, h):
    """Lexicographically first path of the restricted tree with at least h real queries.
    Path steps: ('L', row, lab, auto) light answer; ('P', i, lab, auto) pigeon answer; ('H', x, row_or_None)."""
    holes_all = sorted(Q) + sorted(E); Qs = set(Q)
    filled = set(fill)
    best = {'path': None, 'height': 0}
    def real(path): return sum(1 for st in path if st[0] == 'H' or (st[0] != 'T' and not st[3]))
    def leaf(path):
        best['height'] = max(best['height'], real(path))
        if real(path) >= h and best['path'] is None: best['path'] = list(path)
    def avail(assign, emptied, row):
        used = set(assign.values())
        if row in filled: return [fill[row]]
        return sorted(l for l in Q if l not in used and l not in emptied)
    def rec(assign, emptied, path, killed=frozenset()):
        if best['path'] is not None: return
        if real(path) >= h: leaf(path); return
        idx, st, rows, pa = pick_term(F, assign, emptied, mu, killed)
        if idx is None or st == 'true': leaf(path); return
        term = F[idx]
        def tail(assign, emptied, path, pos):
            if best['path'] is not None: return
            if real(path) >= h: leaf(path); return
            while pos < len(rows) and rows[pos] in assign: pos += 1
            if pos == len(rows): rec(assign, emptied, path, killed); return
            row = rows[pos]
            av = avail(assign, emptied, row)
            if not av: leaf(path); return
            for lab in av:
                a2 = dict(assign); a2[row] = lab
                tail(a2, emptied, path + [('L', row, lab, row in filled)], pos + 1)
                if best['path'] is not None: return
        if pa and PIN_TEST and term['pin'][1] not in Qs:
            i, x = term['pin']
            if i in filled and fill[i] == x:
                a2 = dict(assign); a2[i] = x; tail(a2, emptied, path + [('T', i, x, True)], 0)
            else:
                rec(assign, emptied, path + [('T', i, x, False)], killed | {idx})
            return
        if pa:
            i, x = term['pin']
            for lab in avail(assign, emptied, i):
                a2 = dict(assign); a2[i] = lab; p2 = path + [('P', i, lab, i in filled)]
                after = (lambda a, em, pth: rec(a, em, pth, killed)) if (SKIP_KILLED and lab != x) else (lambda a, em, pth: tail(a, em, pth, 0))
                if lab == x or x not in Qs or real(p2) >= h or (lab not in Qs and not HOLE_ALWAYS):
                    after(a2, emptied, p2) if real(p2) < h else leaf(p2)
                else:
                    for j in sorted(r for r in R if r not in a2 and r not in filled):
                        a3 = dict(a2); a3[j] = x
                        after(a3, emptied, p2 + [('H', x, j)])
                        if best['path'] is not None: return
                    after(a2, emptied | {x}, p2 + [('H', x, None)])
                if best['path'] is not None: return
            return
        tail(dict(assign), emptied, path, 0)
    rec(dict(mu), frozenset(), [])
    return best

class NotRich(Exception): pass

def encode(F, mu, R, E, fill, path, Q):
    """Code (rho*, sigma, beta, delta) of a restricted path.  rho* is the code assignment (moved light rows at code
    labels); sigma maps each filled row to ('E', label) if its label survives in E(rho*) or ('slot', k) if it is the
    code label of the k-th moved row; beta lists per node (tail flags, round kind); delta lists the recorded answers."""
    assign = dict(mu); emptied = set(); code = dict(mu); free_out = sorted(E); Qs = set(Q)
    moved = []; betas = []; deltas = []; pos = 0
    while pos < len(path):
        idx, st, rows, pa = pick_term(F, assign, emptied, mu)
        assert idx is not None and st == 'free'
        term = F[idx]; flags = []; kind = 'none'
        if pa and pos < len(path):
            step = path[pos]; i, x = term['pin']
            assert step[0] == 'P' and step[1] == i, 'the round queries the pigeon first'
            lab = step[2]
            if step[3]:
                kind = 'filled'; assign[i] = lab; pos += 1
                if HOLE_ALWAYS and x in Qs and pos < len(path) and path[pos][0] == 'H':
                    kind = 'filled_round'; st2 = path[pos]; assert st2[1] == x
                    if st2[2] is None: emptied.add(x); deltas.append(('empty', None))
                    else: assign[st2[2]] = x; deltas.append(('row', st2[2]))
                    pos += 1
            else:
                kind = 'pigeon'; assign[i] = lab; deltas.append(('lab', lab)); pos += 1
                if lab != x and pos < len(path) and path[pos][0] == 'H':
                    kind = 'round'; st2 = path[pos]; assert st2[1] == x
                    if st2[2] is None: emptied.add(x); deltas.append(('empty', None))
                    else: assign[st2[2]] = x; deltas.append(('row', st2[2]))
                    pos += 1
        for row, lits in term['tail']:
            if row in assign or pos >= len(path) or path[pos][0] != 'L':
                flags.append(0); continue
            step = path[pos]; assert step[1] == row, 'path row differs from the term row order'
            cons = [l for l in free_out if consistent(lits, l)]
            if not cons: raise NotRich()
            code[row] = cons[0]; free_out.remove(cons[0]); moved.append(row)
            assign[row] = step[2]; deltas.append(('ans', step[2])); flags.append(1); pos += 1
        betas.append((tuple(flags), kind))
    code_labels = [code[r] for r in moved]
    sigma = {}
    for f, lab in fill.items():
        sigma[f] = ('slot', code_labels.index(lab)) if lab in code_labels else ('E', lab)
    return (tuple(sorted(code.items())), tuple(sorted(sigma.items())), tuple(betas), tuple(deltas))

def decode(F, code):
    code_assign, sigma, betas, deltas = code
    cur = dict(code_assign); base = dict(code_assign); emptied = set(); d = 0
    touched = []; moved = []; outs = []
    for flags, kind in betas:
        idx, st, rows, pa = pick_term(F, cur, emptied, base)
        if idx is None or st == 'false': return None
        term = F[idx]
        if kind != 'none':
            if not pa: return None
            i, x = term['pin']
            if kind in ('filled', 'filled_round'):
                cur[i] = OUT; outs.append(i)
                if kind == 'filled_round':
                    k, val = deltas[d]; d += 1
                    if k == 'empty': emptied.add(x)
                    elif k == 'row': cur[val] = x; touched.append(val)
                    else: return None
            else:
                k, val = deltas[d]; d += 1
                if k != 'lab': return None
                cur[i] = val; touched.append(i)
                if kind == 'round':
                    k, val = deltas[d]; d += 1
                    if k == 'empty': emptied.add(x)
                    elif k == 'row': cur[val] = x; touched.append(val)
                    else: return None
        for (row, lits), flag in zip(term['tail'], flags):
            if flag:
                k, val = deltas[d]; d += 1
                if k != 'ans': return None
                cur[row] = val; touched.append(row); moved.append(row)
    for row in touched + outs: cur.pop(row, None)
    for row in moved: base.pop(row, None)
    code_labels = [code_assign_get(code_assign, r) for r in moved]
    fill = {}
    for f, (k, v) in sigma:
        fill[f] = code_labels[v] if k == 'slot' else v
    return tuple(sorted(base.items())), tuple(sorted(fill.items()))

def encode_entry(F, mu, R, E, fill, path, Q):
    """The encoding of the entry's Section 2: code (rho*, sigma, m, beta, delta).  Filled rows are never moved and
    are recorded by nothing at their pigeon query (the decoder marks them OUT); m is the number of moved rows; beta
    lists, in path order, one bit per round (whether the node moves a row) and, per moved row, its position among
    the term's tail rows and a last-of-node bit; delta lists the real light answers and the round answers.  The
    decoder processes nodes until the m-th move; a node without a round and without a move cannot occur on G
    under the hole-always rule when no filled row lies in a tail."""
    assign = dict(mu); emptied = set(); code = dict(mu); free_out = sorted(E); Qs = set(Q)
    filled = set(fill); m = sum(1 for st in path if st[0] == 'L' and not st[3]); fill_inv = {lab: row for row, lab in fill.items()}
    moved = []; betas = []; deltas = []; pos = 0; killed = set()
    while len(moved) < m:
        idx, st, rows, pa = pick_term(F, assign, emptied, mu, killed)
        assert idx is not None and st == 'free'
        term = F[idx]; pos0 = pos; had_round = False
        if pa and PIN_TEST and term['pin'][1] not in Qs:
            i, x = term['pin']; step = path[pos]; assert step[0] == 'T' and step[1] == i; pos += 1
            if step[3]: assign[i] = x
            else: killed.add(idx); continue
        elif pa:
            i, x = term['pin']; step = path[pos]
            assert step[0] == 'P' and step[1] == i, 'the round queries the pigeon first'
            lab = step[2]; assign[i] = lab; pos += 1
            if i not in filled: deltas.append(('lab', lab))
            if pos < len(path) and path[pos][0] == 'H':
                st2 = path[pos]; assert st2[1] == x
                if st2[2] is None: emptied.add(x); deltas.append(('empty', None))
                else: assign[st2[2]] = x; deltas.append(('row', st2[2]))
                pos += 1
            if SKIP_KILLED and lab != x:
                assert pos > pos0; continue
            had_round = True
        node_moves = []
        for k, (row, lits) in enumerate(term['tail']):
            if row in assign: continue
            if row in filled:
                assert pos < len(path) and path[pos][0] == 'L' and path[pos][1] == row
                assign[row] = fill[row]; pos += 1; continue   # not covered by the count: filled tail rows
            step = path[pos]; assert step[0] == 'L' and step[1] == row, 'path row differs from the term row order'
            cons = [l for l in free_out if consistent(lits, l) and not (PIN_TEST and CODE_RULE == 'avoid-X' and l in X_PINS) and not (CODE_RULE == 'own' and (fill_inv[l], l) in PINS)]
            if not cons: raise NotRich()
            code[row] = cons[0]; free_out.remove(cons[0]); moved.append(row); node_moves.append(k)
            assign[row] = step[2]; deltas.append(('ans', step[2])); pos += 1
            if len(moved) == m: break
        if had_round: betas.append(('R', bool(node_moves)))
        for t, k in enumerate(node_moves): betas.append(('M', k, t == len(node_moves) - 1))
        assert pos > pos0, 'a node of the path without a query'
    sigma = tuple(sorted(fill))
    code_labels = [code[r] for r in moved]
    return (tuple(sorted(code.items())), sigma, m, tuple(betas), tuple(deltas), tuple(('slot', code_labels.index(fill[f])) if fill[f] in code_labels else ('E', fill[f]) for f in sigma))

def decode_entry(F, code, Q):
    code_assign, sigma, m, betas, deltas, sig_labels = code
    cur = dict(code_assign); base = dict(code_assign); emptied = set(); d = 0; b = 0; Qs = set(Q)
    filled = set(sigma); touched = []; moved = []; killed = set()
    sig = dict(zip(sigma, sig_labels))
    while len(moved) < m:
        idx, st, rows, pa = pick_term(F, cur, emptied, base, killed)
        if idx is None or st == 'false': return None
        term = F[idx]; has_moves = True
        if pa and PIN_TEST and term['pin'][1] not in Qs:
            i, x = term['pin']
            if i in filled and sig[i] == ('E', x): cur[i] = x; touched.append(i)
            else: killed.add(idx); continue
        elif pa:
            i, x = term['pin']
            if i in filled:
                cur[i] = sig[i][1] if sig[i][0] == 'E' else OUT; touched.append(i); lab = None
            else:
                k, val = deltas[d]; d += 1
                if k != 'lab': return None
                cur[i] = val; touched.append(i); lab = val
            if x in Qs and lab != x and (HOLE_ALWAYS or (lab is not None and lab in Qs)):
                k, val = deltas[d]; d += 1
                if k == 'empty': emptied.add(x)
                elif k == 'row': cur[val] = x; touched.append(val)
                else: return None
            if SKIP_KILLED and lab != x: continue
            kind, has_moves = betas[b]; b += 1
            if kind != 'R': return None
        while has_moves:
            kind, k, last = betas[b]; b += 1
            if kind != 'M': return None
            row = term['tail'][k][0]
            kk, val = deltas[d]; d += 1
            if kk != 'ans': return None
            cur[row] = val; touched.append(row); moved.append(row)
            if last: break
    for row in moved: base.pop(row, None)
    code_labels = [code_assign_get(code_assign, r) for r in moved]
    fill = {}
    for f, (k, v) in zip(sigma, sig_labels):
        fill[f] = code_labels[v] if k == 'slot' else v
    return tuple(sorted(base.items())), tuple(sorted(fill.items()))

# ---------------------------------------------------------------------------------------------------------------
# Compact mode (cycle 208): the tree is the recorded compact complete-term tree T_c(F, rho') for rho' = rho u rho''
# (matched-first preference; at an alive pin (i in R', x in Q) the pigeon over the unused holes of Q, then on every
# answer other than x the hole x over the unassigned rows of R' and the empty branch; then every uncovered tail row).
# The pair space is only the counting device: the code is (rho*, sigma, beta, delta) with code labels in
# E(rho) n C(p) whose own filling row is not pinned to them; the decoder simulates T_c from rho*, sigma and the
# records, treating a pin at an outside label as satisfied exactly when the row's known label is that label.

def status_dec(term, assign, emptied, Qs):
    """Term status for the decoder: a pin at an outside label is dead unless its row is known to sit there."""
    free = []
    for row, lits in term['tail']:
        if row in assign:
            if not consistent(lits, assign[row]): return 'false', None, None
        else:
            free.append(row)
    pin = term['pin']; pin_alive = False
    if pin is not None:
        i, x = pin
        if i in assign:
            if assign[i] != x: return 'false', None, None
        elif x not in Qs: return 'false', None, None
        else:
            if x in emptied or x in set(assign.values()): return 'false', None, None
            pin_alive = True
    if not free and not pin_alive: return 'true', None, None
    return 'free', free, pin_alive

def pick_term_c(F, assign, emptied, base, Qs, dec):
    first = None
    for idx, term in enumerate(F):
        st, rows, pa = (status_dec(term, assign, emptied, Qs) if dec else status(term, assign, emptied))
        if st == 'false': continue
        pin = term['pin']
        if pin is not None and base.get(pin[0]) == pin[1]:
            return idx, st, rows, pa
        if first is None: first = (idx, st, rows, pa)
    return first if first is not None else (None, None, None, None)

def first_long_path_compact(F, mu1, Rp, Q, h):
    """Lexicographically first path of T_c(F, rho') with at least h queries; mu1 = mu u rho''; Rp = R' (compact
    residual rows).  Steps: ('L', row, hole), ('P', i, hole), ('H', x, row_or_None)."""
    Qs = set(Q); best = {'path': None, 'height': 0}
    def leaf(path):
        best['height'] = max(best['height'], len(path))
        if len(path) >= h and best['path'] is None: best['path'] = list(path)
    def avail(assign, emptied):
        used = set(assign.values()); return sorted(l for l in Q if l not in used and l not in emptied)
    def rec(assign, emptied, path):
        if best['path'] is not None: return
        if len(path) >= h: leaf(path); return
        idx, st, rows, pa = pick_term_c(F, assign, emptied, mu1, Qs, False)
        if idx is None or st == 'true': leaf(path); return
        term = F[idx]
        def tail(assign, emptied, path, pos):
            if best['path'] is not None: return
            if len(path) >= h: leaf(path); return
            while pos < len(rows) and rows[pos] in assign: pos += 1
            if pos == len(rows): rec(assign, emptied, path); return
            row = rows[pos]; av = avail(assign, emptied)
            if not av: leaf(path); return
            for lab in av:
                a2 = dict(assign); a2[row] = lab
                tail(a2, emptied, path + [('L', row, lab)], pos + 1)
                if best['path'] is not None: return
        if pa:
            i, x = term['pin']; av = avail(assign, emptied)
            if not av: leaf(path); return
            for lab in av:
                a2 = dict(assign); a2[i] = lab; p2 = path + [('P', i, lab)]
                if lab == x or len(p2) >= h: tail(a2, emptied, p2, 0)
                else:
                    for j in sorted(r for r in Rp if r not in a2):
                        a3 = dict(a2); a3[j] = x
                        tail(a3, emptied, p2 + [('H', x, j)], 0)
                        if best['path'] is not None: return
                    tail(a2, emptied | {x}, p2 + [('H', x, None)], 0)
                if best['path'] is not None: return
            return
        tail(dict(assign), emptied, path, 0)
    rec(dict(mu1), frozenset(), [])
    return best

def encode_compact(F, mu, R, E, fill, path, Q):
    """Code (rho*, sigma, m, beta, delta) of a path of T_c(F, rho'); code labels obey CODE_RULE."""
    Qs = set(Q); mu1 = dict(mu); mu1.update(fill)
    assign = dict(mu1); emptied = set(); code = dict(mu); free_out = sorted(E)
    fill_inv = {lab: row for row, lab in fill.items()}
    m = sum(1 for st in path if st[0] == 'L'); moved = []; betas = []; deltas = []; pos = 0
    xcur = set()   # cycle 210: pin labels of the path's current terms so far (including this node's)
    global LAST_XCUR_HIT; LAST_XCUR_HIT = False
    while len(moved) < m:
        idx, st, rows, pa = pick_term_c(F, assign, emptied, mu1, Qs, False)
        assert idx is not None and st == 'free'
        term = F[idx]; pos0 = pos
        if term['pin'] is not None: xcur.add(term['pin'][1])
        if pa:
            i, x = term['pin']; step = path[pos]
            assert step[0] == 'P' and step[1] == i, 'the round queries the pigeon first'
            lab = step[2]; assign[i] = lab; deltas.append(('lab', lab)); pos += 1
            if lab != x:
                st2 = path[pos]; assert st2[0] == 'H' and st2[1] == x
                if st2[2] is None: emptied.add(x); deltas.append(('empty', None))
                else: assign[st2[2]] = x; deltas.append(('row', st2[2]))
                pos += 1
            betas.append(('R', None))   # placeholder so that the decoder's reads stay aligned: replaced below
        node_moves = []
        for k, (row, lits) in enumerate(term['tail']):
            if row in assign: continue
            step = path[pos]; assert step[0] == 'L' and step[1] == row, 'path row differs from the term row order'
            if WIDE_W is not None and len(lits) > WIDE_W:
                moved.append(row); node_moves.append(('W', k))   # cycle 211: a wide row stays residual in rho*; its answer is in delta
            else:
                cons = [l for l in free_out if consistent(lits, l) and not (CODE_RULE == 'avoid-X' and l in X_PINS) and not (CODE_RULE in ('own', 'own-two-role') and (fill_inv[l], l) in PINS) and not (CODE_RULE in ('own-two-role', 'current-two-role') and l in PINS_BY_ROW.get(row, ())) and not (CODE_RULE in ('current', 'current-two-role') and l in xcur)]
                if not cons: raise NotRich()
                if cons[0] in xcur: LAST_XCUR_HIT = True
                code[row] = cons[0]; free_out.remove(cons[0]); moved.append(row); node_moves.append(('M', k))
            assign[row] = step[2]; deltas.append(('ans', step[2])); pos += 1
            if len(moved) == m: break
        if betas and betas[-1] == ('R', None): betas[-1] = ('R', bool(node_moves))
        for t, (kind, k) in enumerate(node_moves): betas.append((kind, k, t == len(node_moves) - 1))
        assert pos > pos0, 'a node of the path without a query'
    sigma = tuple(sorted(fill)); code_labels = [code[r] for r in moved if r in code]   # placed moves, in order
    return (tuple(sorted(code.items())), sigma, m, tuple(betas), tuple(deltas),
            tuple(('slot', code_labels.index(fill[f])) if fill[f] in code_labels else ('E', fill[f]) for f in sigma))

def decode_compact(F, code, Q):
    code_assign, sigma, m, betas, deltas, sig_labels = code
    Qs = set(Q); sig = dict(zip(sigma, sig_labels))
    cur = dict(code_assign); base = dict(code_assign)
    slot_row = {}
    for f, (k, v) in sig.items():
        cur[f] = v if k == 'E' else OUT     # a slot label is outside Q; under the own rule at no pin of f
        if k == 'E': base[f] = v
        else: slot_row[v] = f
    emptied = set(); d = 0; b = 0; touched = []; moved = []; placed = []
    while len(moved) < m:
        idx, st, rows, pa = pick_term_c(F, cur, emptied, base, Qs, True)
        if idx is None or st == 'false': return None
        term = F[idx]; has_moves = True; progress = (len(moved), d)
        if pa:
            i, x = term['pin']
            k, val = deltas[d]; d += 1
            if k != 'lab': return None
            cur[i] = val; touched.append(i)
            if val != x:
                k, val2 = deltas[d]; d += 1
                if k == 'empty': emptied.add(x)
                elif k == 'row': cur[val2] = x; touched.append(val2)
                else: return None
            kind, has_moves = betas[b]; b += 1
            if kind != 'R': return None
        while has_moves:
            kind, k, last = betas[b]; b += 1
            if kind not in ('M', 'W'): return None
            row = term['tail'][k][0]
            kk, val = deltas[d]; d += 1
            if kk != 'ans': return None
            cur[row] = val; touched.append(row); moved.append(row)
            if kind == 'M':
                placed.append(row)
                if REVEAL_SLOTS and (len(placed) - 1) in slot_row:   # cycle 210: the k-th code label is now known
                    f = slot_row[len(placed) - 1]; lab = code_assign_get(code_assign, row); cur[f] = lab; base[f] = lab
            if last: break
        if progress == (len(moved), d): return None
    for row in moved: base.pop(row, None)
    for f in sigma: base.pop(f, None)
    code_labels = [code_assign_get(code_assign, r) for r in placed]
    fill = {f: (code_labels[v] if k == 'slot' else v) for f, (k, v) in sig.items()}
    return tuple(sorted(base.items())), tuple(sorted(fill.items()))

# ---------------------------------------------------------------------------------------------------------------
# Wide-round tree (cycle 212): rows are light (at most WIDE_W literals in every term) or wide.  At the root the wide
# graph G has an edge (j, x) for every residual wide row j of a term with pattern p and every hole x of Q in C(p); a
# canonical minimum vertex cover C = (C_rows, C_holes) of G is fixed.  At the current term a wide uncovered row j is
# resolved by a pigeon query when j is in C_rows and otherwise by hole queries at the unresolved holes of C(p) n Q
# (all in C_holes); a term with a wide uncovered row whose cube has no unresolved hole of Q counts as falsified.
# Light rows are moved as in the complete-term tree.  Every wide query is answered from delta; no beta entry.

WIDE_ROWS = frozenset()   # cycle 212: rows that are wide in every term (light and wide rows are disjoint sets)

def is_wide(lits, row=None):
    return (WIDE_W is not None and len(lits) > WIDE_W) or (row is not None and row in WIDE_ROWS)

def wide_graph(F, Rp, Qs, assign):
    edges = set()
    for t in F:
        for row, lits in t['tail']:
            if is_wide(lits, row) and row in Rp and row not in assign:
                for x in Qs:
                    if consistent(lits, x): edges.add((row, x))
    return edges

def min_vertex_cover(edges):
    """Canonical minimum vertex cover: smallest size, then fewest rows, then lexicographic."""
    rows = sorted({j for j, x in edges}); holes = sorted({x for j, x in edges})
    for k in range(len(rows) + len(holes) + 1):
        for kr in range(min(k, len(rows)) + 1):
            kh = k - kr
            if kh > len(holes): continue
            for cr in itertools.combinations(rows, kr):
                for ch in itertools.combinations(holes, kh):
                    if all(j in cr or x in ch for j, x in edges): return frozenset(cr), frozenset(ch)
    return frozenset(), frozenset()

def unresolved_holes(lits, Qs, assign, emptied):
    used = set(assign.values())
    return sorted(x for x in Qs if consistent(lits, x) and x not in used and x not in emptied)

def status_w(term, assign, emptied, Qs, dec):
    """Status in the wide-round tree; dec selects the decoder's rule for pins at outside labels."""
    free = []
    for row, lits in term['tail']:
        if row in assign:
            if not consistent(lits, assign[row]): return 'false', None, None
        else:
            if is_wide(lits, row) and not unresolved_holes(lits, Qs, assign, emptied): return 'false', None, None
            free.append(row)
    pin = term['pin']; pin_alive = False
    if pin is not None:
        i, x = pin
        if i in assign:
            if assign[i] != x: return 'false', None, None
        elif x not in Qs: return 'false', None, None
        else:
            if x in emptied or x in set(assign.values()): return 'false', None, None
            pin_alive = True
    if not free and not pin_alive: return 'true', None, None
    return 'free', free, pin_alive

def pick_term_w(F, assign, emptied, base, Qs, dec):
    first = None
    for idx, term in enumerate(F):
        st, rows, pa = status_w(term, assign, emptied, Qs, dec)
        if st == 'false': continue
        pin = term['pin']
        if pin is not None and base.get(pin[0]) == pin[1]:
            return idx, st, rows, pa
        if first is None: first = (idx, st, rows, pa)
    return first if first is not None else (None, None, None, None)

def first_long_path_wide(F, mu1, Rp, Q, h, stats=None):
    """Lexicographically first path of the wide-round tree with at least h queries (or the height when none).
    Steps: ('L', row, hole) light move; ('P', i, hole) pigeon of a round; ('H', x, row_or_None) hole query of a round;
    ('WP', j, hole) wide pigeon query; ('WH', x, row_or_None) wide hole query.  stats, if given, collects the maximum
    number of wide queries on a path and the cover size."""
    Qs = set(Q); best = {'path': None, 'height': 0, 'max_wide': 0}
    cover = min_vertex_cover(wide_graph(F, Rp, Qs, mu1))
    best['cover'] = len(cover[0]) + len(cover[1])
    def leaf(path):
        best['height'] = max(best['height'], len(path))
        best['max_wide'] = max(best['max_wide'], sum(1 for st in path if st[0] in ('WP', 'WH')))
        if len(path) >= h and best['path'] is None: best['path'] = list(path)
    def avail(assign, emptied):
        used = set(assign.values()); return sorted(l for l in Q if l not in used and l not in emptied)
    def rec(assign, emptied, path):
        if best['path'] is not None: return
        if len(path) >= h: leaf(path); return
        idx, st, rows, pa = pick_term_w(F, assign, emptied, mu1, Qs, False)
        if idx is None or st == 'true': leaf(path); return
        term = F[idx]
        def tail(assign, emptied, path, pos):
            if best['path'] is not None: return
            if len(path) >= h: leaf(path); return
            tl = term['tail']
            while pos < len(tl) and tl[pos][0] in assign: pos += 1
            if pos == len(tl): rec(assign, emptied, path); return
            row, lits = tl[pos]
            if not is_wide(lits, row) or row in cover[0]:
                av = avail(assign, emptied)
                if not av: leaf(path); return
                kind = 'L' if not is_wide(lits, row) else 'WP'
                for lab in av:
                    a2 = dict(assign); a2[row] = lab
                    tail(a2, emptied, path + [(kind, row, lab)], pos + 1)
                    if best['path'] is not None: return
                return
            holes = unresolved_holes(lits, Qs, assign, emptied)
            if not holes: tail(assign, emptied, path, pos + 1); return   # the row stays uncovered; the term is falsified at the next selection
            x = holes[0]
            for i in sorted(r for r in Rp if r not in assign):
                a2 = dict(assign); a2[i] = x
                tail(a2, emptied, path + [('WH', x, i)], pos)
                if best['path'] is not None: return
            tail(dict(assign), emptied | {x}, path + [('WH', x, None)], pos)
        if pa:
            i, x = term['pin']; av = avail(assign, emptied)
            if not av: leaf(path); return
            for lab in av:
                a2 = dict(assign); a2[i] = lab; p2 = path + [('P', i, lab)]
                if lab == x or len(p2) >= h: tail(a2, emptied, p2, 0)
                else:
                    for j in sorted(r for r in Rp if r not in a2):
                        a3 = dict(a2); a3[j] = x
                        tail(a3, emptied, p2 + [('H', x, j)], 0)
                        if best['path'] is not None: return
                    tail(a2, emptied | {x}, p2 + [('H', x, None)], 0)
                if best['path'] is not None: return
            return
        tail(dict(assign), emptied, path, 0)
    rec(dict(mu1), frozenset(), [])
    return best

def encode_wide(F, mu, R, E, fill, path, Q):
    """Code of a path of the wide-round tree, cut after its m-th light move: (rho*, sigma, m, beta, delta) with the
    current-term rule for light moves; wide queries have no beta entry, their answers are in delta."""
    Qs = set(Q); mu1 = dict(mu); mu1.update(fill)
    assign = dict(mu1); emptied = set(); code = dict(mu); free_out = sorted(E)
    fill_inv = {lab: row for row, lab in fill.items()}
    Rp = [r for r in R if r not in fill]
    cover = min_vertex_cover(wide_graph(F, Rp, Qs, mu1))
    m = sum(1 for st in path if st[0] == 'L'); moved = []; betas = []; deltas = []; pos = 0
    xcur = set()
    global LAST_XCUR_HIT; LAST_XCUR_HIT = False
    while len(moved) < m:
        idx, st, rows, pa = pick_term_w(F, assign, emptied, mu1, Qs, False)
        assert idx is not None and st == 'free'
        term = F[idx]; pos0 = pos
        if term['pin'] is not None: xcur.add(term['pin'][1])
        if pa:
            i, x = term['pin']; step = path[pos]
            assert step[0] == 'P' and step[1] == i, 'the round queries the pigeon first'
            lab = step[2]; assign[i] = lab; deltas.append(('lab', lab)); pos += 1
            if lab != x:
                st2 = path[pos]; assert st2[0] == 'H' and st2[1] == x
                if st2[2] is None: emptied.add(x); deltas.append(('empty', None))
                else: assign[st2[2]] = x; deltas.append(('row', st2[2]))
                pos += 1
        betas.append(('N', None)); node_beta = len(betas) - 1; node_moves = []
        for k, (row, lits) in enumerate(term['tail']):
            if row in assign: continue
            if is_wide(lits, row):
                if row in cover[0]:
                    step = path[pos]; assert step[0] == 'WP' and step[1] == row, ('wide pigeon expected', step)
                    assign[row] = step[2]; deltas.append(('wlab', step[2])); pos += 1
                else:
                    while True:
                        holes = unresolved_holes(lits, Qs, assign, emptied)
                        if not holes: break
                        x = holes[0]; step = path[pos]; assert step[0] == 'WH' and step[1] == x, ('wide hole expected', step)
                        pos += 1
                        if step[2] is None: emptied.add(x); deltas.append(('wempty', None))
                        else: assign[step[2]] = x; deltas.append(('wrow', step[2]))
                        if row in assign: break
                continue
            step = path[pos]; assert step[0] == 'L' and step[1] == row, ('light move expected', step)
            cons = [l for l in free_out if consistent(lits, l) and not (CODE_RULE in ('own', 'own-two-role') and (fill_inv[l], l) in PINS) and not (CODE_RULE in ('own-two-role', 'current-two-role') and l in PINS_BY_ROW.get(row, ())) and not (CODE_RULE in ('current', 'current-two-role') and l in xcur)]
            if not cons: raise NotRich()
            if cons[0] in xcur: LAST_XCUR_HIT = True
            code[row] = cons[0]; free_out.remove(cons[0]); moved.append(row); node_moves.append(k)
            assign[row] = step[2]; deltas.append(('ans', step[2])); pos += 1
            if len(moved) == m: break
        betas[node_beta] = ('N', bool(node_moves))
        for t, k in enumerate(node_moves): betas.append(('M', k, t == len(node_moves) - 1))
        assert pos > pos0, 'a node of the path without a query'
    sigma = tuple(sorted(fill)); code_labels = [code[r] for r in moved]
    return (tuple(sorted(code.items())), sigma, m, tuple(betas), tuple(deltas),
            tuple(('slot', code_labels.index(fill[f])) if fill[f] in code_labels else ('E', fill[f]) for f in sigma))

def decode_wide(F, code, Q):
    code_assign, sigma, m, betas, deltas, sig_labels = code
    Qs = set(Q); sig = dict(zip(sigma, sig_labels))
    cur = dict(code_assign); base = dict(code_assign); slot_row = {}
    for f, (k, v) in sig.items():
        cur[f] = v if k == 'E' else OUT
        if k == 'E': base[f] = v
        else: slot_row[v] = f
    rows_all = sorted(set(r for t in F for r, _ in t['tail']) | set(cur) | set(t['pin'][0] for t in F if t['pin'] is not None))
    Rp = [r for r in rows_all if r not in cur]     # residual rows in alpha; wide rows are never placed
    cover = min_vertex_cover(wide_graph(F, Rp, Qs, cur))
    emptied = set(); d = 0; b = 0; moved = []
    while len(moved) < m:
        idx, st, rows, pa = pick_term_w(F, cur, emptied, base, Qs, True)
        if idx is None or st == 'false': return None
        term = F[idx]; progress = (len(moved), d)
        if pa:
            i, x = term['pin']
            k, val = deltas[d]; d += 1
            if k != 'lab': return None
            cur[i] = val
            if val != x:
                k, val2 = deltas[d]; d += 1
                if k == 'empty': emptied.add(x)
                elif k == 'row': cur[val2] = x
                else: return None
        kind, has_moves = betas[b]; b += 1
        if kind != 'N': return None
        done = False
        for k, (row, lits) in enumerate(term['tail']):
            if is_wide(lits, row):
                if row in cur: continue          # wide rows are never placed: cur agrees with reality
                if row in cover[0]:
                    kk, val = deltas[d]; d += 1
                    if kk != 'wlab': return None
                    cur[row] = val
                else:
                    while True:
                        holes = unresolved_holes(lits, Qs, cur, emptied)
                        if not holes: break
                        x = holes[0]; kk, val = deltas[d]; d += 1
                        if kk == 'wempty': emptied.add(x)
                        elif kk == 'wrow': cur[val] = x
                        else: return None
                        if row in cur: break
                continue
            # a light row: moved at this node iff beta says so (a placed row of this node's moves sits at its code label in cur)
            if not has_moves or b >= len(betas) or betas[b][0] != 'M' or betas[b][1] != k: continue
            _, kb, last = betas[b]; b += 1
            kk, val = deltas[d]; d += 1
            if kk != 'ans': return None
            cur[row] = val; moved.append(row)
            if REVEAL_SLOTS and (len(moved) - 1) in slot_row:
                f = slot_row[len(moved) - 1]; lab = code_assign_get(code_assign, row); cur[f] = lab; base[f] = lab
            if last: has_moves = False
            if len(moved) == m: done = True; break
        if progress == (len(moved), d) and not done: return None
    for row in moved: base.pop(row, None)
    for f in sigma: base.pop(f, None)
    code_labels = [code_assign_get(code_assign, r) for r in moved]
    fill = {f: (code_labels[v] if k == 'slot' else v) for f, (k, v) in sig.items()}
    return tuple(sorted(base.items())), tuple(sorted(fill.items()))

def code_assign_get(code_assign, row):
    for r, l in code_assign:
        if r == row: return l
    raise KeyError(row)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--L', type=int, default=3); ap.add_argument('--L2', type=int, default=1)
    ap.add_argument('--e', type=int, default=1); ap.add_argument('--w', type=int, default=1)
    ap.add_argument('--h', type=int, default=2); ap.add_argument('--terms', type=int, default=6)
    ap.add_argument('--pinned-rows', type=int, default=5); ap.add_argument('--tail-rows', type=int, default=2)
    ap.add_argument('--labels', type=int, default=0, help='if positive, pins use only this many labels (few pinned labels)')
    ap.add_argument('--seed', type=int, default=20260918); ap.add_argument('--out', required=True)
    ap.add_argument('--max-pairs', type=int, default=3_000_000)
    ap.add_argument('--hole-always', action='store_true', help='query the hole after every pigeon answer other than the pin')
    ap.add_argument('--fill-domain', choices=('any', 'notail'), default='any', help='rows the filling may use: any residual row, or only rows outside every tail')
    ap.add_argument('--skip-killed', action='store_true', help='leave the node after a pigeon answer other than the pin (no tail queries); filled-pigeon nodes then carry no record')
    ap.add_argument('--code-rule', choices=('avoid-X', 'own', 'own-two-role', 'current', 'current-two-role', 'any'), default='avoid-X', help='avoid-X: code labels outside the pinned labels; own: code labels whose own filling row is not pinned to them; current: code labels outside the pin labels of the current terms of the nodes up to the move (cycle 210); current-two-role: also outside the moved row\'s own pinned labels')
    ap.add_argument('--dense-example', action='store_true', help='the all-pairs reader of the dense-cube obstruction: every pinned row pinned to every label of the cube of one literal, tails of that literal on three rows (cycle 210)')
    ap.add_argument('--wide-rows', type=int, default=0, help='the last K rows of B are wide rows (cycle 212): their tails carry --wide-lits literals and they are resolved by wide rounds in --tree wide')
    ap.add_argument('--wide-lits', type=int, default=2, help='literals per tail pattern of a wide row')
    ap.add_argument('--wide-example', choices=('same-pattern', 'distinct', 'one-pin'), default=None, help='the three readers of the wide-rows entry (rows 3.. are wide, pattern bits 0..L-2)')
    ap.add_argument('--wide-w', type=int, default=None, help='tail rows with more literals than this are wide: moved without a code label, the answer recorded in delta (cycle 211)')
    ap.add_argument('--reveal-slots', action='store_true', help='decoder learns a slot row\'s label when the move with that code label is decoded (needed by the current rules)')
    ap.add_argument('--two-role', action='store_true', help='tails may use pinned rows (a row pinned in one term and light in another)')
    ap.add_argument('--two-role-example', action='store_true', help='the recorded two-role counterexample reader of the mixed-term tool')
    ap.add_argument('--two-role-example2', action='store_true', help='a two-role row pinned at an outside label that is consistent with its light pattern: exhibits the need to exclude the moved row\'s own pinned labels')
    ap.add_argument('--tree', choices=('slack', 'compact', 'wide'), default='slack', help='slack: the restricted slack tree of cycle 207; compact: the compact complete-term tree of rho itself, simulated by the decoder (cycle 208)')
    ap.add_argument('--pin-test', action='store_true', help='resolve a pin at a free outside label by a pin test and choose code labels outside the pinned labels (entry encoding only)')
    ap.add_argument('--encoding', choices=('node', 'entry'), default='node', help='node: per-node record, filled tail rows moved; entry: the encoding of the entry (filled rows never moved, no per-node record)')
    a = ap.parse_args()
    global HOLE_ALWAYS, PIN_TEST, X_PINS, SKIP_KILLED, CODE_RULE, PINS, REVEAL_SLOTS, WIDE_W, WIDE_ROWS; HOLE_ALWAYS = a.hole_always; PIN_TEST = a.pin_test; SKIP_KILLED = a.skip_killed; CODE_RULE = a.code_rule; REVEAL_SLOTS = a.reveal_slots; WIDE_W = a.wide_w
    n = 2 ** a.L; N = 2 ** a.L2; e = a.e; rng = random.Random(a.seed)
    while True:
        vecs = [rng.randrange(n) for _ in range(a.L2)]; span = {0}
        for v in vecs: span |= {x ^ v for x in span}
        if len(span) == N: break
    tr = rng.randrange(n); Q = set(x ^ tr for x in span); O = sorted(set(range(n)) - Q)
    rows_all = list(range(n + 1)); A = sorted(rng.sample(rows_all, a.pinned_rows))
    B = rows_all if a.two_role else [r for r in rows_all if r not in A]
    label_pool = rng.sample(range(n), a.labels) if a.labels > 0 else list(range(n))
    WIDE_ROWS = frozenset(B[len(B) - a.wide_rows:]) if a.wide_rows > 0 else frozenset()
    F = []
    while len(F) < a.terms:
        kind = rng.random(); pin = None
        if kind < 0.85: pin = (rng.choice(A), rng.choice(label_pool))
        tail = []
        if kind > 0.1:
            for row in rng.sample(B, rng.randint(1, a.tail_rows)):
                if pin is not None and row == pin[0]: continue
                nl = a.wide_lits if row in WIDE_ROWS else rng.randint(1, a.w)
                bits = rng.sample(range(a.L), nl); tail.append((row, [(t, rng.randint(0, 1)) for t in bits]))
        if pin is None and not tail: continue
        F.append({'pin': pin, 'tail': tail})
    if a.wide_example:
        A = [0, 1, 2]; Bw = list(range(3, n + 1)); WIDE_ROWS = frozenset(Bw); B = Bw
        pw = [(t, 0) for t in range(a.L - 1)]
        if a.wide_example == 'same-pattern': F = [{'pin': None, 'tail': [(j, pw)]} for j in Bw]
        elif a.wide_example == 'distinct': F = [{'pin': None, 'tail': [(j, [(t, (k >> t) & 1) for t in range(a.L - 1)])]} for k, j in enumerate(Bw)]
        else: F = [{'pin': (0, 1), 'tail': [(j, pw)]} for j in Bw]
    if a.two_role_example:
        q0, q1 = sorted(Q)[:2]; A = [0, 1, 2, 3]
        F = [{'pin': (0, q0), 'tail': [(5, [(0, 0)])]}, {'pin': (1, q1), 'tail': [(0, [(1, 0)])]}, {'pin': None, 'tail': [(6, [(2, 1)])]}]
        a.two_role = True
    if a.two_role_example2:
        q0 = sorted(Q)[0]; o0 = O[0]; A = [0, 1]
        b0 = [(t, (o0 >> t) & 1) for t in range(a.L)][:1]   # one literal of row 0 consistent with o0
        F = [{'pin': (0, o0), 'tail': [(5, [(1, 0)])]}, {'pin': (1, q0), 'tail': [(0, b0)]}, {'pin': None, 'tail': [(6, [(2, 1)]), (5, [(1, 1)])]}]
        a.two_role = True
    if a.dense_example:
        A = list(range(n - 2)); cube = [y for y in range(n) if (y >> 0) & 1 == 0]   # every other row is a tail row
        F = [{'pin': (i, y), 'tail': [(n - 2 + (i + y) % 3, [(0, 0)])]} for i in A for y in cube]
        a.two_role = False
    X = set(t['pin'][1] for t in F if t['pin'] is not None)
    X_PINS = set(X); PINS = set(t['pin'] for t in F if t['pin'] is not None)
    global PINS_BY_ROW; PINS_BY_ROW = {}
    for t in F:
        if t['pin'] is not None: PINS_BY_ROW.setdefault(t['pin'][0], set()).add(t['pin'][1])
    tailrows = set(row for t in F for row, _ in t['tail'])
    q = n + 1 - (N + 1 + e)
    size = math.comb(n + 1, q) * math.factorial(n - N) // math.factorial(e)
    fills_per = math.factorial(N + 1 + e) // math.factorial(N + 1)
    if a.fill_domain == 'notail': fills_per = 'at most ' + str(fills_per)
    fp = fills_per if isinstance(fills_per, int) else int(fills_per.split()[-1])
    print(f'|Phi_e| = {size}, fillings per restriction {fills_per}, pairs at most {size * fp}', file=sys.stderr)
    if size * fp > a.max_pairs: sys.exit(f'refusing to enumerate {size * fp} pairs (limit {a.max_pairs})')
    stats = {'pairs': 0, 'G': 0, 'bad': 0, 'bad_G': 0, 'rich_G': 0, 'rich_offG': 0, 'fail_G': 0, 'fail_offG': 0, 'max_height': 0, 'xcur_ok': 0, 'xcur_fail': 0, 'noxcur_fail': 0, 'rich_moves_G': 0, 'rich_moves_offG': 0, 'fail_moves': 0}
    for matched in itertools.combinations(rows_all, q):
        R = sorted(set(rows_all) - set(matched))
        for labs in itertools.permutations(O, q):
            mu = dict(zip(matched, labs)); E = sorted(set(O) - set(labs))
            onG = not (set(E) & X)
            for frows in itertools.permutations([r for r in R if a.fill_domain == 'any' or r not in tailrows], e):
                fill = dict(zip(frows, E)); stats['pairs'] += 1; stats['G'] += onG
                if a.tree == 'compact':
                    mu1 = dict(mu); mu1.update(fill); Rp = [r for r in R if r not in fill]
                    res = first_long_path_compact(F, mu1, Rp, Q, a.h)
                elif a.tree == 'wide':
                    mu1 = dict(mu); mu1.update(fill); Rp = [r for r in R if r not in fill]
                    res = first_long_path_wide(F, mu1, Rp, Q, a.h)
                    stats['max_wide'] = max(stats.get('max_wide', 0), res['max_wide']); stats['wide_gt_cover'] = stats.get('wide_gt_cover', 0) + (res['max_wide'] > res['cover'])
                else:
                    res = first_long_path(F, mu, R, Q, E, fill, a.h)
                stats['max_height'] = max(stats['max_height'], res['height'])
                if res['path'] is None: continue
                stats['bad'] += 1; stats['bad_G'] += onG
                try:
                    if a.tree == 'compact': code = encode_compact(F, mu, R, E, fill, res['path'], Q)
                    elif a.tree == 'wide': code = encode_wide(F, mu, R, E, fill, res['path'], Q)
                    else: code = encode(F, mu, R, E, fill, res['path'], Q) if a.encoding == 'node' else encode_entry(F, mu, R, E, fill, res['path'], Q)
                except NotRich:
                    continue
                stats['rich_G' if onG else 'rich_offG'] += 1
                has_moves = a.tree in ('compact', 'wide') and code[2] >= 1
                if has_moves: stats['rich_moves_G' if onG else 'rich_moves_offG'] += 1
                try:
                    if a.tree == 'compact': dec = decode_compact(F, code, Q)
                    elif a.tree == 'wide': dec = decode_wide(F, code, Q)
                    else: dec = decode(F, code) if a.encoding == 'node' else decode_entry(F, code, Q)
                except (KeyError, IndexError, TypeError, ValueError):
                    dec = None
                if dec != (tuple(sorted(mu.items())), tuple(sorted(fill.items()))):
                    stats['fail_G' if onG else 'fail_offG'] += 1
                    if a.tree in ('compact', 'wide'): stats['xcur_fail' if LAST_XCUR_HIT else 'noxcur_fail'] += 1
                    if has_moves: stats['fail_moves'] += 1
                elif a.tree in ('compact', 'wide') and LAST_XCUR_HIT: stats['xcur_ok'] += 1
    rec = {'L': a.L, 'L2': a.L2, 'n': n, 'N': N, 'e': e, 'w': a.w, 'h': a.h, 'seed': a.seed, 'labels': a.labels, 'hole_always': HOLE_ALWAYS, 'encoding': a.encoding, 'fill_domain': a.fill_domain, 'pin_test': PIN_TEST, 'skip_killed': SKIP_KILLED, 'code_rule': CODE_RULE, 'reveal_slots': REVEAL_SLOTS, 'wide_w': WIDE_W, 'wide_rows': sorted(WIDE_ROWS), 'wide_example': a.wide_example, 'tree': a.tree, 'two_role': a.two_role, 'two_role_example': a.two_role_example, 'two_role_example2': a.two_role_example2, 'dense_example': a.dense_example,
           'Q': sorted(Q), 'A': A, 'X': sorted(X), 'terms': [{'pin': t['pin'], 'tail': [[r, l] for r, l in t['tail']]} for t in F], **stats}
    with open(a.out, 'a') as f: f.write(json.dumps(rec) + '\n')
    print(json.dumps({k: v for k, v in rec.items() if k not in ('terms', 'Q', 'A')}))
    return 0 if stats['fail_G'] == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
