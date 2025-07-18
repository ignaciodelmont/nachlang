from llvmlite import ir, binding

global_context = ir.global_context

VOID = ir.VoidType()
INT8 = ir.IntType(8)
BOOL = ir.IntType(1)
NUMBER = ir.DoubleType()
INT32 = ir.IntType(32)
INT64 = ir.IntType(64)
STRING = ir.IntType(8)
VOID = ir.VoidType()
NACHTYPE = global_context.get_identified_type("struct.nachtype")

NACHTYPE.set_body(INT8, NUMBER, STRING.as_pointer(), BOOL)

TYPE_MAPPINGS = {0: NUMBER, 1: STRING, 2: BOOL}


CONDITIONAL_OPS_MAPPINGS = {
    "==": INT8(0),
    "!=": INT8(1),
    "<": INT8(2),
    "<=": INT8(3),
    ">": INT8(4),
    ">=": INT8(5),
}

# TODO: https://mapping-high-level-constructs-to-llvm-ir.readthedocs.io/en/latest/appendix-a-how-to-implement-a-string-type-in-llvm/index.html
# TODO: REFERENCE https://www.udemy.com/course/programming-language-with-llvm/learn/lecture/37292452?start=0#overview


#
# Function getters
#


def get_symbol_by_name(builder, name):
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


def get_bool_pointer(builder, nach_type_ptr):
    bool_ptr = builder.gep(nach_type_ptr, [INT32(0), INT32(3)], inbounds=True)
    return bool_ptr


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


def set_bool_type(builder, nach_type_ptr):
    set_type(builder, nach_type_ptr, INT8(2))


#
# Value loaders
#


def load_type(builder, nach_type_ptr):
    """
    Loads the type of a NACHTYPE struct

    Returns an INT8
    """
    type_ptr = get_type_pointer(builder, nach_type_ptr)
    return builder.load(type_ptr)


def load_number(builder, nach_type_ptr):
    return builder.call(get_symbol_by_name(builder, "load_number"), [nach_type_ptr])


def load_number_as_int(builder, nach_type_ptr):
    return builder.call(
        get_symbol_by_name(builder, "load_number_as_int"), [nach_type_ptr]
    )


def load_string(builder, nach_type_ptr):
    return builder.call(get_symbol_by_name(builder, "load_string"), [nach_type_ptr])


def load_bool(builder, nach_type_ptr):
    return builder.call(get_symbol_by_name(builder, "load_bool"), [nach_type_ptr])


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


def define_load_number_as_int(builder):
    """
    Defines the load_number_as_int function in the module
    """
    module = builder.module
    function_type = ir.FunctionType(INT64, [NACHTYPE.as_pointer()])
    function = ir.Function(module, function_type, name="load_number_as_int")
    fn_builder = ir.IRBuilder(function.append_basic_block("entry"))
    nach_type_ptr = function.args[0]
    number_ptr = get_number_pointer(fn_builder, nach_type_ptr)
    number = fn_builder.load(number_ptr)
    fn_builder.ret(fn_builder.fptosi(number, INT64))


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


def define_load_bool(builder):
    """
    Defines the load_bool function in the module
    """
    module = builder.module
    function_type = ir.FunctionType(BOOL, [NACHTYPE.as_pointer()])
    function = ir.Function(module, function_type, name="load_bool")
    fn_builder = ir.IRBuilder(function.append_basic_block())
    nach_type_ptr = function.args[0]
    bool_ptr = get_bool_pointer(fn_builder, nach_type_ptr)
    boolean = fn_builder.load(bool_ptr)
    fn_builder.ret(boolean)


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
    return builder.call(get_symbol_by_name(builder, "allocate_nachtype"), [])


def define_allocate_nachtype(builder):
    """
    Defines a wrapper over malloc to allocate a NACHTYPE in the heap
    """
    module = builder.module
    fnty = ir.FunctionType(NACHTYPE.as_pointer(), [])
    function = ir.Function(module, fnty, name="allocate_nachtype")
    fn_builder = ir.IRBuilder(function.append_basic_block("entry"))
    i8_ptr = fn_builder.call(
        # TODO: Make sure that __sizeof__() actually returns the NACHTYPE size in llvm
        # and not the python object..
        get_symbol_by_name(fn_builder, "malloc"),
        [INT64(NACHTYPE.__sizeof__())],
    )
    nach_type_ptr = fn_builder.bitcast(i8_ptr, NACHTYPE.as_pointer())
    fn_builder.ret(nach_type_ptr)


