import pickle,collections,sys
sys.path.insert(0,'tools')
from cells import COMB,SEQ,basename
nl=pickle.load(open('tools/puzzle_nl.pkl','rb'))
drv={}
for c in nl['cells']:
    b=basename(c['cell']); outs=set(COMB.get(b,{}))
    if b in SEQ: outs=set(SEQ[b]['q'])|set(SEQ[b].get('qn',[]))
    for p,n in c['pins'].items():
        if p in outs: drv[n]=(c['idx'],c['cell'],p)
cnt=collections.Counter()
for c in nl['cells']:
    b=basename(c['cell'])
    if b in SEQ:
        n=c['pins'][SEQ[b]['clk']]
        cnt[drv.get(n,('PORT',str(n),''))[1]]+=1
print("FF clock sources:",dict(cnt))
# who drives clkbuf inputs
for c in nl['cells']:
    if basename(c['cell']).startswith('clkbuf'):
        src=drv.get(c['pins']['A'],('port?',nl['netnames'].get(c['pins']['A'],c['pins']['A']),''))
        print(f"  {c['cell']:28s} @({c['x']:7.2f},{c['y']:7.2f}) A<-{src[1]}  X net {c['pins']['X']}")
