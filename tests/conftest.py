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
        }

    ]