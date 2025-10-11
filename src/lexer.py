import json
import sys
import os

class LexicalError(Exception):
    """Custom exception untuk error leksikal."""
    def __init__(self, message, line, column):
        super().__init__(f"Lexical Error on line {line}, column {column}: {message}")
        self.message = message
        self.line = line
        self.column = column

class Lexer:
    def __init__(self, dfa_rules_path):
        """
        Inisialisasi lexer dengan memuat aturan DFA dari file JSON.
        """
        try:
            with open(dfa_rules_path, 'r') as f:
                self.dfa = json.load(f)
        except FileNotFoundError:
            print(f"FATAL ERROR: dfa.json tidak ditemukan di '{dfa_rules_path}'", file=sys.stderr)
            sys.exit(1)
        
        self.start_state = self.dfa['start_state']
        self.final_states = self.dfa['final_states']
        self.transitions = self.dfa['transitions']
        self.char_classes = self.dfa['character_classes']
        
        # Daftar keywords dan reserved words (dalam lowercase)
        self.keywords = {
            "program", "var", "begin", "end", "if", "then", "else", "while", 
            "do", "for", "to", "downto", "integer", "real", "boolean", "char", 
            "array", "of", "procedure", "function", "const", "type"
        }
        self.reserved_operators = {
            "div": "ARITHMETIC_OPERATOR",
            "mod": "ARITHMETIC_OPERATOR",
            "and": "LOGICAL_OPERATOR",
            "or": "LOGICAL_OPERATOR",
            "not": "LOGICAL_OPERATOR"
        }

    def _get_char_class(self, char):
        """Mendapatkan kelas karakter (letter, digit, dll.) dari sebuah karakter."""
        for class_name, chars in self.char_classes.items():
            if char in chars:
                return class_name
        return char

    def tokenize(self, source_code):
        """
        Memproses source code dan mengubahnya menjadi daftar token.
        Melempar LexicalError jika ada kesalahan.
        """
        tokens = []
        position = 0
        line = 1
        column = 1

        while position < len(source_code):
            
            char = source_code[position]
            if char in self.char_classes.get('whitespace', ''):
                if char == '\n':
                    line += 1
                    column = 1
                else:
                    column += 1
                position += 1
                continue

            current_state = self.start_state
            current_lexeme = ""
            last_match = None
            
            start_line, start_col = line, column

            temp_pos = position
            temp_line, temp_col = line, column

            while True: 
                if temp_pos >= len(source_code):
                    if current_state in ["S_STRING_CONTENT", "S_STRING_QUOTE_END"]:
                        raise LexicalError("Unterminated string literal", start_line, start_col)
                    if current_state in ["S_COMMENT_BLOCK_CONTENT", "S_COMMENT_BLOCK_STAR_END", "S_COMMENT_LINE_CONTENT"]:
                        raise LexicalError("Unterminated comment", start_line, start_col)
                    break

                char = source_code[temp_pos]
                char_class = self._get_char_class(char)
                
                next_state = None
                
                if current_state in self.transitions:
                    possible_transitions = self.transitions[current_state]
                    if char_class in possible_transitions:
                        next_state = possible_transitions[char_class]
                    elif char in possible_transitions:
                        next_state = possible_transitions[char]
                    else:
                        for rule, target_state in possible_transitions.items():
                            if rule.startswith("any_except_"):
                                excluded_chars = rule.split('_')[-1]
                                if char not in excluded_chars:
                                    next_state = target_state
                                    break
                
                if next_state:
                    current_state = next_state
                    current_lexeme += char
                    
                    if char == '\n':
                        temp_line += 1
                        temp_col = 1
                    else:
                        temp_col += 1
                    temp_pos += 1

                    if current_state in self.final_states:
                        last_match = (current_lexeme, self.final_states[current_state], temp_line, temp_col)
                else:
                    break
            
            if last_match:
                lexeme, token_type, end_line, end_col = last_match
                
                if token_type == "IDENTIFIER":
                    lexeme_lower = lexeme.lower()
                    if lexeme_lower in self.keywords:
                        token_type = "KEYWORD"
                    elif lexeme_lower in self.reserved_operators:
                        token_type = self.reserved_operators[lexeme_lower]
                
                if token_type != "COMMENT":
                    tokens.append((token_type, lexeme))
                
                position += len(lexeme)
                line, column = end_line, end_col
            else:
                raise LexicalError(f"Invalid character '{source_code[position]}'", line, column)
        
        return tokens

def main():
    """
    Fungsi utama untuk menjalankan lexer.
    Membutuhkan tepat 2 argumen: file input (.pas) dan file output (.txt).
    """
    if len(sys.argv) != 3:
        print("Usage: python src/lexer.py <source_file_path.pas> <output_file_path.txt>", file=sys.stderr)
        sys.exit(1)

    source_file_path = sys.argv[1]
    output_file_path = sys.argv[2]

    if not source_file_path.lower().endswith('.pas'):
        print(f"Input Error: Source file harus memiliki ekstensi .pas. Diberikan: '{source_file_path}'", file=sys.stderr)
        sys.exit(1)
        
    if not output_file_path.lower().endswith('.txt'):
        print(f"Output Error: Output file harus memiliki ekstensi .txt. Diberikan: '{output_file_path}'", file=sys.stderr)
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    dfa_path = os.path.join(script_dir, "dfa.json")
    
    try:
        with open(source_file_path, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Input file tidak ditemukan di '{source_file_path}'", file=sys.stderr)
        sys.exit(1)
        
    lexer = Lexer(dfa_path)
    
    try:
        tokens = lexer.tokenize(source_code)
        
        output_dir = os.path.dirname(output_file_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        with open(output_file_path, 'w') as f:
            for token_type, lexeme in tokens:
                f.write(f"{token_type}({lexeme})\n")
        
        print(f"Tokenization successful. Output written to '{output_file_path}'")

    except LexicalError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error writing to file '{output_file_path}': {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

