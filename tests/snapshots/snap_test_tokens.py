# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_tokens Test all tokens'] = [
    {
        'name': 'IF',
        'value': 'if'
    },
    {
        'name': 'LOOP',
        'value': 'loop'
    },
    {
        'name': 'RETURN',
        'value': 'return'
    },
    {
        'name': 'TRUE',
        'value': 'true'
    },
    {
        'name': 'False',
        'value': 'false'
    },
    {
        'name': 'OPEN_PAREN',
        'value': '('
    },
    {
        'name': 'CLOSE_PAREN',
        'value': ')'
    },
    {
        'name': 'OPEN_CURLY_BRA',
        'value': '{'
    },
    {
        'name': 'CLOSE_CURLY_BRA',
        'value': '}'
    },
    {
        'name': 'LTE',
        'value': '<='
    },
    {
        'name': 'GTE',
        'value': '>='
    },
    {
        'name': 'LT',
        'value': '<'
    },
    {
        'name': 'GT',
        'value': '>'
    },
    {
        'name': 'ASSIGN',
        'value': '='
    },
    {
        'name': 'STRING_TYPE',
        'value': 'string'
    },
    {
        'name': 'NUMBER_TYPE',
        'value': 'number'
    },
    {
        'name': 'SUM',
        'value': '+'
    },
    {
        'name': 'SUB',
        'value': '-'
    },
    {
        'name': 'DIV',
        'value': '/'
    },
    {
        'name': 'MUL',
        'value': '*'
    },
    {
        'name': 'NUMBER',
        'value': '123'
    },
    {
        'name': 'STRING',
        'value': '"hello from nachlang"'
    },
    {
        'name': 'NUMBER',
        'value': '4'
    },
    {
        'name': 'SUM',
        'value': '+'
    },
    {
        'name': 'DEF',
        'value': 'def'
    }
]
