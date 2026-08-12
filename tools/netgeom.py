import pickle,sys,collections
d=pickle.load(open('tools/puzzle.pkl','rb'))
netof=d['netof']; bb=d['shapebb']
LN=['li1','met1','met2','met3','met4','met5']
target=int(sys.argv[1])
rows=[(LN[bb[i][0]],bb[i][1],bb[i][2]) for i in range(len(bb)) if netof[i]==target]
print(f"net {target}: {len(rows)} shapes")
for r in sorted(rows): print("  ",r[0], tuple(v/1000 for v in r[1]), r[2] if r[2][0]!='inst' else ('inst',r[2][1],d['instances'][r[2][1]]['cell']))
