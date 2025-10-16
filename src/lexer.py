from typing import List, Optional
from token import Token
from dfa import DFASpec
from token_type import TokenType

class Lexer:
    # Mesin utama yang mengubah teks menjadi daftar token berdasarkan aturan DFA
    def __init__(self, source_text: str, dfa_spec: DFASpec):
        self.source = source_text
        self.spec = dfa_spec
        self.pos = 0
        self.line = 1
        self.col = 1

    def _get_char_class(self, char: str) -> str:
        # Mengklasifikasikan sebuah karakter ke dalam kelas yang dikenali DFA
        if not char: return 'eof'
        if char.isalpha(): return 'letter'
        if char.isdigit(): return 'digit'
        if char == '_': return '_'
        return char if len(char) == 1 else 'any_other'

    def _skip_whitespace_and_comments(self):
        # Melewati spasi, tab, baris baru, dan blok komentar
        while self.pos < len(self.source):
            char = self.source[self.pos]
            if char.isspace():
                if char == '\n':
                    self.line += 1
                    self.col = 1
                else:
                    self.col += 1
                self.pos += 1
            elif char == '{' or self.source[self.pos:self.pos+2] == '(*':
                try:
                    self._skip_comment()
                except ValueError as e:
                    print(e)
                    self.pos = len(self.source) # Berhenti memproses
            else:
                break
    
    def _skip_comment(self):
        # Melewati isi komentar hingga penutup komentarnya ditemukan
        start_line, start_col = self.line, self.col
        
        if self.source[self.pos] == '{':
            end_marker = '}'
            self.pos += 1
            self.col += 1
        elif self.source[self.pos:self.pos+2] == '(*':
            end_marker = '*)'
            self.pos += 2
            self.col += 2
        else:
            return

        while self.pos < len(self.source):
            if self.source.startswith(end_marker, self.pos):
                if end_marker == '*)':
                    self.pos += 2
                    self.col += 2
                else:
                    self.pos += 1
                    self.col += 1
                return
            
            if self.source[self.pos] == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.pos += 1
        
        raise ValueError(f"Lexical error: unterminated comment starting at line {start_line}, col {start_col}")


    def get_all_tokens(self) -> List[Token]:
        # Memproses seluruh teks sumber dan mengembalikan daftar token
        tokens: List[Token] = []
        while self.pos < len(self.source):
            self._skip_whitespace_and_comments()
            if self.pos >= len(self.source): break
            
            token = self._get_next_token()
            if token:
                tokens.append(token)
            else:
                char = self.source[self.pos]
                raise ValueError(f"Lexical error at line {self.line}, col {self.col}: Unknown symbol '{char}'")
        return tokens

    def _get_next_token(self) -> Optional[Token]:
        # Mencari satu token berikutnya dari posisi saat ini menggunakan prinsip maximal munch
        current_state_name = self.spec.start_state
        last_accepted_token: Optional[Token] = None
        buffer = ""
        temp_pos = self.pos
        accepted_length: Optional[int] = None
        
        while temp_pos < len(self.source):
            char = self.source[temp_pos]
            current_state = self.spec.states.get(current_state_name)
            if not current_state: break

            char_class = self._get_char_class(char)
            next_state_name = self._find_next_state(current_state, char, char_class)

            if not next_state_name: break
                
            buffer += char
            current_state_name = next_state_name
            temp_pos += 1
            
            next_state = self.spec.states.get(current_state_name)
            if next_state and next_state.get('is_final'):
                token_type_str = next_state['token_type']
                last_accepted_token = Token(
                    ttype=TokenType[token_type_str],
                    value=buffer,
                    line=self.line,
                    col=self.col
                )
                accepted_length = len(buffer)

        if not last_accepted_token: return None

        self._post_process_token(last_accepted_token)
        
        # Majukan kursor utama, gunakan panjang asli token yang diterima
        if accepted_length is None:
            advance_len = len(last_accepted_token.value)
        else:
            advance_len = accepted_length
        for _ in range(advance_len):
            if self.pos < len(self.source) and self.source[self.pos] == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.pos += 1

        return last_accepted_token
    
    def _find_next_state(self, current_state, char, char_class) -> Optional[str]:
        # Mencari transisi yang cocok dari state saat ini
        for trans in current_state.get('transitions', []):
            if trans['input'] == char or trans['input'] == char_class:
                return trans['next_state']
            if trans['input'] == 'any_other' and char != "'":
                 return trans['next_state']
        return None

    def _post_process_token(self, token: Token):
        # Menyesuaikan token setelah diterima (misalnya, keyword, literal string)
        if token.type == TokenType.IDENTIFIER:
            lookup = self.spec.reserved_words.get(token.value.lower())
            if lookup:
                token.type = TokenType[lookup]
        
        if token.type in (TokenType.STRING_LITERAL, TokenType.CHAR_LITERAL):
            inner_content = token.value[1:-1]
            processed_value = inner_content.replace("''", "'")
            token.value = f"'{processed_value}'"