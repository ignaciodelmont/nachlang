# The NachLang Language

A reference for the language as it is implemented, not as it was planned.
Every example below that has an `output` block after it is run by the test
suite (`tests/test_language_reference.py`) and compared against that block,
so what this document shows is what the compiler does.

NachLang is a small, dynamically typed language. Every value is a number, a
string or a boolean; every number is a 64-bit float. Statements are separated
by whitespace, blocks are braces, and the conditional and loop forms are
wrapped in parentheses, which gives the syntax a faintly Lisp-like shape.

```nachlang
defn fib(n) {
    (if (n <= 1) { return n })
    return fib(n - 1) + fib(n - 2)
}

print(fib(20))
```
```output
6765.000000
```

## Lexical structure

### Identifiers

An identifier starts with a letter or underscore and continues with letters,
digits or underscores: `x`, `total_count`, `_hidden`, `fib2`.

### Reserved words

These twelve words are keywords and cannot name a variable or function:

```
def  defn  mut  print  if  loop  return  is_truthy  and  or  true  false
```

A keyword only matches as a whole word. Identifiers that merely *begin* with
one -- `order`, `printer`, `define`, `android`, `returns` -- are ordinary names.

```nachlang
def order 5
def printer 7
print(order + printer)
```
```output
12.000000
```

### Literals

**Numbers** are written as unsigned integers: `0`, `42`, `100000000`. There is
no decimal literal and no negative literal; both are reported as syntax
errors. Every number is stored and computed as a double, so `7 / 2` is `3.5`,
and a negative value is written as a subtraction from zero.

```nachlang
print(7 / 2)
print(0 - 5)
```
```output
3.500000
-5.000000
```

**Strings** are double-quoted. A backslash escapes the next character, and
these escapes are understood:

| escape | meaning |
|---|---|
| `\"` | a double quote |
| `\\` | a backslash |
| `\n` | newline |
| `\t` | tab |
| `\r` | carriage return |

Any other escape is a syntax error. Strings are UTF-8 and may hold any text.

```nachlang
print("say \"hi\"")
print("héllo wörld")
```
```output
say "hi"
héllo wörld
```

**Booleans** are `true` and `false`.

### Comments and whitespace

`#` starts a comment that runs to the end of the line. Spaces, tabs,
newlines and carriage returns separate tokens and otherwise mean nothing.

**Commas mean nothing either.** They are skipped by the lexer wherever they
appear, so `f(a, b)` and `f(a b)` are the same call and `defn f(a, b)` and
`defn f(a b)` are the same definition. Whether to write them is a matter of
taste.

```nachlang
defn total(a, b, c) { return a + b + c }
print(total(1, 2, 3))   # with commas
print(total(1 2 3))     # without
```
```output
6.000000
6.000000
```

## Values

There are three kinds of value. Every one is a *NachType*: a tagged record
carrying its kind, a number, a string pointer and a boolean, of which exactly
one field is meaningful. The compiler does not know the kind of a value until
the program runs, which is what makes the language dynamically typed.

| kind | written as | printed as |
|---|---|---|
| number | `42`, `7 / 2` | `%f`, so `42.000000` |
| string | `"text"` | the text, as is |
| bool | `true`, `false` | `bool(1)`, `bool(0)` |

```nachlang
print(42)
print("text")
print(true)
```
```output
42.000000
text
bool(1)
```

### Truthiness

Conditions do not have to be booleans. Any value can be tested, and
`is_truthy(x)` makes the test explicit and returns a boolean:

| value | truthy? |
|---|---|
| number | yes, unless it is `0` |
| string | yes, unless it is empty |
| bool | its own value |

```nachlang
print(is_truthy(0))
print(is_truthy(3))
print(is_truthy(""))
print(is_truthy("x"))
```
```output
bool(0)
bool(1)
bool(0)
bool(1)
```

## Expressions

### Arithmetic

`+`, `-`, `*` and `/` operate on numbers. `*` and `/` bind tighter than `+`
and `-`, all four group to the left, and parentheses override everything.

```nachlang
print(1 + 2 * 3)
print((1 + 2) * 3)
print(1 - 2 - 3)
print(8 / 2 / 2)
```
```output
7.000000
9.000000
-4.000000
2.000000
```

Division by zero does not raise. It follows IEEE 754: `1 / 0` is `inf` and
`0 / 0` is `nan`.

Arithmetic on a non-number is **not checked**. Applying `+` to a string reads
the string's unused number field and yields `nan` silently. Runtime type
checks are on the to-do list.

### Comparison

