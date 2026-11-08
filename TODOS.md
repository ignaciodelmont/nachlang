# TODOS

## Language

- String operations: concatenation, length, indexing. Escapes and printing are
  done; there is still no way to combine two strings.
- Add Lambdas.

## Rough edges worth a look

- There are five import cycles between `nachlang` and `nachlang.codegen`;
  they work, but they are why `__init__.py` has to import after the warnings
  filter is set up.
- The grammar is ambiguous: 50 shift/reduce and 9 reduce/reduce conflicts,
  down from 122 once the comparison operators got a precedence level.
  `argument_values : argument_values argument_values` and the matching rule for
  `arguments` are what remains. Warnings are hidden unless
  `NACHLANG_PARSER_WARNINGS` is set, which makes it easy to forget.
- Nothing is ever freed. Programs leak by construction unless run with
  `--libgc-path`, which costs roughly 1.6x once the allocator attributes are in
  play. See `bench/RESULTS.md`.
- `fib` still allocates five NACHTYPEs per call: LLVM cannot prove they do not
  escape across a recursive edge. Unboxing numbers, or doing the escape
  analysis in the compiler, is the largest remaining performance win.
- CI checks pull request titles and cuts releases, but does not run the
  tests. `pytest` plus `QUICK=1 ./bench/run_benchmarks.sh` would cover it; the
  benchmark script already exits non-zero on failure. The runner needs `lli`
  on `PATH` (the `llvm` apt package) and, for the benchmark, `opt`.

## MAYBE

- Adding Closures. Functions can reach top level variables now, but not the
  locals of an enclosing function.
- Adopt basedpyright. `standard` mode reports 12 errors today; `recommended`
  reports 2231 warnings, almost all of them missing annotations.
