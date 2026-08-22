"""Shared expectations for reading nachlang's output."""

# Booleans print through a "bool(%d)" format.
TRUE = "bool(1)"
FALSE = "bool(0)"


def num(value):
    """
    Every nachlang number is a double printed through "%f", so 7 comes back
    as "7.000000".
    """
    return f"{value:.6f}"
