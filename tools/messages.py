import sys, random; sys.path.insert(0,'tools')
from sim import Sim
from run_puzzle import BITS_DEFAULT
s=Sim('tools/puzzle_nl.pkl')
def go(bits):
    s.val.clear(); s.state={ci:0 for ci in s.seq}
    s.setport('rst_n',0); s.setport('enable',0); s.setport('I',0)
    for _ in range(3): s.clock()
    s.setport('rst_n',1); s.clock(); s.setport('enable',1)
    for b in bits: s.setport('I',int(b)); s.clock()
    s.setport('enable',0); s.setport('I',0)
    out=[]
    for _ in range(24): s.clock(); out.append(sum(s.getport(f'O[{k}]')<<k for k in range(8)))
    return ''.join(chr(c) for c in out if 32<=c<127), s.getport('success')
cases=[(BITS_DEFAULT,'unique Star Battle solution'),('0'*121,'empty grid'),('1'*121,'all cells filled')]
# grids with 2/row+2/col+2/region that DO have touching stars (adjacency rule dropped)
import itertools, collections
GRID="""DDDDDJJABBI
DDFDDJAABBI
DDFJJJJAABI
DDFJEEEIAAI
FDFJEIIIIII
FFFJEEEIHHH
JJJJJJEIHKK
JCCCEEEIHKK
JCCGIIIIHKK
JJCGGIIIHHH
JCCGIIIIIII""".split('\n')
N=11; LET=sorted(set(''.join(GRID)))
rr={k:[0]*(N+1) for k in LET}
for k in LET:
    for r in range(N-1,-1,-1): rr[k][r]=rr[k][r+1]+GRID[r].count(k)
combos=list(itertools.combinations(range(N),2)); found=[]
def bt(r,rows,colc,regc):
    if len(found)>=6: return
    if r==N:
        if any(abs(x-y)<=1 for i in range(N-1) for x in rows[i] for y in rows[i+1]) or any(c[1]-c[0]<=1 for c in rows):
            found.append(''.join('1' if c in rows[i] else '0' for i in range(N) for c in range(N)))
        return
    for cc in combos:
        if any(colc[c]>=2 for c in cc): continue
        ks=[GRID[r][c] for c in cc]
        if any(regc[k]+ks.count(k)>2 for k in set(ks)): continue
        for c in cc: colc[c]+=1
        for k in ks: regc[k]+=1
        if all(2-colc[c]<=N-r-1 for c in range(N)) and all(2-regc[k]<=rr[k][r+1] for k in LET):
            bt(r+1,rows+[cc],colc,regc)
        for c in cc: colc[c]-=1
        for k in ks: regc[k]-=1
bt(0,[],[0]*N,collections.Counter())
for b in found: cases.append((b,'2/row+col+region but stars touch'))
random.seed(3)
for i in range(12): cases.append((''.join(random.choice('01') for _ in range(121)),'random grid'))
for k in [1,3,22]:
    idx=random.sample(range(121),k); b=['0']*121
    for j in idx: b[j]='1'
    cases.append((''.join(b),f'{k} scattered stars'))
seen={}
for b,lab in cases:
    t,ok=go(b)
    if t not in seen:
        seen[t]=lab; print(f"{t!r:34s} success={ok}   trigger: {lab}", flush=True)
