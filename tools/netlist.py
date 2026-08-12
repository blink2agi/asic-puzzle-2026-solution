"""Turn extracted geometry into a netlist."""
import pickle, collections, sys, re

PKL = sys.argv[1] if len(sys.argv)>1 else 'tools/warmup.pkl'
d = pickle.load(open(PKL,'rb'))
inst, labels = d['instances'], d['labels']

# group labels by tag
bytag = collections.defaultdict(list)
for text,(x,y),li,tag,net in labels: bytag[tag].append((text,net,li,(x,y)))

SKIP = ('decap','tapvpwrvgnd','fill','INTERNAL')
POWER = {'VPWR','VGND','VPB','VNB'}

# top ports
ports = {}
for text,net,li,xy in bytag[('top',0)]:
    ports.setdefault(text, set()).add(net)

netnames = {}
for t,ns in ports.items():
    for n in ns:
        if n is not None: netnames[n]=t

# find power nets: nets with the most VPWR/VGND labels
pwr = collections.Counter(); gnd = collections.Counter()
for i,ins in enumerate(inst):
    for text,net,li,xy in bytag[('inst',i)]:
        if text=='VPWR' and net is not None: pwr[net]+=1
        if text=='VGND' and net is not None: gnd[net]+=1
VPWR = pwr.most_common(1)[0][0] if pwr else None
VGND = gnd.most_common(1)[0][0] if gnd else None
netnames[VPWR]='VPWR'; netnames[VGND]='VGND'
print(f"VPWR net {VPWR} ({pwr[VPWR]} lbls, {len(pwr)} candidates)  VGND net {VGND} ({gnd[VGND]}, {len(gnd)})")

cells=[]
for i,ins in enumerate(inst):
    cn = ins['cell']
    if any(s in cn for s in SKIP): continue
    pins={}
    for text,net,li,xy in bytag[('inst',i)]:
        if text in POWER: continue
        if text in pins and pins[text]!=net:
            pins[text] = pins[text] if pins[text] is not None else net
        else: pins[text]=net
    cells.append(dict(idx=i, cell=cn, x=ins['x'], y=ins['y'], rot=ins['rot'], mx=ins['mx'], pins=pins))

print("cells:",len(cells))
print("ports:",{k:sorted(v) for k,v in sorted(ports.items())})

# net -> list of (cellidx, pin)
netconn = collections.defaultdict(list)
for c in cells:
    for p,n in c['pins'].items(): netconn[n].append((c['idx'],p,c['cell']))
unnamed=[n for n in netconn if n is None]
print("pins with no net:", len(netconn[None]))
if netconn[None][:10]: print("  e.g.",netconn[None][:10])
pickle.dump(dict(cells=cells, ports=ports, netnames=netnames, VPWR=VPWR, VGND=VGND, netconn=dict(netconn)), open(PKL.replace('.pkl','_nl.pkl'),'wb'))
