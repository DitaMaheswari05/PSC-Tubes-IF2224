from Repository.TokenType import TokenType
from Parser.ast import *
from Parser.ErrorHandling import *

class StatementParser:
    # statementparser
    
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
       # compound-statement --> KEYWORD(mulai) statement-list KEYWORD(selesai)
        node = CompoundStatementNode()
        
        # 1. KEYWORD(mulai)
        node.add_child(self._consume(TokenType.KEYWORD, 'mulai'))
        # 2. statement-list
        node.add_child(self.parse_statement_list())
        # 3. KEYWORD(selesai)
        node.add_child(self._consume(TokenType.KEYWORD, 'selesai'))
        
        return node
    
    def parse_statement_list(self) -> StatementListNode:
        # statement-list → statement (SEMICOLON statement)*
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
        # statement → assignment-statement | if-statement | while-statement | for-statement | compound-statement | call-statement | empty-statement
        if not self.parser.current_token:
            return None # End of file

        token = self.parser.current_token
        
        # 1. Dispatcher berdasarkan IDENTIFIER
        if token.getType() == TokenType.IDENTIFIER:
            next_token = self._peek_token()
            
            # 1a. assignment-statement → IDENTIFIER ASSIGN_OPERATOR ...
            # atau record/array assignment → IDENTIFIER DOT/LBRACKET ...
            if (next_token and 
                (next_token.getType() == TokenType.ASSIGN_OPERATOR or
                 next_token.getType() == TokenType.DOT or
                 next_token.getType() == TokenType.LBRACKET)):
                return self.parse_assignment_statement()
            
            # 1b. call-statement → IDENTIFIER LPARENTHESIS ...
            # Sesuai revisi 3[cite: 32], kurung wajib ada
            elif next_token and next_token.getType() == TokenType.LPARENTHESIS:
                # Dipanggil dari statement, berarti ini procedure call
                return self.parse_call_statement(is_function=False)
            
            else:
                raise SyntaxError(f"Unexpected token after IDENTIFIER '{token.getValue()}'. Expected ':=', '.', '[', or '(', got {next_token.getValue() if next_token else 'None'}")
        
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
            elif value == 'ulangi':
                return self.parse_repeat_statement()
            elif value == 'kasus':
                return self.parse_case_statement()
            # writeln adalah built-in procedure call [cite: 229]
            elif value == 'writeln': 
                return self.parse_call_statement(is_function=False)
                
        # Empty statement
        return None
    
    def parse_assignment_statement(self) -> AssignmentStatementNode:
        # assignment-statement → IDENTIFIER ASSIGN_OPERATOR(:=) expression
        # atau record-field-assignment → IDENTIFIER (DOT IDENTIFIER)+ ASSIGN_OPERATOR(:=) expression
        # atau array-assignment → IDENTIFIER LBRACKET expression RBRACKET ASSIGN_OPERATOR(:=) expression
        node = AssignmentStatementNode()
        
        # 1. IDENTIFIER pertama
        node.add_child(self._consume(TokenType.IDENTIFIER))
        
        # cek apakah ada DOT untuk record field access atau LBRACKET untuk array access
        while (self.parser.current_token and 
               (self.parser.current_token.tokenType == TokenType.DOT or
                self.parser.current_token.tokenType == TokenType.LBRACKET)):
            if self.parser.current_token.tokenType == TokenType.DOT:
                # record field access (identifier.field)
                # consume DOT
                node.add_child(self.parser.current_token)
                self.parser.advance()
                
                # expect IDENTIFIER untuk field name
                if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.IDENTIFIER:
                    raise UnexpectedTokenError(TokenType.IDENTIFIER, self.parser.current_token)
                
                # consume field IDENTIFIER
                node.add_child(self.parser.current_token)
                self.parser.advance()
            elif self.parser.current_token.tokenType == TokenType.LBRACKET:
                # array access (identifier[expression])
                # consume LBRACKET
                node.add_child(self.parser.current_token)
                self.parser.advance()
                
                # parse expression untuk index
                node.add_child(self.parser.expression_parser.parse_expression())
                
                # expect RBRACKET
                if not self.parser.current_token or self.parser.current_token.tokenType != TokenType.RBRACKET:
                    raise UnexpectedTokenError(TokenType.RBRACKET, self.parser.current_token)
                
                # consume RBRACKET
                node.add_child(self.parser.current_token)
                self.parser.advance()
                
                # setelah array access, bisa ada field access lagi (untuk array of records)
                # atau langsung assignment
                break
        
        # 2. ASSIGN_OPERATOR (:=)
        node.add_child(self._consume(TokenType.ASSIGN_OPERATOR))
        # 3. expression (Panggil parser rekan Anda)
        node.add_child(self.parser.expression_parser.parse_expression())
        
        return node
    
    def parse_if_statement(self) -> IfStatementNode:
        # if-statement → KEYWORD(jika) expression KEYWORD(maka) statement
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
        # while-statement → KEYWORD(selama) expression KEYWORD(lakukan) statement
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
        # for-statement → KEYWORD(untuk) IDENTIFIER ASSIGN_OPERATOR expression (KEYWORD(ke)/KEYWORD(turun-ke)) expression KEYWORD(lakukan) statement
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
        # call-statement → (procedure-call | function-call) 
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
        # parameter-list → expression (COMMA expression)*
        node = ParameterListNode()
        
        # 1. expression (pertama, wajib ada)
        node.add_child(self.parser.expression_parser.parse_expression())
        
        # 2. (COMMA expression)*
        while self.parser.current_token and self.parser.current_token.getType() == TokenType.COMMA:
            node.add_child(self._consume(TokenType.COMMA))
            node.add_child(self.parser.expression_parser.parse_expression())
            
        return node
    
    def parse_repeat_statement(self) -> RepeatStatementNode:
        # repeat-statement → KEYWORD(ulangi) statement-list KEYWORD(sampai) expression
        node = RepeatStatementNode()
        
        # 1. KEYWORD(ulangi)
        node.add_child(self._consume(TokenType.KEYWORD, 'ulangi'))
        # 2. statement-list
        node.add_child(self.parse_statement_list())
        # 3. KEYWORD(sampai)
        node.add_child(self._consume(TokenType.KEYWORD, 'sampai'))
        # 4. expression (kondisi berhenti)
        node.add_child(self.parser.expression_parser.parse_expression())
        
        return node
    
    def parse_case_statement(self) -> CaseStatementNode:
        # case-statement → KEYWORD(kasus) expression KEYWORD(dari) case-element (SEMICOLON case-element)* KEYWORD(selesai)
        node = CaseStatementNode()
        
        # 1. KEYWORD(kasus)
        node.add_child(self._consume(TokenType.KEYWORD, 'kasus'))
        # 2. expression (selector)
        node.add_child(self.parser.expression_parser.parse_expression())
        # 3. KEYWORD(dari)
        node.add_child(self._consume(TokenType.KEYWORD, 'dari'))
        # 4. case-element pertama
        node.add_child(self.parse_case_element())
        # 5. (SEMICOLON case-element)*
        while self.parser.current_token and self.parser.current_token.getType() == TokenType.SEMICOLON:
            # Cek untuk trailing semicolon sebelum 'selesai'
            if self.parser.current_token and \
               self.parser.position + 1 < len(self.parser.tokens) and \
               self.parser.tokens[self.parser.position + 1].getValue() == 'selesai':
                node.add_child(self._consume(TokenType.SEMICOLON))
                break
            
            node.add_child(self._consume(TokenType.SEMICOLON))
            node.add_child(self.parse_case_element())
        # 6. KEYWORD(selesai)
        node.add_child(self._consume(TokenType.KEYWORD, 'selesai'))
        
        return node
    
    def parse_case_element(self) -> CaseElementNode:
        # case-element → case-label-list COLON statement
        node = CaseElementNode()
        
        # 1. case-label-list
        node.add_child(self.parse_case_label_list())
        # 2. COLON
        node.add_child(self._consume(TokenType.COLON))
        # 3. statement
        node.add_child(self.parse_statement())
        
        return node
    
    def parse_case_label_list(self) -> CaseLabelListNode:
        # case-label-list → constant (COMMA constant)*
        node = CaseLabelListNode()
        
        # 1. constant pertama (bisa NUMBER, CHAR_LITERAL, atau IDENTIFIER)
        if not self.parser.current_token:
            raise SyntaxError("Unexpected end of file in case label")
        
        if self.parser.current_token.getType() in [TokenType.NUMBER, TokenType.CHAR_LITERAL, TokenType.IDENTIFIER]:
            node.add_child(self.parser.current_token)
            self.parser.advance()
        else:
            raise SyntaxError(f"Expected constant in case label, got {self.parser.current_token.getType()}")
        
        # 2. (COMMA constant)*
        while self.parser.current_token and self.parser.current_token.getType() == TokenType.COMMA:
            node.add_child(self._consume(TokenType.COMMA))
            
            if not self.parser.current_token:
                raise SyntaxError("Unexpected end of file after comma in case label")
            
            if self.parser.current_token.getType() in [TokenType.NUMBER, TokenType.CHAR_LITERAL, TokenType.IDENTIFIER]:
                node.add_child(self.parser.current_token)
                self.parser.advance()
            else:
                raise SyntaxError(f"Expected constant in case label, got {self.parser.current_token.getType()}")
        
        return node