from llvmlite import ir, binding

global_context = ir.global_context

VOID = ir.VoidType()
INT8 = ir.IntType(8)
NUMBER = ir.DoubleType()
INT32 = ir.IntType(32)
INT64 = ir.IntType(64)
STRING = ir.IntType(8)
VOID = ir.VoidType()
NACHTYPE = global_context.get_identified_type("struct.nachtype")

NACHTYPE.set_body(INT8, NUMBER, STRING.as_pointer())

type_mappings = {0: NUMBER, 1: STRING}

# TODO: https://mapping-high-level-constructs-to-llvm-ir.readthedocs.io/en/latest/appendix-a-how-to-implement-a-string-type-in-llvm/index.html
# TODO: REFERENCE https://www.udemy.com/course/programming-language-with-llvm/learn/lecture/37292452?start=0#overview


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


def get_string_pointer(builder, nach_type_ptr):
    string_ptr = builder.gep(nach_type_ptr, [INT32(0), INT32(2)], inbounds=True)
    return string_ptr


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
    return builder.call(get_function_by_name(builder, "load_number"), [nach_type_ptr])


def load_string(builder, nach_type_ptr):
    return builder.call(get_function_by_name(builder, "load_string"), [nach_type_ptr])

def define_load_number(builder):
    """
    Defines the load_number function in the module
    """
    module = builder.module
    function_type = ir.FunctionType(NUMBER, [NACHTYPE.as_pointer()])
    function = ir.Function(module, function_type, name="load_number")
    fn_builder = ir.IRBuilder(function.append_basic_block("entry"))
    nach_type_ptr = function.args[0]
    number_ptr = get_number_pointer(fn_builder, nach_type_ptr)
    number = fn_builder.load(number_ptr)
    fn_builder.ret(number)


def define_load_string(builder):
    """
    Defines the load_string function in the module
    """
    module = builder.module
    function_type = ir.FunctionType(STRING.as_pointer(), [NACHTYPE.as_pointer()])
    function = ir.Function(module, function_type, name="load_string")
    fn_builder = ir.IRBuilder(function.append_basic_block())
    nach_type_ptr = function.args[0]
    string_ptr = get_string_pointer(fn_builder, nach_type_ptr)
    string = fn_builder.load(string_ptr)
    fn_builder.ret(string)


#
# Allocations
#
def declare_malloc(builder):
    """
    Declares malloc function to dynamically allocate memory in the heap
    """
    module = builder.module
    fnty = ir.FunctionType(INT8.as_pointer(), [INT64])
    ir.Function(module, fnty, name="malloc")


def _allocate_nachtype(builder):
    """Allocates space for a NACHTYPE and returns a pointer to a NACHTYPE struct"""
    return builder.call(get_function_by_name(builder, "allocate_nachtype"), [])


def define_allocate_nachtype(builder):
    """
    Defines a wrapper over malloc to allocate a NACHTYPE in the heap
    """
    module = builder.module
    fnty = ir.FunctionType(NACHTYPE.as_pointer(), [])
    function = ir.Function(module, fnty, name="allocate_nachtype")
    fn_builder = ir.IRBuilder(function.append_basic_block("entry"))
    i8_ptr = fn_builder.call(get_function_by_name(fn_builder, "malloc"), [INT64(NACHTYPE.__sizeof__())])
    nach_type_ptr = fn_builder.bitcast(i8_ptr, NACHTYPE.as_pointer())
    fn_builder.ret(nach_type_ptr)


def _allocate_string(builder, string):
    """
    Allocates an llvm string in a NACHTYPE struct
    """
    nach_type_ptr = _allocate_nachtype(builder)
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
    value = ir.Constant(ir.ArrayType(STRING, len(string)), bytearray(string, "utf8"))
    allocated_str_space = builder.alloca(ir.ArrayType(STRING, len(string)))
    builder.store(value, allocated_str_space)
    pointer_to_first_char = builder.gep(
        allocated_str_space, [INT32(0), INT32(0)], inbounds=True
    )
    loaded_ptr = builder.load(pointer_to_first_char)
    str_ptr = builder.alloca(STRING)
    builder.store(loaded_ptr, str_ptr, align=1)
    return builder.call(get_function_by_name(builder, "allocate_string"), [str_ptr])


def define_allocate_string(builder):
    """
    Defines the allocate_string function in the module
    """
    module = builder.module
    function_type = ir.FunctionType(NACHTYPE.as_pointer(), [STRING.as_pointer()])
    function = ir.Function(module, function_type, name="allocate_string")
    builder = ir.IRBuilder(function.append_basic_block())
    return_value = function.args[0]
    return builder.ret(_allocate_string(builder, return_value))

def _allocate_number(builder, value):
    """
    Allocates an llvm number in a NACHTYPE struct
    """

    nach_type_ptr = _allocate_nachtype(builder)
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
    builder = ir.IRBuilder(function.append_basic_block("entry"))
    return_value = function.args[0]
    return builder.ret(_allocate_number(builder, return_value))


#
# Ops
#


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
    fn_builder = ir.IRBuilder(function.append_basic_block("entry"))
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


def nach_print(builder, nach_type_ptr):
    """
    Prints a NACHTYPE value
    """
    fn = get_function_by_name(builder, "printf")
    global_fmt = get_function_by_name(builder, "printf_format")
    ptr_fmt = builder.bitcast(global_fmt, STRING.as_pointer())
    builder.call(fn, [ptr_fmt, load_number(builder, nach_type_ptr), load_string(builder, nach_type_ptr), nach_type_ptr])


#
# Fuctions
#

def defn_function(builder, fn_name, fn_arg_number):
    module = builder.module
    fn_type = ir.FunctionType(NACHTYPE.as_pointer(), [NACHTYPE.as_pointer() for i in range(fn_arg_number)])
    fn = ir.Function(module, fn_type, name=fn_name)
    block = fn.append_basic_block(name="entry")
    fn_builder = ir.IRBuilder(block)
    return fn_builder, fn


def return_(builder, value):
    """
    Returns a NACHTYPE value
    """
    return builder.ret(value)


def call_function(builder, fn_name, fn_args):
    """
    Resolves a call to a function
    """
    fn = get_function_by_name(builder, fn_name)
    return builder.call(fn, fn_args)

#
# Print
#

# TODO: IDELMONT review these utility funcs


def _make_bytearray(buf):
    """
    Make a byte array constant from *buf*.
    """
    b = bytearray(buf)
    n = len(b)
    return ir.Constant(ir.ArrayType(ir.IntType(8), n), b)


def add_global_variable(builder, ty, name, addrspace=0):
    module = builder.module
    unique_name = module.get_unique_name(name)
    return ir.GlobalVariable(module, ty, unique_name, addrspace)


def global_constant(builder, name, value, linkage="internal"):
    """
    Get or create a (LLVM module-)global constant with *name* or *value*.
    """
    data = add_global_variable(builder, value.type, name)
    data.linkage = linkage
    data.global_constant = True
    data.initializer = value
    return data


def declare_printf(builder):
    # TODO: Maybe wrap the printf function in a nachlang function
    """
    Declares printf function in the module
    """
    module = builder.module
    format = "double: %f string: %s address(ptr): %p \n\0"
    
    # Make global constant for format string
    cstring = INT8.as_pointer()
    fmt_bytes = _make_bytearray((format).encode("utf8"))
    # Defines a global printing format that will be used when resolving prints
    global_constant(builder, "printf_format", fmt_bytes)
    fnty = ir.FunctionType(NACHTYPE, [cstring], var_arg=True)
    ir.Function(module, fnty, name="printf")


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

    module = ir.Module(name="nachlag_core")
    module.triple = binding.get_default_triple()
    func_type = ir.FunctionType(VOID, [], False)
    base_func = ir.Function(module, func_type, name="main")
    block = base_func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    initialize_core_fns(
        [
            declare_printf,
            declare_malloc,
            define_allocate_nachtype,
            define_load_number,
            define_load_string,
            define_allocate_number,
            define_allocate_string,
            define_add,
            define_sub,
            define_mul,
            define_div,
        ]
    )

    return builder, module
