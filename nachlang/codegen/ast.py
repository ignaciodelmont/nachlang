from dataclasses import dataclass
from enum import Enum
from typing import Any

from nachlang.codegen import llvm
from nachlang import symbol_table, utils


class TypesEnum(Enum):
    INT1 = 0
    INT32 = 1

@dataclass
class NachValue:
    type: TypesEnum
    pointer: Any

def allocate(builder, value, type_: TypesEnum) -> NachValue:
    o = builder.alloca(llvm.NACHTYPE)
    value_type_id = type_.value
    value_ptr = builder.gep(o, [llvm.NUMBER(0), llvm.NUMBER(value_type_id)], inbounds=True)
    llvm_type = llvm.type_mappings[value_type_id]
    # if type is `str` it means we're storing a python resolved value and it needs to be casted
    # otherwise, we're storing an llvm resolved value, so we just store the value itself
    if type(value) == str:
        builder.store(llvm_type(value), value_ptr, align=1)
    else:
        builder.store(value, value_ptr, align=1)
    return NachValue(type_, o)



#
# AST Codegen Resolvers
#

def resolve_ast_node(o: dict, context):
    # NOTE: previously called resolve_ast_object. TODO: Remove this note when done
    """
    Expects an AST Node.

    The "Node Dict" is represented by a dictionary with the following structure

    {
        "name": "<node name>",
        "value": [Token | "Node Dict"]
    }
    """
    return nodes[o["name"]](o["value"], context)


def resolve_with_no_returns(values, context):
    """
    Resolves a list of ast nodes. This gets invoked when there are multiple
    nodes at the same level in the AST tree that have the same parent.

    For example for `statement_list` we find a list of child nodes
    """
    for e in values:
        resolve_ast_node(e, context)

#
# Non-terminals resolvers
#

def resolve_expression(expression, context):
    """
    An expression can be either a terminal or not

    terminals: NUMBER | VAR 
    non-terminals: binary_operation | call_function | print_expression

    """
    def is_terminal_expression(exp):
        return type(exp) != dict

    exp = utils._filter_parens(expression)[0]

    if is_terminal_expression(exp):
        expression_type = exp.name 
        return nodes[expression_type](exp, context)
    
    return resolve_ast_node(exp, context)

def resolve_binary_operation(binary_operation, context):
    """
    Resolves a binary operation

    Args:
        binary_operation: A dict representing a binary operation
        context: A dict representing the context
    """
    builder = context["builder"]
    left = resolve_ast_node(binary_operation[0], context)
    right = resolve_ast_node(binary_operation[2], context)
    operator = binary_operation[1].value
    
    if operator == "+":
        return llvm.add(builder, left, right)
    elif operator == "-":
        return llvm.sub(builder, left, right)
    

#
# Terminal resolvers
#

def resolve_number(num, context):
    builder = context["builder"]
    return llvm.allocate_number(builder, num.value)

def resolve_string(string, context):
    builder = context["builder"]
    return llvm.allocate_string(builder, string.value)
    
#
# Resolvers pointers
#

nodes = {
    # "define_var": resolve_define_var,
    # "argument_values": resolve_argument_values,
    # "define_function": resolve_define_function,
    # "call_function": resolve_call_function,
    # "return": resolve_return,
    # "print_expression": resolve_print_expression,
    # "arguments": resolve_arguments,
    "binary_operation": resolve_binary_operation,
    "expression": resolve_expression,
    "statement_list": resolve_with_no_returns,
    "statement": resolve_with_no_returns,
    # "if_statement": resolve_if_statement,
    "NUMBER": resolve_number,
    "STRING": resolve_string,
    # "OPEN_PAREN": ignore,
    # "CLOSE_PAREN": ignore,
    # "VAR": resolve_var,
}


#
# Utilities
#

def create_context(builder, scope_path):
    """
    Creates a context which provides context information for code generation

    Returns:

    {
        "builder": <llvmlite Builder Object>,
        "scope_path": <scope set for context>: [str]
    }
    """
    symbol_table.add_scope(scope_path)
    return {
        "builder": builder,
        "scope_path": scope_path,
    }

def generate_llvm_ir(ast, builder, module):
    """
    Generates LLVM ir

    Args:
        ast: A dict representing the code AST
        builder: An llvmlite Builder Object
        module: An llvmlite module object
    """

    resolve_ast_node(ast, create_context(builder, ["entrypoint"]))

    builder.ret_void()
    return module