def _allocate_string(builder, string):
    """
    Allocates an llvm string in a NACHTYPE struct
    """
    nach_type_ptr = _allocate_nachtype(builder)

    nach_print_(builder, nach_type_ptr)
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
    return builder.call(get_symbol_by_name(builder, "allocate_string"), [str_ptr])


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
    return builder.call(get_symbol_by_name(builder, "allocate_number"), [value])


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


def _allocate_bool(builder, value):
    """
    Allocates an llvm bool in a NACHTYPE struct
    """
    nach_type_ptr = _allocate_nachtype(builder)
    nach_type_bool_ptr = builder.gep(nach_type_ptr, [INT32(0), INT32(3)], inbounds=True)
    builder.store(value, nach_type_bool_ptr)
    set_bool_type(builder, nach_type_ptr)
    return nach_type_ptr


def allocate_bool(builder, value):
    """
    Allocates a BOOL in a NACHTYPE struct
    """
    return builder.call(
        get_symbol_by_name(builder, "allocate_bool"),
        [BOOL(1) if value == "true" else BOOL(0)],
    )


def define_allocate_bool(builder):
    """
    Defines the allocate_bool function in the module
    """
    module = builder.module
    function_type = ir.FunctionType(NACHTYPE.as_pointer(), [BOOL])
    function = ir.Function(module, function_type, name="allocate_bool")
    builder = ir.IRBuilder(function.append_basic_block("entry"))
    return_value = function.args[0]
    return builder.ret(_allocate_bool(builder, return_value))


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


def define_or(builder):
    """
    Defines the or function in the module
    """
    module = builder.module
    function_type = ir.FunctionType(
        NACHTYPE.as_pointer(), [NACHTYPE.as_pointer(), NACHTYPE.as_pointer()]
    )
    function = ir.Function(module, function_type, name="nach_or")
    fn_builder = ir.IRBuilder(function.append_basic_block("entry"))
    lhs_ptr, rhs_ptr = function.args
    with fn_builder.if_then(load_bool(fn_builder, (is_truthy(fn_builder, lhs_ptr)))):
        fn_builder.ret(lhs_ptr)
    fn_builder.ret(rhs_ptr)


def define_and(builder):
    """
    Defines the and function in the module
    """
    module = builder.module
    function_type = ir.FunctionType(
        NACHTYPE.as_pointer(), [NACHTYPE.as_pointer(), NACHTYPE.as_pointer()]
    )
    function = ir.Function(module, function_type, name="nach_and")
    fn_builder = ir.IRBuilder(function.append_basic_block("entry"))
    lhs_ptr, rhs_ptr = function.args
    with fn_builder.if_then(load_bool(fn_builder, (is_truthy(fn_builder, lhs_ptr)))):
        fn_builder.ret(rhs_ptr)
    fn_builder.ret(lhs_ptr)


def define_comparing_fns(builder):
    """
    Defines comparing fns in the module
    """

    def define_comp_fn(operator, name):
        module = builder.module
        function_type = ir.FunctionType(
            NACHTYPE.as_pointer(), [NACHTYPE.as_pointer(), NACHTYPE.as_pointer()]
        )
        function = ir.Function(module, function_type, name=f"nach_{name}")
        entry = function.append_basic_block("entry")
        fn_builder = ir.IRBuilder(entry)
        lhs_ptr, rhs_ptr = function.args
        fn_builder.call(
            get_symbol_by_name(fn_builder, "validate_are_equal_type"),
            [lhs_ptr, rhs_ptr],
        )

        true = allocate_bool(fn_builder, "true")
        false = allocate_bool(fn_builder, "false")
        ptr_type = load_type(fn_builder, lhs_ptr)

        # By default return false
        default_block = fn_builder.append_basic_block("default")
        fn_builder.position_at_end(default_block)
        fn_builder.ret(false)

        # Number comparison block
        is_comp_number_block = fn_builder.append_basic_block("is_comp_number")
        fn_builder.position_at_end(is_comp_number_block)
        lhs = load_number(fn_builder, lhs_ptr)
        rhs = load_number(fn_builder, rhs_ptr)
        with fn_builder.if_then(fn_builder.fcmp_ordered(operator, lhs, rhs)):
            fn_builder.ret(true)
        fn_builder.ret(false)

        # String comparison block
        is_comp_string_block = fn_builder.append_basic_block("is_comp_string")
        fn_builder.position_at_end(is_comp_string_block)
        fn_builder.ret(compare_strings(fn_builder, lhs_ptr, rhs_ptr, operator))

        # Switch Handler
        fn_builder.position_at_end(entry)
        switch_handler = fn_builder.switch(ptr_type, default_block)
        switch_handler.add_case(INT8(0), is_comp_number_block)
        switch_handler.add_case(INT8(1), is_comp_string_block)

    define_comp_fn("==", "eq")
    define_comp_fn("!=", "neq")
    define_comp_fn("<", "lt")
    define_comp_fn("<=", "lte")
    define_comp_fn(">", "gt")
    define_comp_fn(">=", "gte")


