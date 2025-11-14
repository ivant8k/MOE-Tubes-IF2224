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

# Penambahan Non-Terminal 
DeclarationPart = NonTerminal("<DeclarationPart>")
ConstDeclaration = NonTerminal("<ConstDeclaration>")
TypeDeclaration = NonTerminal("<TypeDeclaration>")
IdentifierList = NonTerminal("<IdentifierList>")
Range = NonTerminal("<Range>")
ArrayType = NonTerminal("<ArrayType>")
SubprogramDeclaration = NonTerminal("<SubprogramDeclaration>")
ProcedureDeclaration = NonTerminal("<ProcedureDeclaration>")
FunctionDeclaration = NonTerminal("<FunctionDeclaration>")
FormalParameterList = NonTerminal("<FormalParameterList>")
ParameterGroup = NonTerminal("<ParameterGroup>")
CompoundStatement = NonTerminal("<CompoundStatement>")
TermPrime = NonTerminal("<TermPrime>")
CompoundStatement = NonTerminal("<CompoundStatement>")
IfStatement = NonTerminal("<IfStatement>")
WhileStatement = NonTerminal("<WhileStatement>")
ForStatement = NonTerminal("<ForStatement>")
ProcedureCall = NonTerminal("<ProcedureCall>")
ParameterList = NonTerminal("<ParameterList>")
RelationalOperator = NonTerminal("<RelationalOperator>")
AdditiveOperator = NonTerminal("<AdditiveOperator>")
MultiplicativeOperator = NonTerminal("<MultiplicativeOperator>")

# Token Types (TokenType)
T_ID = TokenType("IDENTIFIER")
T_NUMBER = TokenType("NUMBER")
T_SEMI = TokenType("SEMICOLON")
T_COLON = TokenType("COLON")
T_ASSIGN = TokenType("ASSIGN_OPERATOR")
T_DOT = TokenType("DOT")
T_COMMA = TokenType("COMMA")
T_LPAREN = TokenType("LPARENTHESIS")
T_RPAREN = TokenType("RPARENTHESIS")
T_LBRACKET = TokenType("LBRACKET")
T_RBRACKET = TokenType("RBRACKET")

# Keywords and Specific Tokens (Token)
T_PROGRAM = Token("KEYWORD", "program")
T_KONSTANTA = Token("KEYWORD", "konstanta")
T_TIPE = Token("KEYWORD", "tipe")
T_VARIABEL = Token("KEYWORD", "variabel")
T_PROSEDUR = Token("KEYWORD", "prosedur")
T_FUNGSI = Token("KEYWORD", "fungsi")
T_MULAI = Token("KEYWORD", "mulai")
T_SELESAI = Token("KEYWORD", "selesai")
T_INTEGER = Token("KEYWORD", "integer")
T_REAL = Token("KEYWORD", "real")
T_BOOLEAN = Token("KEYWORD", "boolean")
T_CHAR = Token("KEYWORD", "char")
T_STRING = Token("KEYWORD", "string")
T_JIKA = Token("KEYWORD", "jika")
T_MAKA = Token("KEYWORD", "maka")
T_SELAINITU = Token("KEYWORD", "selain-itu")
T_SELAMA = Token("KEYWORD", "selama")
T_LAKUKAN = Token("KEYWORD", "lakukan")
T_UNTUK = Token("KEYWORD", "untuk")
T_KE = Token("KEYWORD", "ke")
T_TURUNKE = Token("KEYWORD", "turun-ke")
T_LARIK = Token("KEYWORD", "larik")
T_DARI = Token("KEYWORD", "dari")
T_DAN = Token("KEYWORD", "dan")
T_ATAU = Token("KEYWORD", "atau")
T_TIDAK = Token("KEYWORD", "tidak")


# Specific Tokens (Token)
T_PROGRAM = Token("KEYWORD", "program")
T_VARIABEL = Token("KEYWORD", "variabel")
T_MULAI = Token("KEYWORD", "mulai")
T_SELESAI = Token("KEYWORD", "selesai")
T_INTEGER = Token("KEYWORD", "integer")
T_BAGI = Token("ARITHMETIC_OPERATOR", "bagi")
T_LARIK = Token("KEYWORD", "larik")
T_REAL = Token("KEYWORD", "real")
T_BOOLEAN = Token("KEYWORD", "boolean")
T_CHAR = Token("KEYWORD", "char")
T_STRING = Token("KEYWORD", "string")

