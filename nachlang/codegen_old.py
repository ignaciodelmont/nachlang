from ast import Expression, arg
from dataclasses import dataclass
from enum import Enum
from re import I
from typing import Any, Type
from llvmlite import binding, ir
from nachlang import utils
from nachlang import symbol_table
from functools import partial, reduce
from nachlang.debugger import logger as dlog
import pprint
# LLVM Initialization
# https://llvmlite.readthedocs.io/en/latest/user-guide/binding/initialization-finalization.html?highlight=initialize#initialization-and-finalization

# Types
global_context = ir.global_context
INT32 = ir.IntType(32)
INT8 = ir.IntType(8)
INT8_PTR = ir.IntType(8).as_pointer()
INT1 = ir.IntType(1)
VOID = ir.VoidType()
NACHTYPE = global_context.get_identified_type("struct.nachtype")
NACHTYPE.set_body(INT1, INT32)



def create_context(builder, scope_path):
    context = builder.module.context
    # TODO: Do not use IdentifiedStructType directly
    # https://github.com/numba/llvmlite/blob/a6c58beb5d5bc44ede0430d864d4a2b2951a7ee9/llvmlite/ir/types.py#L369

    # This "looks" promising https://github.com/numba/llvmlite/issues/442 (take a look at struct.Book)
    # struct = ir.IdentifiedStructType(context, "nachtype")
    symbol_table.add_scope(scope_path)
    return {
        "builder": builder,
        "scope_path": scope_path,
        "nachtype": INT32
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
    builder = context["builder"]
    lhs = resolve_expression(bin_op[0]["value"], context)
    rhs = resolve_expression(bin_op[2]["value"], context)
    binary_operand = resolve_operand(bin_op[1], context)

    if type(binary_operand) == partial and binary_operand.func.__name__ == "icmp_signed":
        t = TypesEnum.INT1
        bin_func = lambda lhs, rhs: builder.trunc(binary_operand(lhs, rhs), INT1)
    else:
        # TODO: do better handling of type here
        t = rhs.type
        bin_func = binary_operand

    return allocate(builder, bin_func(load(builder, lhs), load(builder, rhs)), t)


def resolve_define_var(definition, context):
    """
    The value will already be allocated due to the custom Nachtype we're using, so
    all this function has to do is add an entry to the symbol table to reference the
    expression.
    """
    var_name = definition[1]
    expression = definition[2]
    expression_value = nodes["expression"](expression["value"], context)
    scope_path = context["scope_path"]
    symbol_table.add_reference(scope_path, var_name.value, expression_value)
    return expression_value


def resolve_if_statement(if_statement, context):
    """
    Allows both if/else type statements or just if statements

    * if it's an if/else statement the length of the if_statement arg will be equal to 10
    * if it's an if statement the length of the if_statement arg will be equal to 7
    """
    builder = context["builder"]
    
    with builder.if_else(
        load(builder, resolve_ast_object(if_statement[2], context))) as (then, otherwise):
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
        nach_val = resolve_expression(return_statement[1]["value"], context)
        builder.ret(nach_val.pointer)
        # TODO: maybe adding the return to the symbol table is not needed...
        symbol_table.add_return(scope_path, nach_val)
        return nach_val
    else:
        symbol_table.add_return(scope_path, builder.ret_void())


def resolve_define_function(function_definition, context):
    scope_path = context["scope_path"]
    arg_types, arg_names = resolve_arguments(function_definition[3]["value"], context)
    function_types = ir.FunctionType(NACHTYPE.as_pointer(), arg_types)
    fn_name = function_definition[1].value
    fn = ir.Function(module, function_types, name=fn_name)
    fn_args = fn.args
    with nested_scope_context(context, fn, (arg_names, fn_args), fn_name) as ctx:        
        resolve_ast_object(function_definition[6], ctx)
        return_type = NACHTYPE.as_pointer()
        fn.type = ir.FunctionType(return_type, arg_types).as_pointer()
        fn.ftype = ir.FunctionType(return_type, arg_types)
        symbol_table.add_reference(scope_path , fn_name, fn)


def resolve_call_function(call_function, context):
    dlog.info(call_function)
    builder = context["builder"]
    scope_path = context["scope_path"]
    fn_name = call_function[0].value
    fn = symbol_table.get_reference(scope_path , fn_name)
    dlog.info("Printing function")
    dlog.info(fn)
    arg_values = resolve_ast_object(call_function[2], context)
    dlog.info(arg_values)
    return builder.call(fn, (arg_val.pointer for arg_val in arg_values))


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
    nach_value = resolve_expression(print_expression[2]["value"], context)
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
    return builder.call(fn, [ptr_fmt] + list([load(builder, nach_value)]))

####
    
# Function call example https://gist.github.com/ssarangi/6b8e0c8507dae356f72b


def resolve_arguments(arguments, context):
    return tuple(NACHTYPE.as_pointer() for a in arguments), tuple(a.value for a in arguments)

def resolve_argument_values(argument_values, context):
    res = list(map(partial(resolve_ast_object, context=context), argument_values))
    return res
    # return list(map(partial(resolve_ast_object, context=context), argument_values))

#
# Terminals
#
types = {
    0: INT1,
    1: INT32,
}

class TypesEnum(Enum):
    INT1 = 0
    INT32 = 1

types_e = {
    INT1: 0,
    INT32: 1
}

@dataclass
class NachValue:
    type: TypesEnum
    pointer: Any

def get_pointer(nach_value):
    return builder.gep(nach_value.pointer, [INT32(0), INT32(nach_value.type.value)], inbounds=True)

def load(builder, nach_value_or_argument):
    print(nach_value_or_argument)
    dlog.info(nach_value_or_argument)
    if (type(nach_value_or_argument) == ir.Argument):
        print("I'm an argument")
        return builder.load(nach_value_or_argument)
    elif type(nach_value_or_argument) == NachValue:
        print("I'm a value")
        return builder.load(get_pointer(nach_value_or_argument))
    else:
        raise Exception(f"Unexpected value when loading. Value: {nach_value_or_argument}")

def allocate(builder, value, type_: TypesEnum) -> NachValue:
    o = builder.alloca(NACHTYPE)
    value_type_id = type_.value
    value_ptr = builder.gep(o, [INT32(0), INT32(value_type_id)], inbounds=True)
    llvm_type = types[value_type_id]
    
    # if type is `str` it means we're storing a python resolved value and it needs to be casted
    # otherwise, we're storing an llvm resolved value, so we just store the value itself
    if type(value) == str:
        builder.store(llvm_type(value), value_ptr, align=1)
    else:
        builder.store(value, value_ptr, align=1)
    return NachValue(type_, o)

def resolve_number(num, context):
    builder = context["builder"]
    return allocate(builder, num.value, TypesEnum.INT32)


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

    return reference

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