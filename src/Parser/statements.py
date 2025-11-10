from Repository.TokenType import TokenType
from Parser.ast import *
from Parser.ErrorHandling import *

class StatementParser:
    """Parser untuk statements"""
    
    def __init__(self, parser):
        self.parser = parser
    
    def parse_compound_statement(self) -> CompoundStatementNode:
        """
        compound-statement → KEYWORD(mulai) statement-list KEYWORD(selesai)
        """
        node = CompoundStatementNode()
        
        # TO DO
        
        return node
    
    def parse_statement_list(self) -> StatementListNode:
        """
        statement-list → statement (SEMICOLON statement)*
        """
        node = StatementListNode()
        
        # TO DO
        
        return node
    
    def parse_statement(self):
        """
        statement → assignment-statement | if-statement | while-statement |
                   for-statement | compound-statement | call-statement | empty
        """
        # TO DO
        
        # Empty statement
        return None
    
    def parse_assignment_statement(self) -> AssignmentStatementNode:
        """
        assignment-statement → IDENTIFIER ASSIGN_OPERATOR(:=) expression
        """
        node = AssignmentStatementNode()
       # TO DO
        
        return node
    
    def parse_if_statement(self) -> IfStatementNode:
        """
        if-statement → KEYWORD(jika) expression KEYWORD(maka) statement 
                      (KEYWORD(selain-itu) statement)?
        """
        node = IfStatementNode()
        
        # TO DO
        
        return node
    
    def parse_while_statement(self) -> WhileStatementNode:
        """
        while-statement → KEYWORD(selama) expression KEYWORD(lakukan) statement
        """
        node = WhileStatementNode()
        
        # TO DO
        
        return node
    
    def parse_for_statement(self) -> ForStatementNode:
        """
        for-statement → KEYWORD(untuk) IDENTIFIER ASSIGN_OPERATOR expression 
                       (KEYWORD(ke)/KEYWORD(turun-ke)) expression 
                       KEYWORD(lakukan) statement
        """
        node = ForStatementNode()
        
        # TO DO
        
        return node
    
    def parse_call_statement(self, is_function=False) -> CallStatementNode:
        """
        call-statement → IDENTIFIER (LPARENTHESIS parameter-list RPARENTHESIS)?
        
        Args:
            is_function: True jika dipanggil sebagai function call, False untuk procedure call
        """
        node = CallStatementNode(is_function=is_function)
        
        # TO DO
        
        return node