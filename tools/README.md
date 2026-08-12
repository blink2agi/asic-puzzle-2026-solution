# Reverse-engineering toolchain

Requires `gdstk`, `shapely` (and `matplotlib` for `plot_place.py`).

    python -m venv .venv && .venv/bin/pip install gdstk shapely matplotlib

## Pipeline

    python tools/extract.py puzzle.gds "" tools/puzzle.pkl   # GDS -> geometric net extraction
    python tools/netlist.py tools/puzzle.pkl                 # nets + pin labels -> netlist
    python tools/verify_vcd.py                               # replay example_inputs.vcd (312/312)
    python tools/run_puzzle.py                               # feed the solution -> SUCCESS = 1

## Files

| file | what it does |
|---|---|
| `extract.py`   | flattens li1/met1..met5 + mcon/via1..via4 cuts, union-finds shapes into nets |
| `netlist.py`   | maps cell pin labels onto nets, identifies power rails and ports |
| `cells.py`     | functional models for the sky130_fd_sc_hd cells used |
| `sim.py`       | levelized gate-level simulator (async set/reset, clock-tree aware) |
| `emit_verilog.py` | writes `recovered_netlist.v` |
| `cone.py`      | prints the logic cone of a net or flip-flop D input as an expression |
| `ffeq.py`      | builds evaluable truth tables for flip-flop next-state logic |
| `regions.py`   | sweeps the region/column decoders over all (row, col) -> region map |
| `solve.py` / `solve2.py` | Star Battle solver; `solve2` also proves uniqueness |
| `messages.py`  | enumerates every string the output generator can print |
| `morse.py`     | decodes the Morse strip hidden below the die |
| `verify_vcd.py`| cycle-by-cycle check against the supplied VCD |
| `test_warmup.py` | validates the whole flow on `warmup/` against its known Verilog |
| `analyze.py`, `ffgraph.py`, `clktree.py`, `check_nl.py`, `dangling.py`, `netgeom.py`, `probe_net.py`, `eggs.py`, `plot_place.py` | analysis helpers used along the way |
