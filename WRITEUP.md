# Reverse-engineering the Jane Street ASIC puzzle

**Answer: `(* TWO STARS *)`**

The chip is an 11×11 Star Battle solution checker. What follows is how I got there, including
the parts that didn't work.

---

## Opening the file

The first thing I did was check how much of a hole I was in. A GDS with nothing but polygons
means device-level extraction: find the diffusion, find the poly crossings, work out which
transistors are in series and which are in parallel, recover a boolean function per cell, and
only *then* start on connectivity. That's a weekend.

I didn't need to. `puzzle.gds` has 81 structures and they're named:

```
sky130_fd_sc_hd__dfrtp_2       84 instances
sky130_fd_sc_hd__nor2_2        49
sky130_fd_sc_hd__nand2_2       39
...
```

The standard cell hierarchy survived. So did the pin labels — every cell carries `A`, `B`, `Y`,
`VPWR` and so on as text on the li1 and met1 label layers, positioned on the actual pin shape.
What got stripped, per the README, is "many internal names": instance names, net names, and
therefore any indication of which piece of routing belongs to which signal.

That reframes the problem completely. I didn't need to know what a `nand2` does — I know what a
`nand2` does. I needed to know **which wire goes where**, and that information only exists as
geometry.

## Building a net extractor

Sky130 routes on li1 and met1 through met5, with cut layers between them (mcon from li1 to met1,
then via, via2, via3, via4). Connectivity is mechanical:

- two shapes on the same layer are the same net if they overlap or touch;
- two shapes on adjacent layers are the same net if a cut sits between them.

So: flatten the whole design into absolute coordinates, keeping track of which instance each
shape came from, and run union-find.

I used `gdstk` to read the GDS and `shapely` with an STRtree for the geometry. Working in
integer nanometres rather than floating-point microns, so that "touching" is exact and I don't
have to think about epsilon. The whole thing is about 150 lines
([`tools/extract.py`](tools/extract.py)).

One decision worth explaining: I flattened the *interiors* of the standard cells too, not just
their pin shapes. It's tempting to treat each cell as a black box with terminals at the label
coordinates, but top-level routing doesn't necessarily land on the label — it lands on some
other part of the same li1 shape, via an mcon placed anywhere along it. Pulling in the cell
interiors means a cell's internal li1 geometry stitches its own pin together automatically, and
the only cost is some harmless extra nets for internal source/drain nodes that go nowhere.

Numbers for the real design: ~49,000 polygons in, 2,626 nets out. Then dropping each instance's
pin labels onto the net beneath them gives the netlist. **738 cells, 92 flip-flops.**

## Proving the extraction before trusting it

This is the part I'd insist on for any teardown. A netlist that's 99% right is worse than
useless, because you'll spend hours reasoning carefully about a wrong circuit.

**First check.** The repo ships a warm-up: a small design with its original Verilog, its
synthesized netlist, its DEF, and its final GDS — the whole flow, so you can develop against
ground truth. I ran my extractor over `warmup/04_final.gds`, wrote a gate-level simulator, and
tested it against the documented behaviour (`A + B == 496`). 309 vectors, no failures. So the
geometry pipeline works and my sky130 cell models are right, at least for the cells the warm-up
uses.

**Second check, the one that mattered.** `example_inputs.vcd` isn't just stimulus — it also
records what the real chip *did*. I replayed its 312 clock cycles through my simulated netlist
and compared `O[7:0]` and `success` on every single cycle:

```
compared 312 clock cycles against example_inputs.vcd -> mismatches: 0
```

Including the `TRY AGAIN` the reference chip prints for those (deliberately wrong) inputs. That
covers the combinational logic, the flops, the clock tree, the reset behaviour *and* the output
generator. After that I never had to wonder whether a surprising result was a real feature or my
own bug.

Some sanity checks fell out of the extraction itself, and each one had to be chased down:

- **Zero multi-driver nets.** Good — a short would have meant a merge that shouldn't have happened.
- **Exactly one undriven input pin.** Suspicious. More on that below.
- **All fifteen `clkbuf_4` outputs unused.** This looked exactly like a systematic extraction
  bug — some via type I wasn't handling. I dumped the geometry of one and found its output li1
  shape sitting entirely inside the cell with no top-level routing on it at all. They're just
  spare buffers hanging off the clock tree, driving nothing. The 92 flops are all clocked from
  `clkbuf_8` cells, one level up.

