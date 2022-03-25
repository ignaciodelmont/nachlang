import rply
from lexer import tokens as tk

pg = rply.ParserGenerator(
    tokens=list(map(lambda t: t[0], tk)),
    precedence=[
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
def statement(p):
    return build_response("statement", p)


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
def add(p):
    return build_response("binary_operation", p)


@pg.production("define_var : DEF VAR expression")
def define_var(p):
    return build_response("define_var", p)


@pg.production("empty : ")
def empty(p):
    return


parser = pg.build()
