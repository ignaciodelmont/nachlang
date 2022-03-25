from lexer import lexer
from parser import parser
from codegen import generate_llvm_ir
from graph import graph
import pprint

program = """
    def a 4
    a + 1
    1 + 1
    1 * (8 - 9 * 3)
    1 * 2 * 3 * 4
    """

tokens = lexer.lex(program)
ast = parser.parse(tokens)
# pprint.pprint(ast)
# graph(ast)
generate_llvm_ir(ast)
