
from typing import List, Optional
from Model.Token import Token
from Model.DFA import DFA
from Repository.TokenType import TokenType

class Lexer:
    # lexical analyzer 
    def __init__(self, dfa: DFA):
        # DFA yang akan digunakan untuk identifikasi keyword dan transisi jika diperlukan
        self.dfa = dfa
        self.sourceCode = ""
        self.position = 0
        self.lineNumber = 1
        self.columnNumber = 1
        self.tokens: List[Token] = []
    
    def setSourceCode(self, sourceCode: str):
        self.sourceCode = sourceCode
        self.position = 0
        self.lineNumber = 1
        self.columnNumber = 1
        self.tokens = []
    
    def getCurrentChar(self) -> Optional[str]: # getter karakter sekarang
        if self.position >= len(self.sourceCode):
            return None
        return self.sourceCode[self.position]
    
    def peekNextChar(self) -> Optional[str]:
        nextPos = self.position + 1
        if nextPos >= len(self.sourceCode): # kalo lebih ya, gaada apa apa 
            return None
        return self.sourceCode[nextPos]
    
    def advance(self): # adv kek ADT mesin kata Struktur Data kmrn, // maju ke karakter berikutnya
        if self.position < len(self.sourceCode):
            if self.sourceCode[self.position] == '\n':
                self.lineNumber += 1
                self.columnNumber = 1
            else:
                self.columnNumber += 1
            self.position += 1
    
    def isNegativeNumber(self) -> bool: # ini ngecek apakah '-' itu beneran negative number, soalnya  baru tahap awal,
        # katanya harusnya ntar  ARITHMETIC_OPERATOR, tapi karena diQnA masih tahap awal, jadi masuk ke negatif
        # ntar ini dihapus tahap selanjutnya
        if self.getCurrentChar() != '-':
            return False
        
        nextChar = self.peekNextChar()
        if not nextChar or (not nextChar.isdigit() and nextChar != '.'):
            return False
        
        # Bilangan negatif biasanya muncul setelah: operator, delimiter, atau di awal
        if len(self.tokens) == 0:
            return True  # Di awal file
        
        lastToken = self.tokens[-1]
        # Negative number muncul setelah operator assignment, arithmetic, relational
        # atau setelah delimiter seperti '(', ',', dll
        if lastToken.tokenType in [
            TokenType.ASSIGN_OPERATOR,
            TokenType.ARITHMETIC_OPERATOR, 
            TokenType.RELATIONAL_OPERATOR,
            TokenType.LPARENTHESIS,
            TokenType.COMMA,
            TokenType.SEMICOLON,
            TokenType.COLON
        ]:
            return True
        
        return False
    
    def skipWhitespace(self): # Melewati whitespace (spasi, tab, newline, dll)
        while self.getCurrentChar() and self.getCurrentChar().isspace():
            self.advance()
        while self.getCurrentChar() and self.getCurrentChar().isspace():
            self.advance()
    
    def scanNumber(self, includeSign: bool = False) -> Token: #scan number token (dengan atau tanpa tanda negatif, termasuk scientific notation)
        startLine = self.lineNumber
        startColumn = self.columnNumber
        lexeme = ""
        
        if includeSign and self.getCurrentChar() == '-':
            lexeme += self.getCurrentChar()
            self.advance()
        
        while self.getCurrentChar() and self.getCurrentChar().isdigit():
            lexeme += self.getCurrentChar()
            self.advance()
        
        if self.getCurrentChar() == '.' and self.peekNextChar() and self.peekNextChar().isdigit():
            lexeme += self.getCurrentChar()  # add '.'
            self.advance()
            while self.getCurrentChar() and self.getCurrentChar().isdigit():
                lexeme += self.getCurrentChar()
                self.advance()
        
        if self.getCurrentChar() and self.getCurrentChar().lower() == 'e': # buat scientific notation
            lexeme += self.getCurrentChar()
            self.advance()
            if self.getCurrentChar() and self.getCurrentChar() in ['+', '-']:
                lexeme += self.getCurrentChar()
                self.advance()

            # evaluator : harus punya minimal satu digit setelah e/E
            if not self.getCurrentChar() or not self.getCurrentChar().isdigit():
                # error - invalid scientific notation, return UNKNOWN token
                return Token(TokenType.UNKNOWN, f"Malformed exponent in number: {lexeme}", startLine, startColumn)

            # scan digit setelah e/E
            while self.getCurrentChar() and self.getCurrentChar().isdigit():
                lexeme += self.getCurrentChar()
                self.advance()
        
        return Token(TokenType.NUMBER, lexeme, startLine, startColumn)
    
    def scanIdentifierOrKeyword(self) -> Token:
        startLine = self.lineNumber
        startColumn = self.columnNumber
        lexeme = ""
        
        while (self.getCurrentChar() and 
               (self.getCurrentChar().isalnum() or self.getCurrentChar() == '_')):
            lexeme += self.getCurrentChar()
            self.advance()
        
        # cek apakah ada compound keyword dengan dash (selain-itu, turun-ke)
        # peek untuk melihat apakah setelah identifier ada dash
        if self.getCurrentChar() == '-':
            # simpan posisi sekarang untuk bisa rollback jika bukan compound keyword
            savedPosition = self.position
            savedLine = self.lineNumber
            savedColumn = self.columnNumber
            
            # consume dash
            tempLexeme = lexeme + '-'
            self.advance()
            
            # scan bagian kedua setelah dash
            secondPart = ""
            while (self.getCurrentChar() and 
                   (self.getCurrentChar().isalnum() or self.getCurrentChar() == '_')):
                secondPart += self.getCurrentChar()
                self.advance()
            
            # cek apakah lexeme-secondPart adalah keyword di DFA
            compoundLexeme = tempLexeme + secondPart
            if self.dfa.isKeyword(compoundLexeme):
                # ini compound keyword, return sebagai KEYWORD
                return Token(TokenType.KEYWORD, compoundLexeme, startLine, startColumn)
            else:
                # bukan compound keyword, rollback ke posisi sebelum dash
                self.position = savedPosition
                self.lineNumber = savedLine
                self.columnNumber = savedColumn
        
        # keyword atau identifier
        # cek apakah ini keyword yang punya special token type
        if self.dfa.isKeyword(lexeme):
            # cek di reserved_words untuk special token type
            reserved_type = self.dfa.getReservedWordType(lexeme)
            if reserved_type:
                return Token(reserved_type, lexeme, startLine, startColumn)
            else:
                return Token(TokenType.KEYWORD, lexeme, startLine, startColumn)
        else:
            return Token(TokenType.IDENTIFIER, lexeme, startLine, startColumn)
    
    def scanStringLiteral(self) -> Token:
        startLine = self.lineNumber
        startColumn = self.columnNumber
        lexeme = ""
        opening = self.getCurrentChar()
        # skip opening tanda kutip
        self.advance()

        escaped = False
        while self.getCurrentChar():
            ch = self.getCurrentChar()
            if escaped:
                lexeme += ch
                escaped = False
                self.advance()
                continue

            if ch == '\\':
                escaped = True
                self.advance()
                continue

            if ch == opening:
                # akhir tanda kutip
                self.advance()
                return Token(TokenType.STRING_LITERAL, opening + lexeme + opening, startLine, startColumn)

            # # error handling newline
            # if ch == '\n':
            #     return Token(TokenType.LEXICAL_ERROR, f"Unterminated string literal at line {startLine} col {startColumn}", startLine, startColumn)

            lexeme += ch
            self.advance()

        # error (tapi disable dulu)
        # kalo dah EOF tapi belom ketemu closing quote
        # return Token(TokenType.LEXICAL_ERROR, f"Unterminated string literal at line {startLine} col {startColumn}", startLine, startColumn)
    
    def scanCharLiteral(self) -> Token:
        startLine = self.lineNumber
        startColumn = self.columnNumber
        opening = self.getCurrentChar()

        self.advance()
        char = self.getCurrentChar() if self.getCurrentChar() else ''
        if char:
            self.advance()  # skip char
        if self.getCurrentChar() == opening:
            self.advance()
            return Token(TokenType.CHAR_LITERAL, opening + char + opening, startLine, startColumn)

        # err tapi disable dulu
        # kalo dah EOF tapi char belom ketemu closing quote
        # return Token(TokenType.LEXICAL_ERROR, f"Unterminated char literal at line {startLine} col {startColumn}", startLine, startColumn)
    
    def scanComment(self) -> Optional[Token]:
        currentChar = self.getCurrentChar()
        
        if currentChar == '{':
            self.advance()
            while self.getCurrentChar() and self.getCurrentChar() != '}':
                self.advance()
            if self.getCurrentChar() == '}':
                self.advance()
        elif currentChar == '(' and self.peekNextChar() == '*':
            # Comment style: (* ... *)
            self.advance()  # skip (
            self.advance()  # skip *
            while self.getCurrentChar():
                if (self.getCurrentChar() == '*' and 
                    self.peekNextChar() == ')'):
                    self.advance()  # skip *
                    self.advance()  # skip )
                    break
                self.advance() 
        
        return None  # gabakal jadi token
    
    def scanOperator(self) -> Token:
        startLine = self.lineNumber
        startColumn = self.columnNumber
        currentChar = self.getCurrentChar()
        
        if currentChar == ':' and self.peekNextChar() == '=':
            self.advance()
            self.advance()
            return Token(TokenType.ASSIGN_OPERATOR, ':=', startLine, startColumn)
        elif currentChar == '<' and self.peekNextChar() == '>':
            self.advance()
            self.advance()
            return Token(TokenType.RELATIONAL_OPERATOR, '<>', startLine, startColumn)
        elif currentChar == '<' and self.peekNextChar() == '=':
            self.advance()
            self.advance()
            return Token(TokenType.RELATIONAL_OPERATOR, '<=', startLine, startColumn)
        elif currentChar == '>' and self.peekNextChar() == '=':
            self.advance()
            self.advance()
            return Token(TokenType.RELATIONAL_OPERATOR, '>=', startLine, startColumn)
        elif currentChar == '.' and self.peekNextChar() == '.':
            self.advance()
            self.advance()
            return Token(TokenType.RANGE_OPERATOR, '..', startLine, startColumn)
        
        self.advance()
        
        if currentChar in '+-*/':
            return Token(TokenType.ARITHMETIC_OPERATOR, currentChar, startLine, startColumn)
        elif currentChar in '=<>':
            return Token(TokenType.RELATIONAL_OPERATOR, currentChar, startLine, startColumn)
        elif currentChar == ';':
            return Token(TokenType.SEMICOLON, currentChar, startLine, startColumn)
        elif currentChar == ',':
            return Token(TokenType.COMMA, currentChar, startLine, startColumn)
        elif currentChar == ':':
            return Token(TokenType.COLON, currentChar, startLine, startColumn)
        elif currentChar == '.':
            return Token(TokenType.DOT, currentChar, startLine, startColumn)
        elif currentChar == '(':
            return Token(TokenType.LPARENTHESIS, currentChar, startLine, startColumn)
        elif currentChar == ')':
            return Token(TokenType.RPARENTHESIS, currentChar, startLine, startColumn)
        elif currentChar == '[':
            return Token(TokenType.LBRACKET, currentChar, startLine, startColumn)
        elif currentChar == ']':
            return Token(TokenType.RBRACKET, currentChar, startLine, startColumn)
        else:
            return Token(TokenType.UNKNOWN, currentChar, startLine, startColumn)
    
    def tokenize(self) -> List[Token]:
        # Main method 
        self.tokens = []

        while self.position < len(self.sourceCode):
            self.skipWhitespace()

            currentChar = self.getCurrentChar()
            if not currentChar:
                break

            if currentChar.isdigit():
                token = self.scanNumber()
                self.tokens.append(token)
            elif currentChar in ['+', '-'] and self.peekNextChar() and (self.peekNextChar().isdigit() or self.peekNextChar() == '.'):
                token = self.scanNumber(includeSign=True)
                self.tokens.append(token)
            elif currentChar.isalpha() or currentChar == '_':
                token = self.scanIdentifierOrKeyword()
                self.tokens.append(token)
            elif currentChar in ("'", '"'):
                opening = currentChar
                nextPos = self.position + 1
                charCount = 0
                tempPos = nextPos
                while (tempPos < len(self.sourceCode) and 
                       self.sourceCode[tempPos] != opening):
                    charCount += 1
                    tempPos += 1

                if charCount == 1:
                    token = self.scanCharLiteral()
                else:
                    token = self.scanStringLiteral()
                self.tokens.append(token)
            elif currentChar == '{' or (currentChar == '(' and self.peekNextChar() == '*'):
                self.scanComment()
            else:
                token = self.scanOperator()
                self.tokens.append(token)

        self.tokens.append(Token(TokenType.EOF, '', self.lineNumber, self.columnNumber))
        return self.tokens
    
    def getTokens(self) -> List[Token]:
        return self.tokens 