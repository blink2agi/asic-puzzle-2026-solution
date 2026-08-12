import sys, collections, itertools
GRID="""D D D D D J J A B B I
D D F D D J A A B B I
D D F J J J J A A B I
D D F J E E E I A A I
F D F J E I I I I I I
F F F J E E E I H H H
J J J J J J E I H K K
J C C C E E E I H K K
J C C G I I I I H K K
J J C G G I I I H H H
J C C G I I I I I I I"""
R=[l.split() for l in GRID.strip().split('\n')]
N=11; K=2
regions=collections.defaultdict(list)
for r in range(N):
    for c in range(N): regions[R[r][c]].append((r,c))
# connectivity check (4-adjacency)
for k,cells in regions.items():
    s=set(cells); seen={cells[0]}; st=[cells[0]]
    while st:
        r,c=st.pop()
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            p=(r+dr,c+dc)
            if p in s and p not in seen: seen.add(p); st.append(p)
    print(f"region {k}: {len(cells):3d} cells, 4-connected={len(seen)==len(cells)}")
print()
# ---- exact solver: choose 2 columns per row, backtracking ----
sols=[]
colcnt=[0]*N; regcnt=collections.Counter(); rows=[]
combos=list(itertools.combinations(range(N),2))
combos=[c for c in combos if c[1]-c[0]>=2]   # no two adjacent in same row
def ok_adj(prev, cur):
    for a in prev:
        for b in cur:
            if abs(a-b)<=1: return False
    return True
def bt(r):
    if r==N:
        sols.append([tuple(x) for x in rows]); return
    if len(sols)>4: return
    for cc in combos:
        if any(colcnt[c]>=K for c in cc): continue
        if rows and not ok_adj(rows[-1],cc): continue
        keys=[R[r][c] for c in cc]
        if any(regcnt[k]+keys.count(k)>K for k in set(keys)): continue
        # feasibility: remaining rows must supply enough
        for c in cc: colcnt[c]+=1
        for k in keys: regcnt[k]+=1
        rows.append(cc)
        # prune: any column needing K-count more than remaining rows*? loose check
        rem=N-1-r
        if all(K-colcnt[c]<=rem for c in range(N)) and all(K-regcnt[k]<=sum(1 for rr in range(r+1,N) for cc2 in range(N) if R[rr][cc2]==k) for k in regions):
            bt(r+1)
        rows.pop()
        for c in cc: colcnt[c]-=1
        for k in keys: regcnt[k]-=1
bt(0)
print("solutions found:",len(sols))
for s in sols[:3]:
    g=[['.']*N for _ in range(N)]
    for r,cc in enumerate(s):
        for c in cc: g[r][c]='*'
    for r in range(N): print("  "+' '.join(g[r]))
    print("  bits:", ''.join('1' if g[r][c]=='*' else '0' for r in range(N) for c in range(N)))
    print()
