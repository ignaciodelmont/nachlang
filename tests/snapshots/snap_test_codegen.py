# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_codegen LLVM IR for: add constants'] = '''define i32 @"main"() 
{
entry:
  %".2" = add i32 1, 1
}
'''

snapshots['test_codegen LLVM IR for: constant'] = '''define i32 @"main"() 
{
entry:
}
'''

snapshots['test_codegen LLVM IR for: divide constants'] = '''define i32 @"main"() 
{
entry:
  %".2" = add i32 1, 1
  %".3" = mul i32 2, 1
  %".4" = sdiv i32 4, 2
}
'''

snapshots['test_codegen LLVM IR for: multiply constants'] = '''define i32 @"main"() 
{
entry:
  %".2" = add i32 1, 1
  %".3" = mul i32 2, 1
}
'''

snapshots['test_codegen LLVM IR for: substract contsants'] = '''define i32 @"main"() 
{
entry:
  %".2" = add i32 1, 1
  %".3" = mul i32 2, 1
  %".4" = sdiv i32 4, 2
  %".5" = sub i32 21, 123
}
'''
