# Benchmark Results

Produced by `./bench/run_benchmarks.sh`. Re-run it to regenerate; every number
below is a median of 5 runs, verified against the equivalent Python program.

## Environment

| | |
|---|---|
| Machine | Apple M3 Max, 36 GB RAM |
| OS | Darwin 25.5.0 |
| Python | 3.14.7 |
| opt / lli | LLVM 14.0.6 (Homebrew `llvm@14`) |
| llvmlite | 0.44.0 (bundles its own LLVM for the JIT path) |
| Boehm GC | `/opt/homebrew/lib/libgc.dylib` |
| Date | 2026-08-20 |

Fixed startup cost, measured separately and subtracted from every figure below:
NachLang JIT 0.38s (Python startup + IR generation + MCJIT compile),
`lli` 0.01s, `python3` 0.01s.

## Results

Wall-clock seconds, startup subtracted. Lower is better.

| configuration | fib(35) | loop 50M | loop 100M | alloc 10M |
|---|---|---|---|---|
| Python 3 | 0.66 | 3.11 | 5.96 | 0.60 |
| NachLang JIT (malloc) | 1.12 | 1.97 | — | 0.64 |
| `opt -O1` + lli (malloc) | 0.62 | 1.12 | — | 0.23 |
| `opt -O2` + lli (malloc) | 0.42 | 0.04 | — | 0.01 |
| `opt -O3` + lli (malloc) | 0.43 | 0.04 | — | 0.01 |
| NachLang JIT + GC | 1.73 | 3.08 | 6.20 | 1.04 |
| `opt -O3` + lli + GC | 1.14 | 2.07 | 5.18 | 0.94 |

The malloc configurations cannot run loop 100M: nothing is ever freed, so the
workload needs ~11.9 GB. The harness skips those and says so rather than
reporting a number. loop 50M exists precisely so the malloc and GC paths can be
compared on the same workload at a size that fits — its projected 6.0 GB
footprint was confirmed against an actual peak RSS of 6.0 GB.

## Findings

### 1. LLVM eliminates NachLang's allocation overhead entirely — in loops

`alloc 10M` drops from 0.64s to 0.01s at `-O2`, and `loop 50M` from 1.97s to
0.04s. This is not the optimizer deleting the benchmark: the loop survives in
the IR. What disappears is the allocation. After `-O3`, `main`'s hot loop
contains **zero calls** — every `NACHTYPE` is scalarized into `fadd double` in
registers, because LLVM recognizes `malloc` as an allocation function and can
prove the structs never escape.

### 2. Boehm GC blocks that optimization

`GC_malloc` is an opaque external symbol, so LLVM must assume arbitrary side
effects and cannot elide anything around it. At `-O3` on `loop 50M` that is a
**52× penalty** — 2.07s with GC against 0.04s with malloc. The type-dispatch
switch, including its `strcmp` path, also survives into the loop body.

This is the central trade-off in the current runtime:

- **malloc**: fast, optimizable, but leaks by construction — 128 bytes per loop
  iteration, so anything past ~50M iterations exhausts RAM.
- **GC**: flat 65 MB at any scale, but forfeits the single largest optimization
  available, and costs a further ~56% on the unoptimized JIT path.

Worth trying: declare `GC_malloc` with LLVM allocation attributes
(`allockind("alloc,uninitialized")`, `allocsize(0)`, `willreturn nounwind`) so
the optimizer can treat it like `malloc`. That could recover the elision while
keeping memory bounded.

### 3. Recursion keeps its allocations

`fib` after `-O3` still performs 5 × `GC_malloc(32)` per call — LLVM cannot
prove non-escape across the recursive edge. That is why fib gains only ~2.6×
from `-O2` while the loops gain 25–60×.

### 4. NachLang is competitive with CPython, and faster when optimized

At 50M iterations the unoptimized JIT already beats Python (1.97s vs 3.11s).
Optimized, the gap is large: `-O2` is 78× faster than Python on `loop 50M` and
60× on `alloc 10M`. On `fib(35)`, where allocations survive optimization, the
best NachLang configuration is 1.6× faster than Python.

## Caveats

- The JIT figures include no IR-level optimization passes: `runtime.py` never
  builds a `PassManager`. The backend still codegens at `opt=2`, which is
  llvmlite's `create_target_machine()` default, so "JIT" is not "-O0".
- `nachlang` emits `define void @main`, so `lli` returns a junk exit status even
  on a clean run. The harness therefore verifies stdout, not exit codes.
- `-O3` + GC shows the highest run-to-run variance of any configuration
  (loop 100M: 5.19s median against a 3.81s best), presumably collector timing.
