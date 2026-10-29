# How the NachLang Compiler Works

This document describes the compiler as it is built: the pipeline from
source text to running machine code, the representation every value has at
runtime, how names are resolved, and the decisions behind each. For what the
language looks like to someone writing it, see `LANGUAGE.md`. For measured
performance, see `../bench/RESULTS.md`.

## The pipeline

```
 source text
     │
     │  nachlang/lexer.py           rply LexerGenerator
     ▼
 token stream
     │
     │  nachlang/parser.py          rply LALR(1) parser
     ▼
 AST: nested dicts of {"name", "value"} holding rply Tokens at the leaves
     │
     │  nachlang/codegen/ast.py     walks the tree, keeps scope
     │  nachlang/codegen/core.py    emits LLVM IR through llvmlite
     ▼
 LLVM IR module: the program plus a ~450 line runtime prelude
     │
     │  nachlang/runtime.py         parse, verify, optimise, MCJIT
     ▼
 native code, executed in-process by calling main()
```

There is no separate semantic analysis pass and no intermediate
representation of the compiler's own. The AST produced by the parser is the
only data structure between source and IR, and code generation is a single
recursive walk over it. Everything the compiler needs to know about a value
is decided at runtime, in generated code, by reading a type tag.

## Lexer

`nachlang/lexer.py` defines the token set as a list of `(name, regex)` pairs
handed to rply's `LexerGenerator`. rply tries rules in order and takes the
first match, which has one consequence worth knowing: a keyword pattern must
end in a word boundary, or `print` would match the first five characters of
`printer`. The `keyword()` helper adds that boundary to every reserved word
so a new one cannot be added without it.

Three classes of text are declared as *ignored* and never produce tokens:
whitespace in all four forms, `#` comments, and commas. Commas are ignored
rather than parsed because they separate nothing in the language; keeping
them out of the grammar avoids inventing rules for where a purely decorative
character is permitted.

The `STRING` pattern allows backslash escapes so a string can contain a quote.
Decoding those escapes is left to code generation, where the token's source
position is still available for error messages.

## Parser

`nachlang/parser.py` builds an LALR(1) parser with rply's `ParserGenerator`.
Each production is a decorated function that returns a node:

```python
{"name": "define_var", "value": [Token(DEF), Token(VAR, "x"), <expression node>]}
```

The AST is therefore a tree of plain dicts whose `value` lists hold either
further nodes or the raw rply tokens, including punctuation. Code generation
indexes into those lists positionally -- `define_var[1]` is the name token,
`define_var[2]` the expression -- and strips parentheses where it needs the
inner expression. This is simple and it is also why the generator is tightly
coupled to the exact shape of each production.

The grammar declares precedence for arithmetic and the logical operators but
not for comparisons, and two of its productions
(`argument_values : argument_values argument_values`, and the same shape for
`arguments`) are ambiguous. rply resolves the resulting 122 shift/reduce and
9 reduce/reduce conflicts with its defaults, and those defaults are where the
language's comparison-precedence quirk comes from. The generator warnings
that report the conflicts are suppressed unless `NACHLANG_PARSER_WARNINGS` is
set.

Two behaviours are implemented around the parser rather than in the grammar.
A registered error handler turns rply's bare `ParsingError` -- whose message
is `None` -- into a `NachlangSyntaxError` naming the offending token and its
position. And `parse()` materialises the token list before parsing, both so a
lexing error surfaces with a position attached and so that a program with no
tokens can be returned as an empty AST without reaching the grammar; an empty
production for `statement_list` would do the same job at the cost of two more
reduce/reduce conflicts.

## Code generation

Code generation is split across three modules.

**`codegen/ast.py`** walks the tree. A dispatch table maps each node name to
a resolver, and each resolver pulls apart its node, recurses into
sub-expressions, and calls into the layer below to emit code. It owns the
*context*: the current `IRBuilder`, the scope path (`["main"]` at the top
level, `["main", "fib"]` inside `fib`), and the set of names any function
body mentions, which decides how top-level variables are stored.

**`codegen/core.py`** emits IR through llvmlite's `ir` builder API. It
defines the value representation, the runtime prelude, and one function per
operation the AST layer can ask for: allocate a number, add two values,
compare, print, define a function, call one.

**`codegen/llvm.py`** is a thin facade over `core.py` -- one wrapper per
operation, each a single line -- so that `ast.py` depends on a small named
surface rather than on `core.py`'s internals.

The generator does no type inference. When it emits `a + b` it emits a call
to the runtime's `add` function with two pointers, and `add` reads the number
field of each at runtime. The compiler does not know, and does not try to
know, whether `a` is a number.

## The value representation

Every value in a running NachLang program is a heap-allocated 32-byte struct:

```llvm
%"struct.nachtype" = type { i8, double, i8*, i1 }
;                           ^    ^       ^    ^
;                           tag  number  str  bool
```

The tag is `0` for a number, `1` for a string, `2` for a boolean. Exactly one
of the remaining fields is meaningful for a given tag; the others are left
uninitialised. This is the entire mechanism of dynamic typing: every operation
in the runtime prelude reads the tag and branches on it, and every value
passed between functions, stored in a variable or returned is a
`%struct.nachtype*`.

Numbers are doubles, which is why integer literals print as `42.000000` and
why there is no integer division. Strings are copied to the heap on creation
(`allocate_string` calls `strlen`, `malloc` and `strcpy`) and the struct
holds the pointer. Booleans are the exception to "every value is allocated":
`true` and `false` are two module-level constants, `NACH_TRUE` and
`NACH_FALSE`, and producing a boolean is a `select` between their addresses
rather than an allocation.

Choosing a uniform boxed representation keeps the compiler small -- there is
one calling convention, one storage type, one way to print -- at the cost
that `1 + 2` is two allocations, two tag reads, an `fadd`, and a third
allocation for the result. That cost is real at `-O0` and largely disappears
under optimisation; see Performance below.

## The runtime prelude

Every module begins with the same prelude, emitted by `core.initialize()`
before any user code. It declares five C functions -- `printf`, `malloc` (or
`GC_malloc`), `strcmp`, `strcpy`, `strlen` -- and defines twenty-four
functions and seven constants of its own. Grouped by purpose:

| group | symbols |
|---|---|
| allocation | `allocate_nachtype`, `allocate_number`, `allocate_string`, `allocate_bool` |
| field access | `load_number`, `load_number_as_int`, `load_string`, `load_bool` |
| arithmetic | `add`, `sub`, `mul`, `div` |
| comparison | `nach_eq`, `nach_neq`, `nach_lt`, `nach_lte`, `nach_gt`, `nach_gte`, `compare_strings` |
| logic | `nach_and`, `nach_or`, `is_truthy` |
| output | `nach_print` and its three format strings |
| constants | `NACH_TRUE`, `NACH_FALSE`, `NACH_EMPTY_STRING` |

The prelude is generated as IR, not written in C, so it is optimised together
with the program that uses it. This matters more than it sounds: it is what
lets LLVM inline `add` into a loop body, see through it to the `malloc`
inside, and then remove the allocation.

The prelude is about 450 lines of IR. A three-line program produces a module
of 462.

## Names and symbols

User-defined functions are emitted as `nach.<name>` and top-level variables
as `nach.var.<name>`. The prefix keeps user names out of the module's own
namespace, which already holds the twenty-nine symbols above. Without it a
function called `add`, `sub`, `main` or `printf` collided with the prelude and
llvmlite refused to build the module.

Looking a function up by its user-visible name is also what makes the
compile-time checks possible: calling a function that does not exist, defining
one twice, and calling with the wrong number of arguments are all reported by
name before any code runs.

### The symbol table

`nachlang/symbol_table.py` maps a *scope path* to the names defined in that
scope and the storage each one lives in. The top level is `["main"]`; a
function `fib` defined at the top level has scope `["main", "fib"]`. Name
lookup walks from the current scope outward, so a function body finds its own
locals first and then the top level.

Blocks -- `if` and `loop` bodies -- do not get a scope of their own. A name
defined inside one lands in the enclosing scope. That is why a `def` inside a
block is *visible* after the block but crashes the compiler if read: the
symbol table says the name exists, but the `alloca` that backs it sits in a
basic block that does not dominate the use. This is a known bug.

### Where variables live

A variable's storage is a slot holding a `%struct.nachtype*`. Reads are a
`load` from the slot and `mut` is a `store` to it; the value itself is never
copied.

Locals and function parameters are `alloca`s in the function's entry block.
LLVM's `mem2reg` promotes those straight into SSA registers, which is the
cheapest storage there is.

Top-level variables have a complication: an `alloca` belongs to the frame of
the function that created it, so a function body cannot reach one created in
`main`. The first implementation of top-level access made every top-level
`def` a module global instead. That worked and cost about 4x on loops --
LLVM will promote an `alloca` into a register but will not do the same for a
global, and a top-level loop counter is exactly where that lands.

The compiler therefore makes a pass over the AST before generating anything
(`collect_names_used_in_functions`) and gathers every name mentioned inside
any function body. A top-level `def` becomes a module global only if its name
is in that set; otherwise it stays an `alloca` in `main`. The set is a
deliberate over-approximation -- it also collects parameters, locals and
callee names -- because promoting a variable that did not need it costs a
little speed and never correctness.

## Memory