## Problems along the way

Not everything was smooth, and some of these cost more time than the actual reverse-engineering.

**The minimizer was hopeless.** My plan for reading the logic was: enumerate each flop's support
set, build a truth table, run Quine–McCluskey, print a minimal sum-of-products. I wired it up to
sympy's `SOPform` and it didn't finish a single flop in two minutes. I threw it away and wrote a
dumb recursive expression printer instead — walk back from the D pin, substitute each gate's
boolean template, stop at flop outputs and ports. Unminimized nested expressions, which sounds
worse and was actually much better: the structure of the synthesized logic is *visible* in the
nesting, and simplifying by hand takes seconds because the terms repeat.

**Naming a file `struct.py`.** It shadowed the stdlib module, `pickle` imports `struct`, and I
got a circular-import error that had nothing to do with anything. Renamed it. Classic.

**Simulator state keyed by the wrong index.** My `Sim` class enumerated cells into a list and
keyed flop state by list position, while every note I'd taken referred to cells by their
original instance index. Fine until I tried to force internal state to probe the output
generator, at which point I was setting the state of entirely unrelated flip-flops. Added an
explicit `byidx` map.

**Trying to brute-force the output generator from the inside.** I wanted every message the chip
can print, so I forced all 256 states of the eight flops that feed it and ran it forward. Every
seed produced the same string. The reason is that those flops are *loaded* from the result flags
by a one-shot pulse when the done-flag rises, so whatever I forced got overwritten immediately.
The fix was to stop being clever and drive the thing from real inputs — construct grids with the
properties I wanted and see what came out.

**The layout hint, which I never cracked.** The puzzle says the circuit is physically arranged to
hint at its functionality. I plotted cell placement coloured by type; rendered the shape of the
non-filler cells alone; built an 11×11 density heatmap of the die and compared it against the
region map; clustered the placement into blobs and compared blob centroids against region
centroids; rendered met4 and met5 on their own in case the global routing drew something. All
dead ends. What I *did* get from the layout is real but modest: the design breaks into obvious
functional islands, there are eleven repeated slices stacked in a column and another eleven
elsewhere, and the "output generator" box in the README's annotated image told me which 228 cells
I could ignore. I got to the answer from the netlist. If there's a nicer visual tell, I missed it.

## Reading the machine

With a trustworthy netlist, the method is: derive a next-state expression per flop, and look for
structure.

**The counters.** Two groups of four flops each turn out to be plain binary up-counters. Writing
`EN` for `enable & !done`:

```
Q800_next = (Q800 ^ EN)                    & !DEC     bit 0
Q867_next = (Q867 ^ (Q800 & EN))           & !(EN&DEC) bit 1
Q797_next =  Q797 ^ (Q867 & Q800 & EN)                bit 2
Q799_next = (Q799 ^ (Q797&Q867&Q800&EN))   & !(EN&DEC) bit 3
```

and the decode `DEC` that resets them is `!b0 & b1 & !b2 & b3` — binary 1010, decimal 10. So it
counts 0…10 and wraps: **eleven states.** The second group is identical but ticks once per wrap
of the first, and also runs 0…10. A sticky done-flag fires when both are at 10, which is the
121st clock, and gates `enable` off from that point.

11 × 11, fed one bit per clock, row by row. That's the shape of the input.

**The adjacency check.** There's a twelve-deep shift register hanging off `I`. A sticky flag is
set by:

```
Q946_next = ( I & EN & (  (delay1  & col != 0)
                        | (delay10 & col != 10)
                        |  delay11
                        | (delay12 & col != 0) ) ) | Q946
```

In a row-major grid eleven wide, delay 11 is the cell directly above, delay 10 is above-right,
delay 12 is above-left, and delay 1 is to the left. Four of the eight neighbours — exactly the
set you need if each adjacent pair is only to be counted once — and the guards mask them at the
row edges. This is a "no two marks touching, diagonals included" checker and it can't be
anything else. This was the moment the puzzle identified itself.

