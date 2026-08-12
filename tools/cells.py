"""sky130_fd_sc_hd cell functional models (combinational output funcs)."""
def _and(*a): 
    r=1
    for x in a: r&=x
    return r
def _or(*a):
    r=0
    for x in a: r|=x
    return r
N=lambda x: 1-x

# name(base, no _<drive>) -> (outputs dict {pin: lambda p:...})
COMB = {}
def d(name, **outs): COMB[name]=outs

d('inv',      Y=lambda p: N(p['A']))
d('buf',      X=lambda p: p['A'])
d('clkbuf',   X=lambda p: p['A'])
d('clkinv',   Y=lambda p: N(p['A']))
d('dlygate4sd3', X=lambda p: p['A'])
d('and2',     X=lambda p: _and(p['A'],p['B']))
d('and3',     X=lambda p: _and(p['A'],p['B'],p['C']))
d('and4',     X=lambda p: _and(p['A'],p['B'],p['C'],p['D']))
d('and2b',    X=lambda p: _and(N(p['A_N']),p['B']))
d('and3b',    X=lambda p: _and(N(p['A_N']),p['B'],p['C']))
d('and4b',    X=lambda p: _and(N(p['A_N']),p['B'],p['C'],p['D']))
d('and4bb',   X=lambda p: _and(N(p['A_N']),N(p['B_N']),p['C'],p['D']))
d('nand2',    Y=lambda p: N(_and(p['A'],p['B'])))
d('nand3',    Y=lambda p: N(_and(p['A'],p['B'],p['C'])))
d('nand4',    Y=lambda p: N(_and(p['A'],p['B'],p['C'],p['D'])))
d('nand2b',   Y=lambda p: N(_and(N(p['A_N']),p['B'])))
d('nand3b',   Y=lambda p: N(_and(N(p['A_N']),p['B'],p['C'])))
d('nand4b',   Y=lambda p: N(_and(N(p['A_N']),p['B'],p['C'],p['D'])))
d('nand4bb',  Y=lambda p: N(_and(N(p['A_N']),N(p['B_N']),p['C'],p['D'])))
d('or2',      X=lambda p: _or(p['A'],p['B']))
d('or3',      X=lambda p: _or(p['A'],p['B'],p['C']))
d('or4',      X=lambda p: _or(p['A'],p['B'],p['C'],p['D']))
d('or2b',     X=lambda p: _or(p['A'],N(p['B_N'])))
d('or3b',     X=lambda p: _or(p['A'],p['B'],N(p['C_N'])))
d('or4b',     X=lambda p: _or(p['A'],p['B'],p['C'],N(p['D_N'])))
d('or4bb',    X=lambda p: _or(p['A'],p['B'],N(p['C_N']),N(p['D_N'])))
d('nor2',     Y=lambda p: N(_or(p['A'],p['B'])))
d('nor3',     Y=lambda p: N(_or(p['A'],p['B'],p['C'])))
d('nor4',     Y=lambda p: N(_or(p['A'],p['B'],p['C'],p['D'])))
d('nor2b',    Y=lambda p: N(_or(p['A'],N(p['B_N']))))
d('nor3b',    Y=lambda p: N(_or(p['A'],p['B'],N(p['C_N']))))
d('nor4b',    Y=lambda p: N(_or(p['A'],p['B'],p['C'],N(p['D_N']))))
d('nor4bb',   Y=lambda p: N(_or(p['A'],p['B'],N(p['C_N']),N(p['D_N']))))
d('xor2',     X=lambda p: p['A']^p['B'])
d('xnor2',    Y=lambda p: N(p['A']^p['B']))
d('xor3',     X=lambda p: p['A']^p['B']^p['C'])
d('mux2',     X=lambda p: p['A1'] if p['S'] else p['A0'])
d('mux2i',    Y=lambda p: N(p['A1'] if p['S'] else p['A0']))
d('mux4',     X=lambda p: [p['A0'],p['A1'],p['A2'],p['A3']][p['S0']|(p['S1']<<1)])
d('conb',     HI=lambda p:1, LO=lambda p:0)
# AND-OR family:  aXY..o[i]
d('a21o',     X=lambda p: _or(_and(p['A1'],p['A2']),p['B1']))
d('a21oi',    Y=lambda p: N(_or(_and(p['A1'],p['A2']),p['B1'])))
d('a22o',     X=lambda p: _or(_and(p['A1'],p['A2']),_and(p['B1'],p['B2'])))
d('a22oi',    Y=lambda p: N(_or(_and(p['A1'],p['A2']),_and(p['B1'],p['B2']))))
d('a31o',     X=lambda p: _or(_and(p['A1'],p['A2'],p['A3']),p['B1']))
d('a31oi',    Y=lambda p: N(_or(_and(p['A1'],p['A2'],p['A3']),p['B1'])))
d('a32o',     X=lambda p: _or(_and(p['A1'],p['A2'],p['A3']),_and(p['B1'],p['B2'])))
d('a32oi',    Y=lambda p: N(_or(_and(p['A1'],p['A2'],p['A3']),_and(p['B1'],p['B2']))))
d('a41o',     X=lambda p: _or(_and(p['A1'],p['A2'],p['A3'],p['A4']),p['B1']))
d('a41oi',    Y=lambda p: N(_or(_and(p['A1'],p['A2'],p['A3'],p['A4']),p['B1'])))
d('a211o',    X=lambda p: _or(_and(p['A1'],p['A2']),p['B1'],p['C1']))
d('a211oi',   Y=lambda p: N(_or(_and(p['A1'],p['A2']),p['B1'],p['C1'])))
d('a221o',    X=lambda p: _or(_and(p['A1'],p['A2']),_and(p['B1'],p['B2']),p['C1']))
d('a221oi',   Y=lambda p: N(_or(_and(p['A1'],p['A2']),_and(p['B1'],p['B2']),p['C1'])))
d('a222oi',   Y=lambda p: N(_or(_and(p['A1'],p['A2']),_and(p['B1'],p['B2']),_and(p['C1'],p['C2']))))
d('a311o',    X=lambda p: _or(_and(p['A1'],p['A2'],p['A3']),p['B1'],p['C1']))
d('a311oi',   Y=lambda p: N(_or(_and(p['A1'],p['A2'],p['A3']),p['B1'],p['C1'])))
d('a321o',    X=lambda p: _or(_and(p['A1'],p['A2'],p['A3']),_and(p['B1'],p['B2']),p['C1']))
d('a2111o',   X=lambda p: _or(_and(p['A1'],p['A2']),p['B1'],p['C1'],p['D1']))
d('a2111oi',  Y=lambda p: N(_or(_and(p['A1'],p['A2']),p['B1'],p['C1'],p['D1'])))
d('a21bo',    X=lambda p: _or(_and(p['A1'],p['A2']),N(p['B1_N'])))
d('a21boi',   Y=lambda p: N(_or(_and(p['A1'],p['A2']),N(p['B1_N']))))
d('a22bo',    X=lambda p: _or(_and(p['A1'],p['A2']),_and(N(p['B1_N']),N(p['B2_N']))))
d('a2bb2o',   X=lambda p: _or(_and(N(p['A1_N']),N(p['A2_N'])),_and(p['B1'],p['B2'])))
d('a2bb2oi',  Y=lambda p: N(_or(_and(N(p['A1_N']),N(p['A2_N'])),_and(p['B1'],p['B2']))))
d('a31bo',    X=lambda p: _or(_and(p['A1'],p['A2'],p['A3']),N(p['B1_N'])))
# OR-AND family: oXY..a[i]
d('o21a',     X=lambda p: _and(_or(p['A1'],p['A2']),p['B1']))
d('o21ai',    Y=lambda p: N(_and(_or(p['A1'],p['A2']),p['B1'])))
d('o22a',     X=lambda p: _and(_or(p['A1'],p['A2']),_or(p['B1'],p['B2'])))
d('o22ai',    Y=lambda p: N(_and(_or(p['A1'],p['A2']),_or(p['B1'],p['B2']))))
d('o31a',     X=lambda p: _and(_or(p['A1'],p['A2'],p['A3']),p['B1']))
d('o31ai',    Y=lambda p: N(_and(_or(p['A1'],p['A2'],p['A3']),p['B1'])))
d('o32a',     X=lambda p: _and(_or(p['A1'],p['A2'],p['A3']),_or(p['B1'],p['B2'])))
d('o32ai',    Y=lambda p: N(_and(_or(p['A1'],p['A2'],p['A3']),_or(p['B1'],p['B2']))))
d('o41a',     X=lambda p: _and(_or(p['A1'],p['A2'],p['A3'],p['A4']),p['B1']))
d('o41ai',    Y=lambda p: N(_and(_or(p['A1'],p['A2'],p['A3'],p['A4']),p['B1'])))
d('o211a',    X=lambda p: _and(_or(p['A1'],p['A2']),p['B1'],p['C1']))
d('o211ai',   Y=lambda p: N(_and(_or(p['A1'],p['A2']),p['B1'],p['C1'])))
d('o221a',    X=lambda p: _and(_or(p['A1'],p['A2']),_or(p['B1'],p['B2']),p['C1']))
d('o221ai',   Y=lambda p: N(_and(_or(p['A1'],p['A2']),_or(p['B1'],p['B2']),p['C1'])))
d('o311a',    X=lambda p: _and(_or(p['A1'],p['A2'],p['A3']),p['B1'],p['C1']))
d('o311ai',   Y=lambda p: N(_and(_or(p['A1'],p['A2'],p['A3']),p['B1'],p['C1'])))
d('o2111a',   X=lambda p: _and(_or(p['A1'],p['A2']),p['B1'],p['C1'],p['D1']))
d('o2111ai',  Y=lambda p: N(_and(_or(p['A1'],p['A2']),p['B1'],p['C1'],p['D1'])))
d('o21ba',    X=lambda p: _and(_or(p['A1'],p['A2']),N(p['B1_N'])))
d('o21bai',   Y=lambda p: N(_and(_or(p['A1'],p['A2']),N(p['B1_N']))))
d('o22ba',    X=lambda p: _and(_or(p['A1'],p['A2']),_or(N(p['B1_N']),N(p['B2_N']))))
d('o2bb2a',   X=lambda p: _and(_or(N(p['A1_N']),N(p['A2_N'])),_or(p['B1'],p['B2'])))
d('o2bb2ai',  Y=lambda p: N(_and(_or(N(p['A1_N']),N(p['A2_N'])),_or(p['B1'],p['B2']))))
d('o31ba',    X=lambda p: _and(_or(p['A1'],p['A2'],p['A3']),N(p['B1_N'])))
d('maj3',     X=lambda p: 1 if (p['A']+p['B']+p['C'])>=2 else 0)
d('fa',       COUT=lambda p: 1 if (p['A']+p['B']+p['CIN'])>=2 else 0,
              SUM =lambda p: p['A']^p['B']^p['CIN'])
