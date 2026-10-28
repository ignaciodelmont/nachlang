# NachLang

A small, dynamically typed programming language and its compiler. Programs
are lexed and parsed with [rply](https://rply.readthedocs.io/), compiled to
LLVM IR with [llvmlite](https://pypi.org/project/llvmlite/), optimised with
LLVM's standard pipeline, and executed in-process by a JIT.

```nachlang
defn fib(n) {
    (if (n <= 1) { return n })
    return fib(n - 1) + fib(n - 2)
}

print(fib(20))
```

```
$ nachlang fib.nach
6765.000000
```

Every value is a number, a string or a boolean, carried at runtime in a
tagged struct. The compiler emits no type checks of its own; every operation
reads the tag and branches, and LLVM's optimiser removes most of that work
along with most of the allocations. Optimised NachLang runs 1.7x faster than
CPython on recursive `fib(35)` and 84x faster on a tight loop.

## Documentation

- [`docs/LANGUAGE.md`](docs/LANGUAGE.md) — the language reference: syntax,
  semantics, precedence, scoping, errors, and the known gaps. Every example
  in it is executed by the test suite.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — how the compiler works:
  the pipeline, the value representation, name resolution, memory, and the
  decisions behind each.
- [`bench/RESULTS.md`](bench/RESULTS.md) — measured performance against
  CPython across optimisation levels and allocators, with method.
- [`TODOS.md`](TODOS.md) — known bugs, missing features, rough edges.

## Installation

Requires Python 3.10–3.12 and [Poetry](https://python-poetry.org/).

```sh
brew install llvm@14 bdw-gc   # or newer llvm; bdw-gc only for --libgc-path
poetry install
```

The JIT does not use the system LLVM — llvmlite bundles its own — but `lli`
must be on `PATH` for the compiler to start, and `opt`/`lli` are what the
ahead-of-time path and the benchmark suite run. LLVM 14 works for everything
except optimising a garbage-collected build ahead of time, which needs
LLVM 15 or newer; see `--no-gc-alloc-attrs`.

## Usage

```sh
poetry run nachlang program.nach
```

| flag | effect |
|---|---|
| `--opt-level N` | LLVM optimisation level, 0–3. Default 3. `0` runs no IR passes. |
| `--libgc-path PATH` | allocate with the Boehm collector at `PATH` instead of `malloc` |
| `--output-ll` | write the unoptimised LLVM IR to `program.nach.ll` |
| `--compile-only` | stop after compiling; do not run |
| `--graph-ast` | render the AST with graphviz |
| `--no-gc-alloc-attrs` | omit the LLVM 15 allocator attributes from `GC_malloc`, for older external tools |

Errors go to standard error and exit with status 1. A program that completes
exits with the value `main` returned, which is 0.

Setting `NACHLANG_PARSER_WARNINGS` to any value shows rply's grammar warnings
at startup; they are hidden by default.

## Development

```sh
poetry run pytest                   # 271 tests, ~18s
poetry run black nachlang/ tests/   # formatting
poetry run pylint nachlang/
QUICK=1 ./bench/run_benchmarks.sh   # benchmark smoke test
./bench/run_benchmarks.sh           # full benchmark run, a few minutes
```

The execution tests run each program in a subprocess, so a crash in generated
code fails one test rather than the runner.

## History

This is a rewrite of an earlier version at
<https://gitlab.com/ignaciodelmont/nachlang_>, taking a more functional
approach to code generation.
