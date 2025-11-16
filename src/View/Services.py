from typing import List, Optional
from Model.Lexer import Lexer
from Model.DFA import DFA
from Model.Token import Token
from Repository.Parser import Parser as DFAParser
from Parser.parser import SyntaxParser
from Parser.ast import ProgramNode
from Repository.TokenType import TokenType
import os

class Services: # kek class panggil func dari berbagai class
    def __init__(self):
        # dependencies
        self.dfaParser = DFAParser()  # Renamed untuk membedakan dengan syntax parser
        self.lexer: Optional[Lexer] = None
        self.dfa: Optional[DFA] = None
    
    def loadDFA(self, dfaFilePath: str) -> DFA:
        try:
            # Parse DFA menggunakan DFAParser
            self.dfa = self.dfaParser.parseDFA(dfaFilePath)
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
    
    def performLexicalAnalysis(self, sourceCode: str) -> List[Token]:  # 
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
    
    def performSyntaxAnalysis(self, tokens: List[Token]) -> Optional[ProgramNode]:
        # melakukan syntax analysis dengan memanggil parser (dri Parser/parser.py) 
        # Input: list of tokens dari lexer
        # Output: ProgramNode (root dari parse tree) 
        # driver syntax parser
        try:
            syntaxParser = SyntaxParser(tokens) # instance
            parseTree = syntaxParser.parse() # parse program, dapetin parse tree
            return parseTree
        except Exception as e:
            self.showErrorMessage(f"Syntax error: {str(e)}")
            return None
    
    def displayParseTree(self, parseTree: ProgramNode):
        # antar muka user untuk nampilin parse tree 
        if parseTree:
            print("\n=== Parse Tree ===")
            # handle encoding error untuk unicode box drawing characters
            try:
                print(parseTree.to_string())
            except UnicodeEncodeError:
                # fallback: encode dengan errors='replace' untuk avoid crash
                tree_string = parseTree.to_string()
                print(tree_string.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
        else:
            print("Parse tree kosong!")
    
    def saveParseTreeToFile(self, parseTree: ProgramNode, inputFilePath: str):
        try:
            outputDir = "../test/milestone-2/output"
            os.makedirs(outputDir, exist_ok=True)
            
            # Dapatkan nama file dari path input
            inputFileName = os.path.basename(inputFilePath)
            # Ganti ekstensi .pas dengan .txt
            outputFileName = os.path.splitext(inputFileName)[0] + ".txt"
            outputFilePath = os.path.join(outputDir, outputFileName)
            
            # Tulis parse tree ke file
            with open(outputFilePath, 'w', encoding='utf-8') as f:
                if parseTree:
                    f.write("=== Parse Tree ===\n")
                    f.write(parseTree.to_string())
                else:
                    f.write("Parse tree kosong!\n")
            
            print(f"\nParse tree berhasil disimpan ke: {outputFilePath}")
        
        except Exception as e:
            self.showErrorMessage(f"Gagal menyimpan parse tree: {str(e)}")
    
    def processFile(self, pascalFilePath: str, dfaFilePath: str, showTokens: bool = False, showParseTree: bool = True, saveOutput: bool = True) -> Optional[ProgramNode]:
        # MAIN METHOD KESELURUHAN, yang bakal dipanggil di entry point main.py
        try:
            if not self.validatePascalFilePath(pascalFilePath):
                return None
            self.initializeLexer(dfaFilePath)
            sourceCode = self.loadPascalFile(pascalFilePath)
            tokens = self.performLexicalAnalysis(sourceCode)
            
            # kalo showTokens True
            if showTokens:
                print("\n=== Tokens ===")
                self.displayTokens(tokens)
            
            # Syntax analysis
            parseTree = self.performSyntaxAnalysis(tokens)
            # kalo showParseTree True (defaultnya secara spek sih true)
            if showParseTree and parseTree:
                self.displayParseTree(parseTree)
            
            # Simpan output
            if saveOutput and parseTree:
                self.saveParseTreeToFile(parseTree, pascalFilePath)
            
            return parseTree
            
        except Exception as e:
            self.showErrorMessage(f"err: {str(e)}")
            return None
    def showErrorMessage(self, message: str = "err"):
        # Menampilkan pesan error
        print(f"ERROR: {message}")
    
    def loadTokensFromFile(self, tokenFilePath: str) -> List[Token]:
        # Membaca hasil tokenisasi dari output milestone-1 (.txt)
        try:
            with open(tokenFilePath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            tokens = []
            for line in lines:
                line = line.strip()
                if not line or line.startswith('==='):  # Skip empty lines dan headers
                    continue
                
                # Parse format: TYPE(value) atau TYPE
                token = self.parseTokenFromString(line)
                if token:
                    tokens.append(token)
            
            return tokens
        
        except FileNotFoundError:
            self.showErrorMessage(f"File token {tokenFilePath} tidak ditemukan")
            raise
        except Exception as e:
            self.showErrorMessage(f"Gagal membaca file token {tokenFilePath}: {str(e)}")
            raise

    def parseTokenFromString(self, tokenString: str) -> Optional[Token]:
        # Parse string token format 'TYPE(value)' atau 'TYPE' menjadi objek Token
        try:
            # Contoh format: KEYWORD(program), IDENTIFIER, dll
            if '(' in tokenString and ')' in tokenString:
                # Format: TYPE(value)
                type_part = tokenString[:tokenString.index('(')]
                value_part = tokenString[tokenString.index('(')+1:tokenString.rindex(')')]
            else:
                # Format: TYPE (tanpa value)
                type_part = tokenString
                value_part = None
            
            # Convert string ke TokenType enum
            try:
                token_type = TokenType[type_part]
            except KeyError:
                self.showErrorMessage(f"Unknown token type: {type_part}")
                return None
            
            # Asumsi: Token(tokenType, value, line, column)
            return Token(token_type, value_part, 0, 0)
        
        except Exception as e:
            self.showErrorMessage(f"Gagal parsing token string '{tokenString}': {str(e)}")
            return None

    def processFileWithTokenInput(self, tokenFilePath: str, showParseTree: bool = True, saveOutput: bool = True) -> Optional[ProgramNode]:
        # Proses file menggunakan token file (.txt) dari milestone 1
        try:
            # Load tokens dari file
            tokens = self.loadTokensFromFile(tokenFilePath)
            
            if not tokens:
                self.showErrorMessage("Tidak ada token yang berhasil di-load")
                return None
            
            print(f"\n{len(tokens)} tokens berhasil di-load dari {tokenFilePath}")
            
            # Syntax analysis
            parseTree = self.performSyntaxAnalysis(tokens)
            
            # Display parse tree
            if showParseTree and parseTree:
                self.displayParseTree(parseTree)
            
            # Save output
            if saveOutput and parseTree:
                self.saveParseTreeToFile(parseTree, tokenFilePath)
            
            return parseTree
            
        except Exception as e:
            self.showErrorMessage(f"Error processing token file: {str(e)}")
            return None