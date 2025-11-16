import json
import sys
import os
from typing import List
from models import Token, TokenType, Lexeme

class LexicalError(Exception):
    """Custom exception untuk error leksikal."""
    def __init__(self, message:str, line:int, column:int) -> None:
        super().__init__(f"Lexical Error on line {line}, column {column}: {message}")
        self.message = message
        self.line = line
        self.column = column

class Lexer:
    def __init__(self, dfa_rules_path:str) -> None:
        """
        Inisialisasi lexer dengan memuat aturan DFA dari file JSON.
        """
        try:
            with open(dfa_rules_path, 'r') as f:
                self.dfa = json.load(f)
        except FileNotFoundError:
            print(f"FATAL ERROR: dfa.json tidak ditemukan di '{dfa_rules_path}'", file=sys.stderr)
            sys.exit(1)
        
        self.start_state = self.dfa['start_state']
        self.final_states = self.dfa['final_states']
        self.transitions = self.dfa['transitions']
        self.char_classes = self.dfa['character_classes']
        
        # Daftar keywords dan reserved words dari DFA (dalam lowercase)
        self.keywords = self.dfa.get('keywords', {})
        self.reserved_operators = self.dfa.get('reserved_operators', {})
        
        # Daftar keyword yang mengandung tanda hubung (hyphen)
        # self.hyphenated_keywords = {'selain-itu', 'turun-ke'}

    def _get_char_class(self, char:str):
        """Mendapatkan kelas karakter (letter, digit, dll.) dari sebuah karakter."""
        for class_name, chars in self.char_classes.items():
            if char in chars:
                return class_name
        return char

    # def _merge_hyphenated_keywords(self, tokens:List[Token]) -> List[Token]:
    #     """
    #     Post-processing untuk menggabungkan token yang membentuk keyword ber-hyphen.
    #     Menggabungkan urutan: IDENTIFIER/KEYWORD + ARITHMETIC_OPERATOR('-') + IDENTIFIER/KEYWORD
    #     menjadi satu KEYWORD jika hasilnya adalah 'selain-itu' atau 'turun-ke'.
        
    #     Args:
    #         tokens: List of (token_type, lexeme) tuples
            
    #     Returns:
    #         List of (token_type, lexeme) tuples dengan keyword ber-hyphen yang sudah digabung
    #     """
    #     merged_tokens = []
    #     i = 0
        
    #     while i < len(tokens):
    #         # Cek apakah ada pola: token1 + '-' + token2
    #         if (i + 2 < len(tokens) and
    #             tokens[i].token_type in ['IDENTIFIER', 'KEYWORD'] and
    #             tokens[i + 1].token_type == 'ARITHMETIC_OPERATOR' and
    #             tokens[i + 1].lexeme == '-' and
    #             tokens[i + 2].token_type in ['IDENTIFIER', 'KEYWORD']):
                
    #             # Bentuk kandidat keyword dengan menggabungkan lexeme
    #             candidate = (tokens[i].lexeme + '-' + tokens[i + 2].lexeme).lower()
                
    #             # Jika kandidat adalah keyword ber-hyphen yang valid
    #             if candidate in self.hyphenated_keywords:
    #                 # Gabungkan menjadi satu token KEYWORD
    #                 merged_tokens.append(Token('KEYWORD', candidate))
    #                 i += 3  # Skip tiga token yang sudah digabung
    #                 continue
            
    #         # Jika bukan pola keyword ber-hyphen, tambahkan token seperti biasa
    #         merged_tokens.append(tokens[i])
    #         i += 1
        
    #     return merged_tokens

    def tokenize(self, source_code:str) -> List[Token]:
        """
        Memproses source code dan mengubahnya menjadi daftar token.
        Melempar LexicalError jika ada kesalahan.
        """
        tokens = []
        position = 0
        line = 1
        column = 1

        # Main Loop: Memproses semua karakter sampai karakter habis
        while position < len(source_code):
            char = source_code[position]
            # Jika karakter adalah whitespace, lewati dan perbarui posisi
            if char in self.char_classes.get('whitespace', ''):
                if char == '\n':
                    # Jika newline, perbarui baris dan kolom
                    line += 1
                    column = 1
                else:
                    # Jika spasi atau tab, cukup perbarui kolom
                    column += 1
                position += 1
                continue # Lanjut ke iterasi berikutnya untuk karakter selanjutnya
            
            # Handle komentar blok { ... }
            if char == '{':
                position += 1
                column += 1
                while position < len(source_code) and source_code[position] != '}':
                    if source_code[position] == '\n':
                        line += 1
                        column = 1
                    else:
                        column += 1
                    position += 1
                # Skip closing }
                if position < len(source_code):
                    position += 1
                    column += 1
                continue
            
            # Handle komentar line (* ... *)
            if char == '(' and position + 1 < len(source_code) and source_code[position + 1] == '*':
                position += 2
                column += 2
                while position + 1 < len(source_code):
                    if source_code[position] == '*' and source_code[position + 1] == ')':
                        position += 2
                        column += 2
                        break
                    if source_code[position] == '\n':
                        line += 1
                        column = 1
                    else:
                        column += 1
                    position += 1
                continue

            # Mulai dari state awal DFA
            current_state = self.start_state
            current_lexeme = ""
            last_match = None # Menyimpan token terakhir yang valid
            
            start_line, start_col = line, column

            # Pointer sementara untuk simulasi DFA dan pointer utama tidak akan diubah sampai ketemu satu token utuh
            temp_pos = position
            temp_line, temp_col = line, column 

            # Inner Loop: Simulasi DFA untuk menemukan token terpanjang
            while True: 
                # Cek apakah EOF?
                if temp_pos >= len(source_code):
                    # Error handling untuk string yang tidak ditutup
                    if current_state in ["S_STRING_CONTENT", "S_STRING_QUOTE_END"]:
                        raise LexicalError("Unterminated string literal", start_line, start_col)
                    break

                # Ambil karakter dan tentukan kelasnya
                char = source_code[temp_pos]
                char_class = self._get_char_class(char)
                
                next_state = None
                
                # Pencarian transisi DFA
                if current_state in self.transitions:
                    possible_transitions = self.transitions[current_state]
                    # Prioritas 1: Apakah ada aturan untuk kelas karakter karakter
                    if char_class in possible_transitions:
                        next_state = possible_transitions[char_class]
                    # Prioritas 2: Apakah ada aturan untuk karakter literal
                    elif char in possible_transitions:
                        next_state = possible_transitions[char]
                    else:
                        # Prioritas 3: Cek aturan khusus seperti "any_except_..."
                        for rule, target_state in possible_transitions.items():
                            if rule.startswith("any_except_"):
                                excluded_chars = rule.split('_')[-1]
                                if char not in excluded_chars:
                                    next_state = target_state
                                    break
                
                # Pemrosesan hasil transisi
                if next_state:
                    current_state = next_state
                    current_lexeme += char
                    
                    # Majukan pointer sementara
                    if char == '\n':
                        temp_line += 1
                        temp_col = 1
                    else:
                        temp_col += 1
                    temp_pos += 1

                    # Jika sudah state final, simpan token di last_match
                    if current_state in self.final_states:
                        last_match = (current_lexeme, self.final_states[current_state], temp_line, temp_col)
                else:
                    # Jika tidak ada transisi yang valid, keluar dari loop
                    break
            
            # Finalisasi token setelah inner loop
            if last_match:
                # Jika last_match ada, berarti kita menemukan token valid
                lexeme, token_type, end_line, end_col = last_match
                
                if token_type == "IDENTIFIER":
                    # Jika token adalah identifier, cek apakah itu keyword atau reserved word menggunakan DFA mapping
                    lexeme_lower = lexeme.lower()
                    if lexeme_lower in self.keywords:
                        token_type = self.keywords[lexeme_lower]
                    elif lexeme_lower in self.reserved_operators:
                        token_type = self.reserved_operators[lexeme_lower]
                
                # Tambahkan token ke daftar token
                tokens.append(Token(token_type, lexeme, end_line, end_col))
                
                # Perbarui posisi utama ke posisi setelah token yang ditemukan
                position += len(lexeme)
                # Perbarui baris dan kolom utama
                line, column = end_line, end_col
            else:
                # Jika tidak ada token valid yang ditemukan, lempar error
                raise LexicalError(f"Invalid character '{source_code[position]}'", line, column)
        
        # Post-processing: Gabungkan keyword ber-hyphen seperti "selain-itu" dan "turun-ke"
        # tokens = self._merge_hyphenated_keywords(tokens)
        
        # return daftar token yang ditemukan
        return tokens

