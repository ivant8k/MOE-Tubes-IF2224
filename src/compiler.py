import sys, os

from lexical.lexer import Lexer, LexicalError
from syntax.syntax import SyntaxAnalyzer, SyntaxError
from semantic.semantic import SemanticAnalyzer, SemanticError
from semantic.print_tree import ASTPrinter

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
    DFA_FILE_PATH = os.path.join(BASE_DIR, 'lexical', 'dfa.json')

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
        parse_tree = parser.parse(tokens=tokens)
        # print(parse_tree)
    except SyntaxError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1) # Keluar jika ada error sintaks
    except Exception as e:
        print(f"\nFATAL PARSER ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # --- 4. Jalankan Semantic Analyzer (parse_tree -> AST -> [ASTDecorated, SymbolTable]) ---
    try:
        semantic_analyzer = SemanticAnalyzer()
        decorated_ast, symbol_table, ast = semantic_analyzer.analyze(parse_tree, debug=True)
        # Print Output
        print(symbol_table)
        print(decorated_ast)

    except SemanticError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1) # Keluar jika ada error semantik
    except Exception as e:
        print(f"\nFATAL SEMANTIC ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()