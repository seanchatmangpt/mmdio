grammar OPQL;

// from https://stackoverflow.com/questions/74247524/what-is-the-meaning-of-the-antlr-syntax-in-this-grammar-file

// Any rules that begin with a capital letter (often we captilize the entire rule name to make it obvious) is a Lexer rule.
// Rules that begin with lower case letters are parser rules.

// When multiple Lexer rules could match you input, two "tie breakers" come into play.
// 1 - if a rules matches more characters in your input stream than other rules, then that will be the rules used to produce a token.
// 2 - if there is a tie of multiple Lexer rules matching the same sequence of input characters, then the Lexer rules that appears first in your grammar will be used to generate a token.


PATTERN_TKN : 'PATTERN' ;
SUBJECT_TO_TKN : 'ST' | 'SUBJECTTO' ;
FILTER_TKN : 'FILTER' ;

RETURN_TKN : 'RETURN' ;
OCEL_TKN : 'OCEL' ;

KEEP_TKN : 'KEEP' ;
DISTINCT_TKN : 'DISTINCT' ;
ORDER_BY_TKN : 'ORDERBY' ;
ASC_TKN : 'ASC' | 'ASCENDING' ;
DESC_TKN : 'DESC' | 'DESCENDING' ;
LIMIT_TKN : 'LIMIT' ;
BINNED_TKN : 'BINNED' ;

WHEN_TKN : 'WHEN' ;
NOT_MATERIALIZED_TKN : 'NOT' [ \t\r\n]+ 'MATERIALIZED' ;
MATERIALIZED_TKN : 'MATERIALIZED' ;

AS_TKN : 'AS' ;

DOT : '.' ;
LSEP : ',' ;
COLON : ':' ;
LEFT_BR : '(' ;
RIGHT_BR : ')' ;
LEFT_SBR : '[' ;
RIGHT_SBR : ']' ;
ASTERISK : '*' ;
AT : '@' ;

EVENT_TKN     : 'E' ;
OBJECT_TKN    : 'O' ;
TIMESTAMP_TKN : 'T' ;
DURATION_TKN  : 'D' ;

r_timestamp : TIMESTAMP_TKN LEFT_BR STRING RIGHT_BR ;
r_duration : DURATION_TKN LEFT_BR
                 INT LSEP
                 INT LSEP
                 INT LSEP
                 (INT | FLOAT)
                 RIGHT_BR ;

TRUE_TKN : 'True' ;
FALSE_TKN : 'False' ;
r_constantBool : TRUE_TKN | FALSE_TKN ;

NONE_TKN : 'None' ;

r_propertyTimestamp : SYMBOLICNAME | r_timestamp ;
r_eoProperty : SYMBOLICNAME LEFT_SBR STRING (AT r_propertyTimestamp)? RIGHT_SBR ;

r_rvFunctionArg : r_expression | r_fullquery ;

r_rvFunctionCall : SYMBOLICNAME LEFT_BR r_rvFunctionArg (LSEP r_rvFunctionArg)* RIGHT_BR ;

r_propositionalRule : SUBJECT_TO_TKN r_expression ;

r_orderItem : r_expression (ASC_TKN | DESC_TKN)? ;
r_order : ORDER_BY_TKN r_orderItem (LSEP r_orderItem)* ;

fragment DIGIT : ('0'..'9') ;
fragment DIGIT_EX_ZERO : ('1'..'9') ;
INT : '0' | DIGIT_EX_ZERO DIGIT* ;
FLOAT : INT '.' DIGIT+ ;
r_limit : LIMIT_TKN INT ;

NEG_INF_TKN : '-inf' ;
POS_INF_TKN : ('+')? 'inf' ;
r_intervalLimit : INT | FLOAT | NEG_INF_TKN | POS_INF_TKN ;
r_intervalTarget : INT | FLOAT | STRING ;
r_binningInterval : (LEFT_BR | LEFT_SBR) r_intervalLimit LSEP r_intervalLimit (RIGHT_BR | RIGHT_SBR) AS_TKN r_intervalTarget ;

r_binning : BINNED_TKN LEFT_BR r_binningInterval (LSEP r_binningInterval)* RIGHT_BR ;

r_sname : r_expression (AS_TKN SYMBOLICNAME)? ;

r_cte : r_subquery (AS_TKN SYMBOLICNAME)? ;

r_projectionItem : r_cte | r_sname r_binning? ;
r_projection : DISTINCT_TKN? ASTERISK r_order? r_limit?
             | DISTINCT_TKN? (ASTERISK LSEP)? r_projectionItem (LSEP r_projectionItem)* r_order? r_limit? ;

r_keepRule : KEEP_TKN r_projection r_propositionalRule? ;

r_returnRule : RETURN_TKN (OCEL_TKN | r_projection r_propositionalRule?) ;

r_filterRule : FILTER_TKN SYMBOLICNAME (LSEP SYMBOLICNAME)* ;

r_whenRule : WHEN_TKN r_expression AS_TKN SYMBOLICNAME r_propositionalRule? ;

