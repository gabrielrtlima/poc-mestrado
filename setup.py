from setuptools import setup, find_packages

setup(
    name="pydocgen",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "pydocgen=pydocgen.cli:main",
        ],
    },
    install_requires=[
        # Liste aqui as dependências do projeto
    ],
    author="Seu Nome",
    author_email="seu.email@example.com",
    description="Uma ferramenta CLI para documentar funções em projetos Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/pydocgen",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
