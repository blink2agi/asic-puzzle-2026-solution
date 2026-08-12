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
        if p in o: drv[n]=c['idx']
portname={}
for k,v in ports.items():
    for n in v: portname[n]=k

def cone(startnets, stop_at_ff=True):
    seen=set(); stack=list(startnets); cellset=set()
    while stack:
        n=stack.pop()
        if n in seen or n in (VPWR,VGND): continue
        seen.add(n)
        ci=drv.get(n)
        if ci is None: continue
        cellset.add(ci)
        c=cells[ci]; b=basename(c['cell'])
        if b in SEQ and stop_at_ff:
            s=SEQ[b]
            for p in ('d','clk'):
                if s.get(p): stack.append(c['pins'][s[p]])
            if 'rst' in s: stack.append(c['pins'][s['rst'][0]])
            continue
        for p,nn in c['pins'].items():
            if p not in outs_of[ci]: stack.append(nn)
    return cellset, seen

succ_cells, succ_nets = cone(ports['success'])
print("cells in success cone (through FFs):", len(succ_cells))
h=collections.Counter(basename(cells[ci]['cell']) for ci in succ_cells)
print(dict(sorted(h.items())))
ffs=[ci for ci in succ_cells if basename(cells[ci]['cell']) in SEQ]
print("FFs in success cone:",len(ffs))
allff=[c['idx'] for c in nl['cells'] if basename(c['cell']) in SEQ]
print("total FFs:",len(allff), " not in success cone:",len(set(allff)-set(ffs)))
notin=[ci for ci in cells if ci not in succ_cells and basename(cells[ci]['cell']) not in ('diode',)]
print("cells NOT in success cone:",len(notin))
xs=[cells[ci]['x'] for ci in notin]; ys=[cells[ci]['y'] for ci in notin]
print("  their x range",min(xs),max(xs)," y range",min(ys),max(ys))
xs=[cells[ci]['x'] for ci in succ_cells]; ys=[cells[ci]['y'] for ci in succ_cells]
print("success-cone x range",min(xs),max(xs)," y range",min(ys),max(ys))
print("1275 in cone?",1275 in succ_cells, " 1293 in cone?",1293 in succ_cells)
# O[] cone
oc,_=cone([n for i in range(8) for n in ports[f'O[{i}]']])
print("cells in O[] cone:",len(oc), "overlap with success cone:",len(oc&succ_cells))
