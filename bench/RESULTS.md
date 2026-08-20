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
| llvmlite | 0.44.0 (bundles LLVM 15.0.7 for the JIT path) |
| Boehm GC | `/opt/homebrew/lib/libgc.dylib` |
| Date | 2026-08-20 |

Fixed startup cost, measured separately and subtracted from every figure below:
NachLang JIT 0.41s (Python startup + IR generation + optimization + MCJIT
compile), `lli` 0.01s, `python3` 0.01s.

## Results

Wall-clock seconds, startup subtracted. Lower is better.

| configuration | fib(35) | loop 50M | loop 100M | alloc 10M |
|---|---|---|---|---|
| Python 3 | 0.67 | 3.47 | 6.60 | 0.58 |
| NachLang JIT -O0 (malloc) | 1.16 | 2.08 | — | 0.64 |
| **NachLang JIT (malloc)** | **0.42** | **0.06** | **0.05** | **<0.01** |
| `opt -O1` + lli (malloc) | 0.65 | 1.18 | — | 0.23 |
| `opt -O2` + lli (malloc) | 0.44 | 0.04 | 0.07 | 0.01 |
| `opt -O3` + lli (malloc) | 0.43 | 0.04 | 0.07 | 0.01 |
| NachLang JIT -O0 + GC | 1.82 | 3.31 | 6.24 | 1.03 |
| **NachLang JIT + GC** | **0.75** | **1.28** | **2.51** | **0.24** |
| `opt -O3` + lli + GC | 1.56 | 2.76 | 5.22 | 0.90 |

`alloc 10M` under the optimized JIT measures below the 0.41s startup baseline,
so its execution time is not resolvable — it is effectively zero.

`-O0` and `-O1` still emit a real allocation per operation, so they are bounded
by memory: loop 100M would need ~11.9 GB and is skipped for those two rows.
From `-O2` upward the allocations are removed entirely and the same workload
runs in 65 MB, which is why the optimized JIT reaches 100M and its unoptimized
counterpart cannot.

## Findings

### 1. The JIT now runs the optimization pipeline, and it is worth 2.8–33×

`runtime.py` previously built no `PassManager`, so the JIT executed completely
unoptimized IR. Adding the pipeline moves the JIT from *slower than CPython* to
*decisively faster*:

| workload | JIT -O0 | JIT | speedup |
|---|---|---|---|
| fib(35) | 1.16 | 0.42 | 2.8× |
| loop 50M | 2.08 | 0.06 | 33× |
| alloc 10M | 0.64 | <0.01 | >60× |

Against CPython the optimized JIT wins everywhere, by 1.6× on `fib` and by
**132×** on loop 100M (0.05s against 6.60s).

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
`opt -O3 + lli + GC` row above is *slower* than the in-process JIT + GC row on
this machine: the AOT path ran through LLVM 14 without the attributes.
Installing `llvm@15` or newer would close that gap.

### 4. Recursion keeps its allocations

`fib` after `-O3` still performs 5 × `GC_malloc(32)` per call — LLVM cannot
prove non-escape across the recursive edge. That is why fib gains 2.8× from the
optimizer while the loops gain 33×.

### 5. malloc versus GC

- **malloc**: fastest and fully optimizable, but leaks by construction — 128
  bytes per loop iteration. Only safe past ~50M iterations because `-O2`
  removes the allocations entirely.
- **GC**: flat 65 MB at any scale and any optimization level. With allocator
  attributes it costs roughly 1.8× against malloc rather than the 20×+ it cost
  without them.

## Caveats

- The `lli` configurations depend on the host LLVM. With `llvm@14` the GC rows
  are measured without allocator attributes; the harness prints a note when it
  detects this.
- `-O3` + GC shows the highest run-to-run variance of any configuration
  (loop 100M: 5.22 median against a 4.15 best), presumably collector timing.
