from Repository.TokenType import TokenType
from Parser.ast import *
from Parser.ErrorHandling import *

class ExpressionParser:
    """Parser untuk expressions"""
    
    def __init__(self, parser):
        self.parser = parser
    
    def parse_expression(self) -> ExpressionNode:
        """
        expression → simple-expression (relational-operator simple-expression)?
        """
        node = ExpressionNode()
        # TO DO
        return node
    
    def parse_simple_expression(self) -> SimpleExpressionNode:
        """
        simple-expression → (ARITHMETIC_OPERATOR(+/-))? term (additive-operator term)*
        """
        node = SimpleExpressionNode()
        
        # TO DO
        
        return node
    
    def parse_term(self) -> TermNode:
        """
        term → factor (multiplicative-operator factor)*
        """
        node = TermNode()
        
        # TO DO
        
        return node
    
    def parse_factor(self) -> FactorNode:
        """
        factor → IDENTIFIER | NUMBER | CHAR_LITERAL | STRING_LITERAL |
                (LPARENTHESIS expression RPARENTHESIS) |
                LOGICAL_OPERATOR(tidak) factor |
                function-call
        """
        node = FactorNode()
        
        # TO DO
        
        return node
    
    def is_additive_operator(self, token) -> bool:
        """Check apakah token adalah additive operator (+, -, atau)"""
    
    def is_multiplicative_operator(self, token) -> bool:
        """Check apakah token adalah multiplicative operator (*, /, bagi, mod, dan)"""
    
    def parse_parameter_list(self) -> ParameterListNode:
        """
        parameter-list → expression (COMMA expression)*
        """
        node = ParameterListNode()
        
        # TO DO
        
        return node