/*
* Entry rule
*/
r_entryPoint : r_fullquery EOF ;

r_fullquery : r_contextRule* r_returnRule ;

r_contextRule : r_patternRule | r_filterRule | r_keepRule | r_whenRule ;

r_patternRule : PATTERN_TKN r_graphPatternList r_propositionalRule? ;

r_graphPatternList : r_graph (LSEP r_graph)* ;

r_graph : r_event ((r_relationAny | r_relationRd) r_graphWithoutEvent)?
        | r_object ((r_relationAny | r_relationLd) r_graph | r_relationRd r_graphWithoutEvent)? ;

r_graphWithoutEvent : r_object ((r_relationAny | r_relationLd) r_graph)? ;

r_event : EVENT_TKN LEFT_BR r_tag? (COLON r_name)? RIGHT_BR ;
r_object : OBJECT_TKN LEFT_BR r_tag? (COLON r_name)? RIGHT_BR ;
r_relationAny : '-' LEFT_SBR r_tag? (COLON r_name)? RIGHT_SBR '-' ;
r_relationRd : '-' LEFT_SBR r_tag? (COLON r_name)? RIGHT_SBR '->' ;
r_relationLd : '<-' LEFT_SBR r_tag? (COLON r_name)? RIGHT_SBR '-' ;

r_tag : SYMBOLICNAME ;

//string already has double quotes in it, so dont add them here!
r_name : STRING;

r_subquery : MATERIALIZED_TKN? LEFT_BR r_fullquery RIGHT_BR
           | NOT_MATERIALIZED_TKN LEFT_BR r_fullquery RIGHT_BR
           ;

r_valueType : r_eoProperty | INT | FLOAT | r_constantBool | NONE_TKN | STRING | r_timestamp | r_duration | SYMBOLICNAME | r_rvFunctionCall ;

// adapted from cypher grammar
OR : 'OR' ;
XOR : 'XOR' ;
AND : 'AND' ;
NOT : 'NOT' ;

EQUAL_TO : '==' ;
LE : '<=' ;
GE : '>=' ;
GT : '>' ;
LT : '<' ;
NOT_EQUAL : '!=' ;

PLUS : '+' ;
SUB : '-' ;
DIV : '/' ;
MOD : '%' ;
CARET : '^' ;

r_expression
    : (PLUS | SUB) r_expression                             # r_exUnary
    | <assoc=right> r_expression CARET r_expression         # r_exPower
    | r_expression (ASTERISK | DIV | MOD) r_expression      # r_exMulDiv
    | r_expression (PLUS | SUB) r_expression                # r_exAddSub
    | r_expression r_compareSign r_expression               # r_exCompare
    | NOT r_expression                                      # r_exNot
    | r_expression AND r_expression                         # r_exAnd
    | r_expression XOR r_expression                         # r_exXor
    | r_expression OR r_expression                          # r_exOr
    | LEFT_BR r_expression RIGHT_BR                         # r_exGrouped
    | r_valueType                                           # r_exAtomic
    ;

r_compareSign : EQUAL_TO | LE | GE | GT | LT | NOT_EQUAL ;

// taken and adapted from PQL grammar
fragment DQ : '"' ;

SYMBOLICNAME : ( 'a'..'z' | 'A'..'Z') ( 'a'..'z' | 'A'..'Z' | '0'..'9' | '_' )*;

STRING : DQ ( ESC_SEQ | ~('\\'|'"') )* DQ ;

fragment ESC_SEQ : '\\' ('\\"'|'\\'|'/'|'b'|'f'|'n'|'r'|'t') ; // omitted unicode escapes for now

//gratefully taken from cypher grammar

SP : ( WHITESPACE )+ -> skip ;

WHITESPACE
          :  SPACE
              | TAB
              | LF
              | VT
              | FF
              | CR
              | FS
              | GS
              | RS
              | US
              | '\u1680'
              | '\u180e'
              | '\u2000'
              | '\u2001'
              | '\u2002'
              | '\u2003'
              | '\u2004'
              | '\u2005'
              | '\u2006'
              | '\u2008'
              | '\u2009'
              | '\u200a'
              | '\u2028'
              | '\u2029'
              | '\u205f'
              | '\u3000'
              | '\u00a0'
              | '\u2007'
              | '\u202f'
              | Comment
              ;


fragment SPACE : [ ] ;
fragment TAB : [\t] ;
fragment LF : [\n] ;
fragment VT : [\u000B] ;
fragment FF : [\f] ;
fragment CR : [\r] ;
fragment FS : [\u001C] ;
fragment GS : [\u001D] ;
fragment RS : [\u001E] ;
fragment US : [\u001F] ;

Comment
       :  ( '/*' ( Comment_1 | ( '*' Comment_2 ) )* '*/' )
           | ( '//' ( Comment_3 )* CR? ( LF | EOF ) )
           ;


fragment Comment_1 : ~[*] ;

fragment Comment_3 : ~[\n\r] ;

fragment Comment_2 : ~[/] ;
