from llvmlite import ir, binding

global_context = ir.global_context

VOID = ir.VoidType()
INT8 = ir.IntType(8)
NUMBER = ir.DoubleType()
INT32 = ir.IntType(32)
STRING = ir.IntType(8)
VOID = ir.VoidType()
NACHTYPE = global_context.get_identified_type("struct.nachtype")

NACHTYPE.set_body(INT8, NUMBER, STRING.as_pointer())

type_mappings = {0: NUMBER, 1: STRING}


#
# Function getters
#


def get_function_by_name(builder, name):
    module = builder.module
    return module.get_global(name)


#
# Pointer getters
#


def get_type_pointer(builder, nach_type_ptr):
    type_ptr = builder.gep(nach_type_ptr, [INT32(0), INT32(0)], inbounds=True)
    return type_ptr


def get_number_pointer(builder, nach_type_ptr):
    number_ptr = builder.gep(nach_type_ptr, [INT32(0), INT32(1)], inbounds=True)
    return number_ptr


#
# Value setters
#


def set_type(builder, nach_type_ptr, type):
    type_ptr = get_type_pointer(builder, nach_type_ptr)
    builder.store(type, type_ptr)


def set_number_type(builder, nach_type_ptr):
    set_type(builder, nach_type_ptr, INT8(0))


def set_string_type(builder, nach_type_ptr):
    set_type(builder, nach_type_ptr, INT8(1))


#
# Value loaders
#


def load_type(builder, nach_type_ptr):
    type_ptr = get_type_pointer(builder, nach_type_ptr)
    return builder.load(type_ptr)


def load_number(builder, nach_type_ptr):
    number_ptr = get_number_pointer(builder, nach_type_ptr)
    return builder.load(number_ptr)


# Write a function that allocates the string type of the NACHTYPE struct


def _allocate_string(builder, string):
    """
    Allocates an llvm string in a NACHTYPE struct
    """
    nach_type_ptr = builder.alloca(NACHTYPE)
    nach_type_string_ptr = builder.gep(
        nach_type_ptr, [INT32(0), INT32(2)], inbounds=True
    )
    builder.store(string, nach_type_string_ptr)
    set_string_type(builder, nach_type_ptr)
    return nach_type_ptr


def allocate_string(builder, string):
    """
    Allocates a python string in a NACHTYPE struct

    The STRING type is denoted as 1 in the NACHTYPE struct
    """
    str_ptr = builder.alloca(STRING)
    value = ir.Constant(ir.ArrayType(STRING, len(string)), bytearray(string, "utf8"))
    allocated_str_space = builder.alloca(ir.ArrayType(STRING, len(string)))
    builder.store(value, allocated_str_space)
    bitcasted = builder.bitcast(allocated_str_space, STRING)
    builder.store(bitcasted, str_ptr, align=1)
    return _allocate_string(builder, str_ptr)


def _define_binary_operation(builder, name):
    """
    Defines a binary operation in the module
    """

    def get_op(builder):
        return {
            "add": builder.fadd,
            "mul": builder.fmul,
            "sub": builder.fsub,
            "div": builder.fdiv,
        }.get(name)

    module = builder.module
    function_type = ir.FunctionType(
        NACHTYPE.as_pointer(), [NACHTYPE.as_pointer(), NACHTYPE.as_pointer()]
    )
    function = ir.Function(module, function_type, name=name)
    fn_builder = ir.IRBuilder(function.append_basic_block())
    lhs_ptr, rhs_ptr = function.args
    lhs = load_number(fn_builder, lhs_ptr)
    rhs = load_number(fn_builder, rhs_ptr)
    operation = get_op(fn_builder)
    result = operation(lhs, rhs)

    fn_builder.ret(allocate_number(fn_builder, result))


def define_add(builder):
    """
    Defines the add function in the module
    """
    _define_binary_operation(builder, "add")


def define_sub(builder):
    """
    Defines the sub function in the module
    """
    _define_binary_operation(builder, "sub")


def define_mul(builder):
    """
    Defines the mul function in the module
    """
    _define_binary_operation(builder, "mul")


def define_div(builder):
    """
    Defines the div function in the module
    """
    _define_binary_operation(builder, "div")


def add(builder, nach_type_ptr1, nach_type_ptr2):
    """
    Adds two NACHTYPE structs and returns a new NACHTYPE struct
    """
    return builder.call(
        get_function_by_name(builder, "add"), [nach_type_ptr1, nach_type_ptr2]
    )


def sub(builder, nach_type_ptr1, nach_type_ptr2):
    """
    Subtracts two NACHTYPE structs and returns a new NACHTYPE struct
    """
    return builder.call(
        get_function_by_name(builder, "sub"), [nach_type_ptr1, nach_type_ptr2]
    )


def mul(builder, nach_type_ptr1, nach_type_ptr2):
    """
    Multiplies two NACHTYPE structs and returns a new NACHTYPE struct
    """
    return builder.call(
        get_function_by_name(builder, "mul"), [nach_type_ptr1, nach_type_ptr2]
    )


def div(builder, nach_type_ptr1, nach_type_ptr2):
    """
    Divides two NACHTYPE structs and returns a new NACHTYPE struct
    """
    return builder.call(
        get_function_by_name(builder, "div"), [nach_type_ptr1, nach_type_ptr2]
    )


def _allocate_number(builder, value):
    """
    Allocates an llvm number in a NACHTYPE struct
    """
    nach_type_ptr = builder.alloca(NACHTYPE)
    nach_type_number_ptr = builder.gep(
        nach_type_ptr, [INT32(0), INT32(1)], inbounds=True
    )
    builder.store(value, nach_type_number_ptr)
    set_number_type(builder, nach_type_ptr)
    return nach_type_ptr


def allocate_number(builder, value):
    """
    Allocates a NUMBER in a NACHTYPE struct
    """
    return builder.call(get_function_by_name(builder, "allocate_number"), [value])


def define_allocate_number(builder):
    """
    Defines the allocate_number function in the module
    """
    module = builder.module
    function_type = ir.FunctionType(NACHTYPE.as_pointer(), [NUMBER])
    function = ir.Function(module, function_type, name="allocate_number")
    builder = ir.IRBuilder(function.append_basic_block())
    return_value = function.args[0]
    return builder.ret(_allocate_number(builder, return_value))


#
# LLVM initialization
#


def initialize():
    """
    Initializes the module and defines the core nachlang functions
    """

    def initialize_core_fns(fns):
        [fn(builder) for fn in fns]

    # All these initializations are required for code generation!
    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()

    module = ir.Module(name="nachlang_core")
    module.triple = binding.get_default_triple()
    func_type = ir.FunctionType(VOID, [], False)
    base_func = ir.Function(module, func_type, name="entrypoint")
    block = base_func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    initialize_core_fns(
        [define_allocate_number, define_add, define_sub, define_mul, define_div]
    )

    return builder, module
