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

snapshots['test_codegen LLVM IR for: arithmetic precedence'] = '''define i32 @"main"() 
{
entry:
  %".2" = add i32 1, 1
  %".3" = mul i32 2, 1
  %".4" = sdiv i32 4, 2
  %".5" = sub i32 21, 123
  %".6" = sdiv i32 9, 1
  %".7" = mul i32 3, %".6"
  %".8" = add i32 1, %".7"
  %".9" = sdiv i32 4, 5
  %".10" = add i32 1, 9
  %".11" = mul i32 %".9", %".10"
  %".12" = sub i32 %".8", %".11"
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

snapshots['test_codegen LLVM IR for: if statement'] = '''define i32 @"main"() 
{
entry:
  %".2" = add i32 1, 1
  %".3" = mul i32 2, 1
  %".4" = sdiv i32 4, 2
  %".5" = sub i32 21, 123
  %".6" = sdiv i32 9, 1
  %".7" = mul i32 3, %".6"
  %".8" = add i32 1, %".7"
  %".9" = sdiv i32 4, 5
  %".10" = add i32 1, 9
  %".11" = mul i32 %".9", %".10"
  %".12" = sub i32 %".8", %".11"
  %".13" = and i32 1, 2
  %".14" = or i32 %".13", 3
  %".15" = and i32 4, 5
  %".16" = and i32 %".15", 6
  %".17" = or i32 1, 2
  %".18" = and i32 %".16", %".17"
  %".19" = or i32 %".14", %".18"
  %".20" = mul i32 1, 3
  %".21" = add i32 1, 5
  %".22" = and i32 %".20", %".21"
  %".23" = or i32 1, 3
  %".24" = and i32 23, %".23"
  %".25" = or i32 %".22", %".24"
  %".26" = alloca i32
  store i32 1, i32* %".26"
  %".28" = alloca i32
  store i32 1, i32* %".28"
  %".30" = load i32, i32* %".28"
  %".31" = add i32 %".30", 3
  %".32" = icmp slt i32 1, 3
  br i1 %".32", label %"entry.if", label %"entry.else"
entry.if:
  %".34" = alloca i32
  store i32 1, i32* %".34"
  %".36" = load i32, i32* %".34"
  %".37" = add i32 %".36", 4
  br label %"entry.endif"
entry.else:
  %".39" = add i32 5, 3
  br label %"entry.endif"
entry.endif:
  %".41" = icmp slt i32 1, 3
  br i1 %".41", label %"entry.endif.if", label %"entry.endif.else"
entry.endif.if:
  %".43" = alloca i32
  store i32 1, i32* %".43"
  %".45" = load i32, i32* %".43"
  %".46" = add i32 %".45", 4
  br label %"entry.endif.endif"
entry.endif.else:
  br label %"entry.endif.endif"
entry.endif.endif:
}
'''

snapshots['test_codegen LLVM IR for: if/else statement'] = '''define i32 @"main"() 
{
entry:
  %".2" = add i32 1, 1
  %".3" = mul i32 2, 1
  %".4" = sdiv i32 4, 2
  %".5" = sub i32 21, 123
  %".6" = sdiv i32 9, 1
  %".7" = mul i32 3, %".6"
  %".8" = add i32 1, %".7"
  %".9" = sdiv i32 4, 5
  %".10" = add i32 1, 9
  %".11" = mul i32 %".9", %".10"
  %".12" = sub i32 %".8", %".11"
  %".13" = and i32 1, 2
  %".14" = or i32 %".13", 3
  %".15" = and i32 4, 5
  %".16" = and i32 %".15", 6
  %".17" = or i32 1, 2
  %".18" = and i32 %".16", %".17"
  %".19" = or i32 %".14", %".18"
  %".20" = mul i32 1, 3
  %".21" = add i32 1, 5
  %".22" = and i32 %".20", %".21"
  %".23" = or i32 1, 3
  %".24" = and i32 23, %".23"
  %".25" = or i32 %".22", %".24"
  %".26" = alloca i32
  store i32 1, i32* %".26"
  %".28" = alloca i32
  store i32 1, i32* %".28"
  %".30" = load i32, i32* %".28"
  %".31" = add i32 %".30", 3
  %".32" = icmp slt i32 1, 3
  br i1 %".32", label %"entry.if", label %"entry.else"
entry.if:
  %".34" = alloca i32
  store i32 1, i32* %".34"
  %".36" = load i32, i32* %".34"
  %".37" = add i32 %".36", 4
  br label %"entry.endif"
entry.else:
  %".39" = add i32 5, 3
  br label %"entry.endif"
entry.endif:
}
'''

snapshots['test_codegen LLVM IR for: logical ops and arithmetic ops precedence'] = '''define i32 @"main"() 
{
entry:
  %".2" = add i32 1, 1
  %".3" = mul i32 2, 1
  %".4" = sdiv i32 4, 2
  %".5" = sub i32 21, 123
  %".6" = sdiv i32 9, 1
  %".7" = mul i32 3, %".6"
  %".8" = add i32 1, %".7"
  %".9" = sdiv i32 4, 5
  %".10" = add i32 1, 9
  %".11" = mul i32 %".9", %".10"
  %".12" = sub i32 %".8", %".11"
  %".13" = and i32 1, 2
  %".14" = or i32 %".13", 3
  %".15" = and i32 4, 5
  %".16" = and i32 %".15", 6
  %".17" = or i32 1, 2
  %".18" = and i32 %".16", %".17"
  %".19" = or i32 %".14", %".18"
  %".20" = mul i32 1, 3
  %".21" = add i32 1, 5
  %".22" = and i32 %".20", %".21"
  %".23" = or i32 1, 3
  %".24" = and i32 23, %".23"
  %".25" = or i32 %".22", %".24"
}
'''

snapshots['test_codegen LLVM IR for: logical ops precedence'] = '''define i32 @"main"() 
{
entry:
  %".2" = add i32 1, 1
  %".3" = mul i32 2, 1
  %".4" = sdiv i32 4, 2
  %".5" = sub i32 21, 123
  %".6" = sdiv i32 9, 1
  %".7" = mul i32 3, %".6"
  %".8" = add i32 1, %".7"
  %".9" = sdiv i32 4, 5
  %".10" = add i32 1, 9
  %".11" = mul i32 %".9", %".10"
  %".12" = sub i32 %".8", %".11"
  %".13" = and i32 1, 2
  %".14" = or i32 %".13", 3
  %".15" = and i32 4, 5
  %".16" = and i32 %".15", 6
  %".17" = or i32 1, 2
  %".18" = and i32 %".16", %".17"
  %".19" = or i32 %".14", %".18"
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

snapshots['test_codegen LLVM IR for: variable definition'] = '''define i32 @"main"() 
{
entry:
  %".2" = add i32 1, 1
  %".3" = mul i32 2, 1
  %".4" = sdiv i32 4, 2
  %".5" = sub i32 21, 123
  %".6" = sdiv i32 9, 1
  %".7" = mul i32 3, %".6"
  %".8" = add i32 1, %".7"
  %".9" = sdiv i32 4, 5
  %".10" = add i32 1, 9
  %".11" = mul i32 %".9", %".10"
  %".12" = sub i32 %".8", %".11"
  %".13" = and i32 1, 2
  %".14" = or i32 %".13", 3
  %".15" = and i32 4, 5
  %".16" = and i32 %".15", 6
  %".17" = or i32 1, 2
  %".18" = and i32 %".16", %".17"
  %".19" = or i32 %".14", %".18"
  %".20" = mul i32 1, 3
  %".21" = add i32 1, 5
  %".22" = and i32 %".20", %".21"
  %".23" = or i32 1, 3
  %".24" = and i32 23, %".23"
  %".25" = or i32 %".22", %".24"
  %".26" = alloca i32
  store i32 1, i32* %".26"
}
'''

snapshots['test_codegen LLVM IR for: variable definition and usage'] = '''define i32 @"main"() 
{
entry:
  %".2" = add i32 1, 1
  %".3" = mul i32 2, 1
  %".4" = sdiv i32 4, 2
  %".5" = sub i32 21, 123
  %".6" = sdiv i32 9, 1
  %".7" = mul i32 3, %".6"
  %".8" = add i32 1, %".7"
  %".9" = sdiv i32 4, 5
  %".10" = add i32 1, 9
  %".11" = mul i32 %".9", %".10"
  %".12" = sub i32 %".8", %".11"
  %".13" = and i32 1, 2
  %".14" = or i32 %".13", 3
  %".15" = and i32 4, 5
  %".16" = and i32 %".15", 6
  %".17" = or i32 1, 2
  %".18" = and i32 %".16", %".17"
  %".19" = or i32 %".14", %".18"
  %".20" = mul i32 1, 3
  %".21" = add i32 1, 5
  %".22" = and i32 %".20", %".21"
  %".23" = or i32 1, 3
  %".24" = and i32 23, %".23"
  %".25" = or i32 %".22", %".24"
  %".26" = alloca i32
  store i32 1, i32* %".26"
  %".28" = alloca i32
  store i32 1, i32* %".28"
  %".30" = load i32, i32* %".28"
  %".31" = add i32 %".30", 3
}
'''
