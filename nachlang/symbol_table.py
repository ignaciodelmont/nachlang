from functools import reduce
from webbrowser import get

symbol_table = {}

"""
{
    "scope_name": {
        "references": {
            "var_1": "<ref 1>",
            "func_1": <func 1",
        },
        "nested": {
            "func_1": {     // func_1 is a nested scope and it's the func_1 scope, which should be able to access top level scope
                "references": {},
                "nested": {}
            }
        }
    }
}
"""

def add_scope(scope_path):
    """
    Adds a new scope to the symbol table given a path
    """

    path_prefix, new_scope = scope_path[:-1], scope_path[-1]
    scope = get_scope(path_prefix)
    
    scope_structure = {
        "references": {},
        "nested": {},
        "returns": []
    }

    if path_prefix == []:
        scope[new_scope] = scope_structure
        return scope[new_scope]
    else:
        scope["nested"][new_scope] = scope_structure
        return scope["nested"][new_scope]


def get_scope(scope_path):
    """
    Gets a scope from the symbol table given a path
    """
    if scope_path == []:
        return symbol_table

    path_prefix, terminal_path = scope_path[:-1], scope_path[-1]

    def reducer(acc, key):
        if not acc:
            return acc
        
        return acc[key]["nested"]

    pre_scope = reduce(reducer, path_prefix, symbol_table)

    return pre_scope[terminal_path]


def add_reference(scope_path, name, reference):
    scope = get_scope(scope_path)
    scope["references"][name] = reference
    return scope

def add_return(scope_path, reference):
    scope = get_scope(scope_path)
    scope["returns"] = scope["returns"] +[reference]
    return scope

def get_reference(scope_path, name):
    for i in range(len(scope_path)):
        if i == 0:
            scope = get_scope(scope_path)
        else:
            scope = get_scope(scope_path[:-i])

        if name in scope["references"]:
            return scope["references"][name]

    raise Exception(f"'{name}' couldn't be found in scope")





