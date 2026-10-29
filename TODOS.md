# TODOS

## Language

### Bugs found while writing the language reference

- Comparison operators have no entry in the parser's precedence table, so
  they bind looser than `and`/`or` and cannot be chained: `1 < 2 and 3 < 4`
  parses as `1 < (2 and (3 < 4))` and is false. Adding `("left", [EQ, NEQ,
  LT, LTE, GT, GTE])` above `AND` in `parser.py` is the fix; it will change
  the conflict count, so check `NACHLANG_PARSER_WARNINGS=1` before and after.
- A `def` inside an `if` or `loop` body is registered in the enclosing scope,
  so it is visible after the block, but its `alloca` sits in a basic block
  that does not dominate the later use and LLVM rejects the module. Either
  blocks need a scope of their own or every `alloca` needs to go in the
  function's entry block.
- A bare `return` crashes with IndexError, and `return` at the top level
  crashes with an empty message. Both should be reported as syntax errors.

- Do runtime type checks on arithmetic. Comparison now checks kinds, but
  `add`, `sub`, `mul` and `div` read the number field of whatever they are
  given, so `"a" + 1` quietly yields `nan` instead of complaining
  (`codegen/core.py`).
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
