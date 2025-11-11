from Repository.TokenType import TokenType
from Parser.ast import *
from Parser.ErrorHandling import *

class StatementParser:
    """Parser untuk statements"""
    
    def __init__(self, parser):
        self.parser = parser
    
    # Helper Methods

    def _consume(self, expected_type: TokenType, expected_value: str = None) -> Token:
        #Memeriksa token saat ini, mengonsumsinya (advance), dan mengembalikannya. Akan raise error jika token tidak sesuai.
        token = self.parser.current_token
        
        if token is None:
            raise SyntaxError(f"Unexpected end of file. Expected {expected_type}")
            
        if token.getType() != expected_type:
            raise SyntaxError(f"Unexpected token type. Expected {expected_type}, got {token.getType()} ({token.getValue()})")
            
        if expected_value is not None and token.getValue() != expected_value:
            raise SyntaxError(f"Unexpected token value. Expected '{expected_value}', got '{token.getValue()}'")
            
        self.parser.advance()
        return token

    def _peek_token(self) -> Token | None:
        # Melihat token berikutnya tanpa mengonsumsinya. Penting untuk membedakan assignment vs procedure call.
        next_position = self.parser.position + 1
        if next_position < len(self.parser.tokens):
            return self.parser.tokens[next_position]
        return None
    
    # Parsing Methods
    def parse_compound_statement(self) -> CompoundStatementNode:
        """
        compound-statement → KEYWORD(mulai) statement-list KEYWORD(selesai)
        """
        node = CompoundStatementNode()
        
        # 1. KEYWORD(mulai)
        node.add_child(self._consume(TokenType.KEYWORD, 'mulai'))
        # 2. statement-list
        node.add_child(self.parse_statement_list())
        # 3. KEYWORD(selesai)
        node.add_child(self._consume(TokenType.KEYWORD, 'selesai'))
        
        return node
    
    def parse_statement_list(self) -> StatementListNode:
        """
        statement-list → statement (SEMICOLON statement)*
        """
        node = StatementListNode()
        
        # 1. statement (pertama, wajib ada)
        node.add_child(self.parse_statement())
        # 2. (SEMICOLON statement)*
        while self.parser.current_token and self.parser.current_token.getType() == TokenType.SEMICOLON:
            semicolon_token = self._consume(TokenType.SEMICOLON)
            
            # Cek untuk trailing semicolon (e.g., ... ; selesai.)
            # Jika token berikutnya adalah 'selesai' atau 'sampai',
            # berarti ini adalah semicolon terakhir.
            if self.parser.current_token and self.parser.current_token.getValue() in ['selesai', 'sampai']:
                node.add_child(semicolon_token)
                break
                
            node.add_child(semicolon_token)
            node.add_child(self.parse_statement())
        
        return node
    
    def parse_statement(self):
        """
        statement → assignment-statement | if-statement | while-statement |
                   for-statement | compound-statement | call-statement | empty
        """
        if not self.parser.current_token:
            return None # End of file

        token = self.parser.current_token
        
        # 1. Dispatcher berdasarkan IDENTIFIER
        if token.getType() == TokenType.IDENTIFIER:
            next_token = self._peek_token()
            
            # 1a. assignment-statement → IDENTIFIER ASSIGN_OPERATOR ...
            if next_token and next_token.getType() == TokenType.ASSIGN_OPERATOR:
                return self.parse_assignment_statement()
            
            # 1b. call-statement → IDENTIFIER LPARENTHESIS ...
            # Sesuai revisi 3[cite: 32], kurung wajib ada
            elif next_token and next_token.getType() == TokenType.LPARENTHESIS:
                # Dipanggil dari statement, berarti ini procedure call
                return self.parse_call_statement(is_function=False)
            
            else:
                raise SyntaxError(f"Unexpected token after IDENTIFIER '{token.getValue()}'. Expected ':=' or '(', got {next_token.getValue() if next_token else 'None'}")
        
        # 2. Dispatcher berdasarkan KEYWORD
        elif token.getType() == TokenType.KEYWORD:
            value = token.getValue()
            
            if value == 'mulai':
                return self.parse_compound_statement()
            elif value == 'jika':
                return self.parse_if_statement()
            elif value == 'selama':
                return self.parse_while_statement()
            elif value == 'untuk':
                return self.parse_for_statement()
            # writeln adalah built-in procedure call [cite: 229]
            elif value == 'writeln': 
                return self.parse_call_statement(is_function=False)
                
        # Empty statement
        return None
    
    def parse_assignment_statement(self) -> AssignmentStatementNode:
        """
        assignment-statement → IDENTIFIER ASSIGN_OPERATOR(:=) expression
        """
        node = AssignmentStatementNode()
        
        # 1. IDENTIFIER
        node.add_child(self._consume(TokenType.IDENTIFIER))
        # 2. ASSIGN_OPERATOR (:=)
        node.add_child(self._consume(TokenType.ASSIGN_OPERATOR))
        # 3. expression (Panggil parser rekan Anda)
        node.add_child(self.parser.expression_parser.parse_expression())
        
        return node
    
    def parse_if_statement(self) -> IfStatementNode:
        """
        if-statement → KEYWORD(jika) expression KEYWORD(maka) statement 
                      (KEYWORD(selain-itu) statement)?
        """
        node = IfStatementNode()
        
        # 1. KEYWORD(jika)
        node.add_child(self._consume(TokenType.KEYWORD, 'jika'))
        # 2. expression
        node.add_child(self.parser.expression_parser.parse_expression())
        # 3. KEYWORD(maka)
        node.add_child(self._consume(TokenType.KEYWORD, 'maka'))
        # 4. statement
        node.add_child(self.parse_statement())
        # 5. (KEYWORD(selain-itu) statement)? (Opsional)
        if self.parser.current_token and self.parser.current_token.getValue() == 'selain-itu':
            node.add_child(self._consume(TokenType.KEYWORD, 'selain-itu'))
            node.add_child(self.parse_statement())
        
        return node
    
    def parse_while_statement(self) -> WhileStatementNode:
        """
        while-statement → KEYWORD(selama) expression KEYWORD(lakukan) statement
        """
        node = WhileStatementNode()
        
        # 1. KEYWORD(selama)
        node.add_child(self._consume(TokenType.KEYWORD, 'selama'))
        # 2. expression
        node.add_child(self.parser.expression_parser.parse_expression())
        # 3. KEYWORD(lakukan)
        node.add_child(self._consume(TokenType.KEYWORD, 'lakukan'))
        # 4. statement
        node.add_child(self.parse_statement())
        
        return node
    
    def parse_for_statement(self) -> ForStatementNode:
        """
        for-statement → KEYWORD(untuk) IDENTIFIER ASSIGN_OPERATOR expression 
                       (KEYWORD(ke)/KEYWORD(turun-ke)) expression 
                       KEYWORD(lakukan) statement
        """
        node = ForStatementNode()
        
        # 1. KEYWORD(untuk)
        node.add_child(self._consume(TokenType.KEYWORD, 'untuk'))
        # 2. IDENTIFIER
        node.add_child(self._consume(TokenType.IDENTIFIER))
        # 3. ASSIGN_OPERATOR
        node.add_child(self._consume(TokenType.ASSIGN_OPERATOR))
        # 4. expression (start value)
        node.add_child(self.parser.expression_parser.parse_expression())
        # 5. (KEYWORD(ke)/KEYWORD(turun-ke))
        if self.parser.current_token and self.parser.current_token.getValue() == 'ke':
            node.add_child(self._consume(TokenType.KEYWORD, 'ke'))
        elif self.parser.current_token and self.parser.current_token.getValue() == 'turun-ke':
            node.add_child(self._consume(TokenType.KEYWORD, 'turun-ke'))
        else:
            raise SyntaxError("Expected 'ke' or 'turun-ke' in for loop") 
        # 6. expression (end value)
        node.add_child(self.parser.expression_parser.parse_expression())
        # 7. KEYWORD(lakukan)
        node.add_child(self._consume(TokenType.KEYWORD, 'lakukan'))
        # 8. statement
        node.add_child(self.parse_statement())
        
        return node
    
    def parse_call_statement(self, is_function=False) -> CallStatementNode:
        """
        call-statement → IDENTIFIER (LPARENTHESIS parameter-list RPARENTHESIS)?
        
        Args:
            is_function: True jika dipanggil sebagai function call, False untuk procedure call
        """
        node = CallStatementNode(is_function=is_function)
        
        # 1. IDENTIFIER (atau KEYWORD untuk built-in seperti 'writeln')
        if self.parser.current_token.getType() == TokenType.IDENTIFIER:
            node.add_child(self._consume(TokenType.IDENTIFIER))
        elif self.parser.current_token.getType() == TokenType.KEYWORD:
             # Hanya izinkan keyword yg valid sbg procedure, e.g., writeln
            if self.parser.current_token.getValue() == 'writeln':
                 node.add_child(self._consume(TokenType.KEYWORD, 'writeln'))
            else:
                raise SyntaxError(f"Unexpected KEYWORD '{self.parser.current_token.getValue()}' as procedure name")
        else:
            raise SyntaxError(f"Expected IDENTIFIER or KEYWORD for procedure name, got {self.parser.current_token.getType()}")
        # 2. LPARENTHESIS
        node.add_child(self._consume(TokenType.LPARENTHESIS))
        # 3. parameter-list (Opsional)
        # Jika token berikutnya BUKAN ')' berarti ada parameter
        if self.parser.current_token and self.parser.current_token.getType() != TokenType.RPARENTHESIS:
            node.add_child(self.parse_parameter_list())    
        # 4. RPARENTHESIS
        node.add_child(self._consume(TokenType.RPARENTHESIS))
        
        return node
    
    # Helper method untuk parse parameter list
    def parse_parameter_list(self) -> ParameterListNode:
        """
        Mengurai parameter aktual (untuk pemanggilan fungsi/prosedur)
        parameter-list → expression (COMMA expression)*
        """
        node = ParameterListNode()
        
        # 1. expression (pertama, wajib ada)
        node.add_child(self.parser.expression_parser.parse_expression())
        
        # 2. (COMMA expression)*
        while self.parser.current_token and self.parser.current_token.getType() == TokenType.COMMA:
            node.add_child(self._consume(TokenType.COMMA))
            node.add_child(self.parser.expression_parser.parse_expression())
            
        return node