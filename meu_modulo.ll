; ModuleID = "meu_modulo.bc"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"

declare void @"escreva_inteiro"(i32 %".1")

declare void @"escreva_flutuante"(float %".1")

declare i32 @"leia_inteiro"()

declare float @"leia_flutuante"()

@"a" = external global i32
define i32 @"main"()
{
entry:
  %"ret" = alloca i32, align 4
  store i32 10, i32* @"a", align 4
  br label %"if"
exit:
  %".8" = load i32, i32* %"ret"
  ret i32 %".8"
if:
  %"var1_cmp" = load i32, i32* @"a", align 4
  %"a > 5" = icmp sgt i32 %"var1_cmp", 5
  br i1 %"a > 5", label %"if.if", label %"if.endif"
if.if:
  store i32 1, i32* %"ret", align 4
  br label %"if.endif"
if.endif:
  br label %"exit"
}
