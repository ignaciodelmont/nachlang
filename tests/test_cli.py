"""Exit statuses, error reporting, and the compiler flags."""

import pytest

from tests.helpers import num

# Exercises recursion, a loop and mutation at once, so an optimizer that
# breaks any of them shows up here.
MIXED_PROGRAM = """
    defn fib(n) {
        (if (n <= 1) { return n })
        return (fib((n - 1)) + fib((n - 2)))
    }
    def i 0
    def total 0
    (loop (i < 5) {
        mut total (total + i)
        mut i (i + 1)
    })
    print(fib(12))
    print(total)
"""


def test_success_exits_zero(nach):
    assert nach.run("print(1)").returncode == 0


def test_parse_error_exits_nonzero(nach):
    assert nach.run("def 1 1").returncode != 0


def test_unknown_variable_is_reported(nach):
    result = nach.run("print(nope)")
    assert result.returncode != 0
    assert "couldn't be found in scope" in result.stderr


def test_redefining_a_variable_is_reported(nach):
    result = nach.run("def x 1 def x 2")
    assert result.returncode != 0
    assert "already exists in scope" in result.stderr


def test_errors_go_to_stderr_not_stdout(nach):
    result = nach.run("print(nope)")
    assert result.stderr.strip()
    assert not result.stdout.strip()


def test_parse_error_names_the_token_and_position(nach):
    result = nach.run("def 1 1")
    assert "line 1, column 5" in result.stderr
    assert "unexpected NUMBER '1'" in result.stderr


def test_unexpected_character_is_reported(nach):
    result = nach.run("def x $")
    assert "unexpected character '$'" in result.stderr


def test_author_errors_are_not_labelled_internal(nach):
    result = nach.run("print(nope)")
    assert "internal error" not in result.stderr


def test_empty_program_succeeds(nach):
    assert nach.output("") == []


def test_comment_only_program_succeeds(nach):
    assert nach.output("# nothing at all") == []


@pytest.mark.parametrize("level", ["0", "1", "2", "3"])
def test_optimization_level_does_not_change_the_result(nach, level):
    assert nach.output(MIXED_PROGRAM, "--opt-level", level) == [num(144), num(10)]


def test_compile_only_produces_no_output(nach):
    assert nach.output("print(1)", "--compile-only") == []


def test_output_ll_writes_the_module(nach, tmp_path):
    nach.output("print(1)", "--output-ll", "--compile-only")
    emitted = list(tmp_path.glob("*.nach.ll"))
    assert len(emitted) == 1
    text = emitted[0].read_text(encoding="utf-8")
    assert 'define i32 @"main"()' in text


def test_emitted_module_declares_plain_malloc_by_default(nach, tmp_path):
    nach.output("print(1)", "--output-ll", "--compile-only")
    text = next(tmp_path.glob("*.nach.ll")).read_text(encoding="utf-8")
    assert '@"malloc"' in text
    assert "GC_malloc" not in text


def test_calling_an_undefined_function_is_reported(nach):
    result = nach.run("print(nosuchfn(1))")
    assert result.returncode != 0
    assert "'nosuchfn' is not a defined function" in result.stderr


def test_defining_a_function_twice_is_reported(nach):
    result = nach.run("defn f(a) { return a } defn f(a) { return a }")
    assert result.returncode != 0
    assert "'f' is already defined" in result.stderr


def test_calling_with_too_few_arguments_is_reported(nach):
    result = nach.run("defn f(a b) { return a } print(f(1))")
    assert result.returncode != 0
    assert "takes 2 argument(s), got 1" in result.stderr


def test_calling_with_too_many_arguments_is_reported(nach):
    result = nach.run("defn f(a) { return a } print(f(1 2))")
    assert result.returncode != 0
    assert "takes 1 argument(s), got 2" in result.stderr
