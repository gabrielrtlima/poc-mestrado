import argparse
from .file_traverser import traverse_files
from .function_analyzer import analyze_functions
from .documentation_generator import generate_documentation


def main():
    parser = argparse.ArgumentParser(
        description="Documenta funções em um projeto Python."
    )
    parser.add_argument("project_path", help="Caminho para o projeto Python")
    parser.add_argument(
        "output_file", help="Arquivo de saída para a documentação (JSON)"
    )
    parser.add_argument(
        "--ignore", nargs="+", default=[], help="Pastas a serem ignoradas"
    )
    args = parser.parse_args()

    python_files = traverse_files(args.project_path, ignore_dirs=args.ignore)
    functions = analyze_functions(python_files)
    generate_documentation(functions, args.output_file)

    print(f"Documentação gerada em {args.output_file}")


if __name__ == "__main__":
    main()
