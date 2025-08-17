import logging
import os
import shutil
import sys
from ctypes import CFUNCTYPE, c_void_p, cdll
from typing import Optional

import typer

from nachlang import graph, runtime
from nachlang.codegen import ast, core
from nachlang.lexer import lexer
from nachlang.parser import parser

app = typer.Typer()


def verify_llvm():
    if not shutil.which("lli"):
        # pylint: disable=broad-exception-raised
        raise Exception(
            "LLVM not found. Please install LLVM 15 or make sure it's in your PATH."
        )


def should_use_gc(libgc_path: Optional[str] = None):
    if not libgc_path:
        return False

    if not os.path.exists(libgc_path):
        logging.warning("Boehm GC library not found. Falling back to standard malloc.")
        return False

    return True


def generate_ast(program):
    tokens = lexer.lex(program)
    return parser.parse(tokens)


def _cmd_compile_and_run(
    filename: str,
    output_ll: bool = False,
    graph_ast: bool = False,
    compile_only: bool = False,
    libgc_path: Optional[str] = None,
):
    libgc_path = libgc_path or "/opt/homebrew/lib/libgc.1.5.4.dylib"
    with open(filename, "r", encoding="utf-8") as f:
        program = f.read()

    program_ast = generate_ast(program)

    core.USE_GC = should_use_gc(libgc_path)
    core.GC_VERIFIED_PATH = libgc_path if core.USE_GC else None

    if graph_ast:
        graph.graph(program_ast)

    module = ast.generate_llvm_ir(program_ast)

    if output_ll:
        with open(f"{filename}.ll", "w", encoding="utf-8") as f:
            f.write(str(module))

    engine, _parsed_module = runtime.compile_ir(module)

    if compile_only:
        return

    # NOTE: Alternative: run `lli -load path/to/libgc.dylib <file.ll>`
    func_ptr = engine.get_function_address("main")
    cfunc = CFUNCTYPE(None)(func_ptr)
    cfunc()


@app.command()
def cmd_compile_and_run(
    filename: str,
    output_ll: bool = False,
    graph_ast: bool = False,
    compile_only: bool = False,
    libgc_path: Optional[str] = None,
):
    try:
        verify_llvm()
        _cmd_compile_and_run(filename, output_ll, graph_ast, compile_only, libgc_path)
    except Exception as e:
        print(e)
        sys.exit(1)

    sys.exit(0)


def run_app():
    app()


if __name__ == "__main__":
    app()