def define_validate_are_equal_type(builder):
    # TODO: IDELMONT actually raise an exception on this scenario!
    module = builder.module
    function_type = ir.FunctionType(
        NACHTYPE.as_pointer(), [NACHTYPE.as_pointer(), NACHTYPE.as_pointer()]
    )
    function = ir.Function(module, function_type, name="validate_are_equal_type")
    fn_builder = ir.IRBuilder(function.append_basic_block("entry"))
    lhs_ptr, rhs_ptr = function.args
    lhs_type = load_type(fn_builder, lhs_ptr)
    rhs_type = load_type(fn_builder, rhs_ptr)

    with fn_builder.if_then(fn_builder.icmp_signed("!=", lhs_type, rhs_type)):
        fn_builder.ret(allocate_bool(fn_builder, "false"))

    fn_builder.ret(allocate_bool(fn_builder, "true"))


def add(builder, nach_type_ptr1, nach_type_ptr2):
    """
    Adds two NACHTYPE structs and returns a new NACHTYPE struct
    """
    return builder.call(
        get_symbol_by_name(builder, "add"), [nach_type_ptr1, nach_type_ptr2]
    )


def sub(builder, nach_type_ptr1, nach_type_ptr2):
    """
    Subtracts two NACHTYPE structs and returns a new NACHTYPE struct
    """
    return builder.call(
        get_symbol_by_name(builder, "sub"), [nach_type_ptr1, nach_type_ptr2]
    )


def mul(builder, nach_type_ptr1, nach_type_ptr2):
    """
    Multiplies two NACHTYPE structs and returns a new NACHTYPE struct
    """
    return builder.call(
        get_symbol_by_name(builder, "mul"), [nach_type_ptr1, nach_type_ptr2]
    )


def div(builder, nach_type_ptr1, nach_type_ptr2):
    """
    Divides two NACHTYPE structs and returns a new NACHTYPE struct
    """
    return builder.call(
        get_symbol_by_name(builder, "div"), [nach_type_ptr1, nach_type_ptr2]
    )


def or_(builder, nach_type_ptr1, nach_type_ptr2):
    """
    Ors two NACHTYPE structs and returns a new NACHTYPE struct
    """
    return builder.call(
        get_symbol_by_name(builder, "nach_or"), [nach_type_ptr1, nach_type_ptr2]
    )


def and_(builder, nach_type_ptr1, nach_type_ptr2):
    """
    Ands two NACHTYPE structs and returns a new NACHTYPE struct
    """
    return builder.call(
        get_symbol_by_name(builder, "nach_and"), [nach_type_ptr1, nach_type_ptr2]
    )


def compare(builder, lhs, rhs, op):
    """
    Less than or equal to
    """
    comp_fns = {
        "==": lambda: get_symbol_by_name(builder, "nach_eq"),
        "!=": lambda: get_symbol_by_name(builder, "nach_neq"),
        "<": lambda: get_symbol_by_name(builder, "nach_lt"),
        "<=": lambda: get_symbol_by_name(builder, "nach_lte"),
        ">": lambda: get_symbol_by_name(builder, "nach_gt"),
        ">=": lambda: get_symbol_by_name(builder, "nach_gte"),
    }
    return builder.call(comp_fns[op](), [lhs, rhs])


def nach_print_(builder, nach_type_ptr):
    """
    Prints a NACHTYPE value
    """
    fn = get_symbol_by_name(builder, "printf")
    global_fmt = get_symbol_by_name(builder, "printf_format")
    ptr_fmt = builder.bitcast(global_fmt, STRING.as_pointer())
    builder.call(
        fn,
        [
            ptr_fmt,
            load_number(builder, nach_type_ptr),
            load_string(builder, nach_type_ptr),
            load_bool(builder, nach_type_ptr),
            nach_type_ptr,
        ],
    )


def nach_print(builder, nach_type_ptr):
    """
    Prints a NACHTYPE value
    """
    builder.call(get_symbol_by_name(builder, "nach_print"), [nach_type_ptr])


