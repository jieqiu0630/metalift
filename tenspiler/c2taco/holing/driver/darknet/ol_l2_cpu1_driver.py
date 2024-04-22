import time
from collections import defaultdict
from typing import List, Union

from metalift.frontend.llvm import Driver, InvGrammar
from metalift.ir import Bool, FnDecl, FnDeclRecursive, Int
from metalift.ir import List as mlList
from metalift.ir import Object, choose
from metalift.vc_util import and_objects
from tenspiler.tenspiler_common import (
    call_vec_elemwise_mul,
    call_vec_elemwise_sub,
    vec_elemwise_add,
    vec_elemwise_mul,
    vec_elemwise_sub,
)


def target_lang() -> List[Union[FnDecl, FnDeclRecursive]]:
    return [vec_elemwise_add, vec_elemwise_sub, vec_elemwise_mul]


def ps_grammar(
    writes: List[Object], reads: List[Object], in_scope: List[Object], relaxed: bool
) -> Bool:
    n, pred, truth = reads
    error = writes[0]
    vec = choose(truth[:n], pred[:n])
    vec = choose(vec, call_vec_elemwise_sub(vec, vec))
    return error == call_vec_elemwise_mul(vec, vec)


def inv_grammar(
    writes: List[Object], reads: List[Object], in_scope: List[Object], relaxed: bool
) -> Bool:
    n, pred, truth = reads
    error, _, i, _ = writes
    vec = choose(truth[:i], pred[:i])
    vec = choose(vec, call_vec_elemwise_sub(vec, vec))
    return and_objects(i >= 0, i <= n, error == call_vec_elemwise_mul(vec, vec))


if __name__ == "__main__":
    driver = Driver()
    ol_l2_cpu1 = driver.analyze(
        "tenspiler/c2taco/cpp/for_synthesis/darknet/ol_l2_cpu1.ll",
        "tenspiler/c2taco/cpp/for_synthesis/darknet/ol_l2_cpu1.loops",
        "ol_l2_cpu1",
        target_lang,
        defaultdict(lambda: InvGrammar(inv_grammar, [])),
        ps_grammar,
    )

    n = Int("n")
    pred = mlList(Int, "pred")
    truth = mlList(Int, "truth")

    driver.add_var_objects([n, pred, truth])
    driver.add_precondition(n >= 1)
    driver.add_precondition(pred.len() >= n)
    driver.add_precondition(truth.len() >= n)

    ol_l2_cpu1(n, pred, truth)

    start_time = time.time()
    driver.synthesize(filename="ol_l2_cpu1", no_verify=True)
    end_time = time.time()
    print(f"Synthesis took {end_time - start_time} seconds")
