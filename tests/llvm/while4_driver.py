from typing import List

from metalift.frontend.llvm import Driver
from metalift.ir import (Add, And, Call, Choose, Eq, Expr, FnDeclRecursive, Ge,
                         Int, IntLit, Ite, Le, Sub, Var)
from tests.python.utils.utils import codegen


def target_lang() -> List[FnDeclRecursive]:
    x = Var("x", Int())
    sum_n = FnDeclRecursive(
        "sum_n",
        Int(),
        Ite(
            Ge(x, IntLit(1)),
            Add(x, Call("sum_n", Int(), Sub(x, IntLit(1)))),
            IntLit(0),
        ),
        x,
    )
    return [sum_n]


def ps_grammar(writes: List[Var], reads: List[Var]) -> Expr:
    return Eq(writes[0], Call("sum_n", Int(), Choose(IntLit(1), IntLit(2))))

def inv_grammar(writes: List[Var], reads: List[Var]) -> Expr:
    e = Choose(*writes)
    f = Choose(IntLit(1), IntLit(2), IntLit(3))
    c = Eq(e, Call("sum_n", Int(), Sub(e, f)))
    d = And(Ge(e, f), Le(e, f))
    b = And(c, d)
    return b

if __name__ == "__main__":
    driver = Driver()
    test = driver.analyze(
        llvm_filepath="tests/llvm/while4.ll",
        loops_filepath="tests/llvm/while4.loops",
        fn_name="test",
        target_lang_fn=target_lang,
        inv_grammar=inv_grammar,
        ps_grammar=ps_grammar
    )

    test()

    driver.synthesize()

    print("\n\ngenerated code:" + test.codegen(codegen))