The prelude's allocator is `malloc`, and nothing in the language ever calls
`free`. Every arithmetic result, every literal in a loop body, is a fresh
32-byte allocation that is never reclaimed. At `-O0` that is 128 bytes per
iteration of a simple accumulator loop, verified at 6.0 GB predicted against
6.0 GB measured for 50 million iterations.

`--libgc-path` swaps `malloc` for the Boehm collector's `GC_malloc`, which
keeps memory flat at any scale. It costs roughly 1.6x against `malloc` once
one more thing is done: LLVM recognises `malloc` by name and knows it can
delete an allocation that never escapes, but `GC_malloc` is an opaque
external call and gets no such treatment. The compiler annotates it with
LLVM's allocator attributes -- `allockind`, `allocsize`, `alloc-family` --
which lets the optimiser treat it like `malloc`. Those attributes exist from
LLVM 15, which llvmlite bundles; IR destined for an older external `opt` can
be emitted without them via `--no-gc-alloc-attrs`.

## Execution

`nachlang/runtime.py` takes the finished IR module and runs it:

1. parse the IR text back into an LLVM module and verify it;
2. run LLVM's standard optimisation pipeline at `--opt-level` (default 3,
   through the new pass manager);
3. hand the module to an MCJIT execution engine, finalise it, and look up
   `main`;
4. call `main` through `ctypes` as `int (*)(void)` and return its result as
   the process exit status.

Step 2 did not exist for most of the project's life. The JIT compiled
unoptimised IR directly, and the target machine's own instruction selection
was the only optimisation applied. Adding the pipeline is the single largest
performance change in the project's history: 2.9x on recursive `fib`, up to
65x on loops.

`main` returns `i32` rather than `void` so that tools which read the exit
status, including `lli`, see a real value.

### The ahead-of-time path

`--output-ll` writes the unoptimised module to `<file>.ll` beside the source,
and `--compile-only` stops before executing. From there the standard LLVM
tools apply: `opt -O3` to optimise, `lli` to run, `llc` to produce assembly
for any target. `docs/NOTES.md` has the incantations. `lli` needs `-load`
pointing at `libgc` for a GC build, and the host LLVM must be 15 or newer for
the allocator attributes to parse.

## Performance

`bench/RESULTS.md` has the numbers and the method; the shape of them is this.

Unoptimised, NachLang is slower than CPython on recursion and roughly at
parity on loops. Optimised, it is faster everywhere: 1.7x on `fib(35)`, and
84x on a 100-million-iteration loop.

The loop result is not a faster loop. It is the optimiser proving that none
of the structs allocated in the loop body escape, scalarising them into
`fadd` on registers, and deleting every allocation -- after `-O2`, the hot
loop in `main` contains no calls at all. Peak memory for a 20-million
iteration loop falls from 2.45 GB to 0.06 GB for the same reason.

Recursion is the exception. LLVM cannot prove a struct does not escape across
a recursive call, so `fib` keeps five allocations per invocation and gains
only what inlining and tag-check elimination can give it. Removing those
allocations -- by unboxing numbers, or by doing the escape analysis in the
compiler where the call graph is known -- is the largest performance change
still available.

## Testing and benchmarking

`tests/` holds 271 tests, split by language feature, and run in about 18
seconds. The execution tests compile and run real programs in a subprocess
and assert on their output. They are out-of-process for two reasons:
generated code prints through `printf` to the process's file descriptor,
where pytest's `capsys` cannot see it; and a bug in generated code should
fail one test, not take the test runner down. `test_language_reference.py`
extracts every example from `LANGUAGE.md` and checks it against the output
shown there.

`bench/run_benchmarks.sh` measures three workloads across nine
configurations, verifying every run against the equivalent Python program as
an oracle, and refuses to report a configuration that produced the wrong
answer as a fast one. `QUICK=1` runs reduced workloads as a smoke test.

## Map of the repository

```
nachlang/
  __init__.py       CLI entry point (typer); flags; error reporting
  lexer.py          token definitions
  parser.py         grammar, AST construction, syntax errors
  errors.py         NachlangError and its subclasses
  symbol_table.py   scope paths and name resolution
  runtime.py        optimisation pipeline and MCJIT execution
  codegen/
    ast.py          tree walk; scope and context; top-level globals pass
    core.py         value representation, runtime prelude, IR emission
    llvm.py         facade over core.py used by ast.py
  examples/         sample programs
  graph.py          optional AST visualisation (--graph-ast, needs graphviz)
tests/              pytest suite; conftest.py has the subprocess runner
bench/              benchmark suite and RESULTS.md
docs/
  LANGUAGE.md       the language reference
  ARCHITECTURE.md   this document
  NOTES.md          llc / llvm-as recipes for the AOT path
TODOS.md            known bugs, missing features, rough edges
```

`nachlang/nach_types.py`, `types.py` and `debugger.py` are not part of the
pipeline. They are listed in `TODOS.md` as candidates for deletion.
