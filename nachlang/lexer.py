import rply

lexer_generator = rply.LexerGenerator()


tokens = [
    # Print
    ("PRINT", r"print"),
    # Conditional
    ("IF", r"if"),
    # Function
    ("LOOP", r"loop"),
    ("RETURN", r"return"),
    # Booleans
    ("BOOL", r"true|false"),
    ("IS_TRUTHY", r"is_truthy"),
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
    ("AND", r"and"),
    ("OR", r"or"),
    # Functions
    ("DEFN", r"defn"),
    # Vars
    ("DEF", r"def"),
    ("VAR", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("ASSIGN", r"="),
    # Number
    ("NUMBER", r"\d+"),
    # String
    ("STRING", r'"(.*?)"'),
    # COMMA
    ("COMMA", r","),
]


def add_token(t):
    lexer_generator.add(*t)


list(map(lambda t: lexer_generator.add(*t), tokens))

ignores = [r" |\n", r"\#.*"]

list(map(lambda i: lexer_generator.ignore(i), ignores))

lexer = lexer_generator.build()
