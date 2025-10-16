from enum import Enum, auto

# Buat definisiin semua jenis token yang memungkinkan
class TokenType(Enum):
    # Keywords
    KEYWORD = auto()
    # Literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING_LITERAL = auto()
    CHAR_LITERAL = auto()
    # Operators
    ARITHMETIC_OPERATOR = auto()
    RELATIONAL_OPERATOR = auto()
    ASSIGN_OPERATOR = auto()
    LOGICAL_OPERATOR = auto()
    RANGE_OPERATOR = auto()
    # Delimiters
    SEMICOLON = auto()
    COMMA = auto()
    LPARENTHESIS = auto()
    RPARENTHESIS = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COLON = auto()
    DOT = auto()
    # Comments
    COMMENT_START = auto()
    COMMENT_END = auto()
    # Special
    UNKNOWN = auto()
    EOF = auto()