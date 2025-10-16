import sys
import os
from dfa import DFASpec
from lexer import Lexer

def main():
    # Fungsi utama untuk menjalankan lexer dari command line
    if len(sys.argv) != 2:
        print("Usage: python compiler.py <source.pas>")
        sys.exit(1)

    src_path = sys.argv[1]
    if not os.path.exists(src_path):
        print(f"File not found: {src_path}")
        sys.exit(1)

    # Tentukan path ke dfa.json relatif terhadap script ini
    here = os.path.dirname(os.path.abspath(__file__))
    dfa_path = os.path.join(here, "dfa.json")
    
    # Inisialisasi spesifikasi DFA dan Lexer
    dfa_spec = DFASpec.from_file(dfa_path)
    
    try:
        with open(src_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        lexer = Lexer(text, dfa_spec)
        tokens = lexer.get_all_tokens()
        
        # Cetak token yang ditemukan
        for token in tokens:
            print(token)
            
    except ValueError as e:
        print(f"An error occurred: {e}")
        sys.exit(2)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()