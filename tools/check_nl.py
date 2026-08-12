import pickle,collections,sys
sys.path.insert(0,'tools')
from cells import COMB,SEQ,NOFUNC,basename
d=pickle.load(open('tools/puzzle_nl.pkl','rb'))
cells=d['cells']; ports=d['ports']; VPWR,VGND=d['VPWR'],d['VGND']
drv=collections.defaultdict(list); sink=collections.defaultdict(list)
for c in cells:
    b=basename(c['cell'])
    outs=set(COMB.get(b,{})) | set(sum([SEQ[b]['q']+SEQ[b].get('qn',[]) for _ in [0]],[]) if b in SEQ else [])
    for p,n in c['pins'].items():
        (drv if p in outs else sink)[n].append((c['idx'],c['cell'],p))
portnets=set()
for k,v in ports.items(): portnets|=set(v)
inputs=set()
print("multi-driver nets:", [(n,v) for n,v in drv.items() if len(v)>1][:5])
und=[n for n in sink if n not in drv and n not in (VPWR,VGND) and n not in portnets]
print("undriven input nets:",len(und), und[:10])
for n in und[:6]: print("   ",n,sink[n])
nodrv_ports=[k for k in ports if not any(x in drv for x in ports[k])]
print("floating outputs?:",[k for k in ['success']+[f'O[{i}]' for i in range(8)] if not any(x in drv for x in ports[k])])
print("cell type histogram:")
h=collections.Counter(basename(c['cell']) for c in cells)
print(dict(sorted(h.items())))