`==`, `!=`, `<`, `<=`, `>` and `>=` compare two values and return a boolean.
Numbers compare numerically. Strings compare by `strcmp`, so `"a" < "b"` is
true. Booleans compare as the integers 0 and 1, so `false < true`. Two values
of different kinds are never equal: `==` between them is false, `!=` is true,
and the ordering operators are false.

```nachlang
print(1 < 2)
print("a" == "a")
print("a" < "b")
print(true == true)
print(1 == "1")
print(1 != "1")
```
```output
bool(1)
bool(1)
bool(1)
bool(1)
bool(0)
bool(1)
```

Comparison binds looser than arithmetic and tighter than `and` and `or`, so
`2 + 3 * 4 == 14` and `1 < 2 and 3 < 4` both read the way they look. The
operators are left associative, which makes a chain like `1 < 2 < 3` mean
`(1 < 2) < 3` -- a boolean compared to a number, which is false. Chaining is
not a range test.

```nachlang
print(2 + 3 * 4 == 14)
print(1 < 2 and 3 < 4)
print(1 < 2 < 3)
```
```output
bool(1)
bool(1)
bool(0)
```

### Logical operators

`and` and `or` do not return booleans. Like Python's, they return one of
their operands:

- `a and b` is `b` if `a` is truthy, otherwise `a`
- `a or b` is `a` if `a` is truthy, otherwise `b`

`and` binds tighter than `or`. There is no `not`; use `is_truthy` and a
conditional.

```nachlang
print(1 and 2)
print(0 and 2)
print(0 or 5)
print("" or "fallback")
```
```output
2.000000
0.000000
5.000000
fallback
```

### Precedence, from tightest to loosest

| level | operators | grouping |
|---|---|---|
| 1 | parentheses, function calls | — |
| 2 | `*`  `/` | left |
| 3 | `+`  `-` | left |
| 4 | `==` `!=` `<` `<=` `>` `>=` | left |
| 5 | `and` | left |
| 6 | `or` | left |

The grammar lists `/` one level above `*`, but since `(a * b) / c` and
`a * (b / c)` are the same number, that is unobservable.

### Function calls

`name(arg arg ...)`. Arguments are expressions, separated by whitespace or by
commas. The number of arguments must match the definition; calling with the
wrong count is a compile-time error. A call is an expression and may appear
wherever a value may.

```nachlang
defn inc(n) { return n + 1 }
print(inc(inc(1)))
print(inc(3) * 2)
```
```output
3.000000
8.000000
```

## Statements

A program is a sequence of statements. There is no separator; the parser
knows where one ends. An expression on its own is a valid statement whose
value is discarded. A program with no statements at all -- an empty file, or
one holding only comments -- compiles to a program that does nothing.

### `def` — define a variable

`def name expression` creates `name` and gives it a value. Defining a name
that already exists in the same scope is an error.

### `mut` — change a variable

`mut name expression` replaces the value of an existing variable. Mutating a
name that does not exist is an error.

```nachlang
def x 1
print(x)
mut x (x + 4)
print(x)
```
```output
1.000000
5.000000
```

### `print` — write values

`print(a b ...)` writes each argument on its own line, in the format shown in
the Values table. `print()` with no arguments prints nothing. `print` is an
expression, and its value is the last argument it printed -- or the number
`0` if there were none -- so `def x print(5)` prints `5` and sets `x` to it.

```nachlang
print(1 "two" true)
```
```output
1.000000
two
bool(1)
```

### `if` — conditional

```
(if condition { statements })
(if condition { statements } { statements })
```

The whole form is wrapped in parentheses. The condition is any expression and
is tested for truthiness. The second block, if present, runs when the
condition is falsy. Either block may be empty: `{ }`.

```nachlang
def n 7
(if (n > 5) { print("big") } { print("small") })
(if ("") { print("never") })
print("done")
```
```output
big
done
```

### `loop` — while loop

```
(loop condition { statements })
```

Runs the body while the condition is truthy, testing before each iteration.
The body may be empty. There is no `break`.

```nachlang
def i 0
def total 0
(loop (i < 4) {
    mut total (total + i)
    mut i (i + 1)
})
print(total)
```
```output
6.000000
```

### `defn` — define a function

```
defn name(param param ...) { statements }
```

Parameters are names, separated by whitespace or commas. See Functions below.

### `return`

`return expression` leaves the current function with that value. A bare
`return` leaves with the number `0`, the same value a function produces by
running off the end of its body. A `return` outside any function is a syntax
error.

## Functions

