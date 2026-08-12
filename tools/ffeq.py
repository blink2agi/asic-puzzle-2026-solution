import pickle,collections,sys,itertools
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
    for k,qp in enumerate(s['q']): ffq[cells[ci]['pins'][qp]]=(ci,False)
    for qp in s.get('qn',[]):
        n=cells[ci]['pins'].get(qp)
        if n is not None: ffq[n]=(ci,True)

def build(n):
    """return (vars, evalfn) for net n; vars = ordered list of source keys"""
    order=[]; vis={}
    def rec(m):
        if m in vis: return
        if m in ffq or m in pn or m in (VPWR,VGND) or m not in drv:
            vis[m]='leaf'; return
        ci,_=drv[m]
        for p,nn in cells[ci]['pins'].items():
            if p not in outs_of[ci]: rec(nn)
        vis[m]='node'; order.append(m)
    rec(n)
    leaves=sorted([m for m,k in vis.items() if k=='leaf'])
    def key(m):
        if m in ffq: return ('ff',ffq[m][0],ffq[m][1])
        if m in pn:  return ('port',pn[m],False)
        if m==VPWR: return ('const',1,False)
        if m==VGND: return ('const',0,False)
        return ('float',m,False)
    varkeys=[key(m) for m in leaves]
    def ev(assign):
        v={}
        for m,k in zip(leaves,varkeys):
            if k[0]=='const': v[m]=k[1]
            elif k[0]=='float': v[m]=assign.get(k,0)
            else: v[m]=assign[k]
        for m in order:
            ci,op=drv[m]; c=cells[ci]; b=basename(c['cell'])
            p={pp:v[nn] for pp,nn in c['pins'].items() if pp not in outs_of[ci]}
            v[m]=COMB[b][op](p)
        return v[n]
    return leaves,varkeys,ev

def truth(n):
    leaves,vk,ev=build(n)
    free=[i for i,k in enumerate(vk) if k[0] not in ('const',)]
    tt={}
    if len(free)>18: return vk,free,None
    rows=[]
    for bits in itertools.product([0,1],repeat=len(free)):
        assign={}
        for i,b in zip(free,bits): assign[vk[i]]=b
        rows.append(ev(assign))
    return vk,free,rows

def sop(vk,free,rows,maxterms=40):
    names=[]
    for i in free:
        k=vk[i]
        nm = f"ff{k[1]}" if k[0]=='ff' else (k[1] if k[0]=='port' else f"fl{k[1]}")
        if k[2]: nm='~'+nm
        names.append(nm)
    n=len(free); on=[i for i,v in enumerate(rows) if v]
    if not on: return "1'b0", names
    if len(on)==2**n: return "1'b1", names
    # quine-mccluskey via sympy
    from sympy.logic import SOPform
    from sympy import symbols
    syms=symbols(' '.join(f"v{i}" for i in range(n)))
    if n==1: syms=[syms]
    minterms=[[(i>>(n-1-j))&1 for j in range(n)] for i in on]
    e=SOPform(list(syms),minterms)
    s=str(e)
    for i in range(n-1,-1,-1): s=s.replace(f"v{i}",names[i])
    return s, names
if __name__=='__main__':
    import sys
    which=sys.argv[1:] or None
    for ci in sorted(ffs,key=lambda c:(-cells[c]['y'],cells[c]['x'])):
        if which and str(ci) not in which: continue
        s=SEQ[basename(cells[ci]['cell'])]
        vk,free,rows=truth(cells[ci]['pins'][s['d']])
        c=cells[ci]
        if rows is None:
            print(f"ff{ci} @({c['x']:.1f},{c['y']:.1f}) TOO BIG nvars={len(free)}"); continue
        e,names=sop(vk,free,rows)
        print(f"ff{ci:<5d} @({c['x']:6.1f},{c['y']:6.1f}) D = {e}")
