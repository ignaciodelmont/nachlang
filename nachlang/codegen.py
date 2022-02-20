from llvmlite import binding, ir
from nachlang import utils

# LLVM Initialization
# https://llvmlite.readthedocs.io/en/latest/user-guide/binding/initialization-finalization.html?highlight=initialize#initialization-and-finalization


binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()

# TODO: Review this ###
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

# TODO: here's a pattern, very similar for expressions and blocks
# the only diff is that expressions filter out parens, shouldn't be harmful to do
# in blocks too. Here we could have a function that targets both at the same time
def resolve_expression_list(expression_list):
    for e in expression_list:
        expression = list(e.keys())[0]
        nodes[expression](e[expression])

def resolve_expression(expression):
    exp = utils._filter_parens(expression)[0]

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
    if operand.name == "MINUS_SIGN":
        return builder.sub
    if operand.name == "MULTIPLICATION_SIGN":
        return builder.mul
    if operand.name == "DIVISION_SIGN":
        return builder.sdiv

def ignore(item):
    return

nodes = {
    "binary_operation": resolve_binary_operation,
    "expression": resolve_expression,
    "NUMBER": resolve_number,
    "OPEN_PAREN": ignore,
    "CLOSE_PAREN": ignore,
    "expression_list": resolve_expression_list
}

def generate_llvm_ir(ast):
    print(resolve_expression_list(ast["expression_list"]))
    print(module)
    pass
