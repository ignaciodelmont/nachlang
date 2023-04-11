from llvmlite import ir

global_context = ir.global_context


INT8 = ir.IntType(8)
INT32 = ir.IntType(32)
STRING = ir.IntType(8).as_pointer()
VOID = ir.VoidType()
NACHTYPE = global_context.get_identified_type("struct.nachtype")
NACHTYPE.set_body(INT8, INT32, STRING)

type_mappings = {0: INT32, 1: STRING}

# Write a function that allocates the string type of the NACHTYPE struct


def allocate_string(builder, string):
    string_type = NACHTYPE.elements[2]
    string_ptr = builder.alloca(string_type)
    builder.store(string, string_ptr)
    return string_ptr


