from typing import List
from metalift.frontend.python import Driver

from metalift.ir import Call, Choose, Eq, Expr, FnDecl, NewObject, IntObject

from mypy.nodes import Statement

from tests.python.utils.utils import codegen


def target_lang() -> List[FnDecl]:
    x = IntObject("x")
    y = IntObject("y")
    z = IntObject("z")
    fma = FnDecl("fma", IntObject, x + y * z, x, y, z)
    return [fma]


# var := *reads | 0
# added := var + var
# var_or_fma := *reads | fma(added, added, added)
#
# return value := var_or_fma + var_or_fma
#
def ps_grammar(ret_val: NewObject, writes: List[NewObject], reads: List[NewObject], in_scope: List[NewObject]) -> Expr:
    var = Choose(*reads, IntObject(0))
    added = var + var
    var_or_fma = Choose(*reads, Call("fma", IntObject, added, added, added))

    return Eq(ret_val, var_or_fma + var_or_fma)

def inv_grammar(v: NewObject, writes: List[NewObject], reads: List[NewObject], in_scope: List[NewObject]) -> Expr:
    raise Exception("no loop in the source")


if __name__ == "__main__":
    filename = "tests/python/fma1.py"

    driver = Driver()
    test = driver.analyze(filename, "test", target_lang, inv_grammar, ps_grammar)

    base = IntObject("base")
    arg1 = IntObject("arg1")
    base2 = IntObject("base2")
    arg2 = IntObject("arg2")
    driver.add_var_objects([base, arg1, base2, arg2])

    test(base, arg1, base2, arg2)

    driver.synthesize()

    print("\n\ngenerated code:" + test.codegen(codegen))