**The 2-bit saturating counters.** Twenty-two pairs of flops, each pair looking like:

```
a_next = (b | !P) if a else P
b_next = b | (P & a)
```

Hand-simulating from reset gives the encoding `(a,b)`: `00`→0, `10`→1, `01`→2, `11`→3 and stuck.
A saturating count in a Gray-ish code. Each pair's increment condition `P` is gated differently:
eleven of them by a decode of the column index, eleven by a decode of *both* indices — i.e.
region membership. The success condition demands every one of them read `01`, which is exactly 2.

Rows are handled differently and more cleverly: a single 2-bit counter that's cleared at the end
of every row, with its own sticky violation flag that fires unless the count lands on exactly 2
as the row closes. Same guarantee for eleven rows, at the cost of three flops instead of
twenty-two. Rows are sequential in time, so you don't need to store them in parallel.

There's also an 8-bit ripple counter over every set bit in the grid, compared against 22.
Redundant given the row checks, but a nice belt-and-braces.

**The success condition**, once expanded, is:

```
success = !adjacency_violation
        & !row_count_violation
        & (popcount == 22)
        & all 22 column/region counters == 2
```

Two per row, two per column, two per region, nothing touching. **Star Battle** — also known, and
this becomes relevant later, as *Two Not Touch*.

## Getting the region map out

The eleven region counters share one combinational decoder driven by the row and column indices.
Rather than read it, I made it executable: build the cone of logic behind one region counter's D
input as a callable, pin `I=1`, `enable=1`, `done=0`, set the counter's own state to zero, then
sweep the eight counter bits across all 121 (row, col) pairs and record where it fires.

That prints the region map directly:

```
D D D D D J J A B B I
D D F D D J A A B B I
D D F J J J J A A B I
D D F J E E E I A A I
F D F J E I I I I I I
F F F J E E E I H H H
J J J J J J E I H K K
J C C C E E E I H K K
J C C G I I I I H K K
J J C G G I I I H H H
J C C G I I I I I I I
```

Two things made me believe it. It partitions the grid exactly — 121 cells, no overlaps, no gaps
— and all eleven regions are orthogonally connected, which is a property of a real puzzle and not
something a mis-modelled gate would hand you by accident. The same sweep run on the other eleven
counters confirms each covers exactly one full column, which is a free check on the whole method.

## Solving it

Backtracking over rows, choosing two columns per row, pruned by column counts, region counts and
the no-touching rule. It runs instantly and the solution is unique:

```
. . . . . . . ★ . ★ .
★ . . . . ★ . . . . .
. . . . . . . ★ . ★ .
★ . ★ . . . . . . . .
. . . . ★ . ★ . . . .
. . ★ . . . . . ★ . .
. . . . ★ . . . . . ★
. ★ . . . . ★ . . . .
. . . ★ . . . . . . ★
. . . . . ★ . . ★ . .
. ★ . ★ . . . . . . .
```

As a bit stream, row 0 first, left to right:

```
0000000101010000100000000000010101010000000000001010000001000001
000000100000101000010000000100000010000010010001010000000
```

Toggle `rst_n`, raise `enable`, clock those 121 bits into `I`. `success` goes high, and `O[7:0]`
clocks out one ASCII byte per cycle:

```
0x28 0x2a 0x20 0x54 0x57 0x4f 0x20 0x53 0x54 0x41 0x52 0x53 0x20 0x2a 0x29
 (    *        T    W    O         S    T    A    R    S         *    )
```

**`(* TWO STARS *)`** — wrapped in OCaml comment syntax, which is about as clear a signature as a
chip can leave.

## The output generator has opinions

The README says one section generates the output and doesn't affect `success`, and you can ignore
it for the reverse-engineering. True, but it's the most characterful part of the design. Driving
it with different classes of grid turns up five distinct messages:

| input grid | `success` | prints |
|---|---|---|
| the unique solution | high | `(* TWO STARS *)` |
| 2 per row/column/region, but two stars touch | low | `TWO NOT TOUCH` |
| all 121 cells set | low | `BIG BANG` |
| all 121 cells clear | low | `EMPTY SKY` |
| anything else | low | `TRY AGAIN` |

