from ast import Expression, arg
from re import I
from llvmlite import binding, ir
from nachlang import utils
from nachlang import symbol_table
from functools import partial, reduce

# LLVM Initialization
# https://llvmlite.readthedocs.io/en/latest/user-guide/binding/initialization-finalization.html?highlight=initialize#initialization-and-finalization



# Types

INT32 = ir.IntType(32)
INT1 = ir.IntType(1)
VOID = ir.VoidType()

def create_context(builder, scope_path):
    symbol_table.add_scope(scope_path)
    return {
        "builder": builder,
        "scope_path": scope_path
    }

"""
{
    "main": {
        "references": {},
        "nested": {
            "add": {
                "references": {},
                "nested": {}
            }
        }
    }
}
"""

#
# Common resolvers
#


def get_first_key(data: dict, max_length: int = 1):
    if len(data) > max_length:
        raise Exception(f"Unexpected length for {data}")

    return next(iter(data.keys()))


# TODO: rename?
def resolve_ast_object(o: dict, context):
    """
    Expects an AST object.

    The Object is represented by a dictionary which should only contain one key
    """
    return nodes[o["name"]](o["value"], context)


#
# Resolvers
#


def resolve_with_no_returns(values, context):
    for e in values:
        resolve_ast_object(e, context)


def resolve_expression(expression, context):
    exp = utils._filter_parens(expression)[0]

    if type(exp) == dict:
        return resolve_ast_object(exp, context)
    else:
        expression_type = exp.name
        return nodes[expression_type](exp, context)


def resolve_binary_operation(bin_op, context):
    lhs = resolve_expression(bin_op[0]["value"], context)
    binary_operand = resolve_operand(bin_op[1], context)
    rhs = resolve_expression(bin_op[2]["value"], context)
    return binary_operand(lhs, rhs)


def resolve_define_var(definition, context):
    builder = context["builder"]

    var_name = definition[1]

    expression = definition[2]
    expression_value = nodes["expression"](expression["value"], context)

    var_pointer = builder.alloca(INT32)
    
    scope_path = context["scope_path"]
    symbol_table.add_reference(scope_path, var_name.value, var_pointer)

    builder.store(expression_value, var_pointer)


def resolve_if_statement(if_statement, context):
    """
    Allows both if/else type statements or just if statements

    * if it's an if/else statement the length of the if_statement arg will be equal to 10
    * if it's an if statement the length of the if_statement arg will be equal to 7
    """
    builder = context["builder"]

    with builder.if_else(
        builder.trunc(resolve_ast_object(if_statement[2], context), INT1)) as (then, otherwise):
        with then:
            resolve_ast_object(if_statement[4], context)
        with otherwise:
            if len(if_statement) == 10:
                resolve_ast_object(if_statement[7], context)


from contextlib import contextmanager

@contextmanager
def nested_scope_context(context, block_appendable, args, scope_name):
    builder = context["builder"]
    curr_block = builder.block
    new_block = block_appendable.append_basic_block(name="entry")

    new_scope_path = context["scope_path"] + [scope_name]
    new_scope_context = create_context(builder, new_scope_path)

    add_ref = partial(symbol_table.add_reference, new_scope_path)
    
    list(map(lambda a: add_ref(*a), zip(*args)))

    builder.position_at_start(new_block)
    yield new_scope_context
    builder.position_at_end(curr_block)

def resolve_return(return_statement, context):
    builder = context["builder"]
    scope_path = context["scope_path"]
    if len(return_statement) == 2:
        expression = resolve_expression(return_statement[1]["value"], context)
        builder.ret(expression)
        symbol_table.add_return(scope_path, expression)
    else:
        symbol_table.add_return(scope_path, builder.ret_void())


def resolve_define_function(function_definition, context):    
    def infer_return_type(context):
        scope_path = context["scope_path"]
        scope = symbol_table.get_scope(scope_path)
        returns = scope["returns"]

        if not bool(returns):
            return VOID

        all_possible_return_types = [t.type for t in returns]

        if all_possible_return_types.count(all_possible_return_types[0]) == len(all_possible_return_types):
            return all_possible_return_types[0]
        else:
            raise Exception("Return types do not match in function")

    scope_path = context["scope_path"]
    arg_types, arg_names = resolve_arguments(function_definition[3]["value"], context)
    function_types = ir.FunctionType(VOID, arg_types)
    fn_name = function_definition[1].value
    fn = ir.Function(module, function_types, name=fn_name)
    fn_args = fn.args
    with nested_scope_context(context, fn, (arg_names, fn_args), fn_name) as ctx:
        resolve_ast_object(function_definition[6], ctx)
        return_type = infer_return_type(ctx)
        fn.type = ir.FunctionType(return_type, arg_types).as_pointer()
        fn.ftype = ir.FunctionType(return_type, arg_types)
        fn.return_value = return_type
        symbol_table.add_reference(scope_path , fn_name, fn)

