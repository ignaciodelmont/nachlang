import logging
import os
import shutil
import sys
import warnings
from ctypes import CFUNCTYPE, c_int32, c_void_p, cdll
from typing import Optional

import typer
from rply.errors import ParserGeneratorWarning

if not os.getenv("NACHLANG_PARSER_WARNINGS"):
    warnings.filterwarnings("ignore", category=ParserGeneratorWarning)

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
    libgc_path: Optional[str] = None,  # "/opt/homebrew/lib/libgc.1.5.4.dylib"
    opt_level: int = runtime.DEFAULT_OPT_LEVEL,
    gc_alloc_attrs: bool = True,
):
    with open(filename, "r", encoding="utf-8") as f:
        program = f.read()

    program_ast = generate_ast(program)

    core.USE_GC = should_use_gc(libgc_path)
    core.GC_VERIFIED_PATH = libgc_path if core.USE_GC else None
    core.GC_ALLOC_ATTRS = gc_alloc_attrs

    if graph_ast:
        graph.graph(program_ast)

    module = ast.generate_llvm_ir(program_ast)

    if output_ll:
        with open(f"{filename}.ll", "w", encoding="utf-8") as f:
            f.write(str(module))

    engine, _parsed_module = runtime.compile_ir(module, opt_level=opt_level)

    if compile_only:
        return 0

    # NOTE: Alternative: run `lli -load path/to/libgc.dylib <file.ll>`
    func_ptr = engine.get_function_address("main")
    cfunc = CFUNCTYPE(c_int32)(func_ptr)
    return cfunc()


@app.command()
def cmd_compile_and_run(
    filename: str,
    output_ll: bool = False,
    graph_ast: bool = False,
    compile_only: bool = False,
    libgc_path: Optional[str] = None,
    opt_level: int = runtime.DEFAULT_OPT_LEVEL,
    gc_alloc_attrs: bool = True,
):
    try:
        verify_llvm()
        exit_code = _cmd_compile_and_run(
            filename,
            output_ll,
            graph_ast,
            compile_only,
            libgc_path,
            opt_level,
            gc_alloc_attrs,
        )
    except Exception as e:
        print(e)
        sys.exit(1)

    # main now returns an int, so hand its value back to the shell.
    sys.exit(exit_code)


def run_app():
    app()


if __name__ == "__main__":
    app()