def main():
    """
    Fungsi utama untuk menjalankan lexer.
    Dapat menerima 1 argumen (output ke terminal) atau 2 argumen (output ke file):
    - python lexer.py input.pas -> output ke terminal
    - python lexer.py input.pas output.txt -> output ke file
    """
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage:", file=sys.stderr)
        print("  python lexer.py <source_file_path.pas> -> output ke terminal", file=sys.stderr)
        print("  python lexer.py <source_file_path.pas> <output_file_path.txt> -> output ke file", file=sys.stderr)
        sys.exit(1)

    source_file_path = sys.argv[1]
    output_file_path = sys.argv[2] if len(sys.argv) == 3 else None

    if not source_file_path.lower().endswith('.pas'):
        print(f"Input Error: Source file harus memiliki ekstensi .pas. Diberikan: '{source_file_path}'", file=sys.stderr)
        sys.exit(1)
        
    if output_file_path and not output_file_path.lower().endswith('.txt'):
        print(f"Output Error: Output file harus memiliki ekstensi .txt. Diberikan: '{output_file_path}'", file=sys.stderr)
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    dfa_path = os.path.join(script_dir, "dfa.json")
    
    try:
        with open(source_file_path, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Input file tidak ditemukan di '{source_file_path}'", file=sys.stderr)
        sys.exit(1)
        
    lexer = Lexer(dfa_path)
    
    try:
        tokens = lexer.tokenize(source_code)
        
        if output_file_path:
            # Output ke file
            output_dir = os.path.dirname(output_file_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                
            with open(output_file_path, 'w') as f:
                for token_type, lexeme in tokens:
                    f.write(f"{token_type}({lexeme})\n")
            
            print(f"Tokenization successful. Output written to '{output_file_path}'")
        else:
            # Output ke terminal
            print("Tokenization successful. Daftar token:")
            print("=" * 40)
            for token in tokens:
                print(token)

    except LexicalError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error writing to file '{output_file_path}': {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

