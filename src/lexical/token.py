from dataclasses import dataclass, field
from typing import Optional

# ===== Class for Token =====

class TokenType(str):
    pass
class Lexeme(str):
    pass

@dataclass(frozen=True)
class Token:
    token_type: TokenType
    lexeme: Lexeme
    # Posisi, default None jika tidak diberikan
    line: Optional[int] = field(default=None)
    column: Optional[int] = field(default=None)

    def __iter__(self):
        yield self.token_type
        yield self.lexeme

    def __str__(self):
        return f"{self.token_type}({self.lexeme})"

    # Override metode __eq__ untuk perbandingan hanya berdasarkan token_type dan lexeme
    def __eq__(self, other):
        if not isinstance(other, Token):
            return NotImplemented
        return (self.token_type == other.token_type) and (self.lexeme == other.lexeme)
    
    # Override __hash__ untuk memastikan hash yang konsisten dengan __eq__
    def __hash__(self):
        return hash((self.token_type, self.lexeme))