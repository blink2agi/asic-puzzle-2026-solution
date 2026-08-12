import gdstk
lib=gdstk.read_gds('puzzle.gds')
top=[c for c in lib.cells if c.name=='puzzle'][0]
W={'INTERNAL_3':1.38,'INTERNAL_7':4.14}
bars=sorted((r.origin[0], W[r.cell.name]) for r in top.references if r.cell.name in W)
U=1.38
out=[]; 
for i,(x,w) in enumerate(bars):
    out.append('.' if round(w/U)==1 else '-')
    if i+1<len(bars):
        gap=round((bars[i+1][0]-(x+w))/U)
        if gap>=7: out.append('  / ')
        elif gap>=3: out.append(' ')
print("bars:",len(bars))
print("units:",[(round(x/U,2),round(w/U)) for x,w in bars][:8],"...")
msg=''.join(out)
print("MORSE:",msg)
M={'.-':'A','-...':'B','-.-.':'C','-..':'D','.':'E','..-.':'F','--.':'G','....':'H','..':'I',
'.---':'J','-.-':'K','.-..':'L','--':'M','-.':'N','---':'O','.--.':'P','--.-':'Q','.-.':'R',
'...':'S','-':'T','..-':'U','...-':'V','.--':'W','-..-':'X','-.--':'Y','--..':'Z',
'-----':'0','.----':'1','..---':'2','...--':'3','....-':'4','.....':'5','-....':'6',
'--...':'7','---..':'8','----.':'9','.-.-.-':'.','--..--':',','..--..':'?','-..-.':'/','-....-':'-'}
words=[w for w in msg.split('  / ')]
print("DECODED:", ' '.join(''.join(M.get(c,'?'+c+'?') for c in w.split(' ') if c) for w in words))
