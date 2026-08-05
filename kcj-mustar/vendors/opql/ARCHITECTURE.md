# ARCHITECTURE

## What is OPQL?

**Object-centric Process Query Language** — a DSL for querying [OCEL 2.0](https://ocel-standard.org/) event logs. Takes plain-text queries + OCEL files (SQLite or JSON) and returns pandas DataFrames or filtered OCEL databases.

- Author: Patric Mai
- License: AGPLv3
- Python >= 3.11
- Version: 0.1.1 (PyPI: `pip install opql`)

## Query Language Overview

```
PATTERN E(e:"Purchase")-[]-O(o:"Order")
FILTER e
KEEP e["amount"] AS amt ST amt > 100
WHEN hour(e["ocel_time"]) AS hr
RETURN amt AS amount, hr AS hour
```

**Clauses** (applied in order, each transforms the query context):
- `PATTERN` — graph pattern matching over events (`E`), objects (`O`), and relations (`-[]-`, `-[]->`, `<-[]-`)
- `FILTER` — remove matched entities from the OCEL log
- `KEEP` — project/reshape intermediate results (supports `DISTINCT`, `ORDERBY`, `LIMIT`, `BINNED`)
- `WHEN` — compute derived values from expressions
- `RETURN` — final output: either `OCEL` (filtered log) or tabular projection

**Expressions** support: arithmetic (`+`,`-`,`*`,`/`,`%`,`^`), comparison (`==`,`!=`,`<`,`>`,`<=`,`>=`), logic (`AND`,`OR`,`XOR`,`NOT`), property access (`e["prop"]`), timestamps (`T("...")`), durations (`D(d,h,m,s)`), and functions.

**Built-in functions**: `count`, `avg`, `median`, `sum`, `stddev`, `max`, `min`, `abs`, `isnone`, `olead`, `olag`, `year`, `month`, `day`, `hour`, `minute`, `second`, `dayOfWeek`.

## Project Structure

```
opql/
├── lang/                    # Parsing layer
│   ├── OPQL.g4              # ANTLR4 grammar (source of truth)
│   ├── grammar/             # Auto-generated lexer/parser/visitor (DO NOT EDIT)
│   ├── querysolver.py       # Entry point: string → FullQuery AST
│   ├── visitor.py           # ANTLR4 parse tree → AST conversion
│   └── query.py             # AST node classes (FullQuery, Graph, Filter, Keep, When, etc.)
│
├── eval/                    # Evaluation layer
│   ├── querycontext.py      # QueryContext tree — tracks matched entities during evaluation
│   ├── clause/
│   │   ├── pattern.py       # PATTERN clause: graph pattern matching
│   │   ├── filter.py        # FILTER clause: entity removal
│   │   ├── keep.py          # KEEP clause: projection/reshaping
│   │   └── when.py          # WHEN clause: derived value computation
│   └── expression/
│       ├── tree.py          # Expression tree evaluation (arithmetic, logic, comparison)
│       ├── value.py         # Value resolution (property lookups, symbolic names)
│       └── function.py      # Built-in function implementations
│
├── ocel/                    # Data access layer
│   ├── ocellog.py           # OCELLog, OCELEvent, OCELObject — wraps SQLite OCEL database
│   └── ocelimport.py        # Import from JSON/SQLite, create in-memory DBs, indexing
│
├── SQLITEResolver.py        # Orchestrator: runs clauses in sequence, produces final output
├── query_pattern.py         # Pattern matching engine (graph traversal)
├── util.py                  # RunningId counter
│
├── cli/
│   └── cli.py               # CLI entry point (opql-cli command)
│
test/
├── test_ops.py              # Expression/operation tests
├── test_p2p.py              # Integration tests on Procure-to-Pay log
├── test_p2p_special_behaviour.py
├── artifacts/               # Sample OCEL 2.0 files for testing
│   ├── ocel-p2p/
│   └── order-management/
└── cli/queries/             # Sample .opql query files

doc/
└── standard/                # Formal OPQL language specification (LaTeX)
    ├── main.tex             # Document root
    └── sections/            # 14 sections: lexical structure, data types, patterns,
                             #   expressions, clauses, functions, grammar reference, etc.
```

## Data Flow

```
                    ANTLR4
Query string ──────────────> Parse tree ──────> AST (FullQuery)
                  (lexer+parser)        (visitor.py)
                                                  │
                                                  ▼
OCEL SQLite ──> OCELLog ──> SQLITEResolver.resolve_query()
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
               PATTERN         FILTER/KEEP     WHEN
               (graph match)   (prune/project) (derive)
                    │              │              │
                    └──────────────┼──────────────┘
                                   ▼
                          RETURN clause
                           ├── OCEL → sqlite3.Connection
                           └── projection → pandas.DataFrame
```

## Key Types

| Class | Location | Purpose |
|-------|----------|---------|
| `FullQuery` | `lang/query.py` | Top-level AST: list of context rules + return rule |
| `Graph` | `lang/query.py` | PATTERN clause: graph pattern + optional ST filter |
| `GraphExpression` | `lang/query.py` | Expression tree (OR → XOR → AND → NOT → Comparison → AddSub → MulDiv → Power → Atomic) |
| `Projection` | `lang/query.py` | Column selection with DISTINCT, ORDERBY, LIMIT |
| `QueryContext` | `eval/querycontext.py` | Tree of matched entities; parent/children links track pattern matches |
| `OCELLog` | `ocel/ocellog.py` | Database wrapper: event/object/relation queries via SQL |
| `OCELEvent/Object` | `ocel/ocellog.py` | Entity wrappers with property/history access |

## Language Standard

The `doc/standard/` directory contains the authoritative formal specification for OPQL. It is a LaTeX document divided into 14 sections:

| Section | Topic |
|---------|-------|
| 01 | Introduction |
| 02 | Preliminaries (OCEL 2.0 background) |
| 03 | Lexical structure (tokens, whitespace, literals) |
| 04 | Data types |
| 05 | Records and tables |
| 06 | Pattern syntax (events, objects, relations) |
| 07 | Expression semantics |
| 08 | Binning |
| 09 | Query clauses (PATTERN, FILTER, KEEP, WHEN, SUBJECTTO) |
| 10 | RETURN statement |
| 11 | Query composition / subqueries |
| 12 | Built-in function reference |
| 13 | Grammar reference (BNF) |
| 14 | ORDER BY, LIMIT |

The Python implementation in `opql/` is intended to conform to this specification. The standard takes precedence when the implementation diverges.

## Build & Development

**Grammar changes** require regenerating the Python bindings:

```bash
# Install with grammar generation (runs ANTLR4 automatically)
pip install -e .

# Or manually (requires Java + antlr4-tools)
antlr4 -Dlanguage=Python3 -visitor -no-listener opql/lang/OPQL.g4 -o opql/lang/grammar
```

Generated files go to `opql/lang/grammar/` — these are gitignored and rebuilt on install.

**Running tests:**

```bash
pip install -e .
pytest
```

**Dependencies:**
- Runtime: `pandas`, `antlr4-python3-runtime==4.13.1`
- Build: `setuptools>=61`, `antlr4-tools` (needs Java)

**CI** (.gitlab-ci.yml): generate-bindings → test → auto-tag (semantic versioning from MR labels)

## Known Grammar Issues

No grammar issues are currently known. If the implementation behaves in a way that contradicts the language standard in `doc/standard/` or produces unexpected results, please report it in the project's issue tracker.

## OCEL 2.0 Data Model (for context)

The underlying SQLite database follows the OCEL 2.0 schema:
- `event` / `object` — entity tables with `ocel_id`, `ocel_type`
- `event_<type_map>` / `object_<type_map>` — per-type attribute tables
- `event_object` — event-to-object relations (`ocel_event_id`, `ocel_object_id`, `ocel_qualifier`)
- `object_object` — object-to-object relations (`ocel_source_id`, `ocel_target_id`, `ocel_qualifier`)
- `event_map_type` / `object_map_type` — type name → table name mapping
