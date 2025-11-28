from .ast_converter import ASTConverter, ASTNode
from .ast_analyzer import ASTAnalyzerError
from .symbol_table import SymbolTable
from .ast_decorator import ASTDecorator
from syntax.parsetree import Node

from typing import Tuple

class SemanticError(Exception):
    """Custom exception untuk error semantik."""
    def __init__(self, message:str, line:int=None, column:int=None) -> None:
        if line and column:
            super().__init__(f"Semantic Error on line {line}, column {column}: {message}")
        else:
            super().__init__(f"Semantic Error: {message}")
        self.message = message
        self.line = line
        self.column = column

class SemanticAnalyzer:
    converter: ASTConverter
    analyzer: ASTDecorator

    def __init__(self):
        self.converter = ASTConverter()
        self.analyzer = ASTDecorator()
    
    def analyze(self, parse_tree:Node, debug:bool=False) -> Tuple[ASTNode, SymbolTable]:
        try:
            # Jalankan AST Converter
            converter = ASTConverter()
            ast = converter.convert(parse_tree)
            if debug :
                print("[DEBUG] Abstract Syntax Tree (AST)")
                print(ast) # nanti disesuaikan lagi
        
            # Jalankan Analyzer
            analyzer = ASTDecorator()
            decorated_ast = analyzer.generate_decorated_ast(ast)
            
            return decorated_ast, analyzer.symbol_table
                
        except ASTAnalyzerError as e:
            raise SemanticError(message=e)