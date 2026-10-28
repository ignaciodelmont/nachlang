import rply
from rply.errors import LexingError

from nachlang.errors import NachlangSyntaxError
from nachlang.lexer import lexer
from nachlang.lexer import tokens as tk

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
@pg.production("statement : mutate_var")
@pg.production("statement : if_statement")
@pg.production("statement : loop_statement")
@pg.production("statement : define_function")
@pg.production("statement : return")
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


@pg.production(
    "loop_statement : OPEN_PAREN LOOP expression OPEN_CURLY_BRA statement_list CLOSE_CURLY_BRA CLOSE_PAREN"
)
def loop_statement(p):
    return build_response("loop_statement", p)


@pg.production("expression : OPEN_PAREN expression CLOSE_PAREN")
def expression_paren(p):
    return build_response("expression", p)


@pg.production("expression : NUMBER")
@pg.production("expression : STRING")
@pg.production("expression : BOOL")
@pg.production("expression : VAR")
@pg.production("expression : binary_operation")
@pg.production("expression : call_function")
@pg.production("expression : print_expression")
@pg.production("expression : is_truthy_expression")
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


@pg.production("mutate_var : MUT VAR expression")
def mutate_var(p):
    return build_response("mutate_var", p)


@pg.production("return : RETURN")
@pg.production("return : RETURN expression")
def return_(p):
    return build_response("return", p)


# TODO: Rename VAR -> NAME
@pg.production(
    "define_function : DEFN VAR OPEN_PAREN arguments CLOSE_PAREN OPEN_CURLY_BRA statement_list CLOSE_CURLY_BRA"
)
def define_func(p):
    return build_response("define_function", p)


@pg.production("call_function : VAR OPEN_PAREN argument_values CLOSE_PAREN")
def call_func(p):
    return build_response("call_function", p)


@pg.production("print_expression : PRINT OPEN_PAREN argument_values CLOSE_PAREN")
def print_expression(p):
    return build_response("print_expression", p)


@pg.production("is_truthy_expression : IS_TRUTHY OPEN_PAREN expression CLOSE_PAREN")
def is_truthy_expression(p):
    return build_response("is_truthy_expression", p)


@pg.production("argument_values : ")
@pg.production("argument_values : expression")
@pg.production("argument_values : argument_values argument_values")
def argument_values(p):
    if len(p) == 2:
        return build_response("argument_values", p[0]["value"] + p[1]["value"])
    elif len(p) in [0, 1]:
        return build_response("argument_values", p)
    else:
        raise Exception("Unexpected Parsing Error")


@pg.production("arguments : ")
@pg.production("arguments : VAR")
@pg.production("arguments : arguments arguments")
def arguments(p):
    """
    arguments can look like the following expansion

    a
    a,
    a,b
    a,b,

    and so on.


    """

    if len(p) == 2:
        return build_response("arguments", p[0]["value"] + p[1]["value"])
    elif len(p) in [0, 1]:
        return build_response("arguments", p)
    else:
        raise Exception("Unexpected Parsing Error")


# @pg.production("empty : ")
# def empty(p):
#     return


def _syntax_error(message, source_pos):
    """
    Turn one of rply's source positions into a reportable error. The position
    is optional because rply has none to give at end of input.
    """
    if source_pos is None:
        return NachlangSyntaxError(message)
    return NachlangSyntaxError(message, line=source_pos.lineno, column=source_pos.colno)


@pg.error
def error_handler(token):
    """
    rply's default is to raise ParsingError carrying only a source position,
    which reaches the user as a bare tuple. Naming the offending token costs
    nothing and is the difference between a usable message and a puzzle.
    """
    if token.gettokentype() == "$end":
        raise NachlangSyntaxError("unexpected end of input")

    raise _syntax_error(
        f"unexpected {token.gettokentype()} {token.getstr()!r}",
        token.getsourcepos(),
    )


parser = pg.build()


def parse(code):
    """
    Parse source text into an AST.

    Tokens are materialised rather than streamed so that a lexing error
    surfaces here, where it can be reported with a position, and so that a
    program holding no statements can be recognised before it reaches the
    grammar. Giving statement_list an empty production would do the same job
    at the cost of two more reduce/reduce conflicts in a grammar that already
    has plenty.
    """
    try:
        tokens = list(lexer.lex(code))
    except LexingError as error:
        source_pos = error.getsourcepos()
        character = ""
        if source_pos is not None and source_pos.idx < len(code):
            character = f" {code[source_pos.idx]!r}"
        raise _syntax_error(f"unexpected character{character}", source_pos) from error

    if not tokens:
        return build_response("statement_list", [])

    return parser.parse(iter(tokens))
