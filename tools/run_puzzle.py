import sys; sys.path.insert(0,'tools')
from sim import Sim
BITS_DEFAULT="0000000101010000100000000000010101010000000000001010000001000001000000100000101000010000000100000010000010010001010000000"
def run(sim, bits, trace=False):
    sim.val.clear(); sim.state={ci:0 for ci in sim.seq}
    sim.setport('rst_n',0); sim.setport('enable',0); sim.setport('I',0)
    for _ in range(3): sim.clock()
    sim.setport('rst_n',1); sim.clock()
    sim.setport('enable',1)
    outs=[]
    for i,b in enumerate(bits):
        sim.setport('I',int(b)); sim.clock()
        outs.append((sim.getport('success'), tuple(sim.getport(f'O[{k}]') for k in range(8))))
    sim.setport('enable',0); sim.setport('I',0)
    for _ in range(3): sim.clock()
    return sim.getport('success'), outs
if __name__=='__main__':
    bits=sys.argv[1] if len(sys.argv)>1 else BITS_DEFAULT
    s=Sim('tools/puzzle_nl.pkl')
    print("bits len",len(bits))
    ok,outs=run(s,bits)
    print("SUCCESS =",ok)
    o=[sum(v[1][k]<<k for k in range(8)) for v in outs]
    print("final O =",o[-1], repr(chr(o[-1])) if 32<=o[-1]<127 else '')
