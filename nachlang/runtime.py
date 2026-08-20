from llvmlite import binding as llvm

DEFAULT_OPT_LEVEL = 3


def _create_target_machine():
    """
    Create a target machine representing the host
    """
    target = llvm.Target.from_default_triple()
    return target.create_target_machine()


def _create_execution_engine(target_machine):
    """
    Create an ExecutionEngine suitable for JIT code generation on
    the host CPU.  The engine is reusable for an arbitrary number of
    modules.
    """
    # An execution engine with an empty backing module
    backing_mod = llvm.parse_assembly("")
    engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
    return engine


def optimize_module(parsed_module, target_machine, opt_level=DEFAULT_OPT_LEVEL):
    """
    Run the LLVM optimization pipeline over a parsed module, in place.

    Without this the JIT emits every NACHTYPE allocation as a real heap
    allocation. The pipeline is what proves those allocations never escape
    and promotes them into registers, so it is worth a great deal on
    allocation heavy code.

    Note that the target machine already codegens at its own default
    optimization level, so opt_level=0 is "no IR passes", not "no
    optimization at all".
    """
    if opt_level <= 0:
        return

    tuning_options = llvm.create_pipeline_tuning_options(speed_level=opt_level)
    pass_builder = llvm.create_pass_builder(target_machine, tuning_options)
    pass_builder.getModulePassManager().run(parsed_module, pass_builder)


def compile_ir(module, opt_level=DEFAULT_OPT_LEVEL):
    """
    Compile the LLVM IR string with the given engine.
    The compiled module object is returned.
    """
    target_machine = _create_target_machine()
    engine = _create_execution_engine(target_machine)
    # Create a LLVM module object from the IR
    parsed_module = llvm.parse_assembly(str(module))
    parsed_module.verify()
    optimize_module(parsed_module, target_machine, opt_level)
    # Now add the module and make sure it is ready for execution
    engine.add_module(parsed_module)
    engine.finalize_object()
    engine.run_static_constructors()
    return engine, parsed_module
