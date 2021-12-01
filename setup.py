from setuptools import setup

setup(
    name="nachlang",
    version="0.0.1",
    description="An llvm compiler for nachlang",
    author="Ignacio Delmont",
    author_email="ignaciodelmont@gmail.com",
    packages=["nachlang"],
    install_requires=["llvmlite", "rply", "graphviz"]
)