# Benchmark Results

Produced by `./bench/run_benchmarks.sh`. Re-run it to regenerate; every number
below is a median of 3 runs, verified against the equivalent Python program.

## Environment

| | |
|---|---|
| Machine | Apple M3 Max, 36 GB RAM |
| OS | Darwin 25.5.0 |
| Python | 3.14.7 |
| opt / lli | LLVM 14.0.6 (Homebrew `llvm@14`) |
| llvmlite | 0.44.0 (bundles LLVM 15.0.7 for the JIT path) |
| Boehm GC | `/opt/homebrew/lib/libgc.dylib` |
| Date | 2026-08-20 |

Fixed startup cost, measured separately and subtracted from every figure below:
NachLang JIT 0.39s (Python startup + IR generation + optimization + MCJIT
compile), `lli` 0.01s, `python3` 0.01s.

## Results

Wall-clock seconds, startup subtracted. Lower is better.

| configuration | fib(35) | loop 50M | loop 100M | alloc 10M |
|---|---|---|---|---|
| Python 3 | 0.66 | 3.79 | 6.74 | 0.54 |
| NachLang JIT -O0 (malloc) | 1.13 | 1.96 | 4.31 | 0.73 |
| **NachLang JIT (malloc)** | **0.38** | **0.03** | **0.08** | **0.07** |
| `opt -O1` + lli (malloc) | 0.64 | 1.14 | 2.32 | 0.24 |
| `opt -O2` + lli (malloc) | 0.43 | 0.04 | 0.07 | 0.01 |
| `opt -O3` + lli (malloc) | 0.43 | 0.04 | 0.07 | 0.01 |
| NachLang JIT -O0 + GC | 1.71 | 3.21 | 6.60 | 1.19 |
| **NachLang JIT + GC** | **0.63** | **1.31** | **2.56** | **0.34** |
| `opt -O3` + lli + GC | 1.44 | 2.09 | 5.26 | 0.72 |

Every configuration completes at every size on this machine. Scaling from 50M
to 100M is close to linear (Python 1.78×, JIT -O0 2.20×, JIT + GC 1.95×), which
is the main evidence that these numbers are measuring the code.

## Findings

### 1. The JIT now runs the optimization pipeline, and it is worth 2.9–65×

`runtime.py` previously built no `PassManager`, so the JIT executed completely
unoptimized IR. Adding the pipeline moves the JIT from *slower than CPython* to
*decisively faster*:

| workload | JIT -O0 | JIT | speedup |
|---|---|---|---|
| fib(35) | 1.13 | 0.38 | 2.9× |
| loop 50M | 1.96 | 0.03 | 65× |
| loop 100M | 4.31 | 0.08 | 54× |
| alloc 10M | 0.73 | 0.07 | 10× |

Against CPython the optimized JIT wins everywhere: 1.7× on `fib`, and **84×** on
loop 100M (0.08s against 6.74s).

### 2. LLVM eliminates NachLang's allocation overhead — in loops

The loop survives in the IR; the allocation does not. After `-O2`, `main`'s hot
loop contains **zero calls** — every `NACHTYPE` is scalarized into `fadd double`
in registers, because LLVM recognizes `malloc` as an allocation function and can
prove the structs never escape. Peak RSS for loop 20M drops from 2.45 GB at
`-O0` to 0.06 GB at `-O3`.

### 3. Boehm GC needs allocator attributes to be optimizable

`GC_malloc` is an opaque external symbol, so by default LLVM cannot elide
anything around it. Declaring it with LLVM 15 allocator attributes
(`allockind("alloc,uninitialized")`, `allocsize(0)`, `"alloc-family"="gc"`,
`nounwind willreturn`, plus `noalias` on the return) lets the optimizer treat it
like `malloc`. Measured in the JIT, same workload, attributes off vs on:

| workload | without attrs | with attrs | speedup |
|---|---|---|---|
| alloc 10M | 1.35 | 0.67 | 2.0× |
| loop 50M | 3.06 | 1.72 | 1.8× |

This does not reach full parity with `malloc`: allocation sites in `main` drop
from 8 to 3, not to 0, because LLVM's name-based `TargetLibraryInfo` knowledge
of `malloc` enables transforms that attributes alone do not. Adding a paired
`allockind("free")` deallocator was tried and changed nothing.

The attributes require **LLVM 15 or newer** — `allockind` does not parse under
LLVM 14. The JIT always benefits because llvmlite bundles LLVM 15. IR destined
for an older external `opt` must be generated with `--no-gc-alloc-attrs`, which
the harness does automatically after checking `opt --version`. That is why the
`opt -O3 + lli + GC` row is *slower* than the in-process JIT + GC row on this
machine: the AOT path ran through LLVM 14 without the attributes. Installing
`llvm@15` or newer would close that gap.

### 4. Recursion keeps its allocations

`fib` after `-O3` still performs 5 × `GC_malloc(32)` per call — LLVM cannot
prove non-escape across the recursive edge. That is why fib gains 2.9× from the
optimizer while the loops gain 54–65×.

### 5. malloc versus GC

- **malloc**: fastest and fully optimizable, but leaks by construction — 128
  bytes per loop iteration, an upper bound: loop 100M projects to 11.9 GB and
  actually peaks at 8.4 GB, because macOS compresses inactive pages.
- **GC**: flat 65 MB at any scale and any optimization level, and roughly 1.6×
  slower than malloc once allocator attributes are in play.

Note that from `-O2` upward the distinction largely evaporates for loops, since
there are no allocations left to manage.

## Methodology notes

- Correctness is verified on stdout every run, not on exit status.
- The memory guard projects each workload's footprint against physical RAM
  (`MEMORY_BUDGET`, default 60%) and skips only the configurations that still
  allocate per operation, which is `-O0` and `-O1`. Nothing is skipped on a
  36 GB machine; a 16 GB machine would skip loop 100M for those two rows.
- **Repeated large-footprint runs can push the machine into swap**, and a
  median computed through thrash describes the swap subsystem rather than the
  code. One 5-run pass produced a 994s median against a 6.15s best on
  `opt -O3 + lli + GC` at 100M. Any configuration whose median exceeds twice its
  best run is now flagged `UNSTABLE`; the numbers above were taken at `RUNS=3`
  and carry no such flag. Treat a flagged row as "not measured" rather than
  "slow".
- The `lli` rows depend on the host LLVM; with `llvm@14` the GC rows run without
  allocator attributes and the harness prints a note saying so.
