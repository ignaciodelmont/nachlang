import pytest

from nachlang.lexer import lexer


def tokenize(source):
    return [(token.name, token.value) for token in lexer.lex(source)]


def names(source):
    return [name for name, _ in tokenize(source)]


KEYWORDS = [
    ("print", "PRINT"),
    ("if", "IF"),
    ("loop", "LOOP"),
    ("return", "RETURN"),
    ("true", "BOOL"),
    ("false", "BOOL"),
    ("is_truthy", "IS_TRUTHY"),
    ("and", "AND"),
    ("or", "OR"),
    ("defn", "DEFN"),
    ("def", "DEF"),
    ("mut", "MUT"),
]

# Every one of these begins with a reserved word. They are the regression
# cases for keywords matching inside longer identifiers, which used to split
# `order` into OR and a variable called `der`.
KEYWORD_PREFIXED_IDENTIFIERS = [
    "printer",
    "iffy",
    "looping",
    "returns",
    "truest",
    "falsehood",
    "is_truthyish",
    "android",
    "order",
    "defnition",
    "define",
    "mutation",
]


def test_lexes_a_number():
    assert tokenize("123") == [("NUMBER", "123")]


def test_lexes_a_string():
    assert tokenize('"hello there"') == [("STRING", '"hello there"')]


@pytest.mark.parametrize("literal", ["true", "false"])
def test_lexes_a_bool(literal):
    assert tokenize(literal) == [("BOOL", literal)]


def test_lexes_an_identifier():
    assert tokenize("some_var1") == [("VAR", "some_var1")]


def test_identifier_may_start_with_an_underscore():
    assert tokenize("_private") == [("VAR", "_private")]


@pytest.mark.parametrize("source,expected", KEYWORDS)
def test_keyword_lexes_as_itself(source, expected):
    assert tokenize(source) == [(expected, source)]


@pytest.mark.parametrize("identifier", KEYWORD_PREFIXED_IDENTIFIERS)
def test_identifier_starting_with_keyword_stays_whole(identifier):
    assert tokenize(identifier) == [("VAR", identifier)]


@pytest.mark.parametrize("identifier", KEYWORD_PREFIXED_IDENTIFIERS)
def test_identifier_starting_with_keyword_works_as_a_variable(identifier):
    assert names(f"def {identifier} 1") == ["DEF", "VAR", "NUMBER"]


def test_keyword_still_matches_when_followed_by_punctuation():
    assert names("print(1)") == ["PRINT", "OPEN_PAREN", "NUMBER", "CLOSE_PAREN"]


def test_defn_is_not_read_as_def():
    assert names("defn f()") == ["DEFN", "VAR", "OPEN_PAREN", "CLOSE_PAREN"]


@pytest.mark.parametrize(
    "source,expected",
    [
        ("+", "PLUS_SIGN"),
        ("-", "MINUS_SIGN"),
        ("*", "MULTIPLICATION_SIGN"),
        ("/", "DIVISION_SIGN"),
        ("<", "LT"),
        (">", "GT"),
        ("<=", "LTE"),
        (">=", "GTE"),
        ("==", "EQ"),
        ("!=", "NEQ"),
        ("=", "ASSIGN"),
        (",", "COMMA"),
    ],
)
def test_lexes_an_operator(source, expected):
    assert tokenize(source) == [(expected, source)]


def test_two_character_operators_win_over_one():
    assert names("<= >= == !=") == ["LTE", "GTE", "EQ", "NEQ"]


def test_comment_is_dropped():
    assert tokenize("# nothing to see") == []


def test_trailing_comment_is_dropped():
    assert names("print(1) # explain") == [
        "PRINT",
        "OPEN_PAREN",
        "NUMBER",
        "CLOSE_PAREN",
    ]


def test_whitespace_and_newlines_are_dropped():
    assert names("def\n  x\n  1") == ["DEF", "VAR", "NUMBER"]


def test_lexes_a_function_definition():
    assert names("defn add_two(a b) { return a + b }") == [
        "DEFN",
        "VAR",
        "OPEN_PAREN",
        "VAR",
        "VAR",
        "CLOSE_PAREN",
        "OPEN_CURLY_BRA",
        "RETURN",
        "VAR",
        "PLUS_SIGN",
        "VAR",
        "CLOSE_CURLY_BRA",
    ]


def test_lexes_a_loop():
    assert names("(loop (i < 3) { mut i (i + 1) })") == [
        "OPEN_PAREN",
        "LOOP",
        "OPEN_PAREN",
        "VAR",
        "LT",
        "NUMBER",
        "CLOSE_PAREN",
        "OPEN_CURLY_BRA",
        "MUT",
        "VAR",
        "OPEN_PAREN",
        "VAR",
        "PLUS_SIGN",
        "NUMBER",
        "CLOSE_PAREN",
        "CLOSE_CURLY_BRA",
        "CLOSE_PAREN",
    ]
