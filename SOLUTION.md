# Jane Street ASIC Puzzle 2026 — solved

**Final answer: `(* TWO STARS *)`**

The chip is an 11×11 **Star Battle** ("Two Not Touch") solution checker. It clocks in 121 bits
row-major on `I`, and raises `success` for the unique grid with 2 stars per row, per column and
per region, no two stars orthogonally or diagonally adjacent. The output generator then prints
the answer on `O[7:0]`, one ASCII byte per clock.

## Input that makes `success` go high

Toggle `rst_n` low→high, raise `enable`, clock these 121 bits into `I` (row 0 left→right first):

```
00000001010      . . . . . . . * . * .
10000100000      * . . . . * . . . . .
00000001010      . . . . . . . * . * .
10100000000      * . * . . . . . . . .
00001010000      . . . . * . * . . . .
00100000100      . . * . . . . . * . .
00001000001      . . . . * . . . . . *
01000010000      . * . . . . * . . . .
00010000001      . . . * . . . . . . *
00000100100      . . . . . * . . * . .
01010000000      . * . * . . . . . . .
```

## Recovered region map (read out of the decode logic)

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

## All messages the chip can print

| input grid | success | `O[7:0]` |
|---|---|---|
| the unique Star Battle solution | high | `(* TWO STARS *)` |
| 2/row + 2/col + 2/region but stars touch | low | `TWO NOT TOUCH` |
| all 121 cells set | low | `BIG BANG` |
| all 121 cells clear | low | `EMPTY SKY` |
| anything else | low | `TRY AGAIN` |

## Easter eggs

- **Morse code below the die**: 36 bars on layer 200/0 at y = −52.72 µm spell
  **`PER ARENAM AD ASTRA`** — "through sand, to the stars".
- `(* … *)` is OCaml comment syntax.
- `example_inputs.vcd` is dated `Sat Dec 31 23:59:60 2016` — a real leap second.
- 15 `clkbuf_4` cells drive nothing at all.
- **A real bug**: in the output generator, one input net (feeding `a31oi_2` and `a311o_2` around
  x≈177 µm, y≈91 µm) has two sinks and *no driver*. It corrupts one character of
  `TWO NOT TOUCH` (space→`"` if it settles low, final `H`→`J` if high). `success` is unaffected.

## How it was recovered

1. `tools/extract.py` — flattens li1 + met1..met5 and the mcon/via1..via4 cut layers out of
   `puzzle.gds`, then union-finds overlapping shapes joined through cuts. 49k polygons → 2626 nets.
2. `tools/netlist.py` — drops each cell's pin label onto the net beneath it → 738 cells, 92 flops,
   no shorts. Emitted as `recovered_netlist.v` by `tools/emit_verilog.py`.
3. `tools/cells.py` + `tools/sim.py` — sky130 cell models and a gate-level simulator.
4. `tools/regions.py` — sweeps the region decoder over all 121 (row, col) pairs to print the map.
5. `tools/solve.py` / `tools/solve2.py` — solves the Star Battle (solution is unique).

### Validation

- The warm-up design, extracted identically, reproduces its spec `A + B == 496` (309 vectors).
- `tools/verify_vcd.py` replays `example_inputs.vcd`: **312/312 clock cycles match** on both
  `O[7:0]` and `success`, including the reference chip's `TRY AGAIN`.

```bash
python tools/extract.py puzzle.gds "" tools/puzzle.pkl
python tools/netlist.py tools/puzzle.pkl
python tools/verify_vcd.py     # 312/312 cycles match
python tools/run_puzzle.py     # SUCCESS = 1
```
