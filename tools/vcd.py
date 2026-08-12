import re,sys
def parse(path):
    ids={}; cur={}; frames=[]
    body=False; t=None
    for line in open(path):
        line=line.strip()
        m=re.match(r'\$var\s+\w+\s+(\d+)\s+(\S+)\s+(\S+)',line)
        if m: ids[m.group(2)]=m.group(3); continue
        if line=='$enddefinitions $end': body=True; continue
        if not body: continue
        if line.startswith('#'):
            if t is not None: frames.append((t,dict(cur)))
            t=int(line[1:]); continue
        if line.startswith(('$','x')) or not line: continue
        if line[0] in 'bB':
            v,i=line[1:].split()
            cur[ids.get(i,i)]=v
        elif line[0] in '01xzXZ':
            cur[ids.get(line[1:],line[1:])]=line[0]
    if t is not None: frames.append((t,dict(cur)))
    return frames
if __name__=='__main__':
    fr=parse('example_inputs.vcd')
    print("frames",len(fr))
    seq=[]
    prev=None
    for t,st in fr:
        if st.get('clk')=='1' and (prev is None or prev.get('clk')!='1'):
            seq.append((t,st.get('rst_n'),st.get('enable'),st.get('I'),st.get('O'),st.get('success')))
        prev=st
    print("rising edges:",len(seq))
    for x in seq[:12]: print("  ",x)
    print("  ...")
    for x in seq[-6:]: print("  ",x)
    bits=[s[3] for s in seq if s[2]=='1' and s[1]=='1']
    print("bits fed while enable=1:",len(bits))
    print("".join(b if b in '01' else '?' for b in bits))
