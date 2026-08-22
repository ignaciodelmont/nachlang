"""
Documented gaps in the language.

These are strict xfails, so fixing one turns the suite red until the test is
promoted into a real expectation. That is deliberate: nothing here should be
fixed silently, and the list doubles as a to-do.
"""

import pytest

from tests.helpers import num


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
