import pytest

from tests.helpers import num


def test_define_and_read(nach):
    assert nach.output("def x 1 print(x)") == [num(1)]


def test_mutate(nach):
    assert nach.output("def x 1 print(x) mut x 9 print(x)") == [num(1), num(9)]


def test_define_from_an_expression(nach):
    assert nach.output("def x (2 * 3) print(x)") == [num(6)]


def test_mutate_using_its_own_value(nach):
    assert nach.output("def x 1 mut x (x + 4) print(x)") == [num(5)]


def test_holds_a_string(nach):
    assert nach.output('def greeting "hi" print(greeting)') == ["hi"]


def test_holds_a_bool(nach):
    assert nach.output("def flag true print(is_truthy(flag))") == ["bool(1)"]


def test_several_variables_are_independent(nach):
    assert nach.output("def a 1 def b 2 mut a 9 print(a) print(b)") == [
        num(9),
        num(2),
    ]


@pytest.mark.parametrize(
    "identifier", ["order", "printer", "define", "android", "returns", "truest"]
)
def test_name_may_start_with_a_keyword(nach, identifier):
    assert nach.output(f"def {identifier} 5 print({identifier})") == [num(5)]
