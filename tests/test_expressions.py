"""
Literals, arithmetic, comparisons and the logical operators, exercised by
compiling and running real programs.
"""

import pytest

from tests.helpers import FALSE, TRUE, num


def test_prints_a_number(nach):
    assert nach.output("print(7)") == [num(7)]


def test_prints_a_string(nach):
    assert nach.output('print("hey there")') == ["hey there"]


def test_prints_booleans(nach):
    assert nach.output("print(true) print(false)") == [TRUE, FALSE]


def test_statements_run_in_order(nach):
    assert nach.output('print(1) print("two") print(true)') == [num(1), "two", TRUE]


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("1 + 1", num(2)),
        ("1 - 5", num(-4)),
        ("3 * 4", num(12)),
        ("7 / 2", num(3.5)),
    ],
)
def test_arithmetic_operator(nach, expression, expected):
    assert nach.output(f"print({expression})") == [expected]


def test_multiplication_binds_tighter_than_addition(nach):
    assert nach.output("print(1 + 2 * 3)") == [num(7)]


def test_parentheses_override_precedence(nach):
    assert nach.output("print((1 + 2) * 3)") == [num(9)]


def test_numbers_are_floating_point(nach):
    assert nach.output("print(1 / 3)") == ["0.333333"]


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("1 < 2", TRUE),
        ("2 < 1", FALSE),
        ("2 > 1", TRUE),
        ("1 <= 1", TRUE),
        ("1 >= 2", FALSE),
        ("1 == 1", TRUE),
        ("1 != 1", FALSE),
    ],
)
def test_number_comparison(nach, expression, expected):
    assert nach.output(f"print({expression})") == [expected]


@pytest.mark.parametrize(
    "expression,expected",
    [
        ('"a" == "a"', TRUE),
        ('"a" == "b"', FALSE),
        ('"a" != "b"', TRUE),
    ],
)
def test_string_comparison(nach, expression, expected):
    assert nach.output(f"print({expression})") == [expected]


def test_and_yields_the_second_operand_when_the_first_is_truthy(nach):
    assert nach.output("print(1 and 2)") == [num(2)]


def test_and_yields_the_first_operand_when_it_is_falsy(nach):
    assert nach.output("print(0 and 2)") == [num(0)]


def test_or_yields_the_first_truthy_operand(nach):
    assert nach.output("print(1 or 2)") == [num(1)]


def test_or_falls_through_to_the_second_operand(nach):
    assert nach.output("print(0 or 5)") == [num(5)]


@pytest.mark.parametrize(
    "value,expected",
    [
        ("0", FALSE),
        ("3", TRUE),
        ('""', FALSE),
        ('"x"', TRUE),
        ("true", TRUE),
        ("false", FALSE),
    ],
)
def test_is_truthy(nach, value, expected):
    assert nach.output(f"print(is_truthy({value}))") == [expected]


def test_print_takes_several_arguments(nach):
    assert nach.output('print(1 2 "three" true)') == [
        num(1),
        num(2),
        "three",
        TRUE,
    ]


def test_print_arguments_may_be_comma_separated(nach):
    assert nach.output("print(1, 2, 3)") == [num(1), num(2), num(3)]


def test_print_with_no_arguments_prints_nothing(nach):
    assert nach.output("print() print(1)") == [num(1)]


def test_print_evaluates_each_argument(nach):
    assert nach.output("def x 2 print(x + 1, x * 3)") == [num(3), num(6)]


def test_leading_comment_is_ignored(nach):
    assert nach.output("# a comment\nprint(1)") == [num(1)]


def test_trailing_comment_is_ignored(nach):
    assert nach.output("print(1) # explain") == [num(1)]


def test_string_may_contain_an_escaped_quote(nach):
    assert nach.output(r'print("say \"hi\"")') == ['say "hi"']


def test_string_may_contain_a_backslash(nach):
    assert nach.output(r'print("C:\\path")') == [r"C:\path"]


def test_string_supports_newline_and_tab_escapes(nach):
    assert nach.output(r'print("a\nb") print("x\ty")') == ["a", "b", "x\ty"]


def test_string_may_hold_non_ascii_text(nach):
    assert nach.output('print("héllo wörld")') == ["héllo wörld"]


def test_empty_string_prints_an_empty_line(nach):
    assert nach.output('print("")') == [""]


def test_two_strings_on_one_line_stay_separate(nach):
    assert nach.output('print("a") print("b")') == ["a", "b"]


def test_escaped_quotes_compare_equal(nach):
    assert nach.output(r'print("\"" == "\"")') == [TRUE]


def test_unknown_escape_is_rejected(nach):
    result = nach.run(r'print("C:\path")')
    assert result.returncode != 0
    assert r"unknown escape '\p'" in result.stderr


# Booleans are tag 2. The comparison dispatch only knew tags 0 and 1, so every
# comparison of two booleans used to fall through to "false".
@pytest.mark.parametrize(
    "expression,expected",
    [
        ("true == true", TRUE),
        ("false == false", TRUE),
        ("true == false", FALSE),
        ("true != false", TRUE),
        ("true != true", FALSE),
        ("(1 < 2) == true", TRUE),
        ("false < true", TRUE),
        ("true > false", TRUE),
        ("true <= true", TRUE),
    ],
)
def test_bool_comparison(nach, expression, expected):
    assert nach.output(f"print({expression})") == [expected]


# The type check used to be computed and discarded, with the comparison then
# dispatching on the left operand alone and reading garbage from the right.
@pytest.mark.parametrize(
    "expression,expected",
    [
        ('1 == "1"', FALSE),
        ('1 != "1"', TRUE),
        ('"1" != 1', TRUE),
        ("1 == true", FALSE),
        ("1 != true", TRUE),
        ('"a" == true', FALSE),
        ('"a" != true', TRUE),
        ("0 == false", FALSE),
        ("0 != false", TRUE),
        ('1 < "2"', FALSE),
    ],
)
def test_values_of_different_kinds_are_never_equal(nach, expression, expected):
    assert nach.output(f"print({expression})") == [expected]


# Comparison operators used to have no precedence entry, which made them bind
# looser than `and` and `or`: `1 < 2 and 3 < 4` parsed as `1 < (2 and (3 < 4))`.
@pytest.mark.parametrize(
    "expression,expected",
    [
        ("1 < 2 and 3 < 4", TRUE),
        ("1 < 2 and 3 > 4", FALSE),
        ("1 < 2 or 5 < 4", TRUE),
        ("1 > 2 or 5 < 4", FALSE),
        ("(1 < 2) and (3 < 4)", TRUE),
        ("2 + 3 * 4 == 14", TRUE),
        ("1 == 1 == true", TRUE),
    ],
)
def test_comparison_binds_tighter_than_logical_operators(nach, expression, expected):
    assert nach.output(f"print({expression})") == [expected]


def test_chained_comparison_compares_a_bool_to_a_number(nach):
    # Left-associative: (1 < 2) < 3 is true < 3, a mixed-kind comparison.
    assert nach.output("print(1 < 2 < 3)") == [FALSE]


# print is an expression, so it has a value: the last thing it printed.
def test_print_yields_its_last_argument(nach):
    assert nach.output("def x print(5) print(x + 1)") == [num(5), num(6)]


def test_print_of_several_yields_the_last(nach):
    assert nach.output("def x print(1 2 3) print(x)") == [
        num(1),
        num(2),
        num(3),
        num(3),
    ]


def test_print_of_nothing_yields_zero(nach):
    assert nach.output("def x print() print(x)") == [num(0)]
