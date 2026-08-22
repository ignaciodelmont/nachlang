"""
Errors caused by the program being compiled, as opposed to bugs in the
compiler. These carry a readable message and are reported without a
traceback, because the person reading them wrote nachlang, not nachlang's
internals.
"""


class NachlangError(Exception):
    """Base class for anything that is the program author's fault."""


class NachlangSyntaxError(NachlangError):
    """Source that could not be lexed or parsed."""

    def __init__(self, message, line=None, column=None):
        self.line = line
        self.column = column
        if line is not None:
            message = f"line {line}, column {column}: {message}"
        super().__init__(message)


class NachlangNameError(NachlangError):
    """A name used before it was defined, or defined twice."""
