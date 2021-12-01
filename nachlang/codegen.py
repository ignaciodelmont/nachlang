from llvmlite import binding, ir

# LLVM Initialization
# https://llvmlite.readthedocs.io/en/latest/user-guide/binding/initialization-finalization.html?highlight=initialize#initialization-and-finalization


binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()

# Review this ###
module = ir.Module(name=__file__)
module.triple = binding.get_default_triple()
func_type = ir.FunctionType(ir.IntType(32), [], False)
base_func = ir.Function(module, func_type, name="main")
block = base_func.append_basic_block(name="entry")
builder = ir.IRBuilder(block)
####


# Types

INT32 = ir.IntType(32)


# Resolvers

def resolve_expression(expression):
    exp = expression[0]
    if type(exp) == dict:
        expression_type = list(exp.keys())[0]
        return nodes[expression_type](exp[expression_type])
    else:
        expression_type = exp.name
        return nodes[expression_type](exp)


def resolve_binary_operation(bin_op):
    lhs = resolve_expression(bin_op[0]["expression"])
    binary_operand = resolve_operand(bin_op[1])
    rhs = resolve_expression(bin_op[2]["expression"])
    return binary_operand(lhs, rhs)
    

def resolve_number(num):
    return ir.Constant(INT32, num.value)

def resolve_operand(operand):
    if operand.name == "PLUS_SIGN":
        return builder.add

nodes = {
    "binary_operation": resolve_binary_operation,
    "NUMBER": resolve_number
}

def generate_llvm_ir(ast):
    print(resolve_expression(ast["expression"]))
    
    pass
