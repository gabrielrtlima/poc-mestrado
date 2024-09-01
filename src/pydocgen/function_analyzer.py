import ast
import os
from .llm_integration import generate_function_info


def get_type_hint(annotation):
    if isinstance(annotation, ast.Name):
        return annotation.id
    elif isinstance(annotation, ast.Subscript):
        return f"{annotation.value.id}[{get_type_hint(annotation.slice)}]"
    elif isinstance(annotation, ast.Constant):
        return str(annotation.value)
    return None


def get_default_value(default):
    if isinstance(default, ast.Constant):
        return default.value
    elif isinstance(default, ast.List):
        return [get_default_value(elt) for elt in default.elts]
    elif isinstance(default, ast.Dict):
        return {
            get_default_value(key): get_default_value(value)
            for key, value in zip(default.keys, default.values)
        }
    elif isinstance(default, ast.Name):
        return default.id
    elif isinstance(default, ast.Call):
        return f"{default.func.id}()"
    return None


class FunctionCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.function_calls = {}

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name not in self.function_calls:
                self.function_calls[func_name] = 1
            else:
                self.function_calls[func_name] += 1
        self.generic_visit(node)


def analyze_functions(python_files):
    functions = {}
    all_function_calls = {}

    # Primeiro passo: coletar todas as definições de função
    for file_path in python_files:
        with open(file_path, "r") as file:
            content = file.read()
            tree = ast.parse(content)
            dir_path = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)

            if dir_path not in functions:
                functions[dir_path] = {}

            if file_name not in functions[dir_path]:
                functions[dir_path][file_name] = {"functions": {}}

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    params = {}
                    for i, arg in enumerate(node.args.args):
                        param_type = (
                            get_type_hint(arg.annotation) if arg.annotation else None
                        )
                        default_value = None
                        if i >= len(node.args.args) - len(node.args.defaults):
                            default_index = i - (
                                len(node.args.args) - len(node.args.defaults)
                            )
                            default_value = get_default_value(
                                node.args.defaults[default_index]
                            )

                        params[arg.arg] = {
                            "field": arg.arg,
                            "type": param_type,
                            "default": default_value,
                        }

                    return_type = get_type_hint(node.returns) if node.returns else None

                    end_lineno = max(
                        child.end_lineno
                        for child in ast.walk(node)
                        if hasattr(child, "end_lineno")
                    )
                    num_lines = end_lineno - node.lineno + 1

                    # Extrair o código da função
                    function_code = ast.get_source_segment(content, node)

                    # Gerar descrição e exemplo usando o LLM
                    description, example = generate_function_info(
                        function_code, func_name, params, return_type
                    )

                    functions[dir_path][file_name]["functions"][func_name] = {
                        "params": params,
                        "return_type": return_type,
                        "description": description,
                        "example": example,
                        "line_number": node.lineno,
                        "num_lines": num_lines,
                        "calls": 0,
                        "called_in": [],
                    }

    # Segundo passo: contar chamadas de função
    for file_path in python_files:
        with open(file_path, "r") as file:
            content = file.read()
            tree = ast.parse(content)
            visitor = FunctionCallVisitor()
            visitor.visit(tree)

            for func_name, count in visitor.function_calls.items():
                if func_name not in all_function_calls:
                    all_function_calls[func_name] = {"total_calls": 0, "called_in": []}
                all_function_calls[func_name]["total_calls"] += count
                all_function_calls[func_name]["called_in"].append(file_path)

    # Terceiro passo: atualizar as informações de chamada nas definições de função
    for dir_path in functions:
        for file_name in functions[dir_path]:
            for func_name in functions[dir_path][file_name]["functions"]:
                if func_name in all_function_calls:
                    functions[dir_path][file_name]["functions"][func_name]["calls"] = (
                        all_function_calls[func_name]["total_calls"]
                    )
                    functions[dir_path][file_name]["functions"][func_name][
                        "called_in"
                    ] = all_function_calls[func_name]["called_in"]

    return functions
