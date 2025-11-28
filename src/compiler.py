import sys, os

from lexical.lexer import Lexer, LexicalError
from syntax.syntax import SyntaxAnalyzer, SyntaxError
from semantic.ast_converter import ASTConverter
from semantic.analyzer import SemanticAnalyzer
from semantic.ast_decorator import ASTDecorator

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
        # print(parser_tree)
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
        # print("\n=== Abstract Syntax Tree (AST) ===")
        # print(ast)
    except Exception as e:
        print(f"AST Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # --- 5. Phase 4: Semantic Analysis ---
    print("[4/4] Running Semantic Analysis...")
    try:
        analyzer = ASTDecorator()
        decorated_ast = analyzer.generate_decorated_ast(ast)
        
        print("      Success! No semantic errors found.")
        print("\n" + "="*50)
        print("COMPILATION SUCCESSFUL")
        print("="*50)
        
        # Cetak Symbol Table (Tab) - Skip dummy index 0
        print("\n>> Symbol Table (Identifier Table):")
        print(f"{'Idx':<5} | {'id':<15} | {'Obj':<10} | {'Type':<10} | {'nrm':<5} | {'Lev':<5} | {'Adr':<5} | {'link':<5}")
        print("-" * 55)
        for idx, entry in enumerate(analyzer.symbol_table.tab):
            if idx == 0: continue # Skip dummy
            name = entry.identifier
            obj = entry.obj.value if hasattr(entry.obj, 'value') else str(entry.obj)
            typ = entry.type.name if hasattr(entry.type, 'name') else str(entry.type)
            print(f"{idx:<5} | {name:<15} | {obj:<10} | {typ:<10} | {entry.nrm:<5} | {entry.lev:<5} | {entry.adr:<5} | {entry.link:<5}")

        # Cetak Block Table (BTab)
        print("\n>> Block Table (Scope Info):")
        for idx, entry in enumerate(analyzer.symbol_table.btab):
            if idx == 0: continue # Skip dummy global wrapper if needed
            print(f"{idx} | {entry.last} | {entry.lpar} | {entry.psze} | {entry.vsze} |")

        print("\n>> Array Table:" )
        if len(analyzer.symbol_table.atab) == 0:
            print("  (empty)")

        for idx, entry in enumerate(analyzer.symbol_table.atab):
            print(f"Array {idx}: {entry}")

        print("\n=== Final Abstract Syntax Tree (AST) with Semantic Info ===")

        print(decorated_ast)
            
    except Exception as e:
        import traceback
        print(f"      [Semantic Error] {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()