import sys
import os
from typing import List

from lexical.lexer import Lexer, LexicalError
from syntax.rules import getAllProductionRules

from syntax.cfg import CFG
from syntax.parsetree import Node
from lexical.token import Token

class SyntaxError(Exception):
    """Custom exception untuk error sintaks."""
    def __init__(self, message:str, line:int=None, column:int=None) -> None:
        if line and column:
            super().__init__(f"Syntax Error on line {line}, column {column}: {message}")
        else:
            super().__init__(f"Syntax Error: {message}")
        self.message = message
        self.line = line
        self.column = column

class SyntaxAnalyzer():
    """Kelas untuk SyntaxAnalyzer"""
    cfg: CFG

    def __init__(self):
        self.cfg = CFG()
        self.setupProductionRules()

    def setupProductionRules(self):
        self.cfg.addRules(getAllProductionRules())

    def parse(self, tokens:List[Token]) -> Node|SyntaxError:
        parse_tree = self.cfg.parseToken(tokens)

        if parse_tree is not None:
            # Parsing berhasil, TAPI kita harus cek apakah semua token terpakai.
            final_token = self.cfg.currentToken()
            if final_token.token_type == "EOF":
                return parse_tree # success
            else:
                # Parsing selesai tapi masih ada sisa token
                raise SyntaxError(message=f"\n\tUnexpected token {final_token}", line=final_token.line, column=final_token.column)
        else:
            # Parsing Gagal (parser mengembalikan None)
            error_info = self.cfg.max_error_info
            
            if error_info['max_id'] != -1 and error_info['found']:
                found = error_info['found']
                # Format 'expected' set menjadi string yang rapi
                expected_list = [str(e) for e in error_info['expected']]
                if len(expected_list) > 1:
                    expected_str = "one of possible tokens: " + ", ".join(expected_list)
                elif expected_list:
                    expected_str = expected_list[0]
                else:
                    raise SyntaxError(message="Something went wrong", line=found.line, column=found.column)
                raise SyntaxError(message=f"\n\tUnexpected token {found}, \n\tExpected {expected_str}", line=found.line, column=found.column)

            else:
                # Fallback jika tidak ada info error (alasan lain)
                raise SyntaxError(message="Something went wrong")

def main():
    """
    Driver utama untuk parser.
    Mengambil 1 argumen: path ke file source code .pas
    """
    
    # --- 1. Validasi Argumen Input ---
    if len(sys.argv) != 2:
        print("Usage: python syntax.py <source_file_path.pas>", file=sys.stderr)
        sys.exit(1)

    source_file_path = sys.argv[1]
    if not source_file_path.lower().endswith('.pas'):
        print(f"Input Error: Source file harus berekstensi .pas. Diberikan: '{source_file_path}'", file=sys.stderr)
        sys.exit(1)

    # Mendapatkan path absolut ke dfa.json
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # src/syntax/
    DFA_FILE_PATH = os.path.join(BASE_DIR, '..', 'lexical', 'dfa.json')

    # --- 2. Baca Source Code ---
    try:
        with open(source_file_path, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Input file tidak ditemukan di '{source_file_path}'", file=sys.stderr)
        sys.exit(1)
        
    # --- 3. Jalankan Lexer ---
    lexer = Lexer(DFA_FILE_PATH)
    tokens = []
    try:
        tokens = lexer.tokenize(source_code)
    except LexicalError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1) # Keluar jika ada error leksikal
    
    # print("\n--- Daftar Token ---")
    # for token in tokens:
    #     print(token)
    # print("--------------------\n")

    # --- 4. Jalankan Parser ---
    parser = SyntaxAnalyzer()
    try:
        print(parser.parse(tokens=tokens))
    except SyntaxError as e:
        print(e)
    except Exception as e:
        print(f"\nFATAL PARSER ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()