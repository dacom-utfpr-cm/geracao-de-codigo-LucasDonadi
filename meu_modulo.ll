; ModuleID = "meu_modulo.bc"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"

declare void @"escreva_inteiro"(i32 %".1")

declare void @"escreva_flutuante"(float %".1")

declare i32 @"leia_inteiro"()

declare float @"leia_flutuante"()

define i32 @"soma"(i32 %"x", i32 %"y")
{
entry:
  %".4" = add i32 %"x", %"y"
  br label %"exit"
exit:
  ret i32 %".4"
}

define i32 @"sub"(i32 %"z", i32 %"t")
{
entry:
  %".4" = sub i32 %"z", %"t"
  br label %"exit"
exit:
  ret i32 %".4"
}

define i32 @"main"()
{
entry:
  %"a" = alloca i32, align 4
  %"b" = alloca i32, align 4
  %"c" = alloca i32, align 4
  %"i" = alloca i32, align 4
  store i32 0, i32* %"i", align 4
  br label %"loop"
exit:
  %"ret_temp" = load i32, i32* %"retorno", align 4
  ret i32 %"ret_temp"
loop:
  %".4" = call i32 @"leia_inteiro"()
  store i32 %".4", i32* %"a", align 4
  %".6" = call i32 @"leia_inteiro"()
  store i32 %".6", i32* %"b", align 4
  %".8" = load i32, i32* %"a", align 4
  %".9" = load i32, i32* %"b", align 4
  %".10" = call i32 @"soma"(i32 %".8", i32 %".9")
  %".11" = load i32, i32* %"a", align 4
  %".12" = load i32, i32* %"b", align 4
  %".13" = call i32 @"sub"(i32 %".11", i32 %".12")
  %".14" = call i32 @"soma"(i32 %".10", i32 %".13")
  store i32 %".14", i32* %"c", align 4
  %".16" = load i32, i32* %"c"
  call void @"escreva_inteiro"(i32 %".16")
  %".18" = load i32, i32* %"i", align 4
  %"temp" = add i32 %".18", 1
  store i32 %"temp", i32* %"i", align 4
  %"var1_cmp" = load i32, i32* %"i", align 4
  br label %"loop_val"
loop_val:
  %"i == 5" = icmp eq i32 %"var1_cmp", 5
  br i1 %"i == 5", label %"loop", label %"loop_end"
loop_end:
  %"retorno" = alloca i32, align 4
  store i32 0, i32* %"retorno", align 4
  br label %"exit"
}
