import rply

lexer_generator = rply.LexerGenerator()


def keyword(pattern):
    """
    Builds a keyword pattern that cannot match inside a longer identifier.

    Rules are tried in order and the first match wins, so without the trailing
    word boundary `print` would match the first five characters of `printer`
    and leave `er` behind as a separate variable. Every reserved word needs
    this, not just the short ones.
    """
    return rf"(?:{pattern})\b"


tokens = [
    # Print
    ("PRINT", keyword(r"print")),
    # Conditional
    ("IF", keyword(r"if")),
    # Function
    ("LOOP", keyword(r"loop")),
    ("RETURN", keyword(r"return")),
    # Booleans
    ("BOOL", keyword(r"true|false")),
    ("IS_TRUTHY", keyword(r"is_truthy")),
    # Parenthesis
    ("OPEN_PAREN", r"\("),
    ("CLOSE_PAREN", r"\)"),
    # Curly brackets
    ("OPEN_CURLY_BRA", r"\{"),
    ("CLOSE_CURLY_BRA", r"\}"),
    # Operators
    ("DIVISION_SIGN", r"\/"),
    ("MULTIPLICATION_SIGN", r"\*"),
    ("PLUS_SIGN", r"\+"),
    ("MINUS_SIGN", r"\-"),
    # Conditional Operators
    ("LTE", r"<="),
    ("GTE", r">="),
    ("EQ", r"=="),
    ("LT", r"<"),
    ("GT", r">"),
    ("NEQ", r"!="),
    ("AND", keyword(r"and")),
    ("OR", keyword(r"or")),
    # Functions
    ("DEFN", keyword(r"defn")),
    # Vars
    ("DEF", keyword(r"def")),
    ("MUT", keyword(r"mut")),
    ("VAR", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("ASSIGN", r"="),
    # Number
    ("NUMBER", r"\d+"),
    # String. A backslash escapes the character after it, so a string can
    # hold a quote without ending early.
    ("STRING", r'"(?:[^"\\]|\\.)*"'),
]


def add_token(t):
    lexer_generator.add(*t)


list(map(lambda t: lexer_generator.add(*t), tokens))

# Text that carries no meaning and never reaches the parser.
#
# Commas are deliberately in here rather than in the grammar: they separate
# nothing, so `f(a, b)` and `f(a b)` are the same call and the choice is the
# author's taste. Keeping them out of the grammar also avoids inventing a
# rule for where a decorative character is and is not allowed.
ignores = [
    r"[ \t\r\n]+",
    r",",
    r"\#.*",
]

list(map(lambda i: lexer_generator.ignore(i), ignores))

lexer = lexer_generator.build()
