import time
from collections import defaultdict
from typing import List, Union

from metalift.frontend.triton import Driver, InvGrammar
from metalift.ir import Bool, FnDecl, FnDeclRecursive, Int, Axiom, implies
from metalift.ir import List as mlList
from metalift.ir import Object, choose
from metalift.vc_util import and_objects
from tenspiler.codegen.utils import DataType
from tenspiler.tenspiler_common import call_vec_elemwise_add, vec_elemwise_add
from tenspiler.utils.synthesis_utils import run_synthesis_algorithm
from tenspiler.axioms_tenspiler import vec_elemwise_add_axiom


def target_lang() -> List[Union[FnDecl, FnDeclRecursive]]:
    return [vec_elemwise_add, vec_elemwise_add_axiom]


def ps_grammar(
    writes: List[Object], reads: List[Object], in_scope: List[Object], relaxed: bool
) -> Bool:
    x_ptr = reads[0]
    y_ptr = reads[1]
    output_ptr = reads[2]
    n_elements = reads[3]
    vec = choose(x_ptr[:n_elements], y_ptr[:n_elements])
    return output_ptr == call_vec_elemwise_add(vec, vec)


def inv_grammar(
    writes: List[Object], reads: List[Object], in_scope: List[Object], relaxed: bool
) -> Bool:
    # a, b, n = reads
    # out, i, _ = writes
    # vec = choose(a[:i], b[:i])
    print(writes)
    print(reads)
    exit(0)

    x_ptr = reads[0]
    y_ptr = reads[1]
    output_ptr = reads[2]
    n_elements = reads[3]
    vec = choose(x_ptr[:n_elements], y_ptr[:n_elements])
    i, _ = writes
    return and_objects(i >= 0, i <= n_elements, output_ptr == call_vec_elemwise_add(vec, vec))


if __name__ == "__main__":
    driver = Driver()
    vector_add = driver.analyze(
        filepath="tests/triton/vector_add.py", 
        fn_name="add_kernel", 
        target_lang_fn=target_lang,
        inv_grammar=defaultdict(lambda: InvGrammar(inv_grammar, [])),
        ps_grammar=ps_grammar,
    )

    x_ptr = mlList(Int, "x_ptr")
    y_ptr = mlList(Int, "y_ptr")
    output_ptr = mlList(Int, "output_ptr")
    n_elements = Int("n_elements")
    BLOCK_SIZE = Int("BLOCK_SIZE")

    driver.add_var_objects([x_ptr, y_ptr, output_ptr, n_elements, BLOCK_SIZE])
    driver.add_precondition(n_elements >= 1)
    driver.add_precondition(x_ptr.len() >= n_elements)
    driver.add_precondition(y_ptr.len() >= n_elements)

    start_time = time.time()
    vector_add(x_ptr, y_ptr, output_ptr, n_elements, BLOCK_SIZE)
    run_synthesis_algorithm(
        driver=driver,
        data_type=DataType.INT32,
        benchmark_name="vector_add",
        has_relaxed=False,
    )
    end_time = time.time()
    print(f"Synthesis took {end_time - start_time} seconds")

