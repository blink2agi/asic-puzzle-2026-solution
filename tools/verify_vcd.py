import sys; sys.path.insert(0,'tools')
from sim import Sim
from vcd import parse
fr=parse('example_inputs.vcd'); seq=[]; prev=None
for t,st in fr:
    if st.get('clk')=='1' and (prev is None or prev.get('clk')!='1'):
        o=st.get('O','0'); 
        seq.append((st.get('rst_n'),st.get('enable'),st.get('I'), 0 if o in('x','0') else int(o,2),
                    0 if st.get('success') in ('x',None) else int(st.get('success'))))
    prev=st
s=Sim('tools/puzzle_nl.pkl')
s.val.clear(); s.state={ci:0 for ci in s.seq}
mis=0; checked=0
for i,(rn,en,I,Oexp,Sexp) in enumerate(seq):
    s.setport('rst_n',int(rn)); s.setport('enable',int(en)); s.setport('I',int(I)); s.clock()
    O=sum(s.getport(f'O[{k}]')<<k for k in range(8)); S=s.getport('success')
    checked+=1
    if O!=Oexp or S!=Sexp:
        mis+=1
        if mis<8: print(f"  MISMATCH cyc {i}: O got {O} exp {Oexp} | success got {S} exp {Sexp}")
print(f"compared {checked} clock cycles against example_inputs.vcd -> mismatches: {mis}")