A function takes a fixed number of parameters and returns one value. If
control reaches the end of the body without a `return`, the function returns
the number `0`; an empty body `{ }` is allowed and does exactly that.

```nachlang
defn shout(a) { print("side effect") }
print(shout(1))
```
```output
side effect
0.000000
```

Functions must be defined before they are called; there is no hoisting.
Defining the same name twice is an error. Recursion works, and a function may
call any function defined above it, including itself.

Parameters are ordinary local variables and may be mutated. Defining a local
with the same name as a parameter is an error, since both live in the
function's scope.

```nachlang
defn bump(n) {
    mut n (n + 1)
    return n
}
print(bump(1))
```
```output
2.000000
```

A function may be defined inside another function. It is simply a function;
it does not close over anything.

### Scope

There are two kinds of scope: the top level, and each function body.

A function can read and mutate variables defined at the top level. A local
defined with the same name shadows the top-level one inside that function
only, and locals do not escape the function that defined them.

```nachlang
def counter 0
defn bump() {
    mut counter (counter + 1)
    return counter
}
print(bump())
print(bump())
print(counter)
```
```output
1.000000
2.000000
2.000000
```

```nachlang
def x 1
defn f() {
    def x 99
    return x
}
print(f())
print(x)
```
```output
99.000000
1.000000
```

Functions reach top-level variables but **not** the locals of an enclosing
function: there are no closures.

**Blocks are not scopes**, and this is a sharp edge. A `def` inside an `if`
or `loop` body is visible after the block as far as the compiler's name
resolution is concerned, but the storage it created belongs to the block, so
reading it after the block crashes the compiler with an LLVM error
("Instruction does not dominate all uses"). A variable that must be read
after a block should be defined before it and assigned with `mut` inside.
Using the variable only inside the block that defined it is fine.

```nachlang
def result 0
(if (true) { mut result 3 })
print(result)
```
```output
3.000000
```

## Errors

Errors are written to standard error, never mixed into the program's output,
and the process exits with status 1. Errors in the program are reported
plainly; a failure inside the compiler is prefixed `internal error:` so the
two are not confused.

| situation | message |
|---|---|
| bad token | `line 1, column 5: unexpected NUMBER '1'` |
| bad character | `line 1, column 5: unexpected character '$'` |
| truncated input | `unexpected end of input` |
| unknown escape | `line 1, column 7: unknown escape '\p' in string` |
| unknown variable | `'nope' couldn't be found in scope` |
| duplicate variable | `'x' already exists in scope` |
| unknown function | `'nosuchfn' is not a defined function` |
| duplicate function | `'f' is already defined` |
| wrong arity | `'f' takes 2 argument(s), got 1` |
| return outside a function | `line 1, column 1: 'return' outside of a function` |

A program that runs to completion exits with status 0.

## Known limitations

The compiler has no runtime type checking, so operations on values of the
wrong kind produce garbage rather than errors. Apart from that, the gaps in
the language as implemented are:

- A `def` inside a block cannot be read after the block.
- No negative or decimal literals, no `not`, no `break`, no `else if`.
- No string operations beyond printing and comparison: no concatenation,
  length or indexing.
- No closures and no lambdas.
- Nothing is ever freed. A long-running program grows without bound unless
  compiled with `--libgc-path` to use the Boehm collector.

The first is a bug; the rest are features not yet built. All are tracked
in `TODOS.md`.

## Grammar

The grammar as implemented in `nachlang/parser.py`, in EBNF. Terminals are
the token names used there.

```
program        = { statement } ;

statement      = expression
               | "def" NAME expression
               | "mut" NAME expression
               | if_statement
               | loop_statement
               | define_function
               | "return" [ expression ] ;

if_statement   = "(" "if" expression block [ block ] ")" ;
loop_statement = "(" "loop" expression block ")" ;
block          = "{" { statement } "}" ;

define_function = "defn" NAME "(" { NAME } ")" block ;

expression     = "(" expression ")"
               | NUMBER | STRING | BOOL | NAME
               | expression binary_op expression
               | NAME "(" { expression } ")"
               | "print" "(" { expression } ")"
               | "is_truthy" "(" expression ")" ;

binary_op      = "+" | "-" | "*" | "/"
               | "==" | "!=" | "<" | "<=" | ">" | ">="
               | "and" | "or" ;
```

Commas are consumed by the lexer and never reach the grammar, which is why
they appear nowhere above. The grammar is ambiguous as written -- rply
reports 50 shift/reduce and 9 reduce/reduce conflicts, down from 122 before
the comparison operators had a precedence level -- and relies on its
precedence table and on rply's default of shifting to resolve the rest.
