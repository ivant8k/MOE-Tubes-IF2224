from dataclasses import dataclass
from typing import List, Dict, Callable

# ===== Class for Token =====

class TokenType(str):
    pass
class Lexeme(str):
    pass

@dataclass(frozen=True)
class Token:
    token_type: TokenType
    lexeme: Lexeme
    
    def __iter__(self):
        yield self.token_type
        yield self.lexeme

    def __str__(self):
        return f"{self.token_type}({self.lexeme})"



# ===== Class for Parse Tree =====

class NonTerminal(str):
    pass

class Node:
    value: NonTerminal|Token
    children: List["Node"] = []
    
    def __init__(self, value: NonTerminal|Token):
        self.value = value
        self.children: List["Node"] = []

    def addChild(self, node:"Node") -> None:
        self.children.append(node)
    
    def addChildren(self, nodes:List["Node"]) -> None:
        self.children.extend(nodes)

    def __str__(self, level=0, prefix="", is_last=True):
        
        # 1. Tentukan string untuk node ini
        if level == 0:
            # Node root tidak memiliki konektor
            tree_str = f"{self.value}\n"
            child_prefix = "" # Anak dari root tidak punya awalan
        else:
            # Node anak memiliki konektor
            connector = "└── " if is_last else "├── "
            tree_str = f"{prefix}{connector}{self.value}\n"
            
            # Tentukan awalan untuk anak-anak dari node INI
            child_prefix = prefix + ("    " if is_last else "│   ")

        # 2. Rekursif panggil untuk semua anak
        for i, child in enumerate(self.children):
            # Cek apakah anak tersebut adalah anak terakhir
            is_child_last = (i == len(self.children) - 1)
            # Tambahkan representasi string anak ke string tree utama
            tree_str += child.__str__(level + 1, prefix=child_prefix, is_last=is_child_last)
        
        return tree_str
    


# ===== Class for CFG =====

class Epsilon:
    pass

class CFG:
    production_rules: Dict[NonTerminal, Callable[[], Node|None]] # Diubah
    tokens: List[Token]
    currentTokenID = 0

    def __init__(self, tokens:List[Token]):
        self.production_rules = {}
        self.tokens = tokens
    
    # GET TOKEN
    def nextToken(self) -> None:
        self.currentTokenID += 1
    def prevToken(self) -> None:
        self.currentTokenID -= 1
    def currentToken(self) -> Token:
        # Tambahkan penjaga agar tidak error di akhir token
        if self.currentTokenID >= len(self.tokens):
            return Token(TokenType("EOF"), Lexeme("EOF")) # Token Penjaga
        return self.tokens[self.currentTokenID]

    # PRODUCTION RULES
    def addRules(self, rules: Dict[NonTerminal, List[List[NonTerminal|Token|TokenType|Epsilon]]]) -> None:
        for lhs, rhs in rules.items():
            
            # Rule yang didaftarkan
            # 'Kunci' nilai 'lhs' dan 'rhs' saat ini menggunakan argumen default.
            def execute_rules(current_lhs=lhs, current_rhs=rhs) -> Node|None:
                newNode = Node(current_lhs)

                # print(f"Endpoint execute_rules:\n\tcurrent_lhs={current_lhs}\n\tcurrent_rhs={current_rhs}\n\ttoken={self.currentToken()}")
                
                # Simpan posisi token untuk backtracking
                initial_token_id = self.currentTokenID

                # Coba setiap Alternatif
                for alternative in current_rhs:
                    isMatch = True
                    childNodes:List[Node] = []
                    
                    # Reset token pointer untuk setiap alternatif baru
                    self.currentTokenID = initial_token_id

                    # Try Apply
                    # print(f"Alternative Check: {alternative}")
                    for symbol in alternative:
                        # print(f"Matching: simbol={symbol} token={self.currentToken()}")
                        
                        # Inisialisasi childNode
                        childNode: Node = None 

                        if isinstance(symbol, NonTerminal):
                            childNode = self.parse(symbol) # Panggil rekursif
                            # Cek apakah parse rekursif GAGAL
                            if childNode is None:
                                isMatch = False
                        
                        elif isinstance(symbol, Token):
                            if symbol == self.currentToken():
                                isMatch = True
                                childNode = Node(self.currentToken())
                                # KONSUMSI TOKEN
                                self.nextToken()
                            else:
                                isMatch = False
                        
                        elif isinstance(symbol, TokenType):
                            if symbol == self.currentToken().token_type:
                                isMatch = True
                                childNode = Node(self.currentToken())
                                # KONSUMSI TOKEN
                                self.nextToken()
                            else:
                                isMatch = False
                        
                        elif isinstance(symbol, Epsilon):
                            isMatch = True 
                            continue # Epsilon tidak menghasilkan node anak dan tidak konsumsi token
                        
                        if isMatch:
                            if childNode: # Hanya tambahkan jika node berhasil dibuat
                                childNodes.append(childNode)
                        else:
                            # Gagal di tengah alternatif, hentikan loop 'symbol' ini
                            break
                    
                    # Alternatif Cocok (seluruh 'alternative' berhasil di-match)
                    if isMatch:
                        newNode.addChildren(childNodes)
                        # Berhasil! Kembalikan node yang sudah diisi
                        return newNode

                # Jika semua alternatif sudah dicoba dan TIDAK ADA yang cocok
                # Reset token ke posisi awal (sebelum 'execute_rules' ini dipanggil)
                self.currentTokenID = initial_token_id
                # Kembalikan None untuk menandakan kegagalan
                return None

            # Daftarkan Rule
            self.production_rules[lhs] = execute_rules

    def parse(self, lhs:NonTerminal=NonTerminal("<Program>")) -> Node|None: # Mengembalikan None jika gagal
        # print(f"Mencoba parsing aturan: {lhs}")
        if lhs not in self.production_rules:
            raise Exception(f"Aturan produksi untuk {lhs} tidak ditemukan.")
        return self.production_rules[lhs]()