def resolve_call_function(call_function, context):
    builder = context["builder"]
    scope_path = context["scope_path"]
    fn_name = call_function[0].value
    fn = symbol_table.get_reference(scope_path , fn_name)
    arg_values = resolve_ast_object(call_function[2], context)
    return builder.call(fn, arg_values)


voidptr_t = ir.IntType(8).as_pointer()

# https://github.com/numba/numba/blob/main/numba/core/cgutils.py

def make_bytearray(buf):
    """
    Make a byte array constant from *buf*.
    """
    b = bytearray(buf)
    n = len(b)
    return ir.Constant(ir.ArrayType(ir.IntType(8), n), b)

def add_global_variable(context, ty, name, addrspace=0):
    builder = context["builder"]
    module = builder.module
    unique_name = module.get_unique_name(name)
    return ir.GlobalVariable(module, ty, unique_name, addrspace)

def global_constant(context, name, value, linkage='internal'):
    """
    Get or create a (LLVM module-)global constant with *name* or *value*.
    """
    data = add_global_variable(context, value.type, name)
    data.linkage = linkage
    data.global_constant = True
    data.initializer = value
    return data

# originally `printf`
def resolve_print_expression(print_expression, context):
    """
    Calls printf().
    Argument `format` is expected to be a Python string.
    Values to be printed are listed in `args`.
    Note: There is no checking to ensure there is correct number of values
    in `args` and there type matches the declaration in the format string.
    """
    expression = resolve_expression(print_expression[2]["value"], context)

    # return
    builder = context["builder"]

    format = "res: %d \n\r"
    assert isinstance(format, str)
    mod = builder.module
    # Make global constant for format string
    cstring = voidptr_t
    fmt_bytes = make_bytearray((format + '\00').encode('ascii'))
    global_fmt = global_constant(context, "printf_format", fmt_bytes)
    fnty = ir.FunctionType(INT32, [cstring], var_arg=True)
    # Insert printf()
    try:
        fn = mod.get_global('printf')
    except KeyError:
        fn = ir.Function(mod, fnty, name="printf")
    # Call
    ptr_fmt = builder.bitcast(global_fmt, cstring)
    # 
    return builder.call(fn, [ptr_fmt] + list([expression]))

####
    
# Function call example https://gist.github.com/ssarangi/6b8e0c8507dae356f72b


def resolve_arguments(arguments, context):
    return tuple(INT32 for a in arguments), tuple(a.value for a in arguments)

def resolve_argument_values(argument_values, context):
    return list(map(partial(resolve_ast_object, context=context), argument_values))

#
# Terminals
#


def resolve_number(num, *args):
    return ir.Constant(INT32, num.value)


def resolve_operand(operand, context):
    builder = context["builder"]

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

def resolve_var(var, context):
    scope_path = context["scope_path"]
    reference = symbol_table.get_reference(scope_path ,var.value)
    
    if reference == None:
        raise Exception(f"Variable not defined {var.name} at {var.source_pos}")

    if isinstance(reference, ir.Argument):
        return reference
    else:
        return builder.load(reference)


def ignore(item):
    return 


#
# Function pointers
#

nodes = {
    "define_var": resolve_define_var,
    "argument_values": resolve_argument_values,
    "define_function": resolve_define_function,
    "call_function": resolve_call_function,
    "return": resolve_return,
    "print_expression": resolve_print_expression,
    "arguments": resolve_arguments,
    "binary_operation": resolve_binary_operation,
    "expression": resolve_expression,
     "statement_list": resolve_with_no_returns,
    "statement": resolve_with_no_returns,
    "if_statement": resolve_if_statement,
    "NUMBER": resolve_number,
    "OPEN_PAREN": ignore,
    "CLOSE_PAREN": ignore,
    "VAR": resolve_var,
}

#
# LLVM code gen
#

binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()

# TODO: Review this ###
module = ir.Module(name=__file__)
module.triple = binding.get_default_triple()
func_type = ir.FunctionType(VOID, [], False)
base_func = ir.Function(module, func_type, name="entrypoint")
block = base_func.append_basic_block(name="entry")
builder = ir.IRBuilder(block)
####

def print_module_body(module):
    print("\n".join(module._get_body_lines()))


def generate_llvm_ir(ast):
    resolve_ast_object(ast, create_context(builder, ["entrypoint"]))
    # with open("output.ll", "w") as f:
    #     f.write(str(module))
    # print_module_body(module)
    builder.ret_void()
    return module

### Read about state diagrams for documen