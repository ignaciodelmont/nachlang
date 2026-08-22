import pytest

from tests.helpers import num


def test_no_arguments(nach):
    assert nach.output("defn five() { return 5 } print(five())") == [num(5)]


def test_one_argument(nach):
    assert nach.output("defn identity(a) { return a } print(identity(3))") == [num(3)]


def test_two_arguments(nach):
    source = """
        defn plus(a b) { return a + b }
        print(plus(2 3))
    """
    assert nach.output(source) == [num(5)]


def test_three_arguments(nach):
    source = """
        defn total(a b c) { return a + b + c }
        print(total(1 2 3))
    """
    assert nach.output(source) == [num(6)]


def test_nested_calls(nach):
    source = """
        defn inc(n) { return n + 1 }
        print(inc(inc(1)))
    """
    assert nach.output(source) == [num(3)]


def test_call_as_an_operand(nach):
    source = """
        defn double(n) { return n * 2 }
        print(double(3) + 1)
    """
    assert nach.output(source) == [num(7)]


def test_falling_off_the_end_returns_zero(nach):
    source = """
        defn shout(a) { print("side effect") }
        print(shout(1))
    """
    assert nach.output(source) == ["side effect", num(0)]


def test_early_return_from_a_conditional(nach):
    source = """
        defn sign(n) {
            (if (n < 0) { return 0 })
            return 1
        }
        print(sign(0 - 5))
        print(sign(5))
    """
    assert nach.output(source) == [num(0), num(1)]


def test_recursion(nach):
    source = """
        defn fib(n) {
            (if (n <= 1) { return n })
            return (fib((n - 1)) + fib((n - 2)))
        }
        print(fib(10))
    """
    assert nach.output(source) == [num(55)]


def test_arguments_are_mutable_locals(nach):
    source = """
        defn bump(n) {
            mut n (n + 1)
            return n
        }
        print(bump(1))
    """
    assert nach.output(source) == [num(2)]


def test_local_variables_do_not_leak_into_the_caller(nach):
    source = """
        defn make() {
            def hidden 42
            return hidden
        }
        print(make())
        def hidden 1
        print(hidden)
    """
    assert nach.output(source) == [num(42), num(1)]


def test_a_function_may_contain_a_loop(nach):
    source = """
        defn total_to(limit) {
            def i 0
            def total 0
            (loop (i <= limit) {
                mut total (total + i)
                mut i (i + 1)
            })
            return total
        }
        print(total_to(4))
    """
    assert nach.output(source) == [num(10)]


def test_calling_another_function(nach):
    source = """
        defn inc(n) { return n + 1 }
        defn inc_twice(n) { return inc(inc(n)) }
        print(inc_twice(1))
    """
    assert nach.output(source) == [num(3)]


def test_string_returning_function(nach):
    source = """
        defn greeting() { return "hello" }
        print(greeting())
    """
    assert nach.output(source) == ["hello"]


def test_parameters_may_be_comma_separated(nach):
    source = """
        defn plus(a, b) { return a + b }
        print(plus(2 3))
    """
    assert nach.output(source) == [num(5)]


def test_arguments_may_be_comma_separated(nach):
    source = """
        defn plus(a b) { return a + b }
        print(plus(2, 3))
    """
    assert nach.output(source) == [num(5)]


def test_commas_are_optional_on_both_sides(nach):
    source = """
        defn total(a, b, c) { return a + b + c }
        print(total(1, 2, 3))
        print(total(1 2 3))
    """
    assert nach.output(source) == [num(6), num(6)]


def test_trailing_comma_is_allowed(nach):
    source = """
        defn plus(a, b,) { return a + b }
        print(plus(2, 3,))
    """
    assert nach.output(source) == [num(5)]


def test_tab_indented_source_compiles(nach):
    assert nach.output("defn f(a) {\n\treturn a + 1\n}\nprint(f(1))") == [num(2)]


@pytest.mark.parametrize("identifier", ["order", "printer", "define"])
def test_name_may_start_with_a_keyword(nach, identifier):
    source = f"""
        defn {identifier}(a) {{ return a + 1 }}
        print({identifier}(1))
    """
    assert nach.output(source) == [num(2)]
