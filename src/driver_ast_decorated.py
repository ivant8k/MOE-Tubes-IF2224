import sys, os

from lexical.lexer import Lexer, LexicalError
from syntax.syntax import SyntaxAnalyzer, SyntaxError
from semantic.ast_converter import ASTConverter
# [UBAH]: Import ASTDecorator
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
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DFA_FILE_PATH = os.path.join(BASE_DIR, 'lexical', 'dfa.json')

    # --- 2. Baca Source Code ---
    try:
        with open(source_file_path, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Input file tidak ditemukan di '{source_file_path}'", file=sys.stderr)
        sys.exit(1)
        
    # --- 3. Jalankan Lexer ---
    print("[1/4] Running Lexer...")
    lexer = Lexer(DFA_FILE_PATH)
    tokens = []
    try:
        tokens = lexer.tokenize(source_code)
    except LexicalError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    
    # --- 4. Jalankan Parser ---
    print("[2/4] Running Parser...")
    parser = SyntaxAnalyzer()
    parser_tree = None
    try:
        parser_tree = parser.parse(tokens=tokens)
    except SyntaxError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"\nFATAL PARSER ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # --- 5. Jalankan AST Converter ---
    print("[3/4] Converting to AST...")
    ast = None
    try:
        converter = ASTConverter()
        ast = converter.convert(parser_tree)
    except Exception as e:
        print(f"AST Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # --- 6. Phase 4: Semantic Analysis & Decoration ---
    print("[4/4] Running Semantic Analysis & AST Decoration...")
    try:
        # [UBAH]: Gunakan ASTDecorator menggantikan SemanticAnalyzer biasa.
        # Karena ASTDecorator mewarisi SemanticAnalyzer, ia akan melakukan
        # validasi semantik sekaligus mengisi atribut node untuk visualisasi.
        decorator = ASTDecorator()
        decorated_ast = decorator.generate_decorated_ast(ast)
        
        print("      Success! No semantic errors found.")
        print("\n" + "="*50)
        print("COMPILATION SUCCESSFUL")
        print("="*50)
        
        # [INFO]: Gunakan 'decorator.symbol_table' untuk mengambil data tabel
        
        # Cetak Symbol Table (Tab) - Skip dummy index 0
        print("\n>> Symbol Table (Identifier Table):")
        print(f"{'Idx':<5} | {'id':<15} | {'Obj':<10} | {'Type':<10} | {'nrm':<5} | {'Lev':<5} | {'Adr':<5} | {'link':<5}")
        print("-" * 80)
        for idx, entry in enumerate(decorator.symbol_table.tab):
            if idx == 0: continue # Skip dummy
            name = entry.identifier
            obj = entry.obj.value if hasattr(entry.obj, 'value') else str(entry.obj)
            typ = entry.type.name if hasattr(entry.type, 'name') else str(entry.type)
            print(f"{idx:<5} | {name:<15} | {obj:<10} | {typ:<10} | {entry.nrm:<5} | {entry.lev:<5} | {entry.adr:<5} | {entry.link:<5}")

        # Cetak Block Table (BTab)
        print("\n>> Block Table (Scope Info):")
        print(f"{'Idx':<5} | {'Last':<5} | {'LPar':<5} | {'PSize':<5} | {'VSize':<5}")
        print("-" * 40)
        for idx, entry in enumerate(decorator.symbol_table.btab):
            if idx == 0: continue 
            print(f"{idx:<5} | {entry.last:<5} | {entry.lpar:<5} | {entry.psze:<5} | {entry.vsze:<5}")

        # Cetak Array Table (ATab)
        print("\n>> Array Table:" )
        if len(decorator.symbol_table.atab) <= 1: # Index 0 is dummy
            print("  (empty)")
        else:
            for idx, entry in enumerate(decorator.symbol_table.atab):
                if idx == 0: continue
                print(f"Array {idx}: {entry}")

        # Cetak Decorated AST
        print("\n=== Final Abstract Syntax Tree (AST) with Semantic Info ===")
        # Karena ASTNode sudah didesain memiliki method __str__ yang membaca .type dan .symbol_entry,
        # kita cukup print root-nya saja.
        print(decorated_ast)
            
    except Exception as e:
        import traceback
        print(f"      [Semantic Error] {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()