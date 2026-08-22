import pytest
from rply.errors import ParsingError

from nachlang.parser import parse

VALID_PROGRAMS = [
    ("number", "1"),
    ("arithmetic", "1 + 2 * 3"),
    ("parenthesised", "(1 + 2) * 3"),
    ("comparison", "1 <= 2"),
    ("logical", "1 and 2 or 3"),
    ("string", '"hello"'),
    ("bool", "true"),
    ("define variable", "def a 1"),
    ("mutate variable", "def a 1 mut a 2"),
    ("if", "(if (1 < 2) { print(1) })"),
    ("if else", "(if (1 < 2) { print(1) } { print(2) })"),
    ("loop", "def i 0 (loop (i < 3) { mut i (i + 1) })"),
    ("function no args", "defn f() { return 1 }"),
    ("function one arg", "defn f(a) { return a }"),
    ("function many args", "defn f(a b c) { return a + b + c }"),
    ("call", "defn f(a) { return a } f(1)"),
    ("nested call", "defn f(a) { return a } f(f(1))"),
    ("is_truthy", "is_truthy(1)"),
    ("leading comment", "# explain\nprint(1)"),
    ("comma separated params", "defn f(a, b) { return a + b }"),
    ("comma separated args", "defn f(a b) { return a } f(1, 2)"),
    ("trailing comma", "defn f(a, b,) { return a }"),
    ("tab indented", "def\tx\t1"),
]

INVALID_PROGRAMS = [
    ("number as variable name", "def 1 1"),
    ("unclosed call", "print("),
    ("unclosed block", "(if (1) {"),
    ("missing if parens", "if (1) { print(1) }"),
    ("dangling operator", "1 +"),
]


@pytest.mark.parametrize(
    "source", [s for _, s in VALID_PROGRAMS], ids=[n for n, _ in VALID_PROGRAMS]
)
def test_valid_program_parses(source):
    assert parse(source)["name"] == "statement_list"


@pytest.mark.parametrize(
    "source", [s for _, s in INVALID_PROGRAMS], ids=[n for n, _ in INVALID_PROGRAMS]
)
def test_invalid_program_is_rejected(source):
    with pytest.raises(ParsingError):
        parse(source)


# A keyword matching inside a longer identifier used to leave a stray token
# behind and fail to parse, so this belongs at the parser level too.
@pytest.mark.parametrize(
    "identifier", ["order", "printer", "define", "android", "returns", "truest"]
)
def test_keyword_prefixed_name_works_as_a_variable(identifier):
    assert parse(f"def {identifier} 1")["name"] == "statement_list"


@pytest.mark.parametrize("identifier", ["order", "printer", "define"])
def test_keyword_prefixed_name_works_as_a_function(identifier):
    assert parse(f"defn {identifier}(a) {{ return a }}")["name"] == "statement_list"


@pytest.mark.parametrize(
    "with_commas,without",
    [
        ("defn f(a, b) { return a + b }", "defn f(a b) { return a + b }"),
        ("defn f(a b) { return a } f(1, 2)", "defn f(a b) { return a } f(1 2)"),
    ],
)
def test_commas_are_decorative(with_commas, without):
    assert parse(with_commas) == parse(without)


def test_statement_list_holds_every_statement():
    assert len(parse("def a 1 def b 2 def c 3")["value"]) == 3


def test_nested_structure_is_preserved():
    tree = parse("defn f(a) { return a }")
    assert tree["value"][0]["name"] == "statement"
    assert tree["value"][0]["value"][0]["name"] == "define_function"
