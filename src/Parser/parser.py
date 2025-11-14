from typing import List, Optional
from Model.Token import Token
from Repository.TokenType import TokenType
from Parser.ast import *
from Parser.ErrorHandling import *
from Parser.declaration import DeclarationParser
from Parser.expression import ExpressionParser
from Parser.statements import StatementParser

class SyntaxParser:
    # parser recursive descent
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[0] if tokens else None
        # inisialisasi sub-parser
        self.declaration_parser = DeclarationParser(self)
        self.expression_parser = ExpressionParser(self)
        self.statement_parser = StatementParser(self)
    def advance(self): # maju ke token berikutnya kek ADT mesin kata
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None
    
    def parse(self) -> ProgramNode:
        # hasil enkap parsing, entry point
        return self.parseProgram()
    
    def parseProgram(self) -> ProgramNode:
        programNode = ProgramNode()
        # 1. Parse program-header (KEYWORD(program) IDENTIFIER SEMICOLON)
        programNode.add_child(self.parseProgramHeader())
        # 2. Parse declaration-part (konstanta, tipe, variabel, subprogram)
        programNode.add_child(self.declaration_parser.parse_declaration_part())
        # 3. Parse compound-statemet (mulai ... selesai)
        programNode.add_child(self.statement_parser.parse_compound_statement())
        # 4. Expect DOT (.) sebagai akhir program
        if not self.current_token or self.current_token.tokenType != TokenType.DOT:
            raise UnexpectedTokenError(TokenType.DOT, self.current_token)
        # Tambahkan token DOT ke tree
        programNode.add_child(self.current_token)
        self.advance()
        return programNode
    
    def parseProgramHeader(self) -> ProgramHeaderNode :
        # Buat node program-header
        headerNode = ProgramHeaderNode()
        
        # 1. Expect KEYWORD(program)
        if not self.current_token or \
           self.current_token.tokenType != TokenType.KEYWORD or \
           self.current_token.value.lower() != 'program':
            raise UnexpectedTokenError("KEYWORD(program)", self.current_token)
        
        # Tambahkan token 'program' ke tree
        headerNode.add_child(self.current_token)
        self.advance() 
        # 2. Expect IDENTIFIER (nama program)
        if not self.current_token or self.current_token.tokenType != TokenType.IDENTIFIER:
            raise UnexpectedTokenError(TokenType.IDENTIFIER, self.current_token)
        # Tambahkan identifier ke tree
        headerNode.add_child(self.current_token)
        self.advance()
        # 3. Expect SEMICOLON
        if not self.current_token or self.current_token.tokenType != TokenType.SEMICOLON:
            raise UnexpectedTokenError(TokenType.SEMICOLON, self.current_token)
        # Tambahkan semicolon ke tree
        headerNode.add_child(self.current_token)
        self.advance()
        
        return headerNode
