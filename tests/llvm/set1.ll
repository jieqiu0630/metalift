; ModuleID = 'set1.ll'
source_filename = "set1.c"
target datalayout = "e-m:o-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-apple-macosx12.0.0"

%struct.set = type {}

; Function Attrs: noinline nounwind optnone ssp uwtable
define %struct.set* @test(%struct.set* %s, i32 %add, i32 %value) #0 {
entry:
  %s.addr = alloca %struct.set*, align 8
  %add.addr = alloca i32, align 4
  %value.addr = alloca i32, align 4
  store %struct.set* %s, %struct.set** %s.addr, align 8
  store i32 %add, i32* %add.addr, align 4
  store i32 %value, i32* %value.addr, align 4
  %i = load i32, i32* %add.addr, align 4
  %cmp = icmp eq i32 %i, 1
  br i1 %cmp, label %bb, label %bb6

if.then:                                          ; preds = %bb
  %i1 = load %struct.set*, %struct.set** %s.addr, align 8
  %i2 = load i32, i32* %value.addr, align 4
  %call = call %struct.set* @set_add(%struct.set* %i1, i32 %i2)
  store %struct.set* %call, %struct.set** %s.addr, align 8
  br label %if.end

if.else:                                          ; preds = %bb6
  %i3 = load %struct.set*, %struct.set** %s.addr, align 8
  %i4 = load i32, i32* %value.addr, align 4
  %call1 = call %struct.set* @set_remove(%struct.set* %i3, i32 %i4)
  store %struct.set* %call1, %struct.set** %s.addr, align 8
  br label %if.end

if.end:                                           ; preds = %if.else, %if.then
  %i5 = load %struct.set*, %struct.set** %s.addr, align 8
  ret %struct.set* %i5

bb:                                               ; preds = %entry
  br label %if.then

bb6:                                              ; preds = %entry
  br label %if.else
}

declare %struct.set* @set_add(%struct.set*, i32) #1

declare %struct.set* @set_remove(%struct.set*, i32) #1

attributes #0 = { noinline nounwind optnone ssp uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "frame-pointer"="all" "less-precise-fpmad"="false" "min-legal-vector-width"="0" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "frame-pointer"="all" "less-precise-fpmad"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }

!llvm.module.flags = !{!0, !1}
!llvm.ident = !{!2}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"PIC Level", i32 2}
!2 = !{!"Homebrew clang version 11.1.0"}
