from Repository.TokenType import TokenType
from Parser.ast import *
from Parser.ErrorHandling import *

# NOTES
# fungsi advance() merupakan placeholder, karena belum ada implementasi parser

class DeclarationParser:
    """parser untuk bagian deklarasi (const, type, var, subprogram)"""
    
    def __init__(self, parser):
        self.parser = parser
    
    def parse_declaration_part(self) -> DeclarationPartNode:
        node = DeclarationPartNode()
        
        # konstanta
        while self.parser.current_token and \
              self.parser.current_token.tokenType == TokenType.KEYWORD and \
              self.parser.current_token.value.lower() == "konstanta":
            node.add_child(self.parse_const_declaration())
        
        # tipe
        while self.parser.current_token and \
              self.parser.current_token.tokenType == TokenType.KEYWORD and \
              self.parser.current_token.value.lower() == "tipe":
            node.add_child(self.parse_type_declaration())
        
        # var
        while self.parser.current_token and \
              self.parser.current_token.tokenType == TokenType.KEYWORD and \
              self.parser.current_token.value.lower() == "variabel":
            node.add_child(self.parse_var_declaration())
        
        # subprogram
        while self.parser.current_token and \
              self.parser.current_token.tokenType == TokenType.KEYWORD and \
              self.parser.current_token.value.lower() in ["prosedur", "fungsi"]:
            if self.parser.current_token.value.lower() == "prosedur":
                node.add_child(self.parse_procedure_declaration())
            elif self.parser.current_token.value.lower() == "fungsi":
                node.add_child(self.parse_function_declaration())
            else:
                break
        
        return node

    def parse_const_declaration(self) -> ConstDeclarationNode:
        node = ConstDeclarationNode()
        
        # expect 'konstanta' keyword
        if not (self.parser.current_token and 
                self.parser.current_token.tokenType == TokenType.KEYWORD and
                self.parser.current_token.value.lower() == "konstanta"):
            raise UnexpectedTokenError("konstanta", self.parser.current_token)
        
        # tambah node keyword 'konstanta', dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        while True:
            # expect IDENTIFIER
            if not self.parser.current_token or \
                self.parser.current_token.tokenType != TokenType.IDENTIFIER:
                raise UnexpectedTokenError(TokenType.IDENTIFIER, self.parser.current_token)
            
            # tambah node identifier, dan maju ke token berikutnya
            node.add_child(self.parser.current_token)
            self.parser.advance()
            
            # expect '=' (RELATIONAL_OPERATOR)
            if not self.parser.current_token or \
                self.parser.current_token.tokenType != TokenType.RELATIONAL_OPERATOR or \
                self.parser.current_token.value != "=":
                raise UnexpectedTokenError("=", self.parser.current_token)
            
            # tambah node '=', dan maju ke token berikutnya
            node.add_child(self.parser.current_token)
            self.parser.advance()
            
            # expect value (NUMBER, CHAR_LITERAL, STRING_LITERAL, or IDENTIFIER for true/false)
            if not self.parser.current_token or self.parser.current_token.tokenType not in [
                TokenType.NUMBER, TokenType.CHAR_LITERAL, TokenType.STRING_LITERAL, TokenType.IDENTIFIER, TokenType.KEYWORD
            ]:
                raise UnexpectedTokenError("constant value", self.parser.current_token)
            
            # tambah node value, dan maju ke token berikutnya
            node.add_child(self.parser.current_token)
            self.parser.advance()
            
            # expect SEMICOLON
            if not self.parser.current_token or \
                self.parser.current_token.tokenType != TokenType.SEMICOLON:
                raise UnexpectedTokenError(TokenType.SEMICOLON, self.parser.current_token)
            
            # tambah node SEMICOLON, dan maju ke token berikutnya
            node.add_child(self.parser.current_token)
            self.parser.advance()
            
            # cek const lainnya
            if not (self.parser.current_token and 
                    self.parser.current_token.tokenType == TokenType.IDENTIFIER):
                break
        
        return node
    
    def parse_type_declaration(self) -> TypeDeclarationNode:
        node = TypeDeclarationNode()
        
        # expect 'tipe' keyword
        if not (self.parser.current_token and 
                self.parser.current_token.tokenType == TokenType.KEYWORD and
                self.parser.current_token.value.lower() == "tipe"):
            raise UnexpectedTokenError("tipe", self.parser.current_token)
        
        # tambah node 'tipe', dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        while True:
            # expect IDENTIFIER
            if not self.parser.current_token or \
                self.parser.current_token.tokenType != TokenType.IDENTIFIER:
                raise UnexpectedTokenError(TokenType.IDENTIFIER, self.parser.current_token)
            
            # tambah node identifier, dan maju ke token berikutnya
            node.add_child(self.parser.current_token)
            self.parser.advance()
            
            # expect '='
            if not self.parser.current_token or \
                self.parser.current_token.tokenType != TokenType.RELATIONAL_OPERATOR or \
                self.parser.current_token.value != "=":
                raise UnexpectedTokenError("=", self.parser.current_token)
            
            # tambah node '=', dan maju ke token berikutnya
            node.add_child(self.parser.current_token)
            self.parser.advance()
            
            # parse type, dan tambah ke node
            type_node = self.parse_type()
            node.add_child(type_node)
            
            # expect SEMICOLON
            if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.SEMICOLON:
                raise UnexpectedTokenError(TokenType.SEMICOLON, self.parser.current_token)
            
            # tambah node SEMICOLON, dan maju ke token berikutnya
            node.add_child(self.parser.current_token)
            self.parser.advance()
            
            # cek type lainnya
            if not (self.parser.current_token and 
                    self.parser.current_token.tokenType == TokenType.IDENTIFIER):
                break
        
        return node
    
    def parse_var_declaration(self) -> VarDeclarationNode:
        node = VarDeclarationNode()
        
        # expect 'variabel' keyword
        if not (self.parser.current_token and 
                self.parser.current_token.tokenType == TokenType.KEYWORD and
                self.parser.current_token.value.lower() == "variabel"):
            raise UnexpectedTokenError("variabel", self.parser.current_token)
        
        # tambah node 'variabel', dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        while True:
            # parse identifier list
            identifier_list = self.parse_identifier_list()
            node.add_child(identifier_list)
            
            # expect COLON
            if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.COLON:
                raise UnexpectedTokenError(TokenType.COLON, self.parser.current_token)
            
            # tambah node COLON, dan maju ke token berikutnya
            node.add_child(self.parser.current_token)
            self.parser.advance()
            
            # parse type, dan tambah ke node
            type_node = self.parse_type()
            node.add_child(type_node)
            
            # expect SEMICOLON
            if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.SEMICOLON:
                raise UnexpectedTokenError(TokenType.SEMICOLON, self.parser.current_token)
            
            # tambah node SEMICOLON, dan maju ke token berikutnya
            node.add_child(self.parser.current_token)
            self.parser.advance()
            
            # cek type lainnya
            if not (self.parser.current_token and 
                    self.parser.current_token.tokenType == TokenType.IDENTIFIER):
                break
        
        return node
    
    def parse_identifier_list(self) -> IdentifierListNode:
        node = IdentifierListNode()
        
        # expect first IDENTIFIER
        if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.IDENTIFIER:
            raise UnexpectedTokenError(TokenType.IDENTIFIER, self.parser.current_token)
        
        # tambah node IDENTIFIER, dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        # parse identifier lainnya yang dipisahkan koma (jika ada)
        while self.parser.current_token and self.parser.current_token.tokenType == TokenType.COMMA: 
            node.add_child(self.parser.current_token)
            self.parser.advance()
            
            # expect IDENTIFIER setelah koma
            if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.IDENTIFIER:
                raise UnexpectedTokenError(TokenType.IDENTIFIER, self.parser.current_token)
            
            # tambah node IDENTIFIER, dan maju ke token berikutnya
            node.add_child(self.parser.current_token)
            self.parser.advance()
        
        return node
    
    def parse_type(self) -> TypeNode:
        node = TypeNode()
        
        if not self.parser.current_token:
            raise UnexpectedTokenError("type", None)
        
        # cek type array
        if self.parser.current_token.tokenType == TokenType.KEYWORD and \
           self.parser.current_token.value.lower() == "larik":
            array_node = self.parse_array_type()
            node.add_child(array_node)
        # cek tipe dasar (integer, real, boolean, char, string)
        elif self.parser.current_token.tokenType == TokenType.KEYWORD and \
             self.parser.current_token.value.lower() in ["integer", "real", "boolean", "char", "string", "bulat", "desimal", "karakter", "logika"]:
            node.add_child(self.parser.current_token)
            self.parser.advance()
        # cek tipe kustom (IDENTIFIER)
        elif self.parser.current_token.tokenType == TokenType.IDENTIFIER:
            node.add_child(self.parser.current_token)
            self.parser.advance()
        else:
            raise UnexpectedTokenError("type", self.parser.current_token)
        
        return node
    
    def parse_array_type(self) -> ArrayTypeNode:
        node = ArrayTypeNode()
        
        # expect 'larik' keyword
        if not (self.parser.current_token and 
                self.parser.current_token.tokenType == TokenType.KEYWORD and
                self.parser.current_token.value.lower() == "larik"):
            raise UnexpectedTokenError("larik", self.parser.current_token)
        
        # tambah node 'larik', dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        # expect LBRACKET
        if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.LBRACKET:
            raise UnexpectedTokenError(TokenType.LBRACKET, self.parser.current_token)
        
        # tambah node LBRACKET, dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        # parse range
        range_node = self.parse_range()
        node.add_child(range_node)
        
        # expect RBRACKET
        if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.RBRACKET:
            raise UnexpectedTokenError(TokenType.RBRACKET, self.parser.current_token)
        
        # tambah node RBRACKET, dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        # expect 'dari' keyword
        if not (self.parser.current_token and 
                self.parser.current_token.tokenType == TokenType.KEYWORD and
                self.parser.current_token.value.lower() == "dari"):
            raise UnexpectedTokenError("dari", self.parser.current_token)
        
        # tambah node 'dari', dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        # parse element type
        type_node = self.parse_type()
        node.add_child(type_node)
        
        return node
    
    def parse_range(self) -> RangeNode:
        node = RangeNode()
        
        # antara [1..2] atau [Monday..Friday]
        if not self.parser.current_token or self.parser.current_token.tokenType not in [TokenType.NUMBER, TokenType.IDENTIFIER]:
            raise UnexpectedTokenError("number or identifier", self.parser.current_token)
        
        # tambah node start of range, dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        # expect RANGE_OPERATOR (..)
        if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.RANGE_OPERATOR:
            raise UnexpectedTokenError(TokenType.RANGE_OPERATOR, self.parser.current_token)
        
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        # expect end of range
        if not self.parser.current_token or self.parser.current_token.tokenType not in [TokenType.NUMBER, TokenType.IDENTIFIER]:
            raise UnexpectedTokenError("number or identifier", self.parser.current_token)
        
        # tambah node end of range, dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        return node
    
    def parse_procedure_declaration(self) -> ProcedureDeclarationNode:
        node = ProcedureDeclarationNode()
        
        # expect 'prosedur' keyword
        if not (self.parser.current_token and 
                self.parser.current_token.tokenType == TokenType.KEYWORD and
                self.parser.current_token.value.lower() == "prosedur"):
            raise UnexpectedTokenError("prosedur", self.parser.current_token)
        
        # tambah node 'prosedur', dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        # expect IDENTIFIER
        if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.IDENTIFIER:
            raise UnexpectedTokenError(TokenType.IDENTIFIER, self.parser.current_token)
        
        # tambah node IDENTIFIER, dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        # optional formal parameter list
        if self.parser.current_token and self.parser.current_token.tokenType == TokenType.LPARENTHESIS:
            param_list = self.parse_formal_parameter_list()
            node.add_child(param_list)
        
        # expect SEMICOLON
        if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.SEMICOLON:
            raise UnexpectedTokenError(TokenType.SEMICOLON, self.parser.current_token)
        
        # tambah node SEMICOLON, dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        # parse declaration (recursive)
        decl_part = self.parse_declaration_part()
        node.add_child(decl_part)
        
        # parse compound statement 
        # to do, nunggu bagian lain
        
        # expect SEMICOLON
        if self.parser.current_token and self.parser.current_token.tokenType == TokenType.SEMICOLON:
            node.add_child(self.parser.current_token)
            self.parser.advance()
        
        return node
    
    def parse_function_declaration(self) -> FunctionDeclarationNode:
        node = FunctionDeclarationNode()
        
        # expect 'fungsi' keyword
        if not (self.parser.current_token and 
                self.parser.current_token.tokenType == TokenType.KEYWORD and
                self.parser.current_token.value.lower() == "fungsi"):
            raise UnexpectedTokenError("fungsi", self.parser.current_token)
        
        # tambah node 'fungsi', dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        # expect IDENTIFIER
        if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.IDENTIFIER:
            raise UnexpectedTokenError(TokenType.IDENTIFIER, self.parser.current_token)
        
        # tambah node IDENTIFIER, dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        # optional formal parameter list
        if self.parser.current_token and self.parser.current_token.tokenType == TokenType.LPARENTHESIS:
            param_list = self.parse_formal_parameter_list()
            node.add_child(param_list)
        
        # expect COLON
        if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.COLON:
            raise UnexpectedTokenError(TokenType.COLON, self.parser.current_token)
        
        # tambah node COLON, dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        # parse return type
        type_node = self.parse_type()
        node.add_child(type_node)
        
        # expect SEMICOLON
        if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.SEMICOLON:
            raise UnexpectedTokenError(TokenType.SEMICOLON, self.parser.current_token)
        
        # tambah node SEMICOLON, dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        # parse declaration (recursive)
        decl_part = self.parse_declaration_part()
        node.add_child(decl_part)
        
        # parse compound statement
        # to do, nunggu bagian lain
        
        # expect SEMICOLON at the end
        if self.parser.current_token and self.parser.current_token.tokenType == TokenType.SEMICOLON:
            node.add_child(self.parser.current_token)
            self.parser.advance()
        
        return node
    
    def parse_formal_parameter_list(self) -> FormalParameterListNode:
        node = FormalParameterListNode()
        
        # expect LPARENTHESIS
        if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.LPARENTHESIS:
            raise UnexpectedTokenError(TokenType.LPARENTHESIS, self.parser.current_token)
        
        # tambah node LPARENTHESIS, dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        # parse first parameter group
        node.add_child(self.parse_identifier_list())
        
        # expect COLON
        if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.COLON:
            raise UnexpectedTokenError(TokenType.COLON, self.parser.current_token)
        
        # tambah node COLON, dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        # parse type
        type_node = self.parse_type()
        node.add_child(type_node)
        
        # parse additional parameter groups yang dipisahkan semicolons
        while self.parser.current_token and self.parser.current_token.tokenType == TokenType.SEMICOLON:
            node.add_child(self.parser.current_token)
            self.parser.advance()
            
            # cek apakah masih ada parameter lain
            if self.parser.current_token and self.parser.current_token.tokenType == TokenType.RPARENTHESIS:
                break
            
            # parse identifier-list
            identifier_list = self.parse_identifier_list()
            node.add_child(identifier_list)
            
            # expect COLON
            if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.COLON:
                raise UnexpectedTokenError(TokenType.COLON, self.parser.current_token)
            
            # tambah node COLON, dan maju ke token berikutnya
            node.add_child(self.parser.current_token)
            self.parser.advance()
            
            # parse type
            type_node = self.parse_type()
            node.add_child(type_node)
        
        # expect RPARENTHESIS
        if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.RPARENTHESIS:
            raise UnexpectedTokenError(TokenType.RPARENTHESIS, self.parser.current_token)
        
        # tambah node RPARENTHESIS, dan maju ke token berikutnya
        node.add_child(self.parser.current_token)
        self.parser.advance()
        
        return node