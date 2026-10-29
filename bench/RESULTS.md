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
| Date | 2026-10-29 |

Fixed startup cost, measured separately and subtracted from every figure below:
NachLang JIT 0.40s (Python startup + IR generation + optimisation + MCJIT
compile), `lli` 0.01s, `python3` 0.01s.

## Results

Wall-clock seconds, startup subtracted. Lower is better. "unchecked" is the
JIT with `--no-runtime-checks`; every other NachLang row has the arithmetic
type check on, which is the default.

| configuration | fib(35) | loop 50M | loop 100M | alloc 10M |
|---|---|---|---|---|
| Python 3 | 0.67 | 3.21 | 5.89 | 0.57 |
| NachLang JIT -O0 (malloc) | 1.12 | 1.98 | 3.95 | 0.61 |
| **NachLang JIT (malloc)** | **0.62** | **0.03** | **0.05** | **<0.01** |
| NachLang JIT, unchecked | 0.38 | 0.03 | 0.05 | <0.01 |
| `opt -O1` + lli (malloc) | 0.90 | 1.55 | 3.03 | 0.30 |
| `opt -O2` + lli (malloc) | 0.66 | 0.04 | 0.07 | 0.01 |
| `opt -O3` + lli (malloc) | 0.66 | 0.04 | 0.07 | 0.01 |
| NachLang JIT -O0 + GC | 1.66 | 3.17 | 6.15 | 1.00 |
| **NachLang JIT + GC** | **0.98** | **1.21** | **2.40** | **0.35** |
| `opt -O3` + lli + GC | 1.47 | 2.57 | 5.18 | 0.90 |

`alloc 10M` under the optimised JIT measures at or below the 0.40s startup
baseline, so its execution time is not resolvable; it is effectively zero.
The same caveat applies in a milder form to the loops at 0.03–0.05s.

Every configuration completes at every size on this machine. Scaling from 50M
to 100M is close to linear (Python 1.84×, JIT -O0 2.00×, JIT + GC 1.98×),
which is the main evidence that these numbers measure the code.

## Findings

### 1. Runtime type checking costs nothing in loops and 0.24s on `fib(35)`

Arithmetic now checks both operands' type tags before reading the number
field, so `"a" + 1` is a runtime error instead of `nan`. The check is two
loads and a compare per operation. In every loop benchmark the optimiser has
already proven the operands are freshly allocated numbers and folds the check
to nothing: the checked and unchecked rows are identical. Across a call
boundary it cannot -- a parameter's tag is only known at run time -- so
recursion pays in full:

| `fib(35)` | execution | vs CPython |
|---|---|---|
| unchecked | 0.38 | 1.8× faster |
| checked (default) | 0.62 | 1.1× faster -- parity |

Most of the former margin over CPython on recursion was the absence of the
check. The ahead-of-time rows pay it too (`-O3`: 0.43 → 0.66), since the IR
they run carries the same check. The loop results are untouched.

### 2. The optimisation pipeline is worth 1.8–79×

`runtime.py` previously built no `PassManager`, so the JIT executed
completely unoptimised IR. With the pipeline, and checks on:

| workload | JIT -O0 | JIT | speedup |
|---|---|---|---|
| fib(35) | 1.12 | 0.62 | 1.8× (2.9× unchecked) |
| loop 50M | 1.98 | 0.03 | 66× |
| loop 100M | 3.95 | 0.05 | 79× |
| alloc 10M | 0.61 | <0.01 | >60× |

Against CPython the optimised JIT is at parity on `fib` and roughly 100× faster
on loop 100M (5.89s against 0.05s, at the resolution limit of the startup
subtraction).

### 3. LLVM eliminates NachLang's allocation overhead — in loops

The loop survives in the IR; the allocation does not. After `-O2`, `main`'s hot
loop contains **zero calls** — every `NACHTYPE` is scalarized into `fadd double`
in registers, because LLVM recognizes `malloc` as an allocation function and can
prove the structs never escape. Peak RSS for loop 20M drops from 2.45 GB at
`-O0` to 0.06 GB at `-O3`. This is also why the type check is free there: the
tag it would load was stored as a constant a few instructions earlier.

### 4. Boehm GC needs allocator attributes to be optimizable

`GC_malloc` is an opaque external symbol, so by default LLVM cannot elide
anything around it. Declaring it with LLVM 15 allocator attributes
(`allockind("alloc,uninitialized")`, `allocsize(0)`, `"alloc-family"="gc"`,
`nounwind willreturn`, plus `noalias` on the return) lets the optimizer treat it
like `malloc`. Measured in the JIT, same workload, attributes off vs on
(taken before runtime checks existed; the ratio is what matters):

| workload | without attrs | with attrs | speedup |
|---|---|---|---|
| alloc 10M | 1.35 | 0.67 | 2.0× |
| loop 50M | 3.06 | 1.72 | 1.8× |

This does not reach full parity with `malloc`: allocation sites in `main` drop
from 8 to 3, not to 0, because LLVM's name-based `TargetLibraryInfo` knowledge
of `malloc` enables transforms that attributes alone do not.

The attributes require **LLVM 15 or newer** — `allockind` does not parse under
LLVM 14. The JIT always benefits because llvmlite bundles LLVM 15. IR destined
for an older external `opt` must be generated with `--no-gc-alloc-attrs`, which
the harness does automatically after checking `opt --version`. That is why the
`opt -O3 + lli + GC` row is *slower* than the in-process JIT + GC row on this
machine: the AOT path ran through LLVM 14 without the attributes.

### 5. Recursion keeps its allocations

`fib` after `-O3` still performs 5 × `GC_malloc(32)` per call — LLVM cannot
prove non-escape across the recursive edge. That is why fib gains 1.8× from the
optimizer while the loops gain 66–79×, and why it alone pays for the type
check.

### 6. malloc versus GC

- **malloc**: fastest and fully optimizable, but leaks by construction — 128
  bytes per loop iteration, an upper bound: loop 100M projects to 11.9 GB and
  actually peaks at 8.4 GB, because macOS compresses inactive pages.
- **GC**: flat 65 MB at any scale and any optimization level, and roughly 1.6×
  slower than malloc on `fib` once allocator attributes are in play.

From `-O2` upward the distinction largely evaporates for loops, since there
are no allocations left to manage.

## Methodology notes

- Correctness is verified on stdout every run, not on exit status.
- The memory guard projects each workload's footprint against physical RAM
  (`MEMORY_BUDGET`, default 60%) and skips only the configurations that still
  allocate per operation, which is `-O0` and `-O1`. Nothing is skipped on a
  36 GB machine; a 16 GB machine would skip loop 100M for those two rows.
- **Repeated large-footprint runs can push the machine into swap**, and a
  median computed through thrash describes the swap subsystem rather than the
  code. Any configuration whose median exceeds twice its best run is flagged
  `UNSTABLE`; the numbers above were taken at `RUNS=3` and carry no such flag.
  Treat a flagged row as "not measured" rather than "slow".
- `opt -O3` + GC shows the highest run-to-run variance of any configuration
  (loop 100M: 5.18 median against a 3.93 best), presumably collector timing.
- The `lli` rows depend on the host LLVM; with `llvm@14` the GC rows run without
  allocator attributes and the harness prints a note saying so.
- The ahead-of-time rows have no unchecked variant: `--output-ll` emits the IR
  with the default semantics, checks included.
