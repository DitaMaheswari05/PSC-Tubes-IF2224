import sys
import os
from View.Services import Services

def main():
    # HARDCODED!
    defaultDFAPath = "Repository/dfa.json"
    if len(sys.argv) < 2:
        print("Usage: python main.py <pascal_file.pas> [dfa_file.json]")
        print("Example: python main.py ../test/milestone-2/input/Program1.pas")
        return None
    
    pascalFilePath = sys.argv[1]
    dfaFilePath = sys.argv[2] if len(sys.argv) > 2 else defaultDFAPath
    
    # Inisialisasi services --> antarmuka user
    services = Services()
    # Proses file Pascal: lexical analysis + syntax analysis
    # showTokens=False untuk tidak menampilkan token (fokus ke parse tree)
    # showParseTree=True untuk menampilkan parse tree
    # kalo true semua, semuanya ditampilin
    parseTree = services.processFile(pascalFilePath, dfaFilePath, showTokens=False, showParseTree=True, saveOutput=True) # fokus ke parse tree 
    if parseTree: 
        return parseTree
    else: 
        print("Gagal") # debug kalo gagal
        return None
