class SemanticError(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.format_message())
    
    def format_message(self):
        if self.line > 0:
            return f"Semantic error at line {self.line}, column {self.column}: {self.message}"
        return f"Semantic error: {self.message}"
    
    def __str__(self):
        return self.format_message()
    
    def __repr__(self):
        return f"SemanticError('{self.message}', line={self.line}, column={self.column})"


class UndefinedIdentifierError(SemanticError): 
    def __init__(self, identifier: str, line: int = 0, column: int = 0):
        message = f"Undefined identifier: {identifier}"
        super().__init__(message, line, column)
        self.identifier = identifier


class TypeMismatchError(SemanticError):
    def __init__(self, expected: str, got: str, context: str = "", line: int = 0, column: int = 0):
        if context:
            message = f"Type mismatch in {context}: expected {expected}, got {got}"
        else:
            message = f"Type mismatch: expected {expected}, got {got}"
        super().__init__(message, line, column)
        self.expected = expected
        self.got = got
        self.context = context


class RedeclarationError(SemanticError):
    def __init__(self, identifier: str, line: int = 0, column: int = 0):
        message = f"Identifier '{identifier}' already declared in this scope"
        super().__init__(message, line, column)
        self.identifier = identifier


class InvalidAssignmentError(SemanticError):
    def __init__(self, target: str, reason: str, line: int = 0, column: int = 0):
        message = f"Cannot assign to {target}: {reason}"
        super().__init__(message, line, column)
        self.target = target
        self.reason = reason


class InvalidOperationError(SemanticError):
    def __init__(self, operation: str, operand_types: str, line: int = 0, column: int = 0):
        message = f"Invalid operation '{operation}' for operand types: {operand_types}"
        super().__init__(message, line, column)
        self.operation = operation
        self.operand_types = operand_types


class ScopeError(SemanticError):
    def __init__(self, message: str, identifier: str = "", line: int = 0, column: int = 0):
        super().__init__(message, line, column)
        self.identifier = identifier


class ParameterError(SemanticError):
    def __init__(self, function_name: str, expected: int, got: int, line: int = 0, column: int = 0):
        message = f"Function '{function_name}' expects {expected} parameters, got {got}"
        super().__init__(message, line, column)
        self.function_name = function_name
        self.expected = expected
        self.got = got