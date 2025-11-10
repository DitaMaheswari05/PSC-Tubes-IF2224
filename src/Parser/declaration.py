from Repository.TokenType import TokenType
from Parser.ast import *
from Parser.ErrorHandling import *

class DeclarationParser:
    """Parser untuk bagian deklarasi (const, type, var, subprogram)"""
    
    def __init__(self, parser):
        self.parser = parser
    
    def parse_declaration_part(self) -> DeclarationPartNode:
        """
        declaration-part -> (const-declaration)* (type-declaration)* 
                                (var-declaration)* (subprogram-declaration)*
        """
        node = DeclarationPartNode()
        # TO DO
        return node

    
    def parse_const_declaration(self) -> ConstDeclarationNode:
        """
        const-declaration → KEYWORD(konstanta) 
                           (IDENTIFIER = value SEMICOLON)+
        """
        node = ConstDeclarationNode()
        # TO DO
        return node
    
    def parse_type_declaration(self) -> TypeDeclarationNode:
        """
        type-declaration → KEYWORD(tipe) 
                          (IDENTIFIER = type-definition SEMICOLON)+
        """
        node = TypeDeclarationNode()
        # TO DO
        return node
    
    def parse_var_declaration(self) -> VarDeclarationNode:
        """
        var-declaration → KEYWORD(variabel) 
                         (identifier-list COLON type SEMICOLON)+
        """
        node = VarDeclarationNode()
        # TO DO
        return node
    
    def parse_identifier_list(self) -> IdentifierListNode:
        """
        identifier-list → IDENTIFIER (COMMA IDENTIFIER)*
        """
        node = IdentifierListNode()
        # TO DO
        return node
    
    def parse_type(self) -> TypeNode:
        """
        type → KEYWORD(integer/real/boolean/char) | array-type | record-type | IDENTIFIER
        """
        node = TypeNode()
        # TO DO
        return node
    
    def parse_array_type(self) -> ArrayTypeNode:
        """
        array-type → KEYWORD(larik) LBRACKET range RBRACKET KEYWORD(dari) type
        """
        node = ArrayTypeNode()
        # TO DO
        return node
    
    def parse_range(self) -> RangeNode:
        """
        range → expression RANGE_OPERATOR(..) expression
        """
        node = RangeNode()
        # TO DO
        return node
    
    def parse_procedure_declaration(self) -> ProcedureDeclarationNode:
        """
        procedure-declaration → KEYWORD(prosedur) IDENTIFIER 
                               (formal-parameter-list)? SEMICOLON
                               declaration-part compound-statement SEMICOLON
        """
        node = ProcedureDeclarationNode()
        # TO DO
        return node
    
    def parse_function_declaration(self) -> FunctionDeclarationNode:
        """
        function-declaration → KEYWORD(fungsi) IDENTIFIER 
                              (formal-parameter-list)? COLON type SEMICOLON
                              declaration-part compound-statement SEMICOLON
        """
        node = FunctionDeclarationNode()
        # TO DO
        return node
    
    def parse_formal_parameter_list(self) -> FormalParameterListNode:
        """
        formal-parameter-list → LPARENTHESIS parameter-group 
                               (SEMICOLON parameter-group)* RPARENTHESIS
        
        parameter-group → identifier-list COLON type
        """
        node = FormalParameterListNode()
        # TO DO
        return node