# nama file: rules_spek.py
from models import NonTerminal, Token, TokenType, Epsilon
from typing import List, Dict, Union, Any

# Tipe data untuk kejelasan
Symbol = Union[NonTerminal, Token, TokenType, Epsilon]
Alternative = List[Symbol]
Production = List[Alternative]
RuleDict = Dict[NonTerminal, Production]

def setupProductionRules() -> RuleDict:
    """
    Mendefinisikan dan mengembalikan seluruh aturan produksi (CFG)
    untuk bahasa PASCAL-S Indonesia, disesuaikan dengan
    nama node dari Spesifikasi Milestone 2.
    """
    
    rules: RuleDict = {
        
        # --- Program & Block ---
        
        NonTerminal("<program>"): [
            [NonTerminal("<program-header>"), NonTerminal("<Block>"), Token("DOT", ".")]
        ],
        
        NonTerminal("<program-header>"): [
            [Token("KEYWORD", "program"), TokenType("IDENTIFIER"), Token("SEMICOLON", ";")]
        ],
        
        # <Block> adalah node internal, tidak ada di tabel spesifikasi
        # tapi penting untuk struktur
        NonTerminal("<Block>"): [
            [NonTerminal("<declaration-part>"), NonTerminal("<StatementPart>")]
        ],
        
        # --- Bagian Deklarasi ---
        
        NonTerminal("<declaration-part>"): [
            [NonTerminal("<const-declaration>"), NonTerminal("<type-declaration>"), NonTerminal("<var-declaration>"), NonTerminal("<SubprogDeclList>")]
        ],

        # Mengganti <ConstDeclOpt>
        NonTerminal("<const-declaration>"): [
            [Token("KEYWORD", "konstanta"), NonTerminal("<ConstList>")],
            [Epsilon()]
        ],
        
        # Node internal untuk rekursi
        NonTerminal("<ConstList>"): [
            [TokenType("IDENTIFIER"), Token("RELATIONAL_OPERATOR", "="), NonTerminal("<Constant>"), Token("SEMICOLON", ";"), NonTerminal("<ConstList>")],
            [Epsilon()]
        ],
        
        # Mengganti <TypeDeclOpt>
        NonTerminal("<type-declaration>"): [
            [Token("KEYWORD", "tipe"), NonTerminal("<TypeList>")],
            [Epsilon()]
        ],

        # Node internal untuk rekursi
        NonTerminal("<TypeList>"): [
            [TokenType("IDENTIFIER"), Token("RELATIONAL_OPERATOR", "="), NonTerminal("<type>"), Token("SEMICOLON", ";"), NonTerminal("<TypeList>")],
            [Epsilon()]
        ],

        # Mengganti <VarDeclOpt>
        NonTerminal("<var-declaration>"): [
            [Token("KEYWORD", "variabel"), NonTerminal("<VarDeclList>")],
            [Epsilon()]
        ],

        # Node internal untuk rekursi
        NonTerminal("<VarDeclList>"): [
            [NonTerminal("<VarDeclaration>"), Token("SEMICOLON", ";"), NonTerminal("<VarDeclList>")],
            [Epsilon()]
        ],
        
        # Node internal
        NonTerminal("<VarDeclaration>"): [
            [NonTerminal("<identifier-list>"), Token("COLON", ":"), NonTerminal("<type>")]
        ],

        NonTerminal("<identifier-list>"): [
            [TokenType("IDENTIFIER"), NonTerminal("<IdentifierListPrime>")]
        ],

        # Node internal
        NonTerminal("<IdentifierListPrime>"): [
            [Token("COMMA", ","), TokenType("IDENTIFIER"), NonTerminal("<IdentifierListPrime>")],
            [Epsilon()]
        ],
        
        # --- Definisi Tipe ---

        NonTerminal("<type>"): [
            [NonTerminal("<SimpleType>")],
            [NonTerminal("<array-type>")],
            [NonTerminal("<RecordType>")]
        ],
        
        # Node internal
        NonTerminal("<SimpleType>"): [
            [Token("KEYWORD", "integer")],
            [Token("KEYWORD", "real")],
            [Token("KEYWORD", "boolean")],
            [Token("KEYWORD", "char")],
            [TokenType("IDENTIFIER")]
        ],

        NonTerminal("<array-type>"): [
            [Token("KEYWORD", "larik"), Token("LBRACKET", "["), NonTerminal("<range>"), Token("RBRACKET", "]"), Token("KEYWORD", "dari"), NonTerminal("<type>")]
        ],
        
        # Node internal (dari diagram)
        NonTerminal("<RecordType>"): [
            [Token("KEYWORD", "rekaman"), NonTerminal("<var-declaration>"), Token("KEYWORD", "selesai")]
        ],

        NonTerminal("<range>"): [
            [NonTerminal("<Constant>"), Token("RANGE_OPERATOR", ".."), NonTerminal("<Constant>")]
        ],
        
        # --- Konstanta (Node Internal) ---
        
        NonTerminal("<Constant>"): [
            [NonTerminal("<SignOpt>"), NonTerminal("<UnsignedConstant>")],
            [TokenType("STRING_LITERAL")],
            [TokenType("CHAR_LITERAL")],
            [Token("KEYWORD", "true")],
            [Token("KEYWORD", "false")]
        ],
        NonTerminal("<UnsignedConstant>"): [
            [TokenType("NUMBER")],
            [TokenType("IDENTIFIER")]
        ],
        NonTerminal("<SignOpt>"): [
            [NonTerminal("<Sign>")],
            [Epsilon()]
        ],
        NonTerminal("<Sign>"): [
            [Token("ARITHMETIC_OPERATOR", "+")],
            [Token("ARITHMETIC_OPERATOR", "-")]
        ],

        # --- Deklarasi Subprogram ---
        
        # Node internal
        NonTerminal("<SubprogDeclList>"): [
            [NonTerminal("<subprogram-declaration>"), Token("SEMICOLON", ";"), NonTerminal("<SubprogDeclList>")],
            [Epsilon()]
        ],

        NonTerminal("<subprogram-declaration>"): [
            [NonTerminal("<procedure-declaration>")],
            [NonTerminal("<function-declaration>")]
        ],

        NonTerminal("<procedure-declaration>"): [
            [Token("KEYWORD", "prosedur"), TokenType("IDENTIFIER"), NonTerminal("<FormalParamOpt>"), Token("SEMICOLON", ";"), NonTerminal("<Block>")]
        ],

        NonTerminal("<function-declaration>"): [
            [Token("KEYWORD", "fungsi"), TokenType("IDENTIFIER"), NonTerminal("<FormalParamOpt>"), Token("COLON", ":"), NonTerminal("<SimpleType>"), Token("SEMICOLON", ";"), NonTerminal("<Block>")]
        ],
        
        # Node internal
        NonTerminal("<FormalParamOpt>"): [
            [NonTerminal("<formal-parameter-list>")],
            [Epsilon()]
        ],

        NonTerminal("<formal-parameter-list>"): [
            [Token("LPARENTHESIS", "("), NonTerminal("<ParamSectionList>"), Token("RPARENTHESIS", ")")]
        ],

        # Node internal
        NonTerminal("<ParamSectionList>"): [
            [NonTerminal("<ParamSection>"), NonTerminal("<ParamSectionListPrime>")]
        ],
        # Node internal
        NonTerminal("<ParamSectionListPrime>"): [
            [Token("SEMICOLON", ";"), NonTerminal("<ParamSection>"), NonTerminal("<ParamSectionListPrime>")],
            [Epsilon()]
        ],
        # Node internal
        NonTerminal("<ParamSection>"): [
            [NonTerminal("<VarKeywordOpt>"), NonTerminal("<identifier-list>"), Token("COLON", ":"), NonTerminal("<SimpleType>")]
        ],
        # Node internal
        NonTerminal("<VarKeywordOpt>"): [
            [Token("KEYWORD", "variabel")],
            [Epsilon()]
        ],

        # --- Bagian Statement ---
        
        # Node internal
        NonTerminal("<StatementPart>"): [
            [NonTerminal("<compound-statement>")]
        ],

        NonTerminal("<compound-statement>"): [
            [Token("KEYWORD", "mulai"), NonTerminal("<statement-list>"), Token("KEYWORD", "selesai")]
        ],

        NonTerminal("<statement-list>"): [
            [NonTerminal("<Statement>"), NonTerminal("<StatementListPrime>")],
            [Epsilon()]
        ],
        
        # Node internal
        NonTerminal("<StatementListPrime>"): [
            [Token("SEMICOLON", ";"), NonTerminal("<Statement>"), NonTerminal("<StatementListPrime>")],
            [Epsilon()]
        ],
        
        # Node internal
        NonTerminal("<Statement>"): [
            # Urutan ini penting untuk backtracking:
            # Coba <assignment-statement> dulu. Jika gagal,
            # parser akan reset dan coba <procedure/function-call>.
            [NonTerminal("<assignment-statement>")],
            [NonTerminal("<procedure/function-call>")],
            [NonTerminal("<compound-statement>")],
            [NonTerminal("<if-statement>")],
            [NonTerminal("<while-statement>")],
            [NonTerminal("<for-statement>")],
            [NonTerminal("<RepeatStatement>")],
            [NonTerminal("<CaseStatement>")],
            [Epsilon()]
        ],
        
        # --- Jenis-jenis Statement ---

        NonTerminal("<assignment-statement>"): [
            [TokenType("IDENTIFIER"), NonTerminal("<VariableTail>"), Token("ASSIGN_OPERATOR", ":="), NonTerminal("<expression>")]
        ],

        # PERUBAHAN: Mengganti <ProcedureCall>
        # Mengikuti Revisi 2 (penggabungan) dan Revisi 3 (wajib parens)
        # Aturan ini sekarang mewajibkan <parameter-list> (yang punya parens)
        # tidak seperti <ParameterListOpt> (yang opsional).
        NonTerminal("<procedure/function-call>"): [
            [TokenType("IDENTIFIER"), NonTerminal("<parameter-list>")]
        ],

        NonTerminal("<if-statement>"): [
            [Token("KEYWORD", "jika"), NonTerminal("<expression>"), Token("KEYWORD", "maka"), NonTerminal("<Statement>"), NonTerminal("<ElsePart>")]
        ],
        
        # Node internal
        NonTerminal("<ElsePart>"): [
            [Token("KEYWORD", "selain-itu"), NonTerminal("<Statement>")],
            [Epsilon()]
        ],

        NonTerminal("<while-statement>"): [
            [Token("KEYWORD", "selama"), NonTerminal("<expression>"), Token("KEYWORD", "lakukan"), NonTerminal("<Statement>")]
        ],
        
        # Node internal (dari diagram)
        NonTerminal("<RepeatStatement>"): [
            [Token("KEYWORD", "ulangi"), NonTerminal("<statement-list>"), Token("KEYWORD", "sampai"), NonTerminal("<expression>")]
        ],

        NonTerminal("<for-statement>"): [
            [Token("KEYWORD", "untuk"), TokenType("IDENTIFIER"), Token("ASSIGN_OPERATOR", ":="), NonTerminal("<expression>"), NonTerminal("<ForDirection>"), NonTerminal("<expression>"), Token("KEYWORD", "lakukan"), NonTerminal("<Statement>")]
        ],
        
        # Node internal
        NonTerminal("<ForDirection>"): [
            [Token("KEYWORD", "ke")],
            [Token("KEYWORD", "turun-ke")]
        ],
        
        # Node internal (dari diagram)
        NonTerminal("<CaseStatement>"): [
            [Token("KEYWORD", "kasus"), NonTerminal("<expression>"), Token("KEYWORD", "dari"), NonTerminal("<CaseList>"), NonTerminal("<CaseEndOpt>"), Token("KEYWORD", "selesai")]
        ],
        # Node internal
        NonTerminal("<CaseList>"): [
            [NonTerminal("<CaseElement>"), NonTerminal("<CaseListPrime>")]
        ],
        # Node internal
        NonTerminal("<CaseListPrime>"): [
            [Token("SEMICOLON", ";"), NonTerminal("<CaseElement>"), NonTerminal("<CaseListPrime>")],
            [Epsilon()]
        ],
        # Node internal
        NonTerminal("<CaseEndOpt>"): [
            [Token("SEMICOLON", ";")],
            [Epsilon()]
        ],
        # Node internal
        NonTerminal("<CaseElement>"): [
            [NonTerminal("<Constant>"), Token("COLON", ":"), NonTerminal("<Statement>")]
        ],
        
        # --- Parameter Aktual ---
        
        # PERUBAHAN: Menghapus <ParameterListOpt> karena Revisi 3
        # <parameter-list> sekarang mencakup parens
        NonTerminal("<parameter-list>"): [
            [Token("LPARENTHESIS", "("), NonTerminal("<ExpressionListOpt>"), Token("RPARENTHESIS", ")")]
        ],
        
        # Node internal baru untuk menangani list ekspresi opsional di DALAM parens
        NonTerminal("<ExpressionListOpt>"): [
            [NonTerminal("<ExpressionList>")],
            [Epsilon()]
        ],

        # Node internal (diubah dari <ExpressionList> lama)
        NonTerminal("<ExpressionList>"): [
            [NonTerminal("<expression>"), NonTerminal("<ExpressionListPrime>")]
        ],
        
        # Node internal
        NonTerminal("<ExpressionListPrime>"): [
            [Token("COMMA", ","), NonTerminal("<expression>"), NonTerminal("<ExpressionListPrime>")],
            [Epsilon()]
        ],
        
        # --- Ekspresi ---
        
        NonTerminal("<expression>"): [
            [NonTerminal("<simple-expression>"), NonTerminal("<ExpressionPrime>")]
        ],
        # Node internal
        NonTerminal("<ExpressionPrime>"): [
            [NonTerminal("<relational-operator>"), NonTerminal("<simple-expression>")],
            [Epsilon()]
        ],

        NonTerminal("<simple-expression>"): [
            [NonTerminal("<SignedTerm>"), NonTerminal("<SimpleExpressionPrime>")]
        ],
        # Node internal
        NonTerminal("<SignedTerm>"): [
            [NonTerminal("<SignOpt>"), NonTerminal("<term>")]
        ],
        # Node internal
        NonTerminal("<SimpleExpressionPrime>"): [
            [NonTerminal("<additive-operator>"), NonTerminal("<term>"), NonTerminal("<SimpleExpressionPrime>")],
            [Epsilon()]
        ],

        NonTerminal("<term>"): [
            [NonTerminal("<factor>"), NonTerminal("<TermPrime>")]
        ],
        # Node internal
        NonTerminal("<TermPrime>"): [
            [NonTerminal("<multiplicative-operator>"), NonTerminal("<factor>"), NonTerminal("<TermPrime>")],
            [Epsilon()]
        ],
        
        # --- Factor & Variable (Left-Factored) ---

        NonTerminal("<factor>"): [
            # Ini adalah left-factoring untuk membedakan Var vs Func call
            [TokenType("IDENTIFIER"), NonTerminal("<FactorTail>")], 
            [NonTerminal("<Constant>")],
            [Token("LPARENTHESIS", "("), NonTerminal("<expression>"), Token("RPARENTHESIS", ")")],
            [Token("LOGICAL_OPERATOR", "tidak"), NonTerminal("<factor>")]
        ],
        
        # Node internal krusial untuk left-factoring
        # Membedakan antara Panggilan Fungsi (wajib parens) vs Variabel
        NonTerminal("<FactorTail>"): [
            [NonTerminal("<parameter-list>")], # Coba cocokkan sbg Panggilan Fungsi dulu
            [NonTerminal("<VariableTail>")]    # Jika gagal, anggap sbg Variabel (bisa Epsilon)
        ],

        # Node internal
        NonTerminal("<VariableTail>"): [
            [Token("LBRACKET", "["), NonTerminal("<expression>"), Token("RBRACKET", "]"), NonTerminal("<VariableTail>")],
            [Token("DOT", "."), TokenType("IDENTIFIER"), NonTerminal("<VariableTail>")],
            [Epsilon()]
        ],
        
        # --- Kategori Operator ---
        
        NonTerminal("<relational-operator>"): [
            [Token("RELATIONAL_OPERATOR", "=")],
            [Token("RELATIONAL_OPERATOR", "<>")],
            [Token("RELATIONAL_OPERATOR", "<")],
            [Token("RELATIONAL_OPERATOR", "<=")],
            [Token("RELATIONAL_OPERATOR", ">")],
            [Token("RELATIONAL_OPERATOR", ">=")],
        ],
        
        NonTerminal("<additive-operator>"): [
            [Token("ARITHMETIC_OPERATOR", "+")],
            [Token("ARITHMETIC_OPERATOR", "-")],
            [Token("LOGICAL_OPERATOR", "atau")]
        ],
        
        NonTerminal("<multiplicative-operator>"): [
            [Token("ARITHMETIC_OPERATOR", "*")],
            [Token("ARITHMETIC_OPERATOR", "/")],
            [Token("ARITHMETIC_OPERATOR", "bagi")],
            [Token("ARITHMETIC_OPERATOR", "mod")],
            [Token("LOGICAL_OPERATOR", "dan")]
        ],
    }
    
    return rules