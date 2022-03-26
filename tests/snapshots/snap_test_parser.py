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
