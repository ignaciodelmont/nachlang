import rply
from nachlang.lexer import tokens as tk, lexer

pg = rply.ParserGenerator(
    tokens=list(map(lambda t: t[0], tk)),
    precedence=[
        ("left", ["OR"]),
        ("left", ["AND"]),
        ("left", ["PLUS_SIGN", "MINUS_SIGN"]),
        ("left", ["MULTIPLICATION_SIGN"]),
        ("left", ["DIVISION_SIGN"]),
    ],
)


def build_response(name, value):
    return {"name": name, "value": value}


@pg.production("statement_list : statement")
@pg.production("statement_list : statement statement_list")
def statement_list(p):
    """
    Recursively resolve statement list
    """
    if len(p) == 2:
        res = [p[0]] + p[1]["value"]
    else:
        res = p
    return build_response("statement_list", res)


@pg.production("statement : expression")
@pg.production("statement : define_var")
@pg.production("statement : if_statement")
def statement(p):
    return build_response("statement", p)


@pg.production(
    "if_statement : OPEN_PAREN IF expression OPEN_CURLY_BRA statement_list CLOSE_CURLY_BRA OPEN_CURLY_BRA statement_list CLOSE_CURLY_BRA CLOSE_PAREN"
)
@pg.production(
    "if_statement : OPEN_PAREN IF expression OPEN_CURLY_BRA statement_list CLOSE_CURLY_BRA CLOSE_PAREN"
)
def if_statement(p):
    return build_response("if_statement", p)


@pg.production("expression : OPEN_PAREN expression CLOSE_PAREN")
def expression_paren(p):
    return build_response("expression", p)


@pg.production("expression : NUMBER")
@pg.production("expression : VAR")
@pg.production("expression : binary_operation")
def expression(p):
    return build_response("expression", p)


@pg.production("binary_operation : expression PLUS_SIGN expression")
@pg.production("binary_operation : expression MINUS_SIGN expression")
@pg.production("binary_operation : expression MULTIPLICATION_SIGN expression")
@pg.production("binary_operation : expression DIVISION_SIGN expression")
@pg.production("binary_operation : expression EQ expression")
@pg.production("binary_operation : expression NEQ expression")
@pg.production("binary_operation : expression LT expression")
@pg.production("binary_operation : expression GT expression")
@pg.production("binary_operation : expression LTE expression")
@pg.production("binary_operation : expression GTE expression")
@pg.production("binary_operation : expression AND expression")
@pg.production("binary_operation : expression OR expression")
def binop(p):
    return build_response("binary_operation", p)


@pg.production("define_var : DEF VAR expression")
def define_var(p):
    return build_response("define_var", p)


@pg.production("empty : ")
def empty(p):
    return


parser = pg.build()


def parse(code):
    return parser.parse(lexer.lex(code))
