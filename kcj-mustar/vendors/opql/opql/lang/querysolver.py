import logging

import antlr4
import antlr4.error.ErrorListener

import opql.lang.grammar.OPQLLexer
import opql.lang.grammar.OPQLParser
import opql.lang.query
import opql.lang.visitor
from opql.exceptions import OPQLParseError

logger = logging.getLogger(__name__)

class ParserErrorListener(antlr4.error.ErrorListener.ErrorListener):
    def __init__(self):
        self.syntax = []
        self.ambiguity = 0
        self.afc = 0
        self.cs = 0

    def error(self) -> bool:
        return self.syntax != [] or self.ambiguity != 0 or self.afc != 0 or self.cs != 0

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        stack = recognizer.getRuleInvocationStack()
        stack.reverse()
        self.syntax.append((stack,(line, column, offendingSymbol, msg)))
        pass

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        self.ambiguity += 1
        pass

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        self.afc += 1
        pass

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        self.cs += 1
        pass

def scan_query(query_string: str, print_tree:bool = False) -> opql.lang.query.FullQuery:
    lex = opql.lang.grammar.OPQLLexer.OPQLLexer(antlr4.InputStream(query_string))
    token_stream = antlr4.CommonTokenStream(lex)
    token_stream.fill()

    parser = opql.lang.grammar.OPQLParser.OPQLParser(token_stream)

    pel = ParserErrorListener()
    parser.addErrorListener(pel)

    fullqueryctx = parser.r_entryPoint()

    if pel.error():
        if pel.syntax:
            detail = "; ".join(
                f"line {loc[0]}, col {loc[1]}: {loc[3]}"
                for _, loc in pel.syntax
            )
            _, (first_line, first_col, _, _) = pel.syntax[0]
            raise OPQLParseError(f"Syntax error — {detail}", line=first_line, column=first_col)
        raise OPQLParseError("Syntax error (no details available)")

    if print_tree:
        stringtree = fullqueryctx.toStringTree(recog=parser)
        logger.debug(f"Parse tree:\n{stringtree}")

    visitor = opql.lang.visitor.Visitor()
    query_ir = visitor.visitR_entryPoint(fullqueryctx)

    return query_ir


def scan_tree(query_string: str):
    lex = opql.lang.grammar.OPQLLexer.OPQLLexer(antlr4.InputStream(query_string))
    token_stream = antlr4.CommonTokenStream(lex)
    token_stream.fill()

    parser = opql.lang.grammar.OPQLParser.OPQLParser(token_stream)

    return parser.r_entryPoint()

