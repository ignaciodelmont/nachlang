import pytest

@pytest.fixture
def code_samples():
    return [
        {
            "name": "constant",
            "code": "2"
        },
        {
            "name": "add constants",
            "code": "1 + 1"
        },
        {
            "name": "multiply constants",
            "code": "2 * 1"
        },
        {
            "name": "divide constants",
            "code": "4 / 2"
        },
        {
            "name": "substract contsants",
            "code": "21 - 123"
        },
        {
            "name": "arithmetic precedence",
            "code": "1 + 3 * 9 / 1 - 4 / 5 * (1 + 9)"
        },
        {
            "name": "logical ops precedence",
            "code": "1 and 2 or 3 or 4 and 5 and 6 and (1 or 2)"
        },
        {
            "name": "logical ops and arithmetic ops precedence",
            "code": "1 * 3 and 1 + 5 or 23 and (1 or 3)"
        },
        {
            "name": "variable definition",
            "code": "def a 1"
        },
        {
            "name": "variable definition and usage",
            "code": """
                def a 1
                a + 3
            """
        },
        {
            "name": "if/else statement",
            "code": """
            (
                if (1 < 3)
                {
                    def a 1
                    a + 4
                }
                {
                    5 + 3
                }
            )
            """
        },
        {
            "name": "if statement",
            "code": """
            (
                if (1 < 3)
                {
                    def a 1
                    a + 4
                }
            )
            """
        }
    ]