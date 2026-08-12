import itertools, collections, sys
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
N=11; K=2; LET=sorted({R[r][c] for r in range(N) for c in range(N)})
def search(adjacency=True, limit=10**9, want=None):
    sols=[]
    combos=list(itertools.combinations(range(N),2))
    if adjacency: combos=[c for c in combos if c[1]-c[0]>=2]
    remreg={k:[0]*(N+1) for k in LET}
    for k in LET:
        for r in range(N-1,-1,-1):
            remreg[k][r]=remreg[k][r+1]+sum(1 for c in range(N) if R[r][c]==k)
    colc=[0]*N; regc=collections.Counter(); rows=[]
    def bt(r):
        if len(sols)>=limit: return
        if r==N: sols.append(list(rows)); return
        rem=N-r-1
        for cc in combos:
            if any(colc[c]>=K for c in cc): continue
            if adjacency and rows and any(abs(a-b)<=1 for a in rows[-1] for b in cc): continue
            ks=[R[r][c] for c in cc]
            if any(regc[k]+ks.count(k)>K for k in set(ks)): continue
            for c in cc: colc[c]+=1
            for k in ks: regc[k]+=1
            ok = all(K-colc[c]<=rem for c in range(N)) and all(K-regc[k]<=remreg[k][r+1] for k in LET)
            rows.append(cc)
            if ok: bt(r+1)
            rows.pop()
            for c in cc: colc[c]-=1
            for k in ks: regc[k]-=1
    bt(0)
    return sols
a=search(True)
print("Star Battle solutions (with adjacency rule):",len(a))
b=search(False, limit=200)
print("grids with 2/row,2/col,2/region ignoring adjacency:",len(b),"(capped at 200)")
def tobits(s):
    g=[['0']*N for _ in range(N)]
    for r,cc in enumerate(s):
        for c in cc: g[r][c]='1'
    return ''.join(''.join(row) for row in g)
open('tools/sol.txt','w').write(tobits(a[0]))
adjbad=[s for s in b if any(abs(x-y)<=1 for r in range(N-1) for x in s[r] for y in s[r+1]) or any(s[r][1]-s[r][0]<=1 for r in range(N))]
print("of those, ones that DO violate adjacency:",len(adjbad))
open('tools/adjbad.txt','w').write('\n'.join(tobits(s) for s in adjbad[:20]))
