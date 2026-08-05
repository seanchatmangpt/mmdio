# CLAUDE.md — Agent context for OPQL

## What this repository is

This repository contains two things:

1. **A query language implementation** — `opql/` is a Python package implementing OPQL (Object-centric Process Query Language), a DSL for querying [OCEL 2.0](https://ocel-standard.org/) event logs. It uses ANTLR4 for parsing and operates on SQLite/JSON OCEL files.

2. **A formal language standard** — `doc/standard/` is a LaTeX document that authoritatively defines the OPQL language: its syntax, semantics, data types, clauses, expressions, and built-in functions. The implementation is meant to conform to this spec. The standard takes precedence when the two diverge.

## Key facts

- Language: Python 3.11+
- License: AGPLv3
- Grammar: ANTLR4 (`opql/lang/OPQL.g4`); generated bindings go to `opql/lang/grammar/` (gitignored, rebuilt on `pip install -e .`)
- Tests: `pytest` (integration tests use OCEL sample logs in `test/artifacts/`)
- CI: GitLab (`.gitlab-ci.yml`): generate-bindings → test → auto-tag

## Where things live

| Concern | Location |
|---------|----------|
| Language standard (authoritative) | `doc/standard/` (LaTeX, 14 sections) |
| Grammar (source of truth for parser) | `opql/lang/OPQL.g4` |
| AST node classes | `opql/lang/query.py` |
| Parse tree → AST | `opql/lang/visitor.py` |
| Clause evaluation | `opql/eval/clause/` |
| Expression evaluation | `opql/eval/expression/` |
| OCEL data access | `opql/ocel/` |
| Query orchestration | `opql/SQLITEResolver.py` |
| Pattern matching engine | `opql/query_pattern.py` |
| CLI entry point | `opql/cli/cli.py` |

## When editing the grammar

1. Edit `opql/lang/OPQL.g4`
2. Run `pip install -e .` (triggers ANTLR4 regeneration) or manually:
   ```
   antlr4 -Dlanguage=Python3 -visitor -no-listener opql/lang/OPQL.g4 -o opql/lang/grammar
   ```

## When editing the standard

The spec is in `doc/standard/sections/`. Each `.tex` file covers one topic (numbered 01–14). Changes to the spec may require corresponding changes in the implementation and vice versa.
