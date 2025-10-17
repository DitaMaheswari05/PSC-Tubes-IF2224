
from enum import auto
from enum import Enum

class TokenType(Enum): 
    # Keywords
    KEYWORD = auto() # begin, end, if, else, then, while, do, var, const, procedure, function, return, true, false, null
    IDENTIFIER = auto() # nama variabel, nama fungsi, nama prosedur,
    STRING_LITERAL = auto() # string dalam tanda kutip ganda
    CHAR_LITERAL = auto() # karakter dalam tanda kutip tunggal
    NUMBER_LITERAL = auto() # angka
    BOOLEAN_LITERAL = auto() # true atau false
    NULL_LITERAL = auto() # null
    OPERATOR = auto() # +, -, *, /, =, <, >, <=, >=, ==, !=
    DELIMITER = auto() # ; , ( ) { } [ ] :
    COMMENT = auto() # komentar
    WHITESPACE = auto() # spasi, tab, newline
    UNKNOWN = auto() # karakter yang tidak dikenali
    EOF = auto() # end of file
    # Literals
    NUMBER = auto() # angka (Termasuk type data primitf , scientific notation, hex, octal, binary, bilangan negatif, imaginer)
    # Operators
    ARITHMETIC_OPERATOR = auto() # +, -, *, /
    RELATIONAL_OPERATOR = auto() # =, <, >, <=, >=, ==, !=
    ASSIGN_OPERATOR = auto() # :=
    LOGICAL_OPERATOR = auto() # and, or, not
    RANGE_OPERATOR = auto() # ..
    # Delimiters
    SEMICOLON = auto() # ;
    COMMA = auto() # ,
    LPARENTHESIS = auto() # (
    RPARENTHESIS = auto() # )
    LBRACKET = auto() # [
    RBRACKET = auto() # ]
    COLON = auto() # :
    DOT = auto() # .
    # Comments
    # COMMENT_START = auto() # { di spek gajadi 
    # COMMENT_END = auto() # }

