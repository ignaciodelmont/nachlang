import rply
from lexer import tokens as tk

pg = rply.ParserGenerator(
    tokens = list(map(lambda t: t[0], tk)),
    precedence = [
        ("left", ["PLUS_SIGN", "MINUS_SIGN"]),
        ("left", ["MULTIPLY_SIGN"])
    ]
)

@pg.production("expression : OPEN_PAREN expression CLOSE_PAREN")
def expression_paren(p):
    return {"expression": p}


@pg.production("expression : NUMBER")
@pg.production("expression : binary_operation")
def expression(p):
    return {"expression": p}


@pg.production("binary_operation : expression PLUS_SIGN expression")
@pg.production("binary_operation : expression MINUS_SIGN expression")
@pg.production("binary_operation : expression MULTIPLY_SIGN expression")
def add(p):
    return {"binary_operation": p}


@pg.production("empty : ")
def empty(p):
    return


parser = pg.build()