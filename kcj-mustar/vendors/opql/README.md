[![Pipeline](https://gitlab.com/p.mai/opql/badges/master/pipeline.svg)](https://gitlab.com/p.mai/opql/-/pipelines)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
<!-- [![PyPI version](https://badge.fury.io/py/OPQL.svg)](https://pypi.org/project/OPQL/) -->

# OPQL — Object-centric Process Query Language

A high-level query language designed to analyze [OCEL 2.0](https://ocel-standard.org/) event logs natively.

With the advent of the OCEL 2.0 standard, new tooling is required to incorporate the multi-dimensional features and new file formats introduced. OPQL provides a powerful, text-based way to query these logs across all dimensions, allowing for complex pattern matching, temporal analysis, and seamless integration into data transformation pipelines.

---

## Features

- **Pattern Matching** — Match complex event-object relationships using a concise syntax: `PATTERN E(e:"Type")-[]-O(o:"Type")`.
- **Query Composition** — Chain queries together using `KEEP` clauses (similar to CTEs) to build complex analytical pipelines.
- **Temporal Analysis** — Native support for time-based operations, including lead/lag operators (`olead`, `olag`) and duration arithmetic.
- **Aggregates** — Built-in support for standard aggregates (`count`, `avg`, `median`, `sum`, `stddev`, `max`, `min`) that can operate over subqueries.
- **OCEL-Native** — Operates directly on OCEL 2.0 structures, preserving the relationships between events and objects.
- **Flexible Output** — Export results as filtered OCEL (SQLite), or in tabular formats like CSV, Excel, and HTML via Pandas.

---

## Supported Formats

| Format | Read | Write | Notes |
|--------|------|-------|-------|
| OCEL 2.0 (SQLite) | ✓ | ✓ | Native storage and execution engine |
| OCEL 2.0 (JSON) | ✓ | — | Full import support into in-memory SQLite |
| CSV | — | ✓ | Tabular output for result sets |
| Excel (`.xlsx`) | — | ✓ | Tabular output for result sets |
| HTML | — | ✓ | Interactive tables for web visualization |
| Python Pickle | — | ✓ | Serialization of Pandas DataFrames |

---

## Prerequisites

| Requirement | Minimum version | Notes |
|-------------|----------------|-------|
| Python | 3.11 | Required for advanced typing features |
| Pandas | any recent | Used for result set handling and export |
| ANTLR4 Runtime | 4.13.1 | Required for query parsing |

---

## Installation

> **Note:** The PyPI package is currently out of date and is scheduled for an update soon.

For the latest version, it is recommended to install directly from the repository:

```sh
# Recommended: Install into a virtual environment
python -m venv .venv
source .venv/bin/activate
pip install git+https://gitlab.com/p.mai/opql.git
```

For development or building from source:

```sh
git clone https://gitlab.com/p.mai/opql.git
cd opql
pip install -e .
```

---

## Usage

### CLI Tool — `opql-cli`

OPQL comes with a standalone CLI tool for executing queries on OCEL files.

```
Usage: opql-cli <ocelfile.sqlite> <query.txt> [options]

Options:
  -tof, --tableoutformat arg  Output format: csv (default), xlsx, pickle, html
  -sep, --separator arg       Separator for CSV output (default: ,)
  -v, --verbose               Enable verbose logging
```

**Example:**

```sh
# Run a query and save result to CSV
opql-cli log.sqlite query.txt --tableoutformat csv
```

### Library API

You can also embed OPQL into your own Python applications.

```python
import opql.ocel.ocellog
import opql.lang.querysolver
import opql.SQLITEResolver
from opql.ocel.ocelimport import make_inmemory_db, loadSQLITE

# 1. Load your OCEL log
log_db = make_inmemory_db()
loadSQLITE("path/to/log.sqlite", log_db)
log = opql.ocel.ocellog.OCELLog(log_db)

# 2. Define and parse a query
query_string = """
PATTERN E(e:"Create Purchase Requisition")-[]-O(o:"purchase_requisition")
RETURN e["ocel_id"] AS event_id, o["ocel_id"] AS object_id
"""
query_struct = opql.lang.querysolver.scan_query(query_string)

# 3. Resolve and get a Pandas DataFrame
result = opql.SQLITEResolver.resolve_query(log, query_struct)
print(result.head())
```

---

## Architecture

The project is structured to separate language parsing from execution:

- **`opql/lang/`** — Lexical and grammatical definition using ANTLR4. Includes the `visitor` and `querysolver` for AST construction.
- **`opql/eval/`** — Logic for evaluating query clauses (`filter`, `pattern`, `subjectto`, etc.) and the expression tree.
- **`opql/ocel/`** — Infrastructure for importing and managing OCEL 2.0 logs in SQLite and JSON formats.
- **`opql/cli/`** — Command-line interface entry point.
- **`doc/standard/`** — Formal language specification (LaTeX).

---

## Language Standard

A formal specification of the OPQL language is maintained in [`doc/standard/`](doc/standard/). It covers:
- Lexical structure and data types.
- Pattern syntax and expression semantics.
- Query composition and clause definitions.
- Full grammar reference.

The implementation in `opql/` is designed to strictly conform to this specification.

---

## Contributing

Contributions are welcome via merge requests on [GitLab](https://gitlab.com/p.mai/opql).

**Please raise an issue first** to discuss any significant changes or new features before starting work. This helps ensure that your contribution aligns with the project's roadmap and architectural goals.

When contributing, please ensure that:
1. All changes are covered by tests in the `test/` directory.
2. The language standard is updated if new syntax or built-ins are added.
3. Code style follows the existing project conventions.

---

## License

This project is licensed under the **GNU Affero General Public License v3.0**. See [LICENSE](LICENSE) for the full text.

---

## References

- **OCEL 2.0 Standard** — [https://ocel-standard.org/](https://ocel-standard.org/)
- **OCPQ** — A GUI-based solution for OCEL 2.0: [https://github.com/aarkue/OCPQ](https://github.com/aarkue/OCPQ)
