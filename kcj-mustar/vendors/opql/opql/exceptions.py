class OPQLError(Exception):
    """Base class for all OPQL errors."""


class OPQLParseError(OPQLError):
    """Raised when a query string cannot be parsed into a valid AST."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        super().__init__(message)
        self.line = line
        self.column = column


class OPQLEvalError(OPQLError):
    """Raised when a syntactically valid query fails during evaluation."""


class OPQLTypeError(OPQLEvalError):
    """Raised when an expression operand or function argument has the wrong type."""


class OPQLDataError(OPQLError):
    """Raised when the OCEL log contains malformed or missing data."""
