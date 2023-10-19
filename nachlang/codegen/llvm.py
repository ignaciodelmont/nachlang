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


def nach_print(builder, value):
    """
    Prints a nachtype
    """
    return core.nach_print(builder, value)


def defn_function(builder, fn_name, fn_arg_number):
    return core.defn_function(builder, fn_name, fn_arg_number)


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
