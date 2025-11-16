import sys
import os
from View.Services import Services

def main():
    # HARDCODED!
    defaultDFAPath = "Repository/dfa.json"
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Mode 1 (Pascal file): python run.py <pascal_file.pas> [dfa_file.json]")
        print("  Mode 2 (Token file):  python run.py <token_file.txt>")
        print("\nExamples:")
        print("  python run.py ../test/milestone-2/input/Program1.pas")
        print("  python run.py ../test/milestone-1/output/Program1.txt")
        return None
    
    inputFilePath = sys.argv[1]
    
    services = Services()
    
    # Deteksi mode berdasarkan ekstensi file
    if inputFilePath.lower().endswith('.txt'):
        # Mode 2: Input dari token file (milestone 1)
        print(f"Mode: Reading tokens from file: {inputFilePath}")
        parseTree = services.processFileWithTokenInput(
            inputFilePath, 
            showParseTree=True, 
            saveOutput=True
        )
    elif inputFilePath.lower().endswith('.pas'):
        # Mode 1: Input dari Pascal file (proses lengkap: lexer + parser)
        print(f"Mode: Processing Pascal file: {inputFilePath}")
        dfaFilePath = sys.argv[2] if len(sys.argv) > 2 else defaultDFAPath
        parseTree = services.processFile(
            inputFilePath, 
            dfaFilePath, 
            showTokens=False, 
            showParseTree=True, 
            saveOutput=True
        )
    else:
        print("Error: File harus berekstensi .pas atau .txt")
        return None
    
    
    if parseTree: 
        return parseTree
    else: 
        print("Gagal") # debug kalo gagal
        return None