def define_nach_print(builder):
    """
    Defines the nach_print function in the module
    """
    module = builder.module
    function_type = ir.FunctionType(VOID, [NACHTYPE.as_pointer()])
    function = ir.Function(module, function_type, name="nach_print")
    entry = function.append_basic_block("entry")
    fn_builder = ir.IRBuilder(entry)
    nach_type_ptr = function.args[0]
    fn = get_symbol_by_name(fn_builder, "printf")
    global_fmt = get_symbol_by_name(fn_builder, "printf_format")
    ptr_fmt = fn_builder.bitcast(global_fmt, STRING.as_pointer())
    fn_builder.call(
        fn,
        [
            ptr_fmt,
            load_number(fn_builder, nach_type_ptr),
            load_string(fn_builder, nach_type_ptr),
            load_bool(fn_builder, nach_type_ptr),
            nach_type_ptr,
        ],
    )
    fn_builder.ret_void()


#
# Conditionals
#


def define_is_truthy(builder):
    """
    Defines the is_truthy function in the module
    """
    module = builder.module
    function_type = ir.FunctionType(NACHTYPE.as_pointer(), [NACHTYPE.as_pointer()])
    function = ir.Function(module, function_type, name="is_truthy")
    entry = function.append_basic_block("entry")
    fn_builder = ir.IRBuilder(entry)
    nach_type_ptr = function.args[0]

    true = allocate_bool(fn_builder, "true")
    false = allocate_bool(fn_builder, "false")

    # By default return false
    default_block = fn_builder.append_basic_block("default")
    fn_builder.position_at_end(default_block)
    fn_builder.ret(false)

    # If number is 0 return false, return true otherwise
    is_truthy_number_block = fn_builder.append_basic_block("is_truthy_number")
    fn_builder.position_at_end(is_truthy_number_block)
    with fn_builder.if_then(
        fn_builder.fcmp_ordered("==", load_number(fn_builder, nach_type_ptr), NUMBER(0))
    ):
        fn_builder.ret(false)
    fn_builder.ret(true)

    # If string is empty return false, return true otherwise
    is_truthy_string_block = fn_builder.append_basic_block("is_truthy_string")
    fn_builder.position_at_end(is_truthy_string_block)
    empty_string = allocate_string(fn_builder, "")
    compare_strings_result = compare_strings(
        fn_builder, nach_type_ptr, empty_string, "=="
    )
    with fn_builder.if_then(
        fn_builder.fcmp_ordered(
            "==",
            load_number(fn_builder, compare_strings_result),
            NUMBER(0),
        )
    ):
        fn_builder.ret(false)
    fn_builder.ret(true)

    # If bool, return the nach_type_ptr
    is_truthy_bool_block = fn_builder.append_basic_block("is_truthy_bool")
    fn_builder.position_at_end(is_truthy_bool_block)
    fn_builder.ret(nach_type_ptr)

    fn_builder.position_at_end(entry)
    switch_handler = fn_builder.switch(
        load_type(fn_builder, nach_type_ptr), default_block
    )
    switch_handler.add_case(INT8(0), is_truthy_number_block)
    switch_handler.add_case(INT8(1), is_truthy_string_block)
    switch_handler.add_case(INT8(2), is_truthy_bool_block)


def is_truthy(builder, nach_type_ptr):
    """
    Returns a BOOL value indicating if the nach_type_ptr is truthy
    """
    return builder.call(get_symbol_by_name(builder, "is_truthy"), [nach_type_ptr])


#
# Functions
#


def defn_function(builder, fn_name, fn_arg_number):
    module = builder.module
    fn_type = ir.FunctionType(
        NACHTYPE.as_pointer(), [NACHTYPE.as_pointer() for i in range(fn_arg_number)]
    )
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
    fn = get_symbol_by_name(builder, fn_name)
    return builder.call(fn, fn_args)


#
# If statements
#

def if_statement(builder, conditional_expression):
    return builder.if_else(
        load_bool(builder, conditional_expression)
    )
        


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
    """
    Declares printf function in the module
    """
    module = builder.module
    format = "double: %f | string: %s | bool: %d | address(ptr): %p \n\0"

    # Make global constant for format string
    cstring = INT8.as_pointer()
    fmt_bytes = _make_bytearray((format).encode("utf8"))
    # TODO: This shouldn't be here. Remove once we have a nachlang string handler
    # Defines a global printing format that will be used when resolving prints
    global_constant(builder, "printf_format", fmt_bytes)
    fnty = ir.FunctionType(NACHTYPE, [cstring], var_arg=True)
    ir.Function(module, fnty, name="printf")


