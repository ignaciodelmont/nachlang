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
    # TODO: IDELMONT fix string allocation
    return core.allocate_string(builder, string)


def initialize():
    """
    Initializes the llvm module with core functions
    """
    return core.initialize()
