from nachlang.lexer import lexer
from tests.utils import get_raw_tokens


def test_tokens(snapshot):
    program = """if loop return true false ( ) { } <= >= < > =
    string number
    # this should be ignored \n
    + -
    / *
    123
    "hello from nachlang" 4 + def
    """
    tokens = lexer.lex(program)
    snapshot.assert_match(get_raw_tokens(tokens), "Test all tokens")