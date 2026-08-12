import pickle, sys, collections
sys.path.insert(0,'tools')
d=pickle.load(open('tools/puzzle.pkl','rb'))
nl=pickle.load(open('tools/puzzle_nl.pkl','rb'))
target=int(sys.argv[1])
# labels on that net
for text,(x,y),li,tag,net in d['labels']:
    if net==target: print("label",text,(x/1000,y/1000),"layer",li,"tag",tag, "cell", d['instances'][tag[1]]['cell'] if tag[0]=='inst' else '')