# operators
T_PLUS = Token("ARITHMETIC_OPERATOR", "+")
T_MINUS = Token("ARITHMETIC_OPERATOR", "-")
T_STAR = Token("ARITHMETIC_OPERATOR", "*")
T_SLASH = Token("ARITHMETIC_OPERATOR", "/")
T_EQ = Token("RELATIONAL_OPERATOR", "=")
T_NEQ = Token("RELATIONAL_OPERATOR", "<>")
T_LT = Token("RELATIONAL_OPERATOR", "<")
T_LTE = Token("RELATIONAL_OPERATOR", "<=")
T_GT = Token("RELATIONAL_OPERATOR", ">")
T_GTE = Token("RELATIONAL_OPERATOR", ">=")
T_RANGEOP = Token("RANGE_OPERATOR", "..")




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
        [ProgramHeader, DeclarationPart, CompoundStatement, T_DOT]
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
        [T_INTEGER],
        [T_REAL],
        [T_BOOLEAN],
        [T_CHAR],
        [T_STRING],
        [ArrayType]
    ],

    ArrayType: [[T_LARIK, T_LBRACKET, Range, T_RBRACKET, Type]],
    Range: [[Expression, T_RANGEOP, Expression]],
    
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
        [AssignmentStatement],
        [IfStatement],
        [WhileStatement],
        [ForStatement],
        [ProcedureCall],
        [CompoundStatement],
        [EPS]
    ],
    
    # <AssignmentStatement> -> IDENTIFIER := <Expression>
    AssignmentStatement: [
        [T_ID, T_ASSIGN, Expression],
        [T_ID, T_LBRACKET, Expression, T_RBRACKET, T_ASSIGN, Expression]

    ],

    #<IfStatement> -> if <Expression> then <Statement> else <Statement>
    IfStatement: [
        [T_JIKA, Expression, T_MAKA, Statement],
        [T_JIKA, Expression, T_MAKA, Statement, T_SELAINITU, Statement]
    ],

    #<WhileStatement> -> while <Expression> do <Statement>
    WhileStatement: [
        [T_SELAMA, Expression, T_LAKUKAN, Statement],
    ],
    
    # ----- Aturan Ekspresi Aritmatika -----
    # <Expression> -> <SimpleExpression>
    Expression: [
        [SimpleExpression, RelationalOperator, SimpleExpression],
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
        [T_ID, T_LBRACKET, Expression, T_RBRACKET],
        [T_ID, T_LPAREN, ParameterList, T_RPAREN],
        [T_ID, T_LPAREN, T_RPAREN],
        [T_NUMBER],
        # [T_STRINGLIT],
        # [T_CHARLIT],
        [T_LPAREN, Expression, T_RPAREN],
        [T_TIDAK, Factor]
    ],
    
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

    # Penambahan aturan lain dapat dilakukan di sini...
    DeclarationPart: [
        [ConstDeclaration, DeclarationPart],
        [TypeDeclaration, DeclarationPart],
        [VarDeclarationPart, DeclarationPart],
        [SubprogramDeclaration, DeclarationPart],
        [EPS]
    ],

    ConstDeclaration: [
        [T_KONSTANTA, IdentifierList, T_ASSIGN, Expression, T_SEMI],
    ],

    TypeDeclaration: [
        [T_TIPE, T_ID, T_ASSIGN, Type, T_SEMI]
    ],

    IdentifierList: [
        [T_ID, T_COMMA, IdentifierList],
        [T_ID]
    ],

    SubprogramDeclaration: [
        [ProcedureDeclaration],
        [FunctionDeclaration]
    ],

    ProcedureDeclaration: [
        [T_PROSEDUR, T_ID, T_LPAREN, FormalParameterList, T_RPAREN, T_SEMI,
         DeclarationPart, CompoundStatement, T_SEMI]
    ],

    FunctionDeclaration: [
        [T_FUNGSI, T_ID, T_LPAREN, FormalParameterList, T_RPAREN, T_COLON, Type, T_SEMI, DeclarationPart, CompoundStatement, T_SEMI]
    ],

    FormalParameterList: [
        [ParameterGroup, T_SEMI, FormalParameterList],
        [ParameterGroup],
        [EPS]
    ],

    ParameterGroup: [
        [IdentifierList, T_COLON, Type]
    ],


    CompoundStatement: [
        [T_MULAI, StatementList, T_SELESAI]
    ],

    ForStatement: [
        [T_UNTUK, T_ID, T_ASSIGN, Expression, T_KE, Expression, T_LAKUKAN, Statement],
        [T_UNTUK, T_ID, T_ASSIGN, Expression, T_TURUNKE, Expression, T_LAKUKAN, Statement]
    ],

    ProcedureCall: [
        [T_ID, T_LPAREN, ParameterList, T_RPAREN],
        [T_ID, T_LPAREN, T_RPAREN]
    ],

    ParameterList: [
        [Expression, T_COMMA, ParameterList],
        [Expression]
    ],

    RelationalOperator: [
        [T_EQ],
        [T_NEQ],
        [T_LT],
        [T_LTE],
        [T_GT],
        [T_GTE]
    ],

    AdditiveOperator: [
        [T_PLUS],
        [T_MINUS], 
        [T_ATAU]
    ],

    MultiplicativeOperator: [
        [T_STAR], [T_SLASH], [T_BAGI], [T_DAN]
    ],
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