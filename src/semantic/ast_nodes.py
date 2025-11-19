from dataclasses import dataclass, field, fields
from typing import List, Optional, Any, Union

# -----------------------------------------------------------
# Base Node
# -----------------------------------------------------------
@dataclass
class ASTNode:
    """Base class untuk semua node AST"""
    # Atribut untuk Semantic Analysis (diisi kemudian)
    type: Optional[str] = field(default=None, init=False)
    symbol_entry: Optional[dict] = field(default=None, init=False)
    
    def __str__(self):
        """Override string representation untuk mencetak Tree Visual."""
        return self._print_tree()

    def _print_tree(self, prefix="", is_last=True):
        """
        Mencetak pohon AST dengan format visual yang cantik.
        """
        # 1. Siapkan Header Node
        node_name = self.__class__.__name__.replace("Node", "")
        if node_name == "Program": node_name = "ProgramNode"
        
        attrs = []
        children_map = [] # List of (Label, NodeObj)

        for f in fields(self):
            if f.name in ['type', 'symbol_entry']: continue
            
            val = getattr(self, f.name)
            
            if self.__class__.__name__ == "ProgramNode":
                if f.name == "declarations":
                    children_map.append(("Declarations", val)) 
                    continue
                elif f.name == "block":
                    children_map.append(("Block", val)) 
                    continue

            # General Children Handling
            if isinstance(val, ASTNode):
                children_map.append((None, val)) 
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, ASTNode):
                        children_map.append((None, item))
            elif val is not None:
                val_str = f"'{val}'" if isinstance(val, str) else str(val)
                attrs.append(f"{f.name}: {val_str}")

        attr_str = f"({', '.join(attrs)})" if attrs else ""
        
        connector = "\\-- " if is_last else "+-- "
        
        if prefix == "": # Root Node
            result = f"{node_name}{attr_str}\n"
            child_prefix = "    "
        else:
            result = f"{prefix}{connector}{node_name}{attr_str}\n"
            child_prefix = prefix + ("    " if is_last else "|   ")

        # 3. Print Children
        count = len(children_map)
        for i, (label, child) in enumerate(children_map):
            is_last_child = (i == count - 1)
            
            if label: 
                # --- VIRTUAL NODE (Declarations / Block) ---
                sub_connector = "\\-- " if is_last_child else "+-- "
                result += f"{child_prefix}{sub_connector}{label}\n"
                
                virtual_prefix = child_prefix + ("    " if is_last_child else "|   ")
                
                if label == "Block" and isinstance(child, CompoundNode):
                    statements = child.children
                    for k, stmt in enumerate(statements):
                        is_last_stmt = (k == len(statements) - 1)
                        result += stmt._print_tree(virtual_prefix, is_last_stmt)
                
                # Logic standar untuk Declarations (List)
                elif isinstance(child, list):
                    for j, item in enumerate(child):
                        is_last_item = (j == len(child) - 1)
                        result += item._print_tree(virtual_prefix, is_last_item)
                
                # Fallback standar
                elif isinstance(child, ASTNode):
                    result += child._print_tree(virtual_prefix, True)
            
            else:
                result += child._print_tree(child_prefix, is_last_child)

        return result

# -----------------------------------------------------------
# Program
# -----------------------------------------------------------
@dataclass
class ProgramNode(ASTNode):
    """Node untuk Program utama"""
    name: str
    declarations: List[ASTNode]
    block: ASTNode

# -----------------------------------------------------------
# Declarations
# -----------------------------------------------------------
@dataclass
class ConstDeclNode(ASTNode):
    """Node untuk deklarasi konstanta"""
    const_name: str
    value: ASTNode


@dataclass
class TypeDeclNode(ASTNode):
    """Node untuk deklarasi tipe baru"""
    type_name: str
    value: ASTNode


@dataclass
class VarDeclNode(ASTNode):
    """Node untuk deklarasi variabel"""
    var_name: str
    type_node: 'TypeNode'


