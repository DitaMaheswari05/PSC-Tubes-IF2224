import sys
import os
from View.Services import Services

def main():
    # entry point program utama
    
    # Default file 
    # HARDCODED ! 
    defaultDFAPath = "Repository/dfa.json"
    pascalFilePath = sys.argv[1]
    dfaFilePath = sys.argv[2] if len(sys.argv) > 2 else defaultDFAPath
    # Inisialisasi services
    services = Services()
    token = services.processFile(pascalFilePath, dfaFilePath)   
    return token 
