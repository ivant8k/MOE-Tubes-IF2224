from typing import Any, List, Dict, Callable

from models.token import Token, TokenType, Lexeme
from models.parsetree import NonTerminal, Node

# ===== Class for CFG =====

class Epsilon:
    pass

class CFG:
    production_rules: Dict[NonTerminal, Callable[[], Node|None]] # Diubah
    tokens: List[Token]
    currentTokenID = 0
    # UNTUK ERROR REPORTING
    max_error_info: Dict[str, Any]

    def __init__(self):
        self.production_rules = {}
        self.currentTokenID = 0
        
        # Inisialisasi pelacak error
        self.max_error_info = {
            'max_id': -1,      # Token ID terjauh yang gagal
            'expected': set(), # Apa yang diharapkan di posisi itu (bisa banyak)
            'found': None      # Token apa yang ditemukan di posisi itu
        }
    
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

    # ERROR REPORTING
    def record_error(self, expected_symbol: Token|TokenType, found_token: Token):
        """Mencatat kegagalan jika ini adalah yang 'terjauh'."""
        current_fail_id = self.currentTokenID
        
        # Menemukan error di posisi yang LEBIH JAUH.
        if current_fail_id > self.max_error_info['max_id']:
            self.max_error_info['max_id'] = current_fail_id
            self.max_error_info['expected'] = {expected_symbol}
            self.max_error_info['found'] = found_token
        
        # Menemukan error di posisi terjauh yang SAMA.
        elif current_fail_id == self.max_error_info['max_id']:
            # Tambahkan 'symbol' ini sebagai ekspektasi alternatif (contoh: expect ID or NUMBER)
            self.max_error_info['expected'].add(expected_symbol)

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
                                # JANGAN RECORD ERROR DI SINI: biarkan dia cari alternatif
                        
                        elif isinstance(symbol, Token):
                            if symbol == self.currentToken():
                                isMatch = True
                                childNode = Node(self.currentToken())
                                # KONSUMSI TOKEN
                                self.nextToken()
                            else:
                                isMatch = False
                                # RECORD ERROR
                                self.record_error(symbol, self.currentToken())
                        
                        elif isinstance(symbol, TokenType):
                            if symbol == self.currentToken().token_type:
                                isMatch = True
                                childNode = Node(self.currentToken())
                                # KONSUMSI TOKEN
                                self.nextToken()
                            else:
                                isMatch = False
                                # PANGGIL PELACAK ERROR
                                self.record_error(symbol, self.currentToken())
                        
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
    
    def parseToken(self, tokens:List[Token]) -> Node|None:
        self.tokens = tokens
        return self.parse()