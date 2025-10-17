from Repository.TokenType import TokenType

class Token:
    # representasi token hasil lexical analysis
    def __init__(self, tokenType: TokenType, value: str, line: int = 0, column: int = 0):
        self.tokenType = tokenType
        self.value = value
        self.line = line # debug
        self.column = column # deubh
    
    def __str__(self) -> str:
        # TYPE(value)
        return f"{self.tokenType.name}({self.value})"
    
    def __repr__(self) -> str:
        return self.__str__()
    def getType(self) -> TokenType:
        #getter tokentype
        return self.tokenType
    def getValue(self) -> str:
        # getter tokenvalue
        return self.value
    def getPosition(self) -> tuple:
        # getter posisi token
        return (self.line, self.column) 