import gdstk, collections
lib=gdstk.read_gds('puzzle.gds')
top=[c for c in lib.cells if c.name=='puzzle'][0]
print("=== geometry with y<0 (below die) ===")
cnt=collections.Counter()
bb=collections.defaultdict(lambda:[1e9,1e9,-1e9,-1e9])
for p in top.polygons:
    ys=[pt[1] for pt in p.points]
    if min(ys)<0:
        k=(p.layer,p.datatype); cnt[k]+=1
        xs=[pt[0] for pt in p.points]
        b=bb[k]; b[0]=min(b[0],min(xs)); b[1]=min(b[1],min(ys)); b[2]=max(b[2],max(xs)); b[3]=max(b[3],max(ys))
for pth in top.paths:
    for p in pth.to_polygons():
        ys=[pt[1] for pt in p.points]
        if min(ys)<0:
            k=(pth.layers[0],pth.datatypes[0]); cnt[k]+=1
            xs=[pt[0] for pt in p.points]
            b=bb[k]; b[0]=min(b[0],min(xs)); b[1]=min(b[1],min(ys)); b[2]=max(b[2],max(xs)); b[3]=max(b[3],max(ys))
for r in top.references:
    o=r.origin
    if o[1]<0: cnt[('REF',r.cell.name)]+=1
for k,v in cnt.items(): print("  ",k,v, [round(x,2) for x in bb[k]] if k in bb else '')
print("\n=== layer 235/4 poly in top ===")
for p in top.polygons:
    if (p.layer,p.datatype)==(235,4): print("   bbox", p.bounding_box(), "pts",len(p.points))
print("\n=== INTERNAL cells (layer 200/0) ===")
for n in ('INTERNAL_3','INTERNAL_7'):
    c=[x for x in lib.cells if x.name==n][0]
    for p in c.polygons: print(f"  {n}: layer {p.layer}/{p.datatype} pts={len(p.points)} bbox={p.bounding_box()}")
locs=[(r.origin, r.cell.name) for r in top.references if r.cell.name.startswith('INTERNAL')]
print("  INTERNAL placements:", sorted(set((round(o[0],2),round(o[1],2),n) for o,n in locs))[:60])
