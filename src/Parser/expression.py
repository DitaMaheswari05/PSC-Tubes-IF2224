from Repository.TokenType import TokenType
from Parser.ast import *
from Parser.ErrorHandling import *

# function advance() udah ada di parser.py 
# sorry baru dibuat wkwkwk

class ExpressionParser:
    
    def __init__(self, parser):
        self.parser = parser
    
    def parse_expression(self) -> ExpressionNode:
        node = ExpressionNode()
        
        # simple-expression pertama
        node.add_child(self.parse_simple_expression())
        
        # cek apakah ada relational-operator
        if (self.parser.current_token and 
            self.parser.current_token.tokenType == TokenType.RELATIONAL_OPERATOR):
            # relational-operator
            node.add_child(self.parser.current_token)
            self.parser.advance()
            
            # simple-expression kedua
            node.add_child(self.parse_simple_expression()) 
        
        return node
    
    def parse_simple_expression(self) -> SimpleExpressionNode:
        node = SimpleExpressionNode()
        
        # (ARITHMETIC_OPERATOR(+/-))?  - unary operator
        if (self.parser.current_token and 
            self.parser.current_token.tokenType == TokenType.ARITHMETIC_OPERATOR and
            self.parser.current_token.value in ['+', '-']):
            node.add_child(self.parser.current_token)
            self.parser.advance()
        
        # term pertama
        node.add_child(self.parse_term())
        
        # (additive-operator term)*
        while (self.parser.current_token and 
               self.is_additive_operator(self.parser.current_token)):
            # additive-operator (+, -, atau)
            node.add_child(self.parser.current_token)
            self.parser.advance()
            
            # term
            node.add_child(self.parse_term())
        
        return node
    
    def parse_term(self) -> TermNode:
        node = TermNode()
        
        #  factor pertama
        node.add_child(self.parse_factor())
        
        # (multiplicative-operator factor)*
        while (self.parser.current_token and 
               self.is_multiplicative_operator(self.parser.current_token)):
            # multiplicative-operator (*, /, bagi, mod, dan)
            node.add_child(self.parser.current_token)
            self.parser.advance()
            
            # factor
            node.add_child(self.parse_factor())
        
        return node
    
    def parse_factor(self) -> FactorNode:
        node = FactorNode()
        
        if not self.parser.current_token:
            raise UnexpectedEOFError("factor")
        
        token = self.parser.current_token
        
        # NUMBER
        if token.tokenType == TokenType.NUMBER:
            node.add_child(token)
            self.parser.advance()
        
        # CHAR_LITERAL
        elif token.tokenType == TokenType.CHAR_LITERAL:
            node.add_child(token)
            self.parser.advance()
        
        # STRING_LITERAL
        elif token.tokenType == TokenType.STRING_LITERAL:
            node.add_child(token)
            self.parser.advance()
        
        # LOGICAL_OPERATOR(tidak) factor
        elif token.tokenType == TokenType.LOGICAL_OPERATOR and token.value == "tidak":
            node.add_child(token)
            self.parser.advance()
            node.add_child(self.parse_factor())
        
        # (LPARENTHESIS expression RPARENTHESIS)
        elif token.tokenType == TokenType.LPARENTHESIS:
            node.add_child(token)
            self.parser.advance()
            
            node.add_child(self.parse_expression())
            
            if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.RPARENTHESIS:
                raise UnexpectedTokenError(TokenType.RPARENTHESIS, self.parser.current_token)
            
            node.add_child(self.parser.current_token)
            self.parser.advance()
        
        # IDENTIFIER or function-call or KEYWORD (true/false)
        elif token.tokenType == TokenType.IDENTIFIER or token.tokenType == TokenType.KEYWORD:
            # Peek untuk cek apakah ini function call atau identifier biasa
            next_pos = self.parser.position + 1
            if (next_pos < len(self.parser.tokens) and 
                self.parser.tokens[next_pos].tokenType == TokenType.LPARENTHESIS):
                # Ini adalah function call
                node.add_child(self.parser.statement_parser.parse_call_statement(is_function=True))
            else:
                # Identifier biasa atau keyword (true/false)
                node.add_child(token)
                self.parser.advance()
        
        else:
            raise UnexpectedTokenError("factor", token, token.line, token.column)
        
        return node
    
    def is_additive_operator(self, token) -> bool:
        if token.tokenType == TokenType.ARITHMETIC_OPERATOR and token.value in ['+', '-']:
            return True
        if token.tokenType == TokenType.LOGICAL_OPERATOR and token.value == "atau":
            return True
        return False
    
    def is_multiplicative_operator(self, token) -> bool:
        if token.tokenType == TokenType.ARITHMETIC_OPERATOR:
            if token.value in ['*', '/'] or token.value in ['bagi', 'mod']:
                return True
        if token.tokenType == TokenType.LOGICAL_OPERATOR and token.value == "dan":
            return True
        return False
    
    def parse_parameter_list(self) -> ParameterListNode:
        node = ParameterListNode()
        
        #  expression pertama
        node.add_child(self.parse_expression())
        
        # (COMMA expression)*
        while self.parser.current_token and self.parser.current_token.tokenType == TokenType.COMMA:
            node.add_child(self.parser.current_token)
            self.parser.advance()
            
            node.add_child(self.parse_expression())
        
        return node