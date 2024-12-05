from pathlib import Path
from typing import Callable

from metalift.frontend.llvm import Driver, InvGrammar
from metalift.ir import FnDecl, FnDeclRecursive
from metalift.synthesis_common import SynthesisFailed, VerificationFailed
from tenspiler.codegen.numpy_codegen import numpy_codegen
from tenspiler.codegen.utils import DataType
from tenspiler.llm.parser import check_solution
from tenspiler.llm.scripts.models import LLMModel
from tenspiler.llm.scripts.prompts import get_inv_prompt, get_ps_prompt
from tenspiler.llm.scripts.utils import TEMPLATE_ERR, is_single_loop, verify_benchmark

tpcc_benchmarks = {
    "normal_blend_f",
    "normal_blend_8",
    "dissolve_blend_8",
    "darken_blend_8",
    "multiply_blend_8",
    "linear_burn_8",
    "color_burn_8",
    "lighten_blend_8",
    "screen_blend_8",
    "linear_dodge_8",
    "color_dodge_8",
    "overlay_blend_8",
    "mag_array",
    "matrix_add_matrix",
    "mse_array",
    "mult_add_into_cpu",
    "ol_l2_cpu1",
    "ol_l2_cpu2",
    "scale_array",
    "scale_matrix",
    "sum_array",
    "translate_array",
    "fir_small",
    "lmsfir1",
    "lmsfir2",
}


def run_synthesis_with_bound(
    *,
    driver: Driver,
    data_type: DataType,
    benchmark_name: str,
    list_bound: int,
    max_rounds: int,
    has_relaxed: bool,
    no_verify: bool,
):
    try:
        print(f"Trying strict grammar with list bound {list_bound}...")
        # First use strict grammar
        basename = f"{benchmark_name}_strict_listbound{list_bound}_rounds{max_rounds}"
        driver.synthesize(
            filename=basename,
            list_bound=list_bound,
            relaxed_grammar=False,
            rounds_to_guess=max_rounds,
            no_verify=no_verify,
        )
    except SynthesisFailed as e:
        print(f"Strict grammar with list bound {list_bound} failed")
        if not has_relaxed:
            print("No relaxed grammar specified")
            raise e

        # Use relaxed grammar
        print("Trying relaxed grammar...")
        basename = f"{benchmark_name}_relaxed_listbound{list_bound}_rounds{max_rounds}"
        driver.synthesize(
            filename=basename,
            list_bound=list_bound,
            relaxed_grammar=True,
            rounds_to_guess=max_rounds,
        )

    ps_fn_decl = driver.get_actual_ps_fn_decl()

    curr_file_path = Path(__file__).resolve()
    tenspiler_dir = curr_file_path.parent.parent
    generated_code_dir = tenspiler_dir / "codegen" / "generated_code" / benchmark_name
    generated_code_dir.mkdir(parents=True, exist_ok=True)

    # Write numpy code
    np_code = numpy_codegen(ps_fn_decl, driver.synthesized_fns, data_type)
    with open(generated_code_dir / f"{benchmark_name}_numpy.py", "w") as f:
        f.write(np_code)

    # # Write tensorflow code
    # tf_code = tensorflow_codegen(ps_fn_decl, driver.synthesized_fns, data_type)
    # with open(generated_code_dir / f"{benchmark_name}_tensorflow.py", "w") as f:
    #     f.write(tf_code)

    # # Write pytorch code
    # pt_code = pytorch_codegen(ps_fn_decl, driver.synthesized_fns, data_type)
    # with open(generated_code_dir / f"{benchmark_name}_pytorch.py", "w") as f:
    #     f.write(pt_code)

    # if benchmark_name in tpcc_benchmarks:
    #     gaudi_base_dir = generated_code_dir / "gaudi"
    #     gaudi_base_dir.mkdir(parents=True, exist_ok=True)
    #     gaudi_hpp_glue_code, gaudi_cpp_glue_code, gaudi_kernel_code = gaudi_codegen(
    #         ps_fn_decl, driver.synthesized_fns, data_type
    #     )

    #     with open(gaudi_base_dir / f"{benchmark_name}_gaudi.hpp", "w") as f:
    #         f.write(gaudi_hpp_glue_code)
    #     with open(gaudi_base_dir / f"{benchmark_name}_gaudi.cpp", "w") as f:
    #         f.write(gaudi_cpp_glue_code)
    #     with open(gaudi_base_dir / f"{benchmark_name}_gaudi.c", "w") as f:
    #         f.write(gaudi_kernel_code)


def run_synthesis_algorithm(
    *,
    driver: Driver,
    data_type: DataType,
    benchmark_name: str,
    max_rounds: int = 10,
    has_relaxed: bool = False,
    list_bound_start: int = 2,
    no_verify: bool = True,
):
    print(f"Starting synthesis at list bound {list_bound_start}")
    list_bound_start = int(list_bound_start)
    list_bound = list_bound_start
    while True:
        try:
            run_synthesis_with_bound(
                driver=driver,
                data_type=data_type,
                benchmark_name=benchmark_name,
                list_bound=list_bound,
                max_rounds=max_rounds,
                has_relaxed=has_relaxed,
                no_verify=no_verify,
            )
            return
        except VerificationFailed:
            list_bound += 1
        except Exception as e:
            raise e


