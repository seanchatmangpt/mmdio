import subprocess
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop

ANTLR_VERSION = "4.13.1"


def generate_grammar():
    lang_dir = Path(__file__).resolve().parent / "opql" / "lang"
    grammar_dir = lang_dir / "grammar"
    grammar_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "antlr4",
            "-v", ANTLR_VERSION,
            "-visitor",
            "-no-listener",
            "-Dlanguage=Python3",
            "OPQL.g4",
            "-o",
            "grammar",
        ],
        cwd=lang_dir,
        check=True,
    )


class BuildWithGrammar(build_py):
    def run(self):
        generate_grammar()
        super().run()


class DevelopWithGrammar(develop):
    def run(self):
        generate_grammar()
        super().run()


setup(
    cmdclass={
        "build_py": BuildWithGrammar,
        "develop": DevelopWithGrammar,
    }
)