d('ha',       COUT=lambda p: _and(p['A'],p['B']), SUM=lambda p: p['A']^p['B'])

SEQ = {  # name -> (clkpin, dpin, qpins, async: (pin, activelevel, value))
 'dfxtp':  dict(clk='CLK', d='D', q=['Q']),
 'dfxbp':  dict(clk='CLK', d='D', q=['Q'], qn=['Q_N']),
 'dfrtp':  dict(clk='CLK', d='D', q=['Q'], rst=('RESET_B',0,0)),
 'dfrtn':  dict(clk='CLK_N', d='D', q=['Q'], rst=('RESET_B',0,0), negedge=True),
 'dfstp':  dict(clk='CLK', d='D', q=['Q'], rst=('SET_B',0,1)),
 'dfbbn':  dict(clk='CLK_N', d='D', q=['Q'], qn=['Q_N'], negedge=True),
 'dfrbp':  dict(clk='CLK', d='D', q=['Q'], qn=['Q_N'], rst=('RESET_B',0,0)),
 'dfsbp':  dict(clk='CLK', d='D', q=['Q'], qn=['Q_N'], rst=('SET_B',0,1)),
 'edfxtp': dict(clk='CLK', d='D', q=['Q'], en='DE'),
 'sdfxtp': dict(clk='CLK', d='D', q=['Q'], scan=('SCD','SCE')),
 'sdfrtp': dict(clk='CLK', d='D', q=['Q'], scan=('SCD','SCE'), rst=('RESET_B',0,0)),
}
NOFUNC = {'decap','tapvpwrvgnd','fill','diode','tap','fakediode'}

def basename(cellname):
    b = cellname.split('__')[-1]
    parts = b.rsplit('_',1)
    if len(parts)==2 and parts[1].isdigit(): b = parts[0]
    return b
