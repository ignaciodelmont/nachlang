from nachlang.codegen import llvm
from nachlang import symbol_table, utils
from contextlib import contextmanager
from functools import partial


@contextmanager
def nested_scope_context(current_context, new_builder, scope_name):
    yield create_context(new_builder, current_context["scope_path"] + [scope_name])


#
# AST Codegen Resolvers
#


def resolve_ast_node(o: dict, context):
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
        return not isinstance(exp, dict)

    exp = utils.filter_parens(expression)[0]

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

    funcs = {
        "+": llvm.add,
        "-": llvm.sub,
        "*": llvm.mul,
        "/": llvm.div,
        "or": llvm.or_,
        "and": llvm.and_,
        "<=": partial(llvm.compare, op="<="),
        ">=": partial(llvm.compare, op=">="),
        "==": partial(llvm.compare, op="=="),
        "<": partial(llvm.compare, op="<"),
        ">": partial(llvm.compare, op=">"),
        "!=": partial(llvm.compare, op="!="),
    }

    fn = funcs[operator]
    return fn(builder, left, right)


def resolve_if_statement(if_statement, context):
    """
    If statement can be of two forms:
    1. (if (expression) {statement_list})
    2. (if (expression) {statement_list} {statement_list})
    """
    resolved_conditional_expression = resolve_expression(
        if_statement[2]["value"], context
    )
    casted_conditional_expression = llvm.is_truthy(
        context["builder"], resolved_conditional_expression
    )
    with llvm.if_statement(context["builder"], casted_conditional_expression) as (
        then,
        otherwise,
    ):
        with then:
            resolve_ast_node(if_statement[4], context)
        with otherwise:
            # if/else scenario has 10 items
            if len(if_statement) == 10:
                resolve_ast_node(if_statement[7], context)
            else:
                pass


def resolve_print_expression(print_exp, context):
    nach_val_to_resolve = print_exp[2]
    nach_val = resolve_expression(nach_val_to_resolve["value"], context)
    builder = context["builder"]
    llvm.nach_print(builder, nach_val)


def resolve_is_truthy_expression(is_truthy_exp, context):
    builder = context["builder"]
    nach_val_to_resolve = is_truthy_exp[2]
    nach_val = resolve_expression(nach_val_to_resolve["value"], context)
    return llvm.is_truthy(builder, nach_val)


def resolve_defn_function(function_definition, context):
    fn_name = function_definition[1].value
    fn_arg_names = [a.value for a in function_definition[3]["value"]]
    fn_builder, fn = llvm.defn_function(context["builder"], fn_name, len(fn_arg_names))
    with nested_scope_context(context, fn_builder, fn_name) as nested_context:
        fn_args = fn.args
        [
            symbol_table.add_reference(nested_context["scope_path"], arg_name, arg)
            for arg_name, arg in zip(fn_arg_names, fn_args)
        ]
        resolve_ast_node(function_definition[6], nested_context)

        # NOTE: if the last block of a function is not terminated, i.e there's no return
        # statement, we need add an implicit return statement
        if not fn.blocks[-1].is_terminated:
            llvm.return_(fn_builder, llvm.allocate_number(fn_builder, 0))


def resolve_return(return_exp, context):
    """
    Resolves a return statement

    Args:
        return_exp: A dict representing a return statement
        context: A dict representing the context
    """
    builder = context["builder"]
    return_value = resolve_expression(return_exp[1]["value"], context)
    llvm.return_(builder, return_value)


def resolve_call_function(call_fn_exp, context):
    builder = context["builder"]
    fn_name = call_fn_exp[0].value
    args = [
        resolve_expression(arg["value"], context) for arg in call_fn_exp[2]["value"]
    ]
    return llvm.call_function(builder, fn_name, args)


def resolve_define_var(define_var, context):
    """
    Resolves a variable definition

    Args:
        define_var: A list representing a variable definition
            [def_token, var_token, expression]

        context: A dict representing the context
    """
    var_name = define_var[1].value
    expression = define_var[2]
    resolved_expression = resolve_expression(expression["value"], context)
    symbol_table.add_reference(context["scope_path"], var_name, resolved_expression)
    return resolved_expression


def resolve_var(resolve_var, context):
    """
    Resolves a variable

    Args:
        resolve_var: A token representing a variable
        context: A dict representing the context
    """

    var_name = resolve_var.value
    return symbol_table.get_reference(context["scope_path"], var_name)


#
# Terminal resolvers
#


def resolve_number(num, context):
    builder = context["builder"]
    return llvm.allocate_number(builder, num.value)


def resolve_string(string, context):
    builder = context["builder"]
    # Need to remove the extra "" at beginning and end of string
    processed_value = string.value.replace('"', "")

    return llvm.allocate_string(builder, processed_value)


def resolve_bool(bool, context):
    builder = context["builder"]
    return llvm.allocate_bool(builder, bool.value)


#
# Resolvers pointers
#

nodes = {
    "define_var": resolve_define_var,
    # "argument_values": resolve_argument_values,
    "define_function": resolve_defn_function,
    "call_function": resolve_call_function,
    "return": resolve_return,
    "print_expression": resolve_print_expression,
    "is_truthy_expression": resolve_is_truthy_expression,
    # "arguments": resolve_arguments,
    "binary_operation": resolve_binary_operation,
    "expression": resolve_expression,
    "statement_list": resolve_with_no_returns,
    "statement": resolve_with_no_returns,
    "if_statement": resolve_if_statement,
    "BOOL": resolve_bool,
    "NUMBER": resolve_number,
    "STRING": resolve_string,
    # "OPEN_PAREN": ignore,
    # "CLOSE_PAREN": ignore,
    "VAR": resolve_var,
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


def generate_llvm_ir(ast):
    """
    Generates LLVM ir

    Args:
        ast: A dict representing the code AST
        builder: An llvmlite Builder Object
        module: An llvmlite module object
    """
    builder, module = llvm.initialize()
    r = resolve_ast_node(ast, create_context(builder, ["main"]))

    # print(builder.module)

    builder.ret_void()

    # TODO: IDELMONT maybe return the last generated value? as implicit return instead of void?

    return module
