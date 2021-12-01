from lexer import lexer
from parser import parser
from codegen import generate_llvm_ir
from graph import graph
import pprint

program = """1+8"""

tokens = lexer.lex(program)
ast = parser.parse(tokens)
pprint.pprint(ast)
graph(ast)
generate_llvm_ir(ast)

