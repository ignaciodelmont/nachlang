from nachlang.codegen import core


def add(builder, lhs, rhs):
    """
    Adds two nachtypes
    """
    return core.add(builder, lhs, rhs)


def sub(builder, lhs, rhs):
    """
    Subtracts two nachtypes
    """
    return core.sub(builder, lhs, rhs)


def mul(builder, lhs, rhs):
    """
    Multiplies two nachtypes
    """
    return core.mul(builder, lhs, rhs)


def div(builder, lhs, rhs):
    """
    Divides two nachtypes
    """
    return core.div(builder, lhs, rhs)


def or_(builder, lhs, rhs):
    """
    Ors two nachtypes
    """
    return core.or_(builder, lhs, rhs)


def and_(builder, lhs, rhs):
    """
    Ands two nachtypes
    """
    return core.and_(builder, lhs, rhs)


def compare(builder, lhs, rhs, op):
    """
    Less than or equal to
    """
    return core.compare(builder, lhs, rhs, op)


def allocate_number(builder, number):
    """
    Allocates a number on the heap
    """
    return core.allocate_number(builder, core.NUMBER(number))


def allocate_string(builder, string):
    """
    Allocates a string on the heap
    """
    return core.allocate_string(builder, string)


def allocate_bool(builder, boolean):
    """
    Allocates a boolean on the heap
    """
    return core.allocate_bool(builder, boolean)


def nach_print(builder, value):
    """
    Prints a nachtype
    """
    return core.nach_print(builder, value)


def is_truthy(builder, value):
    """
    Checks if a nachtype is truthy
    """
    return core.is_truthy(builder, value)


def defn_function(builder, fn_name, fn_arg_number):
    return core.defn_function(builder, fn_name, fn_arg_number)


def if_statement(builder, conditional_expression):
    return core.if_statement(builder, conditional_expression)


def call_function(builder, fn_name, args):
    """
    Resolves a function call
    """
    return core.call_function(builder, fn_name, args)


def return_(builder, value):
    """
    Returns a nachtype
    """
    return core.return_(builder, value)


def initialize():
    """
    Initializes the llvm module with core functions
    """
    return core.initialize()
