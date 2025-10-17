from typing import List, Optional
from Model.Lexer import Lexer
from Model.DFA import DFA
from Model.Token import Token
from Repository.Parser import Parser

class Services: # kek class panggil func dari berbagai class
    def __init__(self):
        # dependencies
        self.parser = Parser()
        self.lexer: Optional[Lexer] = None
        self.dfa: Optional[DFA] = None
    
    def loadDFA(self, dfaFilePath: str) -> DFA:
        try:
            self.dfa = self.parser.parseDFA(dfaFilePath)
            return self.dfa
        except Exception as e:
            self.showErrorMessage(f"err: {str(e)}")
            raise
    
    def initializeLexer(self, dfaFilePath: str):
        if not self.dfa:
            self.loadDFA(dfaFilePath)
        self.lexer = Lexer(self.dfa)
    
    def loadPascalFile(self, filePath: str) -> str:
        try:
            with open(filePath, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            self.showErrorMessage(f"{filePath} gaada")
            raise
        except Exception as e:
            self.showErrorMessage(f"gabisa baca file {filePath}: {str(e)}")
            raise
    
    def validatePascalFilePath(self, filePath: str) -> bool: # karena harus .pas ye
        if not isinstance(filePath, str) or not filePath.lower().endswith('.pas'):
            self.showErrorMessage("File harus berekstensi .pas")
            return False
        
        try:
            with open(filePath, 'r', encoding='utf-8') as file:
                file.read(1)
            return True
        except FileNotFoundError:
            self.showErrorMessage("Gaada")
            return False
        except Exception as e:
            self.showErrorMessage(f"gabisa akses file: {str(e)}")
            return False
    
    def performLexicalAnalysis(self, sourceCode: str) -> List[Token]:
        # if not self.lexer:
        #     raise Exception("Lexer belum diinisialisasi. Panggil initializeLexer() terlebih dahulu")
        
        self.lexer.setSourceCode(sourceCode)
        tokens = self.lexer.tokenize()
        return tokens
    
    def displayTokens(self, tokens: List[Token]):
        # Menampilkan hasil tokenization
        for token in tokens:
            # Skip EOF token dalam output
            if token.getType().name != 'EOF':
                print(str(token))
    
    def processFile(self, pascalFilePath: str, dfaFilePath: str) -> List[Token]:
        # ### Main method untuk memproses file Pascal
        try:
            if not self.validatePascalFilePath(pascalFilePath):
                return []
            
            self.initializeLexer(dfaFilePath)
            sourceCode = self.loadPascalFile(pascalFilePath)
            tokens = self.performLexicalAnalysis(sourceCode)
            self.displayTokens(tokens)
            
            return tokens
            
        except Exception as e:
            self.showErrorMessage(f"err: {str(e)}")
            return []
    
    def showErrorMessage(self, message: str = "err"):
        # Menampilkan pesan error
        print(f"ERROR: {message}")