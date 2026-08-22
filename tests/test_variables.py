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


# A top level variable lives in a module global, so a function body can reach
# it. It used to be a stack slot in main's frame, which produced invalid IR.
def test_function_can_read_a_top_level_variable(nach):
    source = """
        def base 10
        defn add_base(n) { return n + base }
        print(add_base(5))
    """
    assert nach.output(source) == [num(15)]


def test_function_can_mutate_a_top_level_variable(nach):
    source = """
        def counter 0
        defn bump() {
            mut counter (counter + 1)
            return counter
        }
        print(bump())
        print(bump())
        print(counter)
    """
    assert nach.output(source) == [num(1), num(2), num(2)]


def test_function_can_read_a_top_level_string(nach):
    source = """
        def greeting "hi"
        defn greet() { return greeting }
        print(greet())
    """
    assert nach.output(source) == ["hi"]


def test_a_local_of_the_same_name_shadows_the_outer_one(nach):
    source = """
        def x 1
        defn f() {
            def x 99
            return x
        }
        print(f())
        print(x)
    """
    assert nach.output(source) == [num(99), num(1)]


def test_a_local_does_not_escape_its_function(nach):
    result = nach.run("defn f() { def y 5 return y } print(f()) print(y)")
    assert result.returncode != 0
    assert "'y' couldn't be found in scope" in result.stderr


def test_two_functions_share_one_top_level_variable(nach):
    source = """
        def total 0
        defn add_one() { mut total (total + 1) }
        defn add_ten() { mut total (total + 10) }
        add_one()
        add_ten()
        print(total)
    """
    assert nach.output(source) == [num(11)]


def test_a_top_level_name_may_match_a_runtime_global(nach):
    assert nach.output("def printf_format 7 print(printf_format)") == [num(7)]
