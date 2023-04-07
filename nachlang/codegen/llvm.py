from llvmlite import ir

global_context = ir.global_context

INT8 = ir.IntType(8)
NUMBER = ir.DoubleType()
INT32 = ir.IntType(32)
STRING = ir.IntType(8)
VOID = ir.VoidType()
NACHTYPE = global_context.get_identified_type("struct.nachtype")

NACHTYPE.set_body(INT8, NUMBER, STRING.as_pointer())

type_mappings = {0: NUMBER, 1: STRING}

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
    Allocates a python number in a NACHTYPE struct

    The NUMBER type is denoted as 0 in the NACHTYPE struct
    """
    return _allocate_number(builder, NUMBER(float(value)))


def add(builder, nach_type_ptr1, nach_type_ptr2):
    """
    Adds two NACHTYPE structs and returns a new NACHTYPE struct
    """
    value1 = load_number(builder, nach_type_ptr1)
    value2 = load_number(builder, nach_type_ptr2)
    result = builder.fadd(value1, value2)
    return _allocate_number(builder, result)


def sub(builder, nach_type_ptr1, nach_type_ptr2):
    """
    Subtracts two NACHTYPE structs and returns a new NACHTYPE struct
    """
    value1 = load_number(builder, nach_type_ptr1)
    value2 = load_number(builder, nach_type_ptr2)
    result = builder.fsub(value1, value2)
    return _allocate_number(builder, result)
