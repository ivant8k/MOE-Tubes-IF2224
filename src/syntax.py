from models import CFG, Node, NonTerminal, Token, TokenType, Lexeme, Epsilon
from lexer import Lexer, LexicalError # Asumsi lexer.py ada di folder yang sama
import sys

# !!! HANYA UNTUK CEK KELAS CFG DAN TREE !!! 

# ===== 1. DEFINISI TIPE TOKEN (Untuk Keterbacaan) =====
# Ini membantu membuat aturan lebih mudah dibaca daripada string mentah

# Non-Terminals
S = NonTerminal("<S>")
Program = NonTerminal("<Program>")
ProgramHeader = NonTerminal("<ProgramHeader>")
Block = NonTerminal("<Block>")
VarDeclarationPart = NonTerminal("<VarDeclarationPart>")
VarDeclaration = NonTerminal("<VarDeclaration>")
Type = NonTerminal("<Type>")
StatementPart = NonTerminal("<StatementPart>")
StatementList = NonTerminal("<StatementList>")
Statement = NonTerminal("<Statement>")
AssignmentStatement = NonTerminal("<AssignmentStatement>")
Expression = NonTerminal("<Expression>")
SimpleExpression = NonTerminal("<SimpleExpression>")
SimpleExpressionPrime = NonTerminal("<SimpleExpressionPrime>")
Term = NonTerminal("<Term>")
Factor = NonTerminal("<Factor>")

# Token Types (TokenType)
T_ID = TokenType("IDENTIFIER")
T_NUMBER = TokenType("NUMBER")
T_SEMI = TokenType("SEMICOLON")
T_COLON = TokenType("COLON")
T_ASSIGN = TokenType("ASSIGN_OPERATOR")
T_DOT = TokenType("DOT")
T_LPAREN = TokenType("LPARENTHESIS")
T_RPAREN = TokenType("RPARENTHESIS")

# Specific Tokens (Token)
T_PROGRAM = Token("KEYWORD", "program")
T_VARIABEL = Token("KEYWORD", "variabel")
T_MULAI = Token("KEYWORD", "mulai")
T_SELESAI = Token("KEYWORD", "selesai")
T_INTEGER = Token("KEYWORD", "integer")
T_PLUS = Token("ARITHMETIC_OPERATOR", "+")
T_MINUS = Token("ARITHMETIC_OPERATOR", "-")
T_STAR = Token("ARITHMETIC_OPERATOR", "*")
T_SLASH = Token("ARITHMETIC_OPERATOR", "/")
T_BAGI = Token("ARITHMETIC_OPERATOR", "bagi")

# Epsilon
EPS = Epsilon()


# ===== 2. DEFINISI ATURAN PRODUKSI (CFG) =====

# Grammar ini dirancang untuk Recursive Descent (Top-Down)
# dan sudah di-refactor untuk menghindari Left-Recursion.
# Aturan ini cukup untuk mem-parsing 'input-valid.pas'
# dan ekspresi aritmatika sederhana.

