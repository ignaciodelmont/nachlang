"""
Documented gaps in the language.

These are strict xfails, so fixing one turns the suite red until the test is
promoted into a real expectation. That is deliberate: nothing here should be
fixed silently, and the list doubles as a to-do.
"""

import pytest

from tests.helpers import num


@pytest.mark.xfail(strict=True, reason="COMMA is lexed but has no grammar rule")
def test_arguments_may_be_comma_separated(nach):
    source = """
        defn plus(a, b) { return a + b }
        print(plus(2, 3))
    """
    assert nach.output(source) == [num(5)]


@pytest.mark.xfail(
    strict=True, reason="functions cannot reach variables in an outer scope"
)
def test_function_can_read_an_outer_variable(nach):
    source = """
        def base 10
        defn add_base(n) { return n + base }
        print(add_base(5))
    """
    assert nach.output(source) == [num(15)]


@pytest.mark.xfail(
    strict=True,
    reason="user functions share the module namespace with runtime symbols",
)
@pytest.mark.parametrize("name", ["add", "sub", "mul", "div", "printf", "malloc"])
def test_function_may_be_named_like_a_runtime_symbol(nach, name):
    source = f"""
        defn {name}(a) {{ return a }}
        print({name}(1))
    """
    assert nach.output(source) == [num(1)]


@pytest.mark.xfail(strict=True, reason="print resolves only its first argument")
def test_print_accepts_several_arguments(nach):
    assert nach.output("print(1 2)") == [num(1), num(2)]


@pytest.mark.xfail(strict=True, reason="the lexer has no string escape handling")
def test_string_may_contain_an_escaped_quote(nach):
    assert nach.output(r'print("say \"hi\"")') == ['say "hi"']


@pytest.mark.xfail(strict=True, reason="the grammar requires at least one statement")
@pytest.mark.parametrize(
    "source", ["", "# only a comment", "\n\n"], ids=["empty", "comment only", "blank"]
)
def test_program_without_statements_is_a_no_op(nach, source):
    assert nach.output(source) == []


@pytest.mark.xfail(strict=True, reason="errors are printed to stdout instead of stderr")
def test_errors_go_to_stderr(nach):
    result = nach.run("print(nope)")
    assert result.stderr.strip()
    assert not result.stdout.strip()


@pytest.mark.xfail(
    strict=True, reason="parse errors report a raw tuple with no explanation"
)
def test_parse_error_explains_itself(nach):
    result = nach.run("def 1 1")
    message = result.stdout + result.stderr
    assert "line 1" in message.lower()
