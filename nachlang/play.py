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

ctx = ir.global_context
nachtype = ctx.get_identified_type('struct.nachtype')
nachtype.set_body(int32, int8)

m = ir.Module()
f = ir.Function(m, ir.FunctionType(int32, []), 'main')
bldr = ir.IRBuilder(f.append_basic_block())

o = bldr.alloca(nachtype)
book_ptr_0 = bldr.gep(o, [int32(0), int32(0)], inbounds=True)
bldr.store(int32(5), book_ptr_0, align=1)
book_ptr_1 = bldr.gep(o, [int32(0), int32(1)], inbounds=True)
bldr.store(int8(4), book_ptr_1, align=1)
bldr.ret(int32(0))

print(m)