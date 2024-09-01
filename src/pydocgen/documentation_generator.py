import json


def generate_documentation(functions, output_file):
    with open(output_file, "w") as file:
        json.dump(functions, file, indent=2)