production_rules = {
    # <S> -> <Program>
    S: [
        [Program]
    ],
    
    # <Program> -> <ProgramHeader> <Block> .
    Program: [
        [ProgramHeader, Block, T_DOT]
    ],
    
    # <ProgramHeader> -> program IDENTIFIER ;
    ProgramHeader: [
        [T_PROGRAM, T_ID, T_SEMI]
    ],
    
    # <Block> -> <VarDeclarationPart> <StatementPart>
    Block: [
        [VarDeclarationPart, StatementPart]
    ],
    
    # <VarDeclarationPart> -> variabel <VarDeclaration> ; | epsilon
    # Dibuat opsional (bisa epsilon) jika tidak ada 'variabel'
    VarDeclarationPart: [
        [T_VARIABEL, VarDeclaration, T_SEMI], 
        [EPS]
    ],
    
    # <VarDeclaration> -> IDENTIFIER : <Type>
    # (Disederhanakan, asumsi hanya satu variabel)
    VarDeclaration: [
        [T_ID, T_COLON, Type]
    ],
    
    # <Type> -> integer | real | ... (Kita batasi 'integer' dulu)
    Type: [
        [T_INTEGER]
    ],
    
    # <StatementPart> -> mulai <StatementList> selesai
    StatementPart: [
        [T_MULAI, StatementList, T_SELESAI]
    ],
    
    # <StatementList> -> <Statement> ; <StatementList> | epsilon
    # Aturan rekursif kanan ini mengizinkan 0 atau lebih statement
    StatementList: [
        [Statement, T_SEMI, StatementList],
        [EPS]
    ],
    
    # <Statement> -> <AssignmentStatement> | ... (Kita batasi assignment dulu)
    Statement: [
        [AssignmentStatement]
    ],
    
    # <AssignmentStatement> -> IDENTIFIER := <Expression>
    AssignmentStatement: [
        [T_ID, T_ASSIGN, Expression]
    ],
    
    # ----- Aturan Ekspresi Aritmatika -----
    # <Expression> -> <SimpleExpression>
    Expression: [
        [SimpleExpression]
    ],
    
    # <SimpleExpression> -> <Term> <SimpleExpressionPrime>
    SimpleExpression: [
        [Term, SimpleExpressionPrime]
    ],
    
    # <SimpleExpressionPrime> -> + <Term> <SimpleExpressionPrime>
    #                          | - <Term> <SimpleExpressionPrime>
    #                          | epsilon
    # Ini menangani A + B - C ...
    SimpleExpressionPrime: [
        [T_PLUS, Term, SimpleExpressionPrime],
        [T_MINUS, Term, SimpleExpressionPrime],
        [EPS]
    ],
    
    # <Term> -> <Factor> <TermPrime>
    Term: [
        [Factor] # Disederhanakan untuk input 5 + 10
        # Jika ingin menangani * dan /:
        # [Factor, TermPrime] 
    ],
    
    # <Factor> -> IDENTIFIER | NUMBER | ( <Expression> )
    Factor: [
        [T_ID],
        [T_NUMBER],
        [T_LPAREN, Expression, T_RPAREN]
    ]
    
    # NOTE: <TermPrime> sengaja dihilangkan untuk minimalitas,
    # tapi jika Anda ingin A * B / C, Anda akan menambahkannya:
    # TermPrime = NonTerminal("<TermPrime>")
    # ...
    # Term: [[Factor, TermPrime]],
    # TermPrime: [
    #    [T_STAR, Factor, TermPrime],
    #    [T_SLASH, Factor, TermPrime],
    #    [T_BAGI, Factor, TermPrime],
    #    [EPS]
    # ]
}


# ===== 3. FUNGSI UTAMA UNTUK MENJALANKAN PARSER =====

def main():
    # Gunakan path ke dfa.json Anda
    import os
    dfa_path = os.path.join(os.path.dirname(__file__), "dfa.json") 
    
    # Kode sumber yang AKAN BERHASIL di-parse
    # source_code = """
    # program ProgramValid;
    # variabel
    #   x: integer;
    # mulai
    #   x := 5 + 10;
    # selesai.
    # """
    if len(sys.argv) != 2:
        print("Usage: python syntax.py <source_code_file>")
        sys.exit(1)

    source_file = sys.argv[1]
    try:
        with open(source_file, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {source_file}")
        sys.exit(1)    
    # 1. Jalankan Lexer
    print("Menjalankan Lexer...")
    lexer = Lexer(dfa_path)
    try:
        tokens = lexer.tokenize(source_code)
        print("Tokenisasi berhasil:")
        for token in tokens:
            print(f"  {token}")
    except LexicalError as e:
        print(e)
        return

    print("\n" + "="*30 + "\n")

    # 2. Inisialisasi CFG (Parser)
    parser = CFG(tokens)
    
    # 3. Tambahkan Aturan Produksi
    parser.addRules(production_rules)
    # print(parser.production_rules)
    
    # 4. Mulai Parsing dari Non-Terminal <S>
    print("Menjalankan Parser...")
    try:
        parse_tree = parser.parse()
        
        if parse_tree and parser.currentToken().token_type == "EOF":
            print("\nParsing BERHASIL!")
            print("Parse Tree:")
            print(parse_tree) # Memanggil __str__ dari Node
        elif parse_tree:
             print("\nParsing GAGAL: Sisa token tidak habis.")
             print(f"Berhenti di token: {parser.currentToken()}")
             print("Parse Tree (parsial):")
             print(parse_tree)
        else:
            print("\nParsing GAGAL: Tidak bisa mem-parsing dari awal.")
            print(f"Token error di: {parser.currentToken()}")

    except Exception as e:
        print(f"\nTerjadi error saat parsing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()