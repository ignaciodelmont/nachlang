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
