import rply

lexer_generator = rply.LexerGenerator()

tokens = [
    # Print
    ("PRINT", r'print'),

    # Conditional
    ('IF', r'if'),

    # Function
    ("LOOP", r"loop"),
    ("RETURN", r"return"),

    # Booleans
    ("TRUE", r"true"),
    ("False", r"false"),

    # Parenthesis
    ("OPEN_PAREN", r"\("),
    ("CLOSE_PAREN", r"\)"),

    # Curly brackets
    ('OPEN_CURLY_BRA', r'\{'),
    ('CLOSE_CURLY_BRA', r'\}'),

    # Operators
    ('DIVISION_SIGN', r'\/'),
    ('MULTIPLICATION_SIGN', r'\*'),
    ('PLUS_SIGN', r'\+'),
    ('MINUS_SIGN', r'\-'),
    
    

    # Conditional Operators
    ('LTE', r'<='),
    ('GTE', r'>='),
    ('EQ', r'=='),
    ('LT', r'<'),
    ('GT', r'>'),

    # Types
    ("NUMBER_TYPE", r"number"),
    ("STRING_TYPE", r"string"),

    # Vars
    ("DEF", r"def"),
    ("VAR", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("ASSIGN", r"="),

    # Number
    ("NUMBER", r"\d+"),

    # String
    ("STRING", r'"(.*?)"'),
]

def add_token(t):
    a, b = t
    print(a,b)
    lexer_generator.add(*t)


list(map(lambda t: lexer_generator.add(*t), tokens))

ignores = [
    r" |\n",
    r"\#.*"
]

list(map(lambda i: lexer_generator.ignore(i), ignores))

lexer = lexer_generator.build()
