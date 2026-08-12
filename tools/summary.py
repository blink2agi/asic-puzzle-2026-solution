import sys; sys.path.insert(0,'tools')
GRID="""DDDDDJJABBI
DDFDDJAABBI
DDFJJJJAABI
DDFJEEEIAAI
FDFJEIIIIII
FFFJEEEIHHH
JJJJJJEIHKK
JCCCEEEIHKK
JCCGIIIIHKK
JJCGGIIIHHH
JCCGIIIIIII"""
BITS=open('tools/sol.txt').read().strip()
R=[list(l) for l in GRID.split('\n')]
print("Star Battle 11x11  —  2 stars per row, column and region; stars may not touch (incl. diagonally)\n")
print("    region map                      solution")
print("    " + "  ".join([""]))
for r in range(11):
    left=' '.join(R[r])
    right=' '.join('*' if BITS[r*11+c]=='1' else '.' for c in range(11))
    print(f"   {left}    {right}")
print("\ninput bit stream (121 bits, row-major, MSB=first row/first column, one bit per clock with enable=1):")
for r in range(11): print("   "+BITS[r*11:(r+1)*11])
print("\nflat:",BITS)
print("hex :",hex(int(BITS,2)))
