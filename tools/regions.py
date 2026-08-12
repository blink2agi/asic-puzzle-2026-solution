import sys; sys.path.insert(0,'tools')
from ffeq import build, cells, SEQ, basename, ffq
PAIRS_REGION=[(1464,1423),(1454,1419),(452,1424),(1467,1420),(1499,1495),(1512,1418),
              (1427,1478),(1425,1480),(431,392),(451,453),(444,393)]
PAIRS_COL   =[(250,347),(348,251),(266,318),(252,349),(263,363),(388,418),(271,361),
              (362,262),(267,302),(269,303),(268,304)]
CA=[800,867,797,799]   # counterA bits b0..b3  (column index)
CB=[1090,1095,1087,1086] # counterB bits b0..b3 (row index)
def probe(a,b):
    """return set of (row,col) where this counter increments"""
    s=SEQ[basename(cells[a]['cell'])]
    leaves,vk,ev=build(cells[a]['pins'][s['d']])
    hits=set()
    for row in range(11):
        for col in range(11):
            assign={}
            for k in vk:
                if k[0]=='port': assign[k]= 1 if k[1] in ('I','enable') else 0
                elif k[0]=='ff':
                    f=k[1]; v=0
                    if f in CA: v=(col>>CA.index(f))&1
                    elif f in CB: v=(row>>CB.index(f))&1
                    elif f==663: v=0
                    assign[k]= (1-v) if k[2] else v
                elif k[0]=='float': assign[k]=0
            if ev(assign): hits.add((row,col))
    return hits
print("=== COLUMN counters ===")
for a,b in PAIRS_COL:
    h=probe(a,b); cols=sorted({c for r,c in h}); rows=sorted({r for r,c in h})
    print(f" pair({a},{b}): cells={len(h)} cols={cols} rows={rows}")
print("=== REGION counters ===")
regs=[]
for a,b in PAIRS_REGION:
    h=probe(a,b); regs.append(h)
    print(f" pair({a},{b}): {len(h)} cells")
grid=[['.' for _ in range(11)] for _ in range(11)]
LET='ABCDEFGHIJK'
for i,h in enumerate(regs):
    for r,c in h: grid[r][c]=LET[i] if grid[r][c]=='.' else '!'
print("\nREGION MAP (row 0 = first row fed in):")
for r in range(11): print("  "+' '.join(grid[r]))
import collections
print("region sizes:",[len(h) for h in regs], "total",sum(len(h) for h in regs))
