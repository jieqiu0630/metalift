from typing import List

from metalift.frontend.llvm import Driver
from metalift.ir import (Call, Choose, Expr,
                         FnDeclRecursive, IntObject, Var)
from tests.python.utils.utils import codegen

def double(t):
    return IntObject(Call("double", IntObject, t))

def target_lang():
    x = IntObject("x")
    double = FnDeclRecursive(
        "double",
        IntObject,
        x + x,
        x
    )
    return [double]

def inv_grammar(v: Var, writes: List[Var], reads: List[Var]) -> Expr:
    raise Exception("no invariant")

def ps_grammar(ret_val: Var, writes: List[Var], reads: List[Var]) -> Expr:
    r = writes[0]
    (x, y) = reads
    summary = Choose(
        ret_val == double(x) + double(y),
        ret_val == double(x) - double(y)
    )
    return summary

if __name__ == "__main__":
    driver = Driver()
    test = driver.analyze(
        llvm_filepath="tests/llvm/tuples3.ll",
        loops_filepath="tests/llvm/tuples3.loops",
        fn_name="test",
        target_lang_fn=target_lang,
        inv_grammar=inv_grammar,
        ps_grammar=ps_grammar
    )

    x = IntObject("x")
    y = IntObject("y")
    driver.add_var_objects([x, y])

    test(x, y)

    driver.synthesize()

    print("\n\ngenerated code:" + test.codegen(codegen))