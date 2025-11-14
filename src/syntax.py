# nama file: syntax.py
import sys
import os
from lexer import Lexer, LexicalError
from models import CFG, Node
from rulesSpek import setupProductionRules

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
    print("--- 1. Menjalankan Lexer ---")
    lexer = Lexer(dfa_path)
    tokens = []
    try:
        tokens = lexer.tokenize(source_code)
        print(f"Lexer berhasil: {len(tokens)} token ditemukan.")
    except LexicalError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1) # Keluar jika ada error leksikal
    
    # Opsional: Cetak token untuk debug
    print("\n--- Daftar Token ---")
    for token in tokens:
        print(token)
    print("--------------------\n")

    # --- 4. Jalankan Parser ---
    print("\n--- 2. Menjalankan Parser ---")
    
    # Ambil aturan produksi dari rules.py
    production_rules = setupProductionRules()
    
    # Inisialisasi parser (CFG) dengan token
    parser = CFG(tokens)
    
    # Daftarkan aturan ke parser
    parser.addRules(production_rules)
    
    parse_tree = None
    try:
        # Mulai parsing dari non-terminal <Program> (default di CFG.parse())
        parse_tree = parser.parse()
        
        # --- 5. Periksa Hasil Parsing ---
        if parse_tree is not None:
            # Parsing berhasil, TAPI kita harus cek apakah semua token terpakai.
            final_token = parser.currentToken()
            if final_token.token_type == "EOF":
                print("\n✅ Parsing Berhasil!")
                print("\n--- Parse Tree ---")
                print(parse_tree)
            else:
                # Parsing selesai tapi masih ada sisa token
                print("\n❌ Syntax Error: Parsing selesai, tapi masih ada sisa token yang tidak terduga.", file=sys.stderr)
                print(f"Error di dekat token: {final_token} (Line: ??, Column: ??)", file=sys.stderr)
                # Note: Info baris/kolom tidak disimpan di Token, jadi tidak bisa ditampilkan di sini.
        else:
            # Parsing Gagal (parser mengembalikan None)
            print("\n❌ Syntax Error: Parsing gagal.", file=sys.stderr)
            # Coba tunjukkan token tempat parser gagal
            failed_token_index = parser.currentTokenID
            if failed_token_index < len(tokens):
                failed_at_token = tokens[failed_token_index]
                print(f"Parser berhenti di dekat token #{failed_token_index}: {failed_at_token}", file=sys.stderr)
            else:
                print("Parser berhenti di akhir file (EOF).", file=sys.stderr)
            print("Aktifkan print() di dalam 'models.py' (baris 112, 119, 122) untuk debug langkah-demi-langkah.", file=sys.stderr)

    except Exception as e:
        print(f"\nFATAL PARSER ERROR (mungkin aturan hilang atau bug di parser): {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()