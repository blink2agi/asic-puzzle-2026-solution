"""Extract a netlist from puzzle.gds by geometric connectivity extraction."""
import gdstk, collections, math, pickle, sys
from shapely.geometry import Polygon, box
from shapely.strtree import STRtree

GDS = sys.argv[1] if len(sys.argv) > 1 else 'puzzle.gds'
TOPNAME = sys.argv[2] if len(sys.argv) > 2 else None
OUT = sys.argv[3] if len(sys.argv) > 3 else 'tools/extracted.pkl'

# sky130 layer map
LI1, MET1, MET2, MET3, MET4, MET5 = (67,20),(68,20),(69,20),(70,20),(71,20),(72,20)
ROUTE = [LI1, MET1, MET2, MET3, MET4, MET5]
ROUTE_NAME = ['li1','met1','met2','met3','met4','met5']
PINPURPOSE = {(67,16):LI1,(68,16):MET1,(69,16):MET2,(70,16):MET3,(71,16):MET4,(72,16):MET5}
# cut layer -> (lower route idx, upper route idx)
CUTS = {(67,44):(0,1), (68,44):(1,2), (69,44):(2,3), (70,44):(3,4), (71,44):(4,5)}
LABEL_LAYERS = {(67,5):0,(68,5):1,(69,5):2,(70,5):3,(71,5):4,(72,5):5}

lib = gdstk.read_gds(GDS)
byname = {c.name: c for c in lib.cells}
top = byname[TOPNAME] if TOPNAME else lib.top_level()[0]
print('top cell:', top.name)

def xform(origin, rotation, x_reflection, magnification):
    m = magnification if magnification else 1.0
    c, s = math.cos(rotation or 0.0), math.sin(rotation or 0.0)
    ox, oy = origin
    def f(pt):
        x, y = pt[0]*m, pt[1]*m
        if x_reflection: y = -y
        return (x*c - y*s + ox, x*s + y*c + oy)
    return f

def compose(f, g):   # apply g then f
    return lambda pt: f(g(pt))

IDENT = lambda pt: (pt[0], pt[1])

# ---- collect flat geometry -------------------------------------------------
shapes = collections.defaultdict(list)   # layerkey -> list of (coords, tag)
cutshapes = collections.defaultdict(list)
labels = []   # (text, (x,y), layeridx, tag)

def add_poly(lk, pts, tag):
    coords = [(round(x*1000), round(y*1000)) for (x, y) in pts]
    if lk in CUTS:
        cutshapes[lk].append((coords, tag))
    else:
        if lk in PINPURPOSE: lk = PINPURPOSE[lk]
        if lk in ROUTE: shapes[lk].append((coords, tag))

def walk(cell, tf, tag, depth=0):
    for p in cell.polygons:
        lk = (p.layer, p.datatype)
        if lk in CUTS or lk in ROUTE or lk in PINPURPOSE:
            add_poly(lk, [tf(pt) for pt in p.points], tag)
    for pth in cell.paths:
        lk = (pth.layers[0], pth.datatypes[0])
        if lk in CUTS or lk in ROUTE or lk in PINPURPOSE:
            for poly in pth.to_polygons():
                add_poly(lk, [tf(pt) for pt in poly.points], tag)
    for l in cell.labels:
        lk = (l.layer, l.texttype)
        if lk in LABEL_LAYERS:
            x, y = tf(l.origin)
            labels.append((l.text, (round(x*1000), round(y*1000)), LABEL_LAYERS[lk], tag))
    for r in cell.references:
        base = xform(r.origin, r.rotation, r.x_reflection, r.magnification)
        offsets = [(0.0, 0.0)]
        if r.repetition is not None and r.repetition.size:
            offsets = list(r.repetition.offsets)
        for k, off in enumerate(offsets):
            f = compose(lambda pt, o=off: (pt[0]+o[0], pt[1]+o[1]), base)
            f2 = compose(tf, f)
            if r.cell.name.startswith('sky130_') or r.cell.name.startswith('INTERNAL'):
                ntag = ('inst', len(instances))
                ox, oy = f2((0.0, 0.0))
                instances.append(dict(cell=r.cell.name, x=ox, y=oy,
                                      rot=r.rotation or 0.0, mx=bool(r.x_reflection)))
            else:
                ntag = tag
            walk(r.cell, f2, ntag, depth+1)

instances = []
walk(top, IDENT, ('top', 0))
print("instances:", len(instances))
for lk in ROUTE: print("  ", lk, len(shapes[lk]))
for lk in CUTS: print("  cut", lk, len(cutshapes[lk]))
print("  labels", len(labels))

# ---- union-find over shapes ------------------------------------------------
allsh = []   # (layeridx, shapely geom, tag)
index_by_layer = collections.defaultdict(list)
for li, lk in enumerate(ROUTE):
    for coords, tag in shapes[lk]:
        g = Polygon(coords)
        if not g.is_valid: g = g.buffer(0)
        if g.is_empty: continue
        index_by_layer[li].append(len(allsh))
        allsh.append((li, g, tag))

parent = list(range(len(allsh)))
def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[ra] = rb

trees = {}
for li, idxs in index_by_layer.items():
    geoms = [allsh[i][1] for i in idxs]
    trees[li] = (STRtree(geoms), idxs)
    print(f"  layer {ROUTE_NAME[li]}: {len(idxs)} shapes")

# same-layer merges
for li, (tree, idxs) in trees.items():
    for k, i in enumerate(idxs):
        g = allsh[i][1]
        for j in tree.query(g):
            if idxs[j] != i and g.intersects(allsh[idxs[j]][1]):
                union(i, idxs[j])

# cross-layer via merges
for lk, (lo, hi) in CUTS.items():
    for coords, tag in cutshapes[lk]:
        g = Polygon(coords)
        hits = []
        for li in (lo, hi):
            if li not in trees: continue
            tree, idxs = trees[li]
            for j in tree.query(g):
                if g.intersects(allsh[idxs[j]][1]): hits.append(idxs[j])
        for h in hits[1:]: union(hits[0], h)

nets = collections.defaultdict(list)
for i in range(len(allsh)): nets[find(i)].append(i)
print("distinct nets:", len(nets))

# ---- assign labels to nets -------------------------------------------------
from shapely.geometry import Point
labelnet = []
for text, (x, y), li, tag in labels:
    p = Point(x, y)
    found = None
    if li in trees:
        tree, idxs = trees[li]
        for j in tree.query(p):
            if allsh[idxs[j]][1].intersects(p): found = find(idxs[j]); break
    labelnet.append((text, (x,y), li, tag, found))

with open(OUT,'wb') as f:
    pickle.dump(dict(instances=instances, labels=labelnet,
                     shapebb=[(li, tuple(int(v) for v in g.bounds), tag) for li,g,tag in allsh],
                     netof={i: find(i) for i in range(len(allsh))},
                     shapetags=[(li,tag) for li,g,tag in allsh]), f)
print("saved", OUT)
