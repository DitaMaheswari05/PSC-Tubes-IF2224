from token_type import TokenType

class Token:
    # Mewakili sebuah token yang dihasilkan oleh lexer
    def __init__(self, ttype: TokenType, value: str, line: int, col: int):
        self.type = ttype
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self) -> str:
        return f"{self.type.name}({self.value!r})"