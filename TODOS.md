# TODOS

## Language

- Do runtime type checks on operations. `validate_are_equal_type` computes the
  answer and then throws it away, so `1 == "a"` quietly returns false instead
  of complaining (`codegen/core.py`).
- String operations: concatenation, length, indexing. Escapes and printing are
  done; there is still no way to combine two strings.
- Add Lambdas.

## Rough edges worth a look

- The grammar is ambiguous: 122 shift/reduce and 9 reduce/reduce conflicts.
  `argument_values : argument_values argument_values` and the matching rule for
  `arguments` are the cause. Warnings are hidden unless
  `NACHLANG_PARSER_WARNINGS` is set, which makes it easy to forget.
- `ASSIGN` (`=`) is lexed but appears in no production, so it is dead weight
  the way `COMMA` was before it became decorative.
- `nach_types.py` is never imported and declares a second, conflicting
  `struct.nachtype`. `types.py` holds one unused import, and `debugger.py`
  disables warnings and opens a log file merely by being imported. All three
  look deletable.
- `poetry run format` never runs isort: `run_cmd(black) and run_cmd(isort)`
  short-circuits because a successful black returns 0.
- Nothing is ever freed. Programs leak by construction unless run with
  `--libgc-path`, which costs roughly 1.6x once the allocator attributes are in
  play. See `bench/RESULTS.md`.
- `fib` still allocates five NACHTYPEs per call: LLVM cannot prove they do not
  escape across a recursive edge. Unboxing numbers, or doing the escape
  analysis in the compiler, is the largest remaining performance win.
- No CI. `pytest` plus `QUICK=1 ./bench/run_benchmarks.sh` would cover it; the
  benchmark script already exits non-zero on failure.
- `codegen/ast.py` imports `load_bool` inside a function to dodge a circular
  import, and there are five import cycles between `nachlang` and
  `nachlang.codegen`.

## MAYBE

- Adding Closures. Functions can reach top level variables now, but not the
  locals of an enclosing function.
- Adopt basedpyright. `standard` mode reports 12 errors today; `recommended`
  reports 2231 warnings, almost all of them missing annotations.