Get the counts right and the spacing wrong and the chip tells you the name of the puzzle you're
solving. That's a lovely piece of design.

## The Morse code under the die

The top cell's bounding box is `((0, -52.72), (200, 300))`. The die is 200 × 300. Something is
sitting fifty microns *below* the design.

Thirty-six boxes, on layer 200/0, which nothing else in the file uses. Two widths: 1.38 µm and
4.14 µm — a 1:3 ratio. Measuring the gaps gives 1, 3 and 7 units. Dot, dash, intra-character,
inter-character, word.

```
.--. . .-.  /  .- .-. . -. .- --  /  .- -..  /  .- ... - .-. .-
```

**`PER ARENAM AD ASTRA`** — "through sand, to the stars." A play on *per aspera ad astra*, with
the silicon substituted in. Best easter egg I've found in a puzzle in a long time.

## Smaller finds

`example_inputs.vcd` is dated `Sat Dec 31 23:59:60 2016`. Second sixty is not a typo — that night
carried a leap second.

Fifteen `clkbuf_4` cells sit in the clock tree with their outputs connected to nothing.

And one that I'm fairly sure wasn't intended. There is a genuinely **undriven net** in the output
generator: an input shared by an `a31oi_2` and an `a311o_2` at roughly x=177.5 µm, y=91 µm is
routed between those two gates and to no driver at all. I did not want to believe this was the
chip's fault rather than mine, so I checked the full inventory of via cell types in the file
(all of them use cut layers I handle), listed every layer/datatype present in the entire GDS
(no routing layer I'd overlooked), and dumped every shape of any kind overlapping the stub — just
met4/met5 power crossing over it without vias. The net dangles.

It has a visible consequence. It corrupts one character of `TWO NOT TOUCH`: the space becomes `"`
if the node settles low, and the final `H` becomes `J` if it settles high. Every other message is
immune, and `success` is unaffected either way — which is consistent with the README's note that
this section doesn't feed `success`. Given the cycle-exact VCD match, I'm confident this is in the
silicon and not in my reading of it.

## The toolchain

Everything is Python. Dependencies are `gdstk`, `shapely`, and `matplotlib` for the placement
plots.

```
python tools/extract.py puzzle.gds "" tools/puzzle.pkl   # geometry -> nets
python tools/netlist.py tools/puzzle.pkl                 # nets + pin labels -> netlist
python tools/verify_vcd.py                               # 312/312 cycles vs example_inputs.vcd
python tools/run_puzzle.py                               # feed the solution -> SUCCESS = 1
```

| file | what it does |
|---|---|
| `extract.py` | flattens li1/met1–met5 and the cut layers, union-finds shapes into nets |
| `netlist.py` | maps pin labels onto nets, identifies power rails and ports |
| `cells.py` | functional models for the sky130_fd_sc_hd cells in the design |
| `sim.py` | levelized gate-level simulator; async set/reset, clock-tree aware |
| `cone.py` | prints the logic cone behind any net or flop D input as an expression |
| `ffeq.py` | builds evaluable truth tables for next-state logic |
| `regions.py` | sweeps the decoders over all (row, col) pairs to recover the region map |
| `solve.py`, `solve2.py` | Star Battle solver; `solve2` also proves uniqueness |
| `messages.py` | enumerates every string the output generator can produce |
| `morse.py` | decodes the strip below the die |
| `verify_vcd.py` | cycle-by-cycle check against the supplied VCD |
| `test_warmup.py` | validates the whole flow against the warm-up's known Verilog |

`recovered_netlist.v` is the reconstructed design, 738 instances with placement coordinates in
comments.

## What I'd tell someone starting this

Do the warm-up properly. It exists so you can build your extractor against a design whose answer
you already know, and it'll catch a class of bug you would otherwise carry for hours.

Then find your second check before you start reasoning. The VCD is the real gift in this repo —
it lets you prove your recovered netlist is behaviourally identical to the chip *before* you've
formed a single hypothesis about what the chip does. Everything after that is just reading.
