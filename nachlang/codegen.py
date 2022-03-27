from llvmlite import binding, ir
from nachlang import utils
from functools import partial

# LLVM Initialization
# https://llvmlite.readthedocs.io/en/latest/user-guide/binding/initialization-finalization.html?highlight=initialize#initialization-and-finalization

symbol_table = {}

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


#
# Common resolvers
#


def get_first_key(data: dict, max_length: int = 1):
    if len(data) > max_length:
        raise Exception(f"Unexpected length for {data}")

    return next(iter(data.keys()))


# TODO: rename?
def resolve_ast_object(o: dict):
    """
    Expects an AST object.

    The Object is represented by a dictionary which should only contain one key
    """
    return nodes[o["name"]](o["value"])


#
# Resolvers
#


def resolve_with_no_returns(values):
    for e in values:
        resolve_ast_object(e)


def resolve_expression(expression):
    exp = utils._filter_parens(expression)[0]

    if type(exp) == dict:
        return resolve_ast_object(exp)
    else:
        expression_type = exp.name
        return nodes[expression_type](exp)


def resolve_binary_operation(bin_op):
    lhs = resolve_expression(bin_op[0]["value"])
    binary_operand = resolve_operand(bin_op[1])
    rhs = resolve_expression(bin_op[2]["value"])
    return binary_operand(lhs, rhs)


def resolve_define_var(definition):
    var_name = definition[1]

    expression = definition[2]
    expression_value = nodes["expression"](expression["value"])

    var_pointer = builder.alloca(INT32)
    symbol_table[var_name.value] = var_pointer
    builder.store(expression_value, var_pointer)

def resolve_if_statement(if_statement):
    """
    Allows both if/else type statements or just if statements

    * if it's an if/else statement the length of the if_statement arg will be equal to 10
    * if it's an if statement the length of the if_statement arg will be equal to 7
    """
    with builder.if_else(resolve_ast_object(if_statement[2])) as (then, otherwise):
        with then:
            resolve_ast_object(if_statement[4])
        with otherwise:
            if len(if_statement) == 10:
                resolve_ast_object(if_statement[7])

#
# Terminals
#


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
    if operand.name in ["EQ", "NEQ", "LT", "GT", "GTE", "LTE"]:
        return partial(builder.icmp_signed, operand.value)
    if operand.name == "AND":
        return builder.and_
    if operand.name == "OR":
        return builder.or_

    raise Exception(f"Couldn't resolve operand {operand}")

def resolve_var(var):
    pointer = symbol_table.get(var.value)
    if pointer == None:
        raise Exception(f"Variable not defined {var.name} at {var.source_pos}")
    return builder.load(pointer)


def ignore(item):
    return


#
# Function pointers
#

nodes = {
    "define_var": resolve_define_var,
    "binary_operation": resolve_binary_operation,
    "expression": resolve_expression,
    "NUMBER": resolve_number,
    "OPEN_PAREN": ignore,
    "CLOSE_PAREN": ignore,
    "VAR": resolve_var,
    "statement_list": resolve_with_no_returns,
    "statement": resolve_with_no_returns,
    "if_statement": resolve_if_statement,
}

#
# LLVM code gen
#


def print_module_body(module):
    print("\n".join(module._get_body_lines()))


def generate_llvm_ir(ast):
    resolve_ast_object(ast)
    # with open("output.ll", "w") as f:
    #     f.write(str(module))
    print_module_body(module)
    return module
