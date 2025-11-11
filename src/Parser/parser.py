from typing import List, Optional
from Model.Token import Token
from Repository.TokenType import TokenType
from Parser.ast import *
from Parser.ErrorHandling import *
from Parser.declaration import DeclarationParser
from Parser.expression import ExpressionParser
from Parser.statements import StatementParser

class Parser:
    """
    Main Parser class untuk Pascal-S menggunakan Recursive Descent
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[0] if tokens else None
        
        # Initialize sub-parsers
        self.declaration_parser = DeclarationParser(self)
        self.expression_parser = ExpressionParser(self)
        self.statement_parser = StatementParser(self)
    
    def advance(self):
        """Maju ke token berikutnya"""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None
