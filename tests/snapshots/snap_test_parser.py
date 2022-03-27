# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['test_ast_building Build AST for: add constants'] = {
    'name': 'statement_list',
    'value': [
        {
            'name': 'statement',
            'value': [
                {
                    'name': 'expression',
                    'value': [
                        {
                            'name': 'binary_operation',
                            'value': [
                                {
                                    'name': 'expression',
                                    'value': [
                                        GenericRepr("Token('NUMBER', '1')")
                                    ]
                                },
                                GenericRepr("Token('PLUS_SIGN', '+')"),
                                {
                                    'name': 'expression',
                                    'value': [
                                        GenericRepr("Token('NUMBER', '1')")
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

snapshots['test_ast_building Build AST for: arithmetic precedence'] = {
    'name': 'statement_list',
    'value': [
        {
            'name': 'statement',
            'value': [
                {
                    'name': 'expression',
                    'value': [
                        {
                            'name': 'binary_operation',
                            'value': [
                                {
                                    'name': 'expression',
                                    'value': [
                                        {
                                            'name': 'binary_operation',
                                            'value': [
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        GenericRepr("Token('NUMBER', '1')")
                                                    ]
                                                },
                                                GenericRepr("Token('PLUS_SIGN', '+')"),
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        {
                                                            'name': 'binary_operation',
                                                            'value': [
                                                                {
                                                                    'name': 'expression',
                                                                    'value': [
                                                                        GenericRepr("Token('NUMBER', '3')")
                                                                    ]
                                                                },
                                                                GenericRepr("Token('MULTIPLICATION_SIGN', '*')"),
                                                                {
                                                                    'name': 'expression',
                                                                    'value': [
                                                                        {
                                                                            'name': 'binary_operation',
                                                                            'value': [
                                                                                {
                                                                                    'name': 'expression',
                                                                                    'value': [
                                                                                        GenericRepr("Token('NUMBER', '9')")
                                                                                    ]
                                                                                },
                                                                                GenericRepr("Token('DIVISION_SIGN', '/')"),
                                                                                {
                                                                                    'name': 'expression',
                                                                                    'value': [
                                                                                        GenericRepr("Token('NUMBER', '1')")
                                                                                    ]
                                                                                }
                                                                            ]
                                                                        }
                                                                    ]
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                GenericRepr("Token('MINUS_SIGN', '-')"),
                                {
                                    'name': 'expression',
                                    'value': [
                                        {
                                            'name': 'binary_operation',
                                            'value': [
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        {
                                                            'name': 'binary_operation',
                                                            'value': [
                                                                {
                                                                    'name': 'expression',
                                                                    'value': [
                                                                        GenericRepr("Token('NUMBER', '4')")
                                                                    ]
                                                                },
                                                                GenericRepr("Token('DIVISION_SIGN', '/')"),
                                                                {
                                                                    'name': 'expression',
                                                                    'value': [
                                                                        GenericRepr("Token('NUMBER', '5')")
                                                                    ]
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                },
                                                GenericRepr("Token('MULTIPLICATION_SIGN', '*')"),
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        GenericRepr("Token('OPEN_PAREN', '(')"),
                                                        {
                                                            'name': 'expression',
                                                            'value': [
                                                                {
                                                                    'name': 'binary_operation',
                                                                    'value': [
                                                                        {
                                                                            'name': 'expression',
                                                                            'value': [
                                                                                GenericRepr("Token('NUMBER', '1')")
                                                                            ]
                                                                        },
                                                                        GenericRepr("Token('PLUS_SIGN', '+')"),
                                                                        {
                                                                            'name': 'expression',
                                                                            'value': [
                                                                                GenericRepr("Token('NUMBER', '9')")
                                                                            ]
                                                                        }
                                                                    ]
                                                                }
                                                            ]
                                                        },
                                                        GenericRepr("Token('CLOSE_PAREN', ')')")
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

snapshots['test_ast_building Build AST for: constant'] = {
    'name': 'statement_list',
    'value': [
        {
            'name': 'statement',
            'value': [
                {
                    'name': 'expression',
                    'value': [
                        GenericRepr("Token('NUMBER', '2')")
                    ]
                }
            ]
        }
    ]
}

snapshots['test_ast_building Build AST for: divide constants'] = {
    'name': 'statement_list',
    'value': [
        {
            'name': 'statement',
            'value': [
                {
                    'name': 'expression',
                    'value': [
                        {
                            'name': 'binary_operation',
                            'value': [
                                {
                                    'name': 'expression',
                                    'value': [
                                        GenericRepr("Token('NUMBER', '4')")
                                    ]
                                },
                                GenericRepr("Token('DIVISION_SIGN', '/')"),
                                {
                                    'name': 'expression',
                                    'value': [
                                        GenericRepr("Token('NUMBER', '2')")
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

snapshots['test_ast_building Build AST for: if statement'] = {
    'name': 'statement_list',
    'value': [
        {
            'name': 'statement',
            'value': [
                {
                    'name': 'if_statement',
                    'value': [
                        GenericRepr("Token('OPEN_PAREN', '(')"),
                        GenericRepr("Token('IF', 'if')"),
                        {
                            'name': 'expression',
                            'value': [
                                GenericRepr("Token('OPEN_PAREN', '(')"),
                                {
                                    'name': 'expression',
                                    'value': [
                                        {
                                            'name': 'binary_operation',
                                            'value': [
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        GenericRepr("Token('NUMBER', '1')")
                                                    ]
                                                },
                                                GenericRepr("Token('LT', '<')"),
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        GenericRepr("Token('NUMBER', '3')")
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                GenericRepr("Token('CLOSE_PAREN', ')')")
                            ]
                        },
                        GenericRepr("Token('OPEN_CURLY_BRA', '{')"),
                        {
                            'name': 'statement_list',
                            'value': [
                                {
                                    'name': 'statement',
                                    'value': [
                                        {
                                            'name': 'define_var',
                                            'value': [
                                                GenericRepr("Token('DEF', 'def')"),
                                                GenericRepr("Token('VAR', 'a')"),
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        GenericRepr("Token('NUMBER', '1')")
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    'name': 'statement',
                                    'value': [
                                        {
                                            'name': 'expression',
                                            'value': [
                                                {
                                                    'name': 'binary_operation',
                                                    'value': [
                                                        {
                                                            'name': 'expression',
                                                            'value': [
                                                                GenericRepr("Token('VAR', 'a')")
                                                            ]
                                                        },
                                                        GenericRepr("Token('PLUS_SIGN', '+')"),
                                                        {
                                                            'name': 'expression',
                                                            'value': [
                                                                GenericRepr("Token('NUMBER', '4')")
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        GenericRepr("Token('CLOSE_CURLY_BRA', '}')"),
                        GenericRepr("Token('CLOSE_PAREN', ')')")
                    ]
                }
            ]
        }
    ]
}

snapshots['test_ast_building Build AST for: if/else statement'] = {
    'name': 'statement_list',
    'value': [
        {
            'name': 'statement',
            'value': [
                {
                    'name': 'if_statement',
                    'value': [
                        GenericRepr("Token('OPEN_PAREN', '(')"),
                        GenericRepr("Token('IF', 'if')"),
                        {
                            'name': 'expression',
                            'value': [
                                GenericRepr("Token('OPEN_PAREN', '(')"),
                                {
                                    'name': 'expression',
                                    'value': [
                                        {
                                            'name': 'binary_operation',
                                            'value': [
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        GenericRepr("Token('NUMBER', '1')")
                                                    ]
                                                },
                                                GenericRepr("Token('LT', '<')"),
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        GenericRepr("Token('NUMBER', '3')")
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                GenericRepr("Token('CLOSE_PAREN', ')')")
                            ]
                        },
                        GenericRepr("Token('OPEN_CURLY_BRA', '{')"),
                        {
                            'name': 'statement_list',
                            'value': [
                                {
                                    'name': 'statement',
                                    'value': [
                                        {
                                            'name': 'define_var',
                                            'value': [
                                                GenericRepr("Token('DEF', 'def')"),
                                                GenericRepr("Token('VAR', 'a')"),
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        GenericRepr("Token('NUMBER', '1')")
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    'name': 'statement',
                                    'value': [
                                        {
                                            'name': 'expression',
                                            'value': [
                                                {
                                                    'name': 'binary_operation',
                                                    'value': [
                                                        {
                                                            'name': 'expression',
                                                            'value': [
                                                                GenericRepr("Token('VAR', 'a')")
                                                            ]
                                                        },
                                                        GenericRepr("Token('PLUS_SIGN', '+')"),
                                                        {
                                                            'name': 'expression',
                                                            'value': [
                                                                GenericRepr("Token('NUMBER', '4')")
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        GenericRepr("Token('CLOSE_CURLY_BRA', '}')"),
                        GenericRepr("Token('OPEN_CURLY_BRA', '{')"),
                        {
                            'name': 'statement_list',
                            'value': [
                                {
                                    'name': 'statement',
                                    'value': [
                                        {
                                            'name': 'expression',
                                            'value': [
                                                {
                                                    'name': 'binary_operation',
                                                    'value': [
                                                        {
                                                            'name': 'expression',
                                                            'value': [
                                                                GenericRepr("Token('NUMBER', '5')")
                                                            ]
                                                        },
                                                        GenericRepr("Token('PLUS_SIGN', '+')"),
                                                        {
                                                            'name': 'expression',
                                                            'value': [
                                                                GenericRepr("Token('NUMBER', '3')")
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        GenericRepr("Token('CLOSE_CURLY_BRA', '}')"),
                        GenericRepr("Token('CLOSE_PAREN', ')')")
                    ]
                }
            ]
        }
    ]
}

snapshots['test_ast_building Build AST for: logical ops and arithmetic ops precedence'] = {
    'name': 'statement_list',
    'value': [
        {
            'name': 'statement',
            'value': [
                {
                    'name': 'expression',
                    'value': [
                        {
                            'name': 'binary_operation',
                            'value': [
                                {
                                    'name': 'expression',
                                    'value': [
                                        {
                                            'name': 'binary_operation',
                                            'value': [
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        {
                                                            'name': 'binary_operation',
                                                            'value': [
                                                                {
                                                                    'name': 'expression',
                                                                    'value': [
                                                                        GenericRepr("Token('NUMBER', '1')")
                                                                    ]
                                                                },
                                                                GenericRepr("Token('MULTIPLICATION_SIGN', '*')"),
                                                                {
                                                                    'name': 'expression',
                                                                    'value': [
                                                                        GenericRepr("Token('NUMBER', '3')")
                                                                    ]
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                },
                                                GenericRepr("Token('AND', 'and')"),
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        {
                                                            'name': 'binary_operation',
                                                            'value': [
                                                                {
                                                                    'name': 'expression',
                                                                    'value': [
                                                                        GenericRepr("Token('NUMBER', '1')")
                                                                    ]
                                                                },
                                                                GenericRepr("Token('PLUS_SIGN', '+')"),
                                                                {
                                                                    'name': 'expression',
                                                                    'value': [
                                                                        GenericRepr("Token('NUMBER', '5')")
                                                                    ]
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                GenericRepr("Token('OR', 'or')"),
                                {
                                    'name': 'expression',
                                    'value': [
                                        {
                                            'name': 'binary_operation',
                                            'value': [
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        GenericRepr("Token('NUMBER', '23')")
                                                    ]
                                                },
                                                GenericRepr("Token('AND', 'and')"),
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        GenericRepr("Token('OPEN_PAREN', '(')"),
                                                        {
                                                            'name': 'expression',
                                                            'value': [
                                                                {
                                                                    'name': 'binary_operation',
                                                                    'value': [
                                                                        {
                                                                            'name': 'expression',
                                                                            'value': [
                                                                                GenericRepr("Token('NUMBER', '1')")
                                                                            ]
                                                                        },
                                                                        GenericRepr("Token('OR', 'or')"),
                                                                        {
                                                                            'name': 'expression',
                                                                            'value': [
                                                                                GenericRepr("Token('NUMBER', '3')")
                                                                            ]
                                                                        }
                                                                    ]
                                                                }
                                                            ]
                                                        },
                                                        GenericRepr("Token('CLOSE_PAREN', ')')")
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

snapshots['test_ast_building Build AST for: logical ops precedence'] = {
    'name': 'statement_list',
    'value': [
        {
            'name': 'statement',
            'value': [
                {
                    'name': 'expression',
                    'value': [
                        {
                            'name': 'binary_operation',
                            'value': [
                                {
                                    'name': 'expression',
                                    'value': [
                                        {
                                            'name': 'binary_operation',
                                            'value': [
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        {
                                                            'name': 'binary_operation',
                                                            'value': [
                                                                {
                                                                    'name': 'expression',
                                                                    'value': [
                                                                        GenericRepr("Token('NUMBER', '1')")
                                                                    ]
                                                                },
                                                                GenericRepr("Token('AND', 'and')"),
                                                                {
                                                                    'name': 'expression',
                                                                    'value': [
                                                                        GenericRepr("Token('NUMBER', '2')")
                                                                    ]
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                },
                                                GenericRepr("Token('OR', 'or')"),
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        GenericRepr("Token('NUMBER', '3')")
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                GenericRepr("Token('OR', 'or')"),
                                {
                                    'name': 'expression',
                                    'value': [
                                        {
                                            'name': 'binary_operation',
                                            'value': [
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        {
                                                            'name': 'binary_operation',
                                                            'value': [
                                                                {
                                                                    'name': 'expression',
                                                                    'value': [
                                                                        {
                                                                            'name': 'binary_operation',
                                                                            'value': [
                                                                                {
                                                                                    'name': 'expression',
                                                                                    'value': [
                                                                                        GenericRepr("Token('NUMBER', '4')")
                                                                                    ]
                                                                                },
                                                                                GenericRepr("Token('AND', 'and')"),
                                                                                {
                                                                                    'name': 'expression',
                                                                                    'value': [
                                                                                        GenericRepr("Token('NUMBER', '5')")
                                                                                    ]
                                                                                }
                                                                            ]
                                                                        }
                                                                    ]
                                                                },
                                                                GenericRepr("Token('AND', 'and')"),
                                                                {
                                                                    'name': 'expression',
                                                                    'value': [
                                                                        GenericRepr("Token('NUMBER', '6')")
                                                                    ]
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                },
                                                GenericRepr("Token('AND', 'and')"),
                                                {
                                                    'name': 'expression',
                                                    'value': [
                                                        GenericRepr("Token('OPEN_PAREN', '(')"),
                                                        {
                                                            'name': 'expression',
                                                            'value': [
                                                                {
                                                                    'name': 'binary_operation',
                                                                    'value': [
                                                                        {
                                                                            'name': 'expression',
                                                                            'value': [
                                                                                GenericRepr("Token('NUMBER', '1')")
                                                                            ]
                                                                        },
                                                                        GenericRepr("Token('OR', 'or')"),
                                                                        {
                                                                            'name': 'expression',
                                                                            'value': [
                                                                                GenericRepr("Token('NUMBER', '2')")
                                                                            ]
                                                                        }
                                                                    ]
                                                                }
                                                            ]
                                                        },
                                                        GenericRepr("Token('CLOSE_PAREN', ')')")
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

snapshots['test_ast_building Build AST for: multiply constants'] = {
    'name': 'statement_list',
    'value': [
        {
            'name': 'statement',
            'value': [
                {
                    'name': 'expression',
                    'value': [
                        {
                            'name': 'binary_operation',
                            'value': [
                                {
                                    'name': 'expression',
                                    'value': [
                                        GenericRepr("Token('NUMBER', '2')")
                                    ]
                                },
                                GenericRepr("Token('MULTIPLICATION_SIGN', '*')"),
                                {
                                    'name': 'expression',
                                    'value': [
                                        GenericRepr("Token('NUMBER', '1')")
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

snapshots['test_ast_building Build AST for: substract contsants'] = {
    'name': 'statement_list',
    'value': [
        {
            'name': 'statement',
            'value': [
                {
                    'name': 'expression',
                    'value': [
                        {
                            'name': 'binary_operation',
                            'value': [
                                {
                                    'name': 'expression',
                                    'value': [
                                        GenericRepr("Token('NUMBER', '21')")
                                    ]
                                },
                                GenericRepr("Token('MINUS_SIGN', '-')"),
                                {
                                    'name': 'expression',
                                    'value': [
                                        GenericRepr("Token('NUMBER', '123')")
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

snapshots['test_ast_building Build AST for: variable definition'] = {
    'name': 'statement_list',
    'value': [
        {
            'name': 'statement',
            'value': [
                {
                    'name': 'define_var',
                    'value': [
                        GenericRepr("Token('DEF', 'def')"),
                        GenericRepr("Token('VAR', 'a')"),
                        {
                            'name': 'expression',
                            'value': [
                                GenericRepr("Token('NUMBER', '1')")
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

snapshots['test_ast_building Build AST for: variable definition and usage'] = {
    'name': 'statement_list',
    'value': [
        {
            'name': 'statement',
            'value': [
                {
                    'name': 'define_var',
                    'value': [
                        GenericRepr("Token('DEF', 'def')"),
                        GenericRepr("Token('VAR', 'a')"),
                        {
                            'name': 'expression',
                            'value': [
                                GenericRepr("Token('NUMBER', '1')")
                            ]
                        }
                    ]
                }
            ]
        },
        {
            'name': 'statement',
            'value': [
                {
                    'name': 'expression',
                    'value': [
                        {
                            'name': 'binary_operation',
                            'value': [
                                {
                                    'name': 'expression',
                                    'value': [
                                        GenericRepr("Token('VAR', 'a')")
                                    ]
                                },
                                GenericRepr("Token('PLUS_SIGN', '+')"),
                                {
                                    'name': 'expression',
                                    'value': [
                                        GenericRepr("Token('NUMBER', '3')")
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}
