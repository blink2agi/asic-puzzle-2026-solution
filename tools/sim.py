"""Gate-level simulator over an extracted netlist."""
import pickle, collections, sys
sys.path.insert(0,'tools')
from cells import COMB, SEQ, NOFUNC, basename

class Sim:
    def __init__(self, nlpkl):
        d = pickle.load(open(nlpkl,'rb'))
        self.cells = d['cells']; self.ports = d['ports']
        self.VPWR, self.VGND = d['VPWR'], d['VGND']
        self.val = {}
        self.drivers = {}        # net -> (cellindex, outpin)
        self.comb = []; self.seq = []
        skipped = collections.Counter()
        for ci, c in enumerate(self.cells):
            b = basename(c['cell'])
            if b in NOFUNC: skipped[b]+=1; continue
            if b in COMB:
                self.comb.append(ci)
                for op in COMB[b]:
                    n = c['pins'].get(op)
                    if n is not None: self.drivers[n]=(ci,op)
            elif b in SEQ:
                self.seq.append(ci)
                s = SEQ[b]
                for op in s['q']+s.get('qn',[]):
                    n = c['pins'].get(op)
                    if n is not None: self.drivers[n]=(ci,op)
            else:
                raise SystemExit(f"UNKNOWN CELL {c['cell']} (base {b})")
        self.skipped = skipped
        self.byidx = {c['idx']: i for i,c in enumerate(self.cells)}
        self.order = self._toposort()
        self.state = {ci:0 for ci in self.seq}
        self.prevclk = {ci:0 for ci in self.seq}

    def _toposort(self):
        # dependency: comb cell depends on driver cells of its input nets (comb only)
        deps = {}
        for ci in self.comb:
            c = self.cells[ci]; outs = set(COMB[basename(c['cell'])])
            dd=set()
            for p,n in c['pins'].items():
                if p in outs: continue
                dr = self.drivers.get(n)
                if dr and dr[0] in set(self.comb): dd.add(dr[0])
            deps[ci]=dd
        combset=set(self.comb)
        for ci in deps: deps[ci] &= combset
        order=[]; state={}
        import sys as _s; _s.setrecursionlimit(100000)
        def visit(u, stack):
            st = state.get(u,0)
            if st==2: return
            if st==1: return   # combinational loop -> ignore back edge
            state[u]=1
            for v in deps[u]: visit(v, stack)
            state[u]=2; order.append(u)
        for ci in self.comb: visit(ci, [])
        return order

    def nv(self, n):
        if n == self.VPWR: return 1
        if n == self.VGND: return 0
        return self.val.get(n, 0)

    def propagate(self, iters=3):
        for _ in range(iters):
            changed=False
            for ci in self.order:
                c=self.cells[ci]; b=basename(c['cell']); fns=COMB[b]
                p = {pin: self.nv(n) for pin,n in c['pins'].items()}
                for op,f in fns.items():
                    n=c['pins'].get(op)
                    if n is None: continue
                    try: v=f(p)
                    except KeyError as e: raise SystemExit(f"cell {c['cell']} missing pin {e}; has {sorted(p)}")
                    if self.val.get(n)!=v: self.val[n]=v; changed=True
            # sequential outputs (state + async)
            for ci in self.seq:
                c=self.cells[ci]; s=SEQ[basename(c['cell'])]
                if 'rst' in s:
                    rp,lvl,rv = s['rst']
                    if self.nv(c['pins'][rp])==lvl: self.state[ci]=rv
                for op in s['q']:
                    n=c['pins'].get(op)
                    if n is not None and self.val.get(n)!=self.state[ci]:
                        self.val[n]=self.state[ci]; changed=True
                for op in s.get('qn',[]):
                    n=c['pins'].get(op)
                    if n is not None and self.val.get(n)!=1-self.state[ci]:
                        self.val[n]=1-self.state[ci]; changed=True
            if not changed: return
    def setport(self, name, v):
        for n in self.ports[name]:
            if n is not None: self.val[n]=v
    def getport(self, name):
        ns=[n for n in self.ports[name] if n is not None]
        return self.nv(ns[0]) if ns else None

    def clock(self):
        """one full clock cycle: low then high edge"""
        self.setport('clk',0); self.propagate()
        for ci in self.seq: self.prevclk[ci]=self.nv(self.cells[ci]['pins'][SEQ[basename(self.cells[ci]['cell'])]['clk']])
        d = {}
        for ci in self.seq:
            c=self.cells[ci]; s=SEQ[basename(c['cell'])]
            dv = self.nv(c['pins'][s['d']])
            if 'en' in s and not self.nv(c['pins'][s['en']]): dv=self.state[ci]
            if 'scan' in s and self.nv(c['pins'][s['scan'][1]]): dv=self.nv(c['pins'][s['scan'][0]])
            d[ci]=dv
        self.setport('clk',1); self.propagate()
        for ci in self.seq:
            c=self.cells[ci]; s=SEQ[basename(c['cell'])]
            cur=self.nv(c['pins'][s['clk']])
            neg = s.get('negedge',False)
            edge = (self.prevclk[ci]==1 and cur==0) if neg else (self.prevclk[ci]==0 and cur==1)
            if edge: self.state[ci]=d[ci]
        self.propagate()

if __name__=='__main__':
    s=Sim(sys.argv[1] if len(sys.argv)>1 else 'tools/warmup_nl.pkl')
    print("comb",len(s.comb),"seq",len(s.seq),"skipped",dict(s.skipped))
    print("ports",sorted(s.ports))
