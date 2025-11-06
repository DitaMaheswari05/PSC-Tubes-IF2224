class ErrorHandling(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.formatError)
        
    def formatError(self) -> str:
        if self.line > 0 and self.column > 0:
            return f"Syntax Error at line {self.line}, column {self.column}: {self.message}"
        return f"Syntax Error: {self.message}"