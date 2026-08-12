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
ffq={}
for c in nl['cells']:
    b=basename(c['cell'])
    if b in SEQ:
        for qp in SEQ[b]['q']: ffq[c['pins'][qp]]=f"Q{c['idx']}"
        for qp in SEQ[b].get('qn',[]):
            if c['pins'].get(qp) is not None: ffq[c['pins'][qp]]=f"~Q{c['idx']}"
EXPR={'inv':'!{A}','buf':'{A}','clkbuf':'{A}',
 'and2':'({A}&{B})','and3':'({A}&{B}&{C})','and4':'({A}&{B}&{C}&{D})',
 'and2b':'(!{A_N}&{B})','and3b':'(!{A_N}&{B}&{C})','and4b':'(!{A_N}&{B}&{C}&{D})',
 'and4bb':'(!{A_N}&!{B_N}&{C}&{D})',
 'nand2':'!({A}&{B})','nand3':'!({A}&{B}&{C})','nand4':'!({A}&{B}&{C}&{D})',
 'nand2b':'!(!{A_N}&{B})','nand3b':'!(!{A_N}&{B}&{C})',
 'or2':'({A}|{B})','or3':'({A}|{B}|{C})','or4':'({A}|{B}|{C}|{D})',
 'or3b':'({A}|{B}|!{C_N})','or4b':'({A}|{B}|{C}|!{D_N})','or4bb':'({A}|{B}|!{C_N}|!{D_N})',
 'nor2':'!({A}|{B})','nor3':'!({A}|{B}|{C})','nor4':'!({A}|{B}|{C}|{D})',
 'nor3b':'!({A}|{B}|!{C_N})','nor4b':'!({A}|{B}|{C}|!{D_N})',
 'xor2':'({A}^{B})','xnor2':'!({A}^{B})','mux2':'({S}?{A1}:{A0})',
 'a21o':'(({A1}&{A2})|{B1})','a21oi':'!(({A1}&{A2})|{B1})',
 'a22o':'(({A1}&{A2})|({B1}&{B2}))','a22oi':'!(({A1}&{A2})|({B1}&{B2}))',
 'a31o':'(({A1}&{A2}&{A3})|{B1})','a31oi':'!(({A1}&{A2}&{A3})|{B1})',
 'a32o':'(({A1}&{A2}&{A3})|({B1}&{B2}))','a41oi':'!(({A1}&{A2}&{A3}&{A4})|{B1})',
 'a211o':'(({A1}&{A2})|{B1}|{C1})','a211oi':'!(({A1}&{A2})|{B1}|{C1})',
 'a221o':'(({A1}&{A2})|({B1}&{B2})|{C1})','a221oi':'!(({A1}&{A2})|({B1}&{B2})|{C1})',
 'a311o':'(({A1}&{A2}&{A3})|{B1}|{C1})','a2111oi':'!(({A1}&{A2})|{B1}|{C1}|{D1})',
 'a21bo':'(({A1}&{A2})|!{B1_N})','a21boi':'!(({A1}&{A2})|!{B1_N})',
 'o21a':'(({A1}|{A2})&{B1})','o21ai':'!(({A1}|{A2})&{B1})',
 'o22a':'(({A1}|{A2})&({B1}|{B2}))','o22ai':'!(({A1}|{A2})&({B1}|{B2}))',
 'o31a':'(({A1}|{A2}|{A3})&{B1})','o31ai':'!(({A1}|{A2}|{A3})&{B1})',
 'o32a':'(({A1}|{A2}|{A3})&({B1}|{B2}))','o32ai':'!(({A1}|{A2}|{A3})&({B1}|{B2}))',
 'o211a':'(({A1}|{A2})&{B1}&{C1})','o211ai':'!(({A1}|{A2})&{B1}&{C1})',
 'o221a':'(({A1}|{A2})&({B1}|{B2})&{C1})','o311a':'(({A1}|{A2}|{A3})&{B1}&{C1})',
 'o21ba':'(({A1}|{A2})&!{B1_N})','o21bai':'!(({A1}|{A2})&!{B1_N})',
 'o2bb2a':'((!{A1_N}|!{A2_N})&({B1}|{B2}))','conb':'CONST'}
def ex(n,depth=0,maxd=99):
    if n==VPWR: return "1"
    if n==VGND: return "0"
    if n in ffq: return ffq[n]
    if n in pn: return pn[n]
    if n not in drv: return f"FLOAT{n}"
    ci,op=drv[n]; c=cells[ci]; b=basename(c['cell'])
    if b=='conb': return '1' if op=='HI' else '0'
    if depth>=maxd: return f"n{n}"
    t=EXPR.get(b)
    if t is None: return f"?{b}({n})"
    return t.format(**{p:ex(nn,depth+1,maxd) for p,nn in c['pins'].items() if p not in outs_of[ci]})
if __name__=='__main__':
    tgt=sys.argv[1]; maxd=int(sys.argv[2]) if len(sys.argv)>2 else 4
    if tgt.startswith('ff'):
        ci=int(tgt[2:]); s=SEQ[basename(cells[ci]['cell'])]
        print(f"ff{ci} D =",ex(cells[ci]['pins'][s['d']],0,maxd))
    else:
        print(tgt,"=",ex(list(ports[tgt])[0],0,maxd))

def explain(nets, maxd=3, seen=None):
    if seen is None: seen=set()
    out=[]
    todo=list(nets)
    while todo:
        n=todo.pop(0)
        if n in seen: continue
        seen.add(n)
        e=ex(n,0,maxd)
        out.append((n,e))
        import re
        for m in re.findall(r'\bn(\d+)\b', e):
            if int(m) not in seen: todo.append(int(m))
    return out
