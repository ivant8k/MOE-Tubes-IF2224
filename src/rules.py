# nama file: rules.py
from models import NonTerminal, Token, TokenType, Epsilon
from typing import List, Dict, Union, Any

# Tipe data untuk kejelasan, meskipun tidak divalidasi oleh 'models.py'
Symbol = Union[NonTerminal, Token, TokenType, Epsilon]
Alternative = List[Symbol]
Production = List[Alternative]
RuleDict = Dict[NonTerminal, Production]

def setupProductionRules() -> RuleDict:
    """
    Mendefinisikan dan mengembalikan seluruh aturan produksi (CFG)
    untuk bahasa PASCAL-S dalam format yang diharapkan oleh parser CFG.
    
    Telah dilakukan Left-Factoring pada <Factor> dan <AssignmentStatement>
    untuk menangani ambiguitas 'IDENTIFIER' (variabel vs. fungsi).
    """
    
    rules: RuleDict = {
        
        # --- Program & Block ---
        
        # <Program> ::= <ProgramHeader> <Block> DOT(.)
        NonTerminal("<Program>"): [
            [NonTerminal("<ProgramHeader>"), NonTerminal("<Block>"), Token("DOT", ".")]
        ],
        
        # <ProgramHeader> ::= KEYWORD(program) IDENTIFIER SEMICOLON(;)
        NonTerminal("<ProgramHeader>"): [
            [Token("KEYWORD", "program"), TokenType("IDENTIFIER"), Token("SEMICOLON", ";")]
        ],
        
        # <Block> ::= <DeclarationPart> <StatementPart>
        NonTerminal("<Block>"): [
            [NonTerminal("<DeclarationPart>"), NonTerminal("<StatementPart>")]
        ],
        
        # --- Bagian Deklarasi ---
        
        # <DeclarationPart> ::= <ConstDeclOpt> <TypeDeclOpt> <VarDeclOpt> <SubprogDeclList>
        NonTerminal("<DeclarationPart>"): [
            [NonTerminal("<ConstDeclOpt>"), NonTerminal("<TypeDeclOpt>"), NonTerminal("<VarDeclOpt>"), NonTerminal("<SubprogDeclList>")]
        ],

        # <ConstDeclOpt> ::= KEYWORD(konstanta) <ConstList> | <Epsilon>
        NonTerminal("<ConstDeclOpt>"): [
            [Token("KEYWORD", "konstanta"), NonTerminal("<ConstList>")],
            [Epsilon()]
        ],

        # <ConstList> ::= IDENTIFIER RELATIONAL_OPERATOR(=) <Constant> SEMICOLON(;) <ConstList> | <Epsilon>
        NonTerminal("<ConstList>"): [
            [TokenType("IDENTIFIER"), Token("RELATIONAL_OPERATOR", "="), NonTerminal("<Constant>"), Token("SEMICOLON", ";"), NonTerminal("<ConstList>")],
            [Epsilon()]
        ],
        
        # <TypeDeclOpt> ::= KEYWORD(tipe) <TypeList> | <Epsilon>
        NonTerminal("<TypeDeclOpt>"): [
            [Token("KEYWORD", "tipe"), NonTerminal("<TypeList>")],
            [Epsilon()]
        ],

        # <TypeList> ::= IDENTIFIER RELATIONAL_OPERATOR(=) <Type> SEMICOLON(;) <TypeList> | <Epsilon>
        NonTerminal("<TypeList>"): [
            [TokenType("IDENTIFIER"), Token("RELATIONAL_OPERATOR", "="), NonTerminal("<Type>"), Token("SEMICOLON", ";"), NonTerminal("<TypeList>")],
            [Epsilon()]
        ],

        # <VarDeclOpt> ::= KEYWORD(variabel) <VarDeclList> | <Epsilon>
        NonTerminal("<VarDeclOpt>"): [
            [Token("KEYWORD", "variabel"), NonTerminal("<VarDeclList>")],
            [Epsilon()]
        ],

        # <VarDeclList> ::= <VarDeclaration> SEMICOLON(;) <VarDeclList> | <Epsilon>
        NonTerminal("<VarDeclList>"): [
            [NonTerminal("<VarDeclaration>"), Token("SEMICOLON", ";"), NonTerminal("<VarDeclList>")],
            [Epsilon()]
        ],

        # <VarDeclaration> ::= <IdentifierList> COLON(:) <Type>
        NonTerminal("<VarDeclaration>"): [
            [NonTerminal("<IdentifierList>"), Token("COLON", ":"), NonTerminal("<Type>")]
        ],

        # <IdentifierList> ::= IDENTIFIER <IdentifierListPrime>
        NonTerminal("<IdentifierList>"): [
            [TokenType("IDENTIFIER"), NonTerminal("<IdentifierListPrime>")]
        ],

        # <IdentifierListPrime> ::= COMMA(,) IDENTIFIER <IdentifierListPrime> | <Epsilon>
        NonTerminal("<IdentifierListPrime>"): [
            [Token("COMMA", ","), TokenType("IDENTIFIER"), NonTerminal("<IdentifierListPrime>")],
            [Epsilon()]
        ],
        
        # --- Definisi Tipe ---

        # <Type> ::= <SimpleType> | <ArrayType> | <RecordType>
        NonTerminal("<Type>"): [
            [NonTerminal("<SimpleType>")],
            [NonTerminal("<ArrayType>")],
            [NonTerminal("<RecordType>")]
        ],

        # <SimpleType> ::= KEYWORD(integer) | KEYWORD(real) | ... | IDENTIFIER
        NonTerminal("<SimpleType>"): [
            [Token("KEYWORD", "integer")],
            [Token("KEYWORD", "real")],
            [Token("KEYWORD", "boolean")],
            [Token("KEYWORD", "char")],
            [TokenType("IDENTIFIER")] # Tipe kustom
        ],

        # <ArrayType> ::= KEYWORD(larik) LBRACKET([) <Range> RBRACKET(]) KEYWORD(dari) <Type>
        NonTerminal("<ArrayType>"): [
            [Token("KEYWORD", "larik"), Token("LBRACKET", "["), NonTerminal("<Range>"), Token("RBRACKET", "]"), Token("KEYWORD", "dari"), NonTerminal("<Type>")]
        ],

        # <RecordType> ::= KEYWORD(rekaman) <VarDeclOpt> KEYWORD(selesai)
        NonTerminal("<RecordType>"): [
            [Token("KEYWORD", "rekaman"), NonTerminal("<VarDeclOpt>"), Token("KEYWORD", "selesai")]
        ],

        # <Range> ::= <Constant> RANGE_OPERATOR(..) <Constant>
        NonTerminal("<Range>"): [
            [NonTerminal("<Constant>"), Token("RANGE_OPERATOR", ".."), NonTerminal("<Constant>")]
        ],
        
        # --- Konstanta ---
        
        # <Constant> ::= <SignOpt> <UnsignedConstant> | STRING_LITERAL | CHAR_LITERAL | KEYWORD(true) | KEYWORD(false)
        NonTerminal("<Constant>"): [
            [NonTerminal("<SignOpt>"), NonTerminal("<UnsignedConstant>")],
            [TokenType("STRING_LITERAL")],
            [TokenType("CHAR_LITERAL")],
            [Token("KEYWORD", "true")],
            [Token("KEYWORD", "false")]
        ],
        
        # <UnsignedConstant> ::= NUMBER | IDENTIFIER
        NonTerminal("<UnsignedConstant>"): [
            [TokenType("NUMBER")],
            [TokenType("IDENTIFIER")] # Konstanta yg didefinisikan
        ],
        
        # <SignOpt> ::= <Sign> | <Epsilon>
        NonTerminal("<SignOpt>"): [
            [NonTerminal("<Sign>")],
            [Epsilon()]
        ],
        
        # <Sign> ::= ARITHMETIC_OPERATOR(+) | ARITHMETIC_OPERATOR(-)
        NonTerminal("<Sign>"): [
            [Token("ARITHMETIC_OPERATOR", "+")],
            [Token("ARITHMETIC_OPERATOR", "-")]
        ],

        # --- Deklarasi Subprogram ---
        
        # <SubprogDeclList> ::= <SubprogramDeclaration> SEMICOLON(;) <SubprogDeclList> | <Epsilon>
        NonTerminal("<SubprogDeclList>"): [
            [NonTerminal("<SubprogramDeclaration>"), Token("SEMICOLON", ";"), NonTerminal("<SubprogDeclList>")],
            [Epsilon()]
        ],

        # <SubprogramDeclaration> ::= <ProcedureDeclaration> | <FunctionDeclaration>
        NonTerminal("<SubprogramDeclaration>"): [
            [NonTerminal("<ProcedureDeclaration>")],
            [NonTerminal("<FunctionDeclaration>")]
        ],

        # <ProcedureDeclaration> ::= KEYWORD(prosedur) IDENTIFIER <FormalParamOpt> SEMICOLON(;) <Block>
        NonTerminal("<ProcedureDeclaration>"): [
            [Token("KEYWORD", "prosedur"), TokenType("IDENTIFIER"), NonTerminal("<FormalParamOpt>"), Token("SEMICOLON", ";"), NonTerminal("<Block>")]
        ],

        # <FunctionDeclaration> ::= KEYWORD(fungsi) IDENTIFIER <FormalParamOpt> COLON(:) <SimpleType> SEMICOLON(;) <Block>
        NonTerminal("<FunctionDeclaration>"): [
            [Token("KEYWORD", "fungsi"), TokenType("IDENTIFIER"), NonTerminal("<FormalParamOpt>"), Token("COLON", ":"), NonTerminal("<SimpleType>"), Token("SEMICOLON", ";"), NonTerminal("<Block>")]
        ],

        # <FormalParamOpt> ::= <FormalParameterList> | <Epsilon>
        NonTerminal("<FormalParamOpt>"): [
            [NonTerminal("<FormalParameterList>")],
            [Epsilon()]
        ],

        # <FormalParameterList> ::= LPARENTHESIS(() <ParamSectionList> RPARENTHESIS())
        NonTerminal("<FormalParameterList>"): [
            [Token("LPARENTHESIS", "("), NonTerminal("<ParamSectionList>"), Token("RPARENTHESIS", ")")]
        ],

        # <ParamSectionList> ::= <ParamSection> <ParamSectionListPrime>
        NonTerminal("<ParamSectionList>"): [
            [NonTerminal("<ParamSection>"), NonTerminal("<ParamSectionListPrime>")]
        ],

        # <ParamSectionListPrime> ::= SEMICOLON(;) <ParamSection> <ParamSectionListPrime> | <Epsilon>
        NonTerminal("<ParamSectionListPrime>"): [
            [Token("SEMICOLON", ";"), NonTerminal("<ParamSection>"), NonTerminal("<ParamSectionListPrime>")],
            [Epsilon()]
        ],

        # <ParamSection> ::= <VarKeywordOpt> <IdentifierList> COLON(:) <SimpleType>
        NonTerminal("<ParamSection>"): [
            [NonTerminal("<VarKeywordOpt>"), NonTerminal("<IdentifierList>"), Token("COLON", ":"), NonTerminal("<SimpleType>")]
        ],

        # <VarKeywordOpt> ::= KEYWORD(variabel) | <Epsilon>
        NonTerminal("<VarKeywordOpt>"): [
            [Token("KEYWORD", "variabel")],
            [Epsilon()]
        ],

        # --- Bagian Statement ---
        
        # <StatementPart> ::= <CompoundStatement>
        NonTerminal("<StatementPart>"): [
            [NonTerminal("<CompoundStatement>")]
        ],

        # <CompoundStatement> ::= KEYWORD(mulai) <StatementList> KEYWORD(selesai)
        NonTerminal("<CompoundStatement>"): [
            [Token("KEYWORD", "mulai"), NonTerminal("<StatementList>"), Token("KEYWORD", "selesai")]
        ],

        # <StatementList> ::= <Statement> <StatementListPrime> | <Epsilon>
        NonTerminal("<StatementList>"): [
            [NonTerminal("<Statement>"), NonTerminal("<StatementListPrime>")],
            [Epsilon()] # Mengizinkan blok mulai...selesai kosong
        ],

        # <StatementListPrime> ::= SEMICOLON(;) <Statement> <StatementListPrime> | <Epsilon>
        NonTerminal("<StatementListPrime>"): [
            [Token("SEMICOLON", ";"), NonTerminal("<Statement>"), NonTerminal("<StatementListPrime>")],
            [Epsilon()]
        ],

        # <Statement> ::= <AssignmentStatement> | <ProcedureCall> | ... | <Epsilon>
        NonTerminal("<Statement>"): [
            [NonTerminal("<AssignmentStatement>")],
            [NonTerminal("<ProcedureCall>")],
            [NonTerminal("<CompoundStatement>")],
            [NonTerminal("<IfStatement>")],
            [NonTerminal("<WhileStatement>")],
            [NonTerminal("<ForStatement>")],
            [NonTerminal("<RepeatStatement>")],
            [NonTerminal("<CaseStatement>")],
            [Epsilon()] # Statement kosong
        ],
        
        # --- Jenis-jenis Statement ---

        # <AssignmentStatement> ::= IDENTIFIER <VariableTail> ASSIGN_OPERATOR(:=) <Expression>
        # (Telah di-left-factor, <Variable> di-inline-kan)
        NonTerminal("<AssignmentStatement>"): [
            [TokenType("IDENTIFIER"), NonTerminal("<VariableTail>"), Token("ASSIGN_OPERATOR", ":="), NonTerminal("<Expression>")]
        ],

        # <ProcedureCall> ::= IDENTIFIER <ParameterListOpt>
        NonTerminal("<ProcedureCall>"): [
            [TokenType("IDENTIFIER"), NonTerminal("<ParameterListOpt>")]
        ],

        # <IfStatement> ::= KEYWORD(jika) <Expression> KEYWORD(maka) <Statement> <ElsePart>
        NonTerminal("<IfStatement>"): [
            [Token("KEYWORD", "jika"), NonTerminal("<Expression>"), Token("KEYWORD", "maka"), NonTerminal("<Statement>"), NonTerminal("<ElsePart>")]
        ],

        # <ElsePart> ::= KEYWORD(selain-itu) <Statement> | <Epsilon>
        NonTerminal("<ElsePart>"): [
            [Token("IDENTIFIER", "selain"), Token("ARITHMETIC_OPERATOR", "-"), Token("IDENTIFIER", "itu"), NonTerminal("<Statement>")],
            [Epsilon()]
        ],

        # <WhileStatement> ::= KEYWORD(selama) <Expression> KEYWORD(lakukan) <Statement>
        NonTerminal("<WhileStatement>"): [
            [Token("KEYWORD", "selama"), NonTerminal("<Expression>"), Token("KEYWORD", "lakukan"), NonTerminal("<Statement>")]
        ],

        # <RepeatStatement> ::= KEYWORD(ulangi) <StatementList> KEYWORD(sampai) <Expression>
        NonTerminal("<RepeatStatement>"): [
            [Token("KEYWORD", "ulangi"), NonTerminal("<StatementList>"), Token("KEYWORD", "sampai"), NonTerminal("<Expression>")]
        ],

        # <ForStatement> ::= KEYWORD(untuk) IDENTIFIER ASSIGN_OPERATOR(:=) <Expression> <ForDirection> <Expression> KEYWORD(lakukan) <Statement>
        NonTerminal("<ForStatement>"): [
            [Token("KEYWORD", "untuk"), TokenType("IDENTIFIER"), Token("ASSIGN_OPERATOR", ":="), NonTerminal("<Expression>"), NonTerminal("<ForDirection>"), NonTerminal("<Expression>"), Token("KEYWORD", "lakukan"), NonTerminal("<Statement>")]
        ],

        # <ForDirection> ::= KEYWORD(ke) | KEYWORD(turun-ke)
        NonTerminal("<ForDirection>"): [
            [Token("KEYWORD", "ke")],
            [Token("IDENTIFIER", "turun"), Token("ARITHMETIC_OPERATOR", "-"), Token("KEYWORD", "ke")]
        ],

        # <CaseStatement> ::= KEYWORD(kasus) <Expression> KEYWORD(dari) <CaseList> <CaseEndOpt> KEYWORD(selesai)
        NonTerminal("<CaseStatement>"): [
            [Token("KEYWORD", "kasus"), NonTerminal("<Expression>"), Token("KEYWORD", "dari"), NonTerminal("<CaseList>"), NonTerminal("<CaseEndOpt>"), Token("KEYWORD", "selesai")]
        ],

        # <CaseList> ::= <CaseElement> <CaseListPrime>
        NonTerminal("<CaseList>"): [
            [NonTerminal("<CaseElement>"), NonTerminal("<CaseListPrime>")]
        ],

        # <CaseListPrime> ::= SEMICOLON(;) <CaseElement> <CaseListPrime> | <Epsilon>
        NonTerminal("<CaseListPrime>"): [
            [Token("SEMICOLON", ";"), NonTerminal("<CaseElement>"), NonTerminal("<CaseListPrime>")],
            [Epsilon()]
        ],

        # <CaseEndOpt> ::= SEMICOLON(;) | <Epsilon> (Untuk ; sebelum 'selesai')
        NonTerminal("<CaseEndOpt>"): [
            [Token("SEMICOLON", ";")],
            [Epsilon()]
        ],

        # <CaseElement> ::= <Constant> COLON(:) <Statement>
        NonTerminal("<CaseElement>"): [
            [NonTerminal("<Constant>"), Token("COLON", ":"), NonTerminal("<Statement>")]
        ],
        
        # --- Parameter Aktual ---
        
        # <ParameterListOpt> ::= <ParameterList> | <Epsilon>
        NonTerminal("<ParameterListOpt>"): [
            [NonTerminal("<ParameterList>")],
            [Epsilon()]
        ],

        # <ParameterList> ::= LPARENTHESIS(() <ExpressionList> RPARENTHESIS())
        NonTerminal("<ParameterList>"): [
            [Token("LPARENTHESIS", "("), NonTerminal("<ExpressionList>"), Token("RPARENTHESIS", ")")]
        ],

        # <ExpressionList> ::= <Expression> <ExpressionListPrime>
        NonTerminal("<ExpressionList>"): [
            [NonTerminal("<Expression>"), NonTerminal("<ExpressionListPrime>")]
        ],

        # <ExpressionListPrime> ::= COMMA(,) <Expression> <ExpressionListPrime> | <Epsilon>
        NonTerminal("<ExpressionListPrime>"): [
            [Token("COMMA", ","), NonTerminal("<Expression>"), NonTerminal("<ExpressionListPrime>")],
            [Epsilon()]
        ],
        
        # --- Ekspresi ---
        
        # <Expression> ::= <SimpleExpression> <ExpressionPrime>
        NonTerminal("<Expression>"): [
            [NonTerminal("<SimpleExpression>"), NonTerminal("<ExpressionPrime>")]
        ],

        # <ExpressionPrime> ::= <RelationalOperator> <SimpleExpression> | <Epsilon>
        NonTerminal("<ExpressionPrime>"): [
            [NonTerminal("<RelationalOperator>"), NonTerminal("<SimpleExpression>")],
            [Epsilon()]
        ],

        # <SimpleExpression> ::= <SignedTerm> <SimpleExpressionPrime>
        NonTerminal("<SimpleExpression>"): [
            [NonTerminal("<SignedTerm>"), NonTerminal("<SimpleExpressionPrime>")]
        ],
        
        # <SignedTerm> ::= <SignOpt> <Term>
        NonTerminal("<SignedTerm>"): [
            [NonTerminal("<SignOpt>"), NonTerminal("<Term>")]
        ],

        # <SimpleExpressionPrime> ::= <AdditiveOperator> <Term> <SimpleExpressionPrime> | <Epsilon>
        NonTerminal("<SimpleExpressionPrime>"): [
            [NonTerminal("<AdditiveOperator>"), NonTerminal("<Term>"), NonTerminal("<SimpleExpressionPrime>")],
            [Epsilon()]
        ],

        # <Term> ::= <Factor> <TermPrime>
        NonTerminal("<Term>"): [
            [NonTerminal("<Factor>"), NonTerminal("<TermPrime>")]
        ],

        # <TermPrime> ::= <MultiplicativeOperator> <Factor> <TermPrime> | <Epsilon>
        NonTerminal("<TermPrime>"): [
            [NonTerminal("<MultiplicativeOperator>"), NonTerminal("<Factor>"), NonTerminal("<TermPrime>")],
            [Epsilon()]
        ],
        
        # --- Factor & Variable (Sudah di-Left-Factor) ---

        # <Factor> ::= IDENTIFIER <FactorTail> | <Constant> | ( <Expression> ) | 'tidak' <Factor>
        NonTerminal("<Factor>"): [
            [TokenType("IDENTIFIER"), NonTerminal("<FactorTail>")], # Variabel ATAU Panggilan Fungsi
            [NonTerminal("<Constant>")],
            [Token("LPARENTHESIS", "("), NonTerminal("<Expression>"), Token("RPARENTHESIS", ")")],
            [Token("LOGICAL_OPERATOR", "tidak"), NonTerminal("<Factor>")]
        ],
        
        # <FactorTail> ::= <ParameterList> | <VariableTail>
        # Memisahkan antara Panggilan Fungsi (butuh parameter list) vs Variabel
        NonTerminal("<FactorTail>"): [
            [NonTerminal("<ParameterList>")], # Coba cocokkan sbg Panggilan Fungsi dulu
            [NonTerminal("<VariableTail>")]  # Jika gagal, anggap sbg Variabel (bisa Epsilon)
        ],

        # <VariableTail> ::= LBRACKET ... <VariableTail> | DOT ... <VariableTail> | <Epsilon>
        # (Mendefinisikan akses array/record secara rekursif)
        NonTerminal("<VariableTail>"): [
            [Token("LBRACKET", "["), NonTerminal("<Expression>"), Token("RBRACKET", "]"), NonTerminal("<VariableTail>")],
            [Token("DOT", "."), TokenType("IDENTIFIER"), NonTerminal("<VariableTail>")],
            [Epsilon()]
        ],
        
        # --- Kategori Operator ---
        
        # <RelationalOperator> ::= = | <> | < | <= | > | >=
        NonTerminal("<RelationalOperator>"): [
            [Token("RELATIONAL_OPERATOR", "=")],
            [Token("RELATIONAL_OPERATOR", "<>")],
            [Token("RELATIONAL_OPERATOR", "<")],
            [Token("RELATIONAL_OPERATOR", "<=")],
            [Token("RELATIONAL_OPERATOR", ">")],
            [Token("RELATIONAL_OPERATOR", ">=")],
        ],
        
        # <AdditiveOperator> ::= + | - | 'atau'
        NonTerminal("<AdditiveOperator>"): [
            [Token("ARITHMETIC_OPERATOR", "+")],
            [Token("ARITHMETIC_OPERATOR", "-")],
            [Token("LOGICAL_OPERATOR", "atau")]
        ],
        
        # <MultiplicativeOperator> ::= * | / | 'bagi' | 'mod' | 'dan'
        NonTerminal("<MultiplicativeOperator>"): [
            [Token("ARITHMETIC_OPERATOR", "*")],
            [Token("ARITHMETIC_OPERATOR", "/")],
            [Token("ARITHMETIC_OPERATOR", "bagi")],
            [Token("ARITHMETIC_OPERATOR", "mod")],
            [Token("LOGICAL_OPERATOR", "dan")]
        ],
    }
    
    return rules