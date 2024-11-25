import ast

from tenspiler.llm.scripts.run_with_parser_and_fuzzer_feedback import LLMModel, get_solution_from_llm

def parse_file(file_path: str) -> dict[str, list[str]]:
    """
    Parses a Python file to extract function dependencies.
    Returns a dictionary mapping function names to the list of functions they depend on.
    """
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())

    function_dependencies = {}
    function_code = {}

    class DependencyVisitor(ast.NodeVisitor):
        def __init__(self):
            self.current_function = None

        def visit_FunctionDef(self, node):
            self.current_function = node.name
            function_dependencies[self.current_function] = set()
            function_code[self.current_function] = ast.unparse(node)
            self.generic_visit(node)
            self.current_function = None

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and self.current_function:
                function_dependencies[self.current_function].add(node.func.id)
            self.generic_visit(node)

    visitor = DependencyVisitor()
    visitor.visit(tree)
    return function_dependencies, function_code

def extract_code_blocks(
    func_name: str,
    dependencies: dict[str, str],
    function_code: dict[str, str]
) -> str:
    """
    Extracts code blocks for a given function and its dependencies.
    """
    code_block = function_code[func_name]
    for dependency in dependencies[func_name]:
        if dependency in function_code and func_name != dependency:
            code_block += f"\n\n{function_code[dependency]}"
    return code_block

if __name__ == "__main__":
    input_file = "tenspiler/llm/anon_python_dsl.py"  # Replace with your input file

    # Parse the file to get function dependencies
    dependencies, function_code = parse_file(input_file)

    for i in range(1, 36):
        code_block = extract_code_blocks(f"test{i}", dependencies, function_code)
        print(f"Code block for test{i}:\n{code_block}\n")
        print("-" * 80)
        prompt = f"""
Given the following Python code, add a docstring to the function `test{i}` that describes its behavior as well as all its arguments and return value. You do not need to document other functions, as they are provided as dependencies to `test{i}`.

In addition, generate five test cases for `test{i}`. Return the test inputs as a list of dictionaries, where each item in the list is a dictionary with the input names as keys and the input values as values. Enclose the returned test inputs with a json code block. Explain why your test inputs are comprehensive.

Here is the code block for `test{i}`:
```python
{code_block}
```
"""
        messages = [{"role": "user", "content": prompt}]
        solution = get_solution_from_llm(
            llm_model=LLMModel.GPT,
            messages=messages,
        )
        print("Solution:")
        print(solution)
        print("=" * 80)
