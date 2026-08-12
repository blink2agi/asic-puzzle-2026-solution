import pickle,collections,sys
sys.path.insert(0,'tools')
from cells import COMB,SEQ,NOFUNC,basename
nl=pickle.load(open('tools/puzzle_nl.pkl','rb'))
g =pickle.load(open('tools/puzzle.pkl','rb'))
cells={c['idx']:c for c in nl['cells']}; ports=nl['ports']
VPWR,VGND=nl['VPWR'],nl['VGND']
portnets=set().union(*ports.values())
drv=collections.defaultdict(list); sink=collections.defaultdict(list)
for c in nl['cells']:
    b=basename(c['cell'])
    outs=set(COMB.get(b,{}))
    if b in SEQ: outs=set(SEQ[b]['q'])|set(SEQ[b].get('qn',[]))
    for p,n in c['pins'].items():
        (drv if p in outs else sink)[n].append((c['idx'],c['cell'],p,c['x'],c['y']))
nosink=[n for n in drv if n not in sink and n not in portnets]
print("driven-but-unused nets:",len(nosink))
for n in nosink:
    for e in drv[n]: print("   net",n,e)
print()
nodrv=[n for n in sink if n not in drv and n not in (VPWR,VGND) and n not in portnets]
print("undriven nets:",nodrv)
