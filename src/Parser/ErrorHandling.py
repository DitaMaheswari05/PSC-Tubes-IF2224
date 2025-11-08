from Repository.TokenType import TokenType
from Model.Token import Token

class ParseError(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.format_message())
    
    def format_message(self):
        if self.line > 0:
            return f"Syntax error at line {self.line}, column {self.column}: {self.message}"
        return f"Syntax error: {self.message}"

class UnexpectedTokenError(ParseError):
    def __init__(self, expected, got, line=0, column=0):
        if isinstance(expected, TokenType):
            expected_str = expected.name
        elif isinstance(expected, list):
            expected_str = ", ".join([e.name if isinstance(e, TokenType) else str(e) for e in expected])
        else:
            expected_str = str(expected)
        
        if got is None:
            got_str = "EOF"
        elif isinstance(got, Token):
            got_str = f"{got.tokenType.name}({got.value})"
        else:
            got_str = str(got)
        
        message = f"unexpected token {got_str}, expected {expected_str}"
        
        if isinstance(got, Token) and line == 0 and column == 0:
            line = got.line
            column = got.column
        
        super().__init__(message, line, column)

class UnexpectedEOFError(ParseError):
    def __init__(self, expected="more tokens"):
        message = f"unexpected end of file, expected {expected}"
        super().__init__(message)