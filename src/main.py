import sys
import os
from View.Services import Services

def main():
    # HARDCODED!
    defaultDFAPath = "Repository/dfa.json"
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Mode 1 (Milestone 2 - Syntax only): python run.py <pascal_file.pas> [dfa_file.json]")
        print("  Mode 2 (Milestone 3 - With Semantics): python run.py -s <pascal_file.pas> [dfa_file.json]")
        print("  Mode 3 (Token file): python run.py <token_file.txt>")
        print("\nExamples:")
        print("  python run.py ../test/milestone-2/input/Program1.pas")
        print("  python run.py -s ../test/milestone-3/input/Program1.pas")
        print("  python run.py ../test/milestone-1/output/Program1.txt")
        return None
    
    # Cek apakah mode semantic analysis (-s flag)
    semanticMode = False
    if sys.argv[1] == '-s':
        semanticMode = True
        if len(sys.argv) < 3:
            print("Error: Pascal file required after -s flag")
            return None
        inputFilePath = sys.argv[2]
        dfaFilePath = sys.argv[3] if len(sys.argv) > 3 else defaultDFAPath
    else:
        inputFilePath = sys.argv[1]
        dfaFilePath = sys.argv[2] if len(sys.argv) > 2 else defaultDFAPath
    
    # Inisialisasi services
    services = Services()
    
    # Deteksi mode berdasarkan ekstensi file dan flag
    if inputFilePath.lower().endswith('.txt'):
        # Mode 3: Input dari token file (milestone 1)
        print(f"Mode: Reading tokens from file: {inputFilePath}")
        parseTree = services.processFileWithTokenInput(
            inputFilePath, 
            showParseTree=True, 
            saveOutput=True
        )
        return parseTree
    
    elif inputFilePath.lower().endswith('.pas'):
        if semanticMode:
            # Mode 2: Milestone 3 - Full pipeline dengan semantic analysis
            print(f"Mode: Processing Pascal file with semantic analysis: {inputFilePath}")
            decoratedAST = services.processFileWithSemantics(
                inputFilePath, 
                dfaFilePath, 
                showTokens=False,          # Set True untuk lihat tokens
                showParseTree=False,        # Set True untuk lihat parse tree
                showDecoratedAST=True,      # Tampilkan decorated AST
                showSymbolTables=True,      # Tampilkan symbol tables
                saveOutput=True             # Simpan output ke file
            )
            return decoratedAST
        else:
            # Mode 1: Milestone 2 - Syntax analysis only
            print(f"Mode: Processing Pascal file (syntax only): {inputFilePath}")
            parseTree = services.processFile(
                inputFilePath, 
                dfaFilePath, 
                showTokens=False, 
                showParseTree=True, 
                saveOutput=True
            )
            return parseTree
    
    else:
        print("Error: File harus berekstensi .pas atau .txt")
        return None
