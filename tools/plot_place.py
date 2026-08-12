import pickle,sys,collections
sys.path.insert(0,'tools')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from cells import COMB,SEQ,basename
nl=pickle.load(open('tools/puzzle_nl.pkl','rb'))
g=pickle.load(open('tools/puzzle.pkl','rb'))
W={}   # cell widths (um) from gds bbox
import gdstk
lib=gdstk.read_gds('puzzle.gds')
for c in lib.cells:
    if c.name.startswith('sky130'):
        bb=c.bounding_box(); W[c.name]=bb[1][0]-bb[0][0]
COLORS={'dfrtp':'#d62728','dfstp':'#ff9896','dfxtp':'#8c564b','mux2':'#1f77b4',
        'xor2':'#2ca02c','xnor2':'#98df8a','clkbuf':'#7f7f7f','conb':'#000000',
        'inv':'#9467bd','buf':'#9467bd','diode':'#cccccc'}
fig,ax=plt.subplots(figsize=(14,20))
lab=set()
for c in nl['cells']:
    b=basename(c['cell']); w=W.get(c['cell'],1.0)
    col=COLORS.get(b,'#ffbb78')
    x=c['x']-(w if c['rot'] else 0)
    ax.add_patch(Rectangle((x,c['y']-(2.72 if c['rot'] else 0)),w,2.72,facecolor=col,edgecolor='none'))
for b,col in COLORS.items(): ax.plot([],[],'s',color=col,label=b)
ax.plot([],[],'s',color='#ffbb78',label='other logic')
ax.set_xlim(0,200); ax.set_ylim(0,300); ax.set_aspect('equal'); ax.legend(loc='upper left',fontsize=8)
ax.set_title('puzzle.gds cell placement')
plt.savefig('tools/placement.png',dpi=110,bbox_inches='tight')
print('ok')