# -----------------------------------------------------------
# Types
# -----------------------------------------------------------
@dataclass
class TypeNode(ASTNode):
    """Node untuk tipe data dasar (integer, boolean, char, real)"""
    type_name: str

@dataclass
class ArrayTypeNode(ASTNode):
    """Node untuk tipe array"""
    lower: ASTNode
    upper: ASTNode
    element_type: ASTNode

@dataclass
class RecordTypeNode(ASTNode):
    """Node untuk tipe record"""
    fields: List[VarDeclNode]

# -----------------------------------------------------------
# Subprograms
# -----------------------------------------------------------
@dataclass
class ParameterNode(ASTNode):
    """Node untuk parameter prosedur/fungsi"""
    names: List[str]
    type_node: ASTNode
    is_ref: bool = False  # True jika VAR parameter (pass by reference)

@dataclass
class ProcedureDeclNode(ASTNode):
    """Node untuk deklarasi prosedur"""
    name: str
    params: List[ParameterNode]
    block: ASTNode

@dataclass
class FunctionDeclNode(ASTNode):
    """Node untuk deklarasi fungsi"""
    name: str
    return_type: TypeNode
    params: List[ParameterNode]
    block: ASTNode

# -----------------------------------------------------------
# Statements
# -----------------------------------------------------------
@dataclass
class CompoundNode(ASTNode):
    """Node untuk compound statement (mulai...selesai)"""
    children: List[ASTNode]

@dataclass
class AssignNode(ASTNode):
    """Node untuk assignment statement"""
    target: ASTNode
    value: ASTNode

@dataclass
class ProcedureCallNode(ASTNode):
    """Node untuk pemanggilan prosedur/fungsi"""
    proc_name: str
    arguments: List[ASTNode]

@dataclass
class IfNode(ASTNode):
    """Node untuk if statement"""
    condition: ASTNode
    true_block: ASTNode
    else_block: Optional[ASTNode] = None

@dataclass
class WhileNode(ASTNode):
    """Node untuk while loop"""
    condition: ASTNode
    body: ASTNode

@dataclass
class RepeatNode(ASTNode):
    """Node untuk repeat-until loop"""
    body: List[ASTNode]
    condition: ASTNode

@dataclass
class ForNode(ASTNode):
    """Node untuk for loop"""
    variable: str
    start_expr: ASTNode
    direction: str  # "to" atau "downto"
    end_expr: ASTNode
    body: ASTNode

@dataclass
class CaseElementNode(ASTNode):
    """Node untuk satu elemen case"""
    value: ASTNode
    statement: ASTNode

@dataclass
class CaseNode(ASTNode):
    """Node untuk case statement"""
    expr: ASTNode
    cases: List[CaseElementNode]

# -----------------------------------------------------------
# Expressions & Factors
# -----------------------------------------------------------
@dataclass
class BinOpNode(ASTNode):
    """Node untuk operasi biner (+, -, *, /, =, <>, dll)"""
    op: str
    left: ASTNode
    right: ASTNode

@dataclass
class UnaryOpNode(ASTNode):
    """Node untuk operasi unary (-, tidak/not)"""
    op: str
    expr: ASTNode

@dataclass
class VarNode(ASTNode):
    """Node untuk referensi variabel"""
    name: str

@dataclass
class ArrayAccessNode(ASTNode):
    """Node untuk akses elemen array"""
    array: ASTNode
    index: ASTNode

@dataclass
class FieldAccessNode(ASTNode):
    """Node untuk akses field record"""
    record: ASTNode
    field_name: str

@dataclass
class NumNode(ASTNode):
    """Node untuk literal angka"""
    value: Union[int, float]

@dataclass
class StringNode(ASTNode):
    """Node untuk literal string"""
    value: str

@dataclass
class CharNode(ASTNode):
    """Node untuk literal karakter"""
    value: str

@dataclass
class BoolNode(ASTNode):
    """Node untuk literal boolean"""
    value: bool

@dataclass
class NoOpNode(ASTNode):
    """Node kosong (placeholder)"""
    pass