from tests.helpers import num


def test_taken_branch_runs(nach):
    assert nach.output('(if (1 < 2) { print("yes") })') == ["yes"]


def test_untaken_branch_is_skipped(nach):
    assert nach.output('(if (2 < 1) { print("yes") }) print("after")') == ["after"]


def test_else_branch_runs(nach):
    assert nach.output('(if (2 < 1) { print("a") } { print("b") })') == ["b"]


def test_condition_uses_truthiness_not_only_booleans(nach):
    assert nach.output('(if (1) { print("truthy") })') == ["truthy"]


def test_falsy_condition_skips_the_branch(nach):
    assert nach.output('(if (0) { print("no") }) print("done")') == ["done"]


def test_branch_may_hold_several_statements(nach):
    source = """
        (if (1 < 2) {
            print("one")
            print("two")
        })
    """
    assert nach.output(source) == ["one", "two"]


def test_nested_conditionals(nach):
    source = """
        (if (1 < 2) {
            (if (2 < 3) { print("inner") })
        })
    """
    assert nach.output(source) == ["inner"]


def test_loop_counts(nach):
    source = """
        def i 0
        (loop (i < 3) {
            print(i)
            mut i (i + 1)
        })
    """
    assert nach.output(source) == [num(0), num(1), num(2)]


def test_loop_accumulates(nach):
    source = """
        def total 0
        def i 1
        (loop (i <= 4) {
            mut total (total + i)
            mut i (i + 1)
        })
        print(total)
    """
    assert nach.output(source) == [num(10)]


def test_loop_body_never_runs_when_condition_starts_false(nach):
    source = """
        def i 10
        (loop (i < 3) { print(i) })
        print("done")
    """
    assert nach.output(source) == ["done"]


def test_loop_containing_a_conditional(nach):
    source = """
        def i 0
        (loop (i < 4) {
            (if (i == 2) { print("hit") })
            mut i (i + 1)
        })
    """
    assert nach.output(source) == ["hit"]


# An empty body used to be a syntax error.
def test_if_with_an_empty_body(nach):
    assert nach.output("(if (true) { }) print(1)") == [num(1)]


def test_if_with_an_empty_else(nach):
    assert nach.output("(if (false) { print(0) } { }) print(2)") == [num(2)]


def test_if_with_an_empty_then_and_a_real_else(nach):
    assert nach.output("(if (true) { } { print(0) }) print(3)") == [num(3)]


def test_loop_with_an_empty_body(nach):
    assert nach.output("def i 0 (loop (i < 0) { }) print(4)") == [num(4)]
