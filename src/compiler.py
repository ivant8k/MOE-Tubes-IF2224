import sys, os

from lexical.lexer import Lexer, LexicalError
from syntax.syntax import SyntaxAnalyzer, SyntaxError

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

    # Tentukan path ke dfa.json (diasumsikan berada di direktori yang sama)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dfa_path = os.path.join(script_dir, "dfa.json")
    if not os.path.exists(dfa_path):
        print(f"Fatal Error: 'dfa.json' tidak ditemukan di '{script_dir}'", file=sys.stderr)
        sys.exit(1)

    # --- 2. Baca Source Code ---
    try:
        with open(source_file_path, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Input file tidak ditemukan di '{source_file_path}'", file=sys.stderr)
        sys.exit(1)
        
    # --- 3. Jalankan Lexer ---
    lexer = Lexer(dfa_path)
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