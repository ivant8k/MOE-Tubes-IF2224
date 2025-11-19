import sys, os

from lexical.lexer import Lexer, LexicalError
from syntax.syntax import SyntaxAnalyzer, SyntaxError
from semantic.ast_converter import ASTConverter
# from semantic.semantic_analyzer import SemanticAnalyzer

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
        parser_tree = parser.parse(tokens=tokens)
        print(parser_tree)
    except SyntaxError as e:
        print(e)
    except Exception as e:
        print(f"\nFATAL PARSER ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # --- 4. Jalankan AST Converter ---
    try:
        converter = ASTConverter()
        ast = converter.convert(parser_tree)
        print("\n=== Abstract Syntax Tree (AST) ===")
        print(ast)
    except Exception as e:
        print(f"AST Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # --- 5. Jalankan Semantic Analyzer ---
    # try:
    #     analyzer = SemanticAnalyzer()
    #     analyzer.visit(ast)
        
    #     print("\n=== Compilation Successful ===")
    #     print("\nSymbol Table (Tab):")
    #     # Skip dummy index 0
    #     for idx, entry in enumerate(analyzer.symbol_table.tab):
    #         if idx == 0: continue
    #         print(f"{idx}: {entry}")
        
    #     print("\nBlock Table (BTab):")
    #     for idx, entry in enumerate(analyzer.symbol_table.btab):
    #         print(f"{idx}: {entry}")

    #     # Opsional: Print Array Table jika ada
    #     if analyzer.symbol_table.atab:
    #         print("\nArray Table (ATab):")
    #         for idx, entry in enumerate(analyzer.symbol_table.atab):
    #             print(f"{idx}: {entry}")
            
    # except Exception as e:
    #     print(f"Semantic Error: {e}")
    #     traceback.print_exc()


if __name__ == "__main__":
    main()