def run_llm_synthesis_algorithm(
    *,
    driver: Driver,
    source_file: str,
    env_file_path: str,
    suite_name: str,
    benchmark_name: str,
    llm_model: LLMModel,
    max_num_ps_sols: int = 10,
    max_num_inv_sols: int = 10,
) -> None:
    """
    The flow of the function is as follows:
    1. Start with asking the model to rewrite the function.
    2. Check if solution passes the parser. If it does, proceed. Otherwise, give parser feedback and ask the model to fix the function. Repeat this step for `max_parser_tries` times.
    4. Return the solution. Otherwise, return None.

    we return a list with maximum length of `max_num_tries` and each element containing the following information:
    - solutions: A list of solutions that we tried to pass to parser. Each solution is in the form of (solution, feedback, time_taken) tuple.
    """
    # First we need to get DSL and source code
    dsl_code = "\n\n".join(fn.to_python() for fn in driver.target_lang_fns)
    source_code = Path(source_file).read_text()

    # First we need to generate prompts
    ps_prompt = get_ps_prompt(dsl_code=dsl_code, source_code=source_code)

    # Get result from LLM
    ps_sols: list[str] = []
    found_sol = False
    for ps_sol_index in range(max_num_ps_sols):
        # First we get a new solution. If there are previous incorrect solutions, we show them to the model.
        print(f"===== Starting iteration {ps_sol_index} =====")
        inv_template_message = {"role": "user", "content": ps_prompt}

        if len(ps_sols) > 0:
            messages_for_new_sol = [
                inv_template_message,
                {"role": "assistant", "content": "\n".join(ps_sols)},
                {"role": "user", "content": TEMPLATE_ERR},
            ]
        else:
            messages_for_new_sol = [inv_template_message]
        # ps_sol = get_solution_from_llm(llm_model, messages_for_new_sol, env_file_path)
        ps_sol = """
        def linear_dodge_8(base: List[List[int]], active: List[List[int]]) -> List[List[int]]:
            return matrix_elemwise_add(base, active)
        """
        print("Generated new PS solution", ps_sol)
        ps_sols.append(ps_sol)

        # Check if the solution passes the parser. If it does, we can continue to the next step. Otherwise, we would like to generate another PS.
        try:
            _, ps_fn_decls, ps_inv_calls = check_solution(
                solution=ps_sol,
                expected_num_funcs=1,
                dsl_code=dsl_code,
            )
            print("Passed the parser, continuing to invariant generation")
        except Exception as e:
            print("Failed to pass the parser", e)
            print("Skipping invariant generation")
            continue

        # Generate the invariant
        inv_prompt = get_inv_prompt(
            suite_name=suite_name, benchmark_name=benchmark_name, dsl_code=dsl_code
        )
        inv_sols: list[str] = []
        for inv_sol_index in range(max_num_inv_sols):
            print(f"----- Generating {inv_sol_index} invariant -----")
            inv_template_message = {"role": "user", "content": inv_prompt}

            if len(inv_sols) > 0:
                messages_for_new_sol = [
                    inv_template_message,
                    {"role": "assistant", "content": "\n".join(inv_sols)},
                    {"role": "user", "content": TEMPLATE_ERR},
                ]
            else:
                messages_for_new_sol = [inv_template_message]
            # inv_sol = get_solution_from_llm(llm_model, messages_for_new_sol, env_file_path)
            inv_sol = f"""
            def invariant1(row: int, base: List[List[int]], active: List[List[int]], out: List[List[int]]) -> bool:
                return row >= 0 and row <= len(base) and out == matrix_elemwise_add(base[:row], active[:row])

            def invariant2(row: int, col: int, base: List[List[int]], active: List[List[int]], row_vec: List[int], out: List[List[int]]) -> bool:
                return row >= 0 and row < len(base) and col >= 0 and col <= len(base[0]) and \
                    row_vec == vec_elemwise_add(base[row][:col], active[row][:col]) and \
                    out == matrix_elemwise_add(base[:row], active[:row])
            """
            print("Generated new INV solution", inv_sol)
            inv_sols.append(inv_sol)

            try:
                _, inv_fn_decls, inv_in_calls = check_solution(
                    solution=inv_sol,
                    expected_num_funcs=1 if is_single_loop(benchmark_name) else 2,
                    dsl_code=dsl_code,
                )
                print("Passed the parser, continuing to verification")
            except Exception as e:
                print("Failed to pass the parser", e)
                continue

            # Verify the solution
            verified = verify_benchmark(
                driver=driver,
                benchmark_name=benchmark_name,
                synthesized_fn_decls=[*ps_fn_decls, *inv_fn_decls],
                in_calls=[*ps_inv_calls, *inv_in_calls],
            )
            if verified:
                print("Solution verified")
                found_sol = True
                break

        # If we have a correct solution, we can break out of the loop.
        if found_sol:
            break

    if not found_sol:
        raise Exception("No correct solution found")

    print("Found PS solution")
    print(ps_sol)


def llm_analyze(
    driver: Driver,
    llvm_filepath: str,
    loops_filepath: str,
    fn_name: str,
    target_lang_fn: Callable[[], list[FnDeclRecursive | FnDecl]],
    inv_in_scope_vars: dict[str, list[str]] = {},
):
    return driver.analyze(
        llvm_filepath=llvm_filepath,
        loops_filepath=loops_filepath,
        fn_name=fn_name,
        target_lang_fn=target_lang_fn,
        ps_grammar=None,
        inv_grammars={
            inv_name: InvGrammar(None, in_scope_var_names=var_names)
            for inv_name, var_names in inv_in_scope_vars.items()
        },
    )
