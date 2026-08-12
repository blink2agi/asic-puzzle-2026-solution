import sys; sys.path.insert(0,'tools')
from sim import Sim
s=Sim('tools/warmup_nl.pkl')
def run(a,b):
    s.val.clear(); s.state={ci:0 for ci in s.seq}
    s.setport('rst_n',0); s.setport('en',0); s.setport('A',0); s.setport('B',0); s.clock()
    s.setport('rst_n',1); s.setport('en',1)
    for i in range(7,-1,-1):
        s.setport('A',(a>>i)&1); s.setport('B',(b>>i)&1); s.clock()
    s.setport('en',0); s.clock()
    return s.getport('S')
bad=0
import random
tests=[(248,248),(255,241),(0,0),(240,0),(200,296&255),(100,150),(255,255),(1,495&255),(496-255,255)]
for a,b in tests:
    got=run(a,b); exp=1 if a+b==496 else 0
    st='OK ' if got==exp else 'FAIL'
    if got!=exp: bad+=1
    print(f"{st} A={a:3d} B={b:3d} sum={a+b:4d} S={got} exp={exp}")
random.seed(1)
for _ in range(300):
    a=random.randint(0,255); b=random.randint(0,255)
    if random.random()<0.3: a=random.randint(241,255); b=496-a
    got=run(a,b); exp=1 if a+b==496 else 0
    if got!=exp: bad+=1; print("FAIL",a,b,got,exp)
print("random 300 done; failures:",bad)
