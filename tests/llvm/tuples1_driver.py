from typing import List

from metalift.frontend.llvm import Driver
from metalift.ir import (FnDeclRecursive, IntObject, TupleObject, NewObject, call, choose, make_tuple)
from tests.python.utils.utils import codegen


def tuple_mult(t):
    return call("tuple_mult", IntObject, t)

def target_lang():
    x = TupleObject("x", IntObject, IntObject)
    tuple_mult = FnDeclRecursive(
        "tuple_mult",
        IntObject,
        (x[0] * x[1]).src,
        x.src
    )
    return [tuple_mult]

def inv_grammar(v: NewObject, writes: List[NewObject], reads: List[NewObject]) -> NewObject:
    raise Exception("no inNewObjectiant")

def ps_grammar(ret_val: NewObject, writes: List[NewObject], reads: List[NewObject]) -> NewObject:
    x_tuple = make_tuple(x, x)
    y_tuple = make_tuple(y, y)
    summary = choose(
        ret_val == tuple_mult(x_tuple) + tuple_mult(y_tuple),
        ret_val == tuple_mult(x_tuple) - tuple_mult(y_tuple)
    )
    return summary

if __name__ == "__main__":
    driver = Driver()
    test = driver.analyze(
        llvm_filepath="tests/llvm/tuples1.ll",
        loops_filepath="tests/llvm/tuples1.loops",
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