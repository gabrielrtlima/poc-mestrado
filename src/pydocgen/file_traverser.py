import os

DEFAULT_IGNORE = [
    "venv",
    "env",
    ".venv",
    ".env",
    "__pycache__",
    ".git",
    "build",
    "dist",
]


def traverse_files(project_path: str = "test", ignore_dirs=None) -> list[str]:
    if ignore_dirs is None:
        ignore_dirs = []

    ignore_dirs = set(DEFAULT_IGNORE + ignore_dirs)

    python_files = []
    for root, dirs, files in os.walk(project_path):
        # Remove as pastas ignoradas da lista de diretórios
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files
