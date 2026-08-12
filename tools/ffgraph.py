import pickle,collections,sys
sys.path.insert(0,'tools')
from cells import COMB,SEQ,basename
nl=pickle.load(open('tools/puzzle_nl.pkl','rb'))
cells={c['idx']:c for c in nl['cells']}
ports=nl['ports']; VPWR,VGND=nl['VPWR'],nl['VGND']
drv={}; outs_of={}
for c in nl['cells']:
    b=basename(c['cell']); o=set(COMB.get(b,{}))
    if b in SEQ: o=set(SEQ[b]['q'])|set(SEQ[b].get('qn',[]))
    outs_of[c['idx']]=o
    for p,n in c['pins'].items():
        if p in o: drv[n]=(c['idx'],p)
pn={}
for k,v in ports.items():
    for n in v: pn[n]=k
ffs=[c['idx'] for c in nl['cells'] if basename(c['cell']) in SEQ]
ffq={}
for ci in ffs:
    s=SEQ[basename(cells[ci]['cell'])]
    ffq[cells[ci]['pins'][s['q'][0]]]=ci

def support(n, seen=None):
    """set of (kind,id) sources feeding net n, stopping at FF outputs/ports"""
    if seen is None: seen=set()
    out=set()
    stack=[n]; vis=set()
    while stack:
        m=stack.pop()
        if m in vis: continue
        vis.add(m)
        if m in ffq: out.add(('ff',ffq[m])); continue
        if m in pn: out.add(('port',pn[m])); continue
        if m in (VPWR,VGND): out.add(('const',m)); continue
        if m not in drv: out.add(('float',m)); continue
        ci,_=drv[m]
        for p,nn in cells[ci]['pins'].items():
            if p not in outs_of[ci]: stack.append(nn)
    return out

G={}
for ci in ffs:
    s=SEQ[basename(cells[ci]['cell'])]
    G[ci]=support(cells[ci]['pins'][s['d']])
# connected components / structure
print("FF count",len(ffs))
for ci in sorted(ffs, key=lambda c:(-cells[c]['y'],cells[c]['x'])):
    c=cells[ci]
    dep=sorted([f"ff{d}" for k,d in G[ci] if k=='ff'])
    prt=sorted([d for k,d in G[ci] if k=='port'])
    print(f"ff{ci:<5d} {basename(c['cell']):6s} @({c['x']:6.1f},{c['y']:6.1f}) ndeps={len(dep):3d} ports={prt}")
