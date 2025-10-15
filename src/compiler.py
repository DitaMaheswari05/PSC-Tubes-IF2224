"""
- Scanning huruf demi huruf menggunakan DFA
- Aturan DFA dibaca dari dfa.json
- Output: daftar token "TYPE(value)"
"""
# REVISI YA GAIS
"""
Pascal-S Lexer (Milestone 1 IF2224 TBFO) - OOP DFA Engine
- Murni Object-Oriented.
- Membaca definisi DFA komprehensif dari dfa.json.
- Menerapkan "maximal munch" untuk menemukan token terpanjang yang valid.
"""

import json
import sys
import os
from typing import Dict, Any, Tuple, Optional, List

class Token:
    def __init__(self, ttype: str, value: str, line: int, col: int): #object tokennya dibuat
        self.type = ttype
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self) -> str:
        return f"{self.type}({self.value})"

class DFASpec:
    """Memuat dan menyediakan akses ke spesifikasi DFA dari file JSON."""
    def __init__(self, spec: Dict[str, Any]):
        self.start_state: str = spec['start_state'] # state awal
        self.states: Dict[str, Any] = spec['states'] # semua state 
        self.reserved_words: Dict[str, str] = spec['reserved_words'] # kata kunci 

    @classmethod
    def from_file(cls, filepath: str) -> 'DFASpec':
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return cls(json.load(f))
        except Exception as e:
            print(f"Gagal memuat atau mem-parsing {filepath}: {e}")
            sys.exit(1)

class Lexer:
    """Mesin utama yang mengubah teks sumber menjadi daftar token berdasarkan DFA."""
    def __init__(self, source_text: str, dfa_spec: DFASpec):
        self.source = source_text
        self.spec = dfa_spec
        self.pos = 0
        self.line = 1
        self.col = 1

    def _get_char_class(self, char: str) -> str:
        """Mengklasifikasikan sebuah karakter ke dalam kelas yang dikenali DFA."""
        if not char: return 'eof'
        if char.isalpha(): return 'letter'
        if char.isdigit(): return 'digit'
        if char == '_': return '_'
        # Untuk input literal seperti ';' atau '+', kita kembalikan karakternya sendiri
        # 'any_other' digunakan untuk aturan umum dalam string/char literal
        return char if len(char) == 1 else 'any_other'

    def _skip_whitespace(self):
        while self.pos < len(self.source) and self.source[self.pos].isspace():
            if self.source[self.pos] == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.pos += 1

    def _skip_comment(self, start_marker: str):
        """Melewati isi komentar hingga penutupnya ditemukan."""
        start_line, start_col = self.line, self.col
        end_markers = {'{': '}', '(*': '*)'}
        end_marker = end_markers.get(start_marker)
        if not end_marker: return

        while self.pos < len(self.source):
            # Cek penutup
            if len(end_marker) == 1 and self.source[self.pos] == end_marker:
                self.pos += 1; self.col += 1
                return
            if len(end_marker) == 2 and self.source[self.pos:self.pos+2] == end_marker:
                self.pos += 2; self.col += 2
                return
            
            # Maju
            if self.source[self.pos] == '\n':
                self.line += 1; self.col = 1
            else:
                self.col += 1
            self.pos += 1
        
        raise ValueError(f"Lexical error: unterminated comment starting at line {start_line}, col {start_col}")

    def get_all_tokens(self) -> List[Token]:
        """Memproses seluruh teks sumber dan mengembalikan daftar token."""
        tokens: List[Token] = []
        while self.pos < len(self.source):
            self._skip_whitespace()
            if self.pos >= len(self.source): break
            
            token = self._get_next_token()
            if token:
                if token.type == 'COMMENT_START':
                    self._skip_comment(token.value)
                    continue
                # Abaikan token penutup komentar yang mungkin lolos
                if token.type == 'COMMENT_END':
                    continue
                tokens.append(token)
            else:
                char = self.source[self.pos]
                raise ValueError(f"Lexical error at line {self.line}, col {self.col}: Unknown symbol '{char}'")
        return tokens

    def _get_next_token(self) -> Optional[Token]:
        """Mencari satu token berikutnya dari posisi saat ini menggunakan prinsip maximal munch."""
        current_state_name = self.spec.start_state
        last_accepted_token: Optional[Token] = None
        buffer = ""

        temp_pos = self.pos
        
        while temp_pos < len(self.source):
            char = self.source[temp_pos]
            
            current_state = self.spec.states.get(current_state_name)
            if not current_state: break

            char_class = self._get_char_class(char)
            next_state_name = None
            
            # Cari transisi yang cocok
            for trans in current_state.get('transitions', []):
                # Cocokkan dengan input literal (e.g., ';', '=', '<')
                if trans['input'] == char:
                    next_state_name = trans['next_state']
                    break
                # Cocokkan dengan kelas karakter (e.g., 'letter', 'digit')
                if trans['input'] == char_class:
                    next_state_name = trans['next_state']
                    break
                # Fallback untuk string/char literal
                if trans['input'] == 'any_other' and char != "'":
                     next_state_name = trans['next_state']
                     break

            if not next_state_name: break
                
            buffer += char
            current_state_name = next_state_name
            temp_pos += 1
            
            # Cek apakah state saat ini adalah final state
            next_state = self.spec.states.get(current_state_name)
            if next_state and next_state.get('is_final'):
                last_accepted_token = Token(
                    ttype=next_state['token_type'],
                    value=buffer,
                    line=self.line,
                    col=self.col
                )

        if not last_accepted_token:
            return None

        # Post-processing untuk token yang sudah diterima
        if last_accepted_token.type == 'IDENTIFIER':
            lookup = self.spec.reserved_words.get(last_accepted_token.value.lower())
            if lookup:
                last_accepted_token.type = lookup
        
        if last_accepted_token.type in ('STRING_LITERAL', 'CHAR_LITERAL'):
            inner_content = last_accepted_token.value[1:-1]
            processed_value = inner_content.replace("''", "'")
            # Sesuaikan nilai token agar sesuai format output yang diharapkan
            last_accepted_token.value = f"'{processed_value}'"

        # Majukan kursor utama sesuai panjang token yang diterima
        for char_in_token in last_accepted_token.value:
            # PERBAIKAN: Gunakan `char_in_token` untuk cek baris baru, bukan `self.source[self.pos]`
            if char_in_token == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.pos += 1

        return last_accepted_token

def main():
    """Fungsi utama untuk menjalankan lexer dari command line."""
    if len(sys.argv) != 2:
        print("Usage: python compiler.py <source.pas>")
        sys.exit(1)

    src_path = sys.argv[1]
    if not os.path.exists(src_path):
        print(f"File not found: {src_path}")
        sys.exit(1)

    here = os.path.dirname(os.path.abspath(__file__))
    dfa_path = os.path.join(here, "dfa.json")
    
    dfa_spec = DFASpec.from_file(dfa_path)

    with open(src_path, "r", encoding="utf-8") as f:
        text = f.read()

    lexer = Lexer(text, dfa_spec)
    try:
        tokens = lexer.get_all_tokens()
        for token in tokens:
            print(token)
    except ValueError as e:
        print(str(e))
        sys.exit(2)

if __name__ == "__main__":
    main()