def declare_strcmp(builder):
    """
    Declares strcmp function in the module
    """
    module = builder.module
    fnty = ir.FunctionType(INT32, [STRING.as_pointer(), STRING.as_pointer()])
    ir.Function(module, fnty, name="strcmp")


def define_empty_string(builder):
    global_constant(builder, "empty_string", _make_bytearray("".encode("utf8")))


def define_compare_strings(builder):
    """
    Defines the compare_strings function in the module
    """
    module = builder.module
    function_type = ir.FunctionType(
        NACHTYPE.as_pointer(), [NACHTYPE.as_pointer(), NACHTYPE.as_pointer(), INT8]
    )
    function = ir.Function(module, function_type, name="compare_strings")
    entry = function.append_basic_block("entry")
    fn_builder = ir.IRBuilder(entry)
    # TODO: These pointers are just wrong. WTH is going on here?
    string1_ptr, string2_ptr, op_type = function.args

    string1 = load_string(fn_builder, string1_ptr)
    string2 = load_string(fn_builder, string2_ptr)

    comparison_result = fn_builder.call(
        get_symbol_by_name(fn_builder, "strcmp"), [string1, string2]
    )

    false = allocate_bool(fn_builder, "false")
    true = allocate_bool(fn_builder, "true")

    default_block = fn_builder.append_basic_block("default")
    fn_builder.position_at_end(default_block)
    fn_builder.ret(false)

    # If op_type is 0, compare '=='
    eq_block = fn_builder.append_basic_block("eq_block")
    fn_builder.position_at_end(eq_block)
    with fn_builder.if_then(fn_builder.icmp_signed("==", comparison_result, INT32(0))):
        fn_builder.ret(true)
    fn_builder.ret(false)

    # If op_type is 1, compare '!='
    neq_block = fn_builder.append_basic_block("neq_block")
    fn_builder.position_at_end(neq_block)
    with fn_builder.if_then(fn_builder.icmp_signed("!=", comparison_result, INT32(0))):
        fn_builder.ret(true)
    fn_builder.ret(false)

    # If op_type is 2, compare '<'
    lt_block = fn_builder.append_basic_block("lt_block")
    fn_builder.position_at_end(lt_block)
    with fn_builder.if_then(fn_builder.icmp_signed("<", comparison_result, INT32(0))):
        fn_builder.ret(true)
    fn_builder.ret(false)

    # If op_type is 3, compare '<='
    lte_block = fn_builder.append_basic_block("lte_block")
    fn_builder.position_at_end(lte_block)
    with fn_builder.if_then(fn_builder.icmp_signed("<=", comparison_result, INT32(0))):
        fn_builder.ret(true)
    fn_builder.ret(false)

    # If op_type is 4, compare '>'
    gt_block = fn_builder.append_basic_block("gt_block")
    fn_builder.position_at_end(gt_block)
    with fn_builder.if_then(fn_builder.icmp_signed(">", comparison_result, INT32(0))):
        fn_builder.ret(true)
    fn_builder.ret(false)

    # If op_type is 5, compare '>='
    gte_block = fn_builder.append_basic_block("gte_block")
    fn_builder.position_at_end(gte_block)
    with fn_builder.if_then(fn_builder.icmp_signed(">=", comparison_result, INT32(0))):
        fn_builder.ret(true)
    fn_builder.ret(false)

    fn_builder.position_at_end(entry)
    switch_handler = fn_builder.switch(op_type, default_block)
    switch_handler.add_case(INT8(0), eq_block)
    switch_handler.add_case(INT8(1), neq_block)
    switch_handler.add_case(INT8(2), lt_block)
    switch_handler.add_case(INT8(3), lte_block)
    switch_handler.add_case(INT8(4), gt_block)
    switch_handler.add_case(INT8(5), gte_block)


def compare_strings(builder, string1, string2, op_type):
    """
    Compares two strings and returns a NACHTYPE struct
    """

    return builder.call(
        get_symbol_by_name(builder, "compare_strings"),
        [string1, string2, CONDITIONAL_OPS_MAPPINGS[op_type]],
    )


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
            declare_strcmp,
            define_allocate_nachtype,
            define_load_number,
            define_load_number_as_int,
            define_load_string,
            define_load_bool,
            define_allocate_number,
            define_allocate_string,
            define_allocate_bool,
            define_nach_print,
            define_empty_string,
            define_compare_strings,
            define_is_truthy,
            define_validate_are_equal_type,
            define_comparing_fns,
            define_add,
            define_sub,
            define_mul,
            define_div,
            define_or,
            define_and,
        ]
    )

    return builder, module
