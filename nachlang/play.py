from llvmlite import ir, binding

# module = ir.Module(name=__file__)

# I8 = ir.IntType(8)
# VOID = ir.VoidType()

# struct = ir.LiteralStructType([I8, VOID])
# print(struct)
# module.triple = binding.get_default_triple()
# func_type = ir.FunctionType(struct, [], False)
# base_func = ir.Function(module, func_type, name="entrypoint")
# block = base_func.append_basic_block(name="entry")
# builder = ir.IRBuilder(block)

# # https://github.com/numba/llvmlite/issues/442

# # struct = ir.LiteralStructType([I8,VOID])

# struct_ptr = builder.alloca(struct)
# int_ptr = builder.gep(struct_ptr, [ir.Constant(I8, 0)])
# print(int_ptr)

# print(builder.store(ir.Constant(I8, 1), int_ptr))
# print(builder.load(int_ptr))
# print(builder.load(struct_ptr))


# builder.ret(builder.add(ir.Constant(I8, 1), ir.Constant(I8, 1)))

# print(module)

# ---

import llvmlite.ir as ir

int8 = ir.IntType(8)
int32 = ir.IntType(32)
string_ptr = ir.IntType(8).as_pointer()
string = ir.IntType(8)

ctx = ir.global_context
nachtype = ctx.get_identified_type('struct.nachtype')
nachtype.set_body(int8, int32.as_pointer(), string.as_pointer())

m = ir.Module()
f = ir.Function(m, ir.FunctionType(int32, []), 'main')
bldr = ir.IRBuilder(f.append_basic_block())

# o = bldr.alloca(nachtype)
# book_ptr_0 = bldr.gep(o, [int32(0), int32(0)], inbounds=True)
# bldr.store(int32(5), book_ptr_0, align=1)
# book_ptr_1 = bldr.gep(o, [int32(0), int32(1)], inbounds=True)
# bldr.store(int8(4), book_ptr_1, align=1)
# bldr.ret(int32(0))

def allocate_string(builder, string_value):
    """
    TODO: Check the following

    https://stackoverflow.com/questions/37901866/get-pointer-to-first-element-of-array-in-llvm-ir

    %str2 = alloca i8*
    %1 = alloca [4 x i8]
    store [4 x i8] c"foo\00", [4 x i8]* %1
    %2 = bitcast [4 x i8]* %1 to i8*
    store i8* %2, i8** %str2
    """
    str_ptr = bldr.alloca(string)

    value = ir.Constant(ir.ArrayType(int8, len(string_value)), bytearray(string_value, 'utf8'))
    allocated_str_space = bldr.alloca(ir.ArrayType(int8, len(string_value)))
    stored_value = bldr.store(value, allocated_str_space)
    # print(stored_value)
    # print(allocated_str_space)
    bitcasted = bldr.bitcast(allocated_str_space, string)
    stored_str = bldr.store(bitcasted, str_ptr, align=1)
    # print(stored_str)
    nach_ptr = bldr.alloca(nachtype)
    nach_str_ptr = bldr.gep(nach_ptr, [int32(0), int32(2)], inbounds=True)
    print(nach_str_ptr, "\n\n", str_ptr, "\n\n\n")
    bldr.store(str_ptr, nach_str_ptr, align=1)



allocate_string(bldr, "Hey there")

def allocate_number(builder, number_value):
    number_ptr = bldr.alloca(int32) 
    bldr.store(int32(number_value), number_ptr, align=1)

    nach_type_ptr = bldr.alloca(nachtype)
    nach_type_number_ptr = bldr.gep(nach_type_ptr, [int32(0), int32(1)], inbounds=True)

    bldr.store(number_ptr, nach_type_number_ptr, align=1)

# allocate_number(bldr, 5)

print(m)
