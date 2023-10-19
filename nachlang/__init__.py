from nachlang.lexer import lexer
from nachlang.parser import parser
from nachlang.codegen import ast
from nachlang import graph
from nachlang import runtime
from ctypes import CFUNCTYPE, c_void_p
import typer

app = typer.Typer()


def generate_ast(program):
    tokens = lexer.lex(program)
    return parser.parse(tokens)


@app.command()
def compile(filename: str, output_ll: bool = False, graph_ast: bool = False):
    with open(filename, "r") as f:
        program = f.read()

    program_ast = generate_ast(program)

    if graph_ast:
        graph.graph(program_ast)

    module = ast.generate_llvm_ir(program_ast)

    if output_ll:
        with open("out.ll", "w") as f:
            f.write(str(module))

    engine, parsed_module = runtime.compile_ir(module)

    func_ptr = engine.get_function_address("main")
    cfunc = CFUNCTYPE(None)(func_ptr)
    cfunc()


def compile():
    app()

if __name__ == "__main__":
    app()
