# ============================
#   ast_nodes.py  (FIXED)
# ============================

from dataclasses import dataclass, field, fields
from typing import List, Optional, Any

# -----------------------------------------------------------
# Base Node
# -----------------------------------------------------------
@dataclass
class ASTNode:
    # init=False: Jangan masukkan ke constructor __init__
    # Karena field ini baru diisi saat Semantic Analysis (Phase 4)
    type: Optional[str] = field(default=None, init=False)
    symbol_entry: Optional[dict] = field(default=None, init=False)
    def __str__(self):
        """Override string representation untuk mencetak Tree Visual."""
        return self._print_tree()

    def _print_tree(self, prefix="", is_last=True):
        """
        Mencetak pohon AST dengan format visual yang cantik.
        Menangani 'Virtual Node' seperti 'Declarations' dan 'Block'.
        """
        # 1. Siapkan Header Node (Nama Class + Atribut Primitif)
        node_name = self.__class__.__name__.replace("Node", "") # Hapus suffix 'Node' agar lebih bersih
        if node_name == "Program": node_name = "ProgramNode" # Kecuali ProgramNode biar sama persis
        
        attrs = []
        children_map = [] # List of (Label, NodeObj)

        # Pisahkan antara Atribut Primitif (str/int) dan Children (ASTNode)
        for f in fields(self):
            if f.name in ['type', 'symbol_entry']: continue
            
            val = getattr(self, f.name)
            
            # Special Handling untuk ProgramNode agar sesuai spesifikasi
            if self.__class__.__name__ == "ProgramNode":
                if f.name == "declarations":
                    # Masukkan sebagai Virtual Node
                    children_map.append(("Declarations", val)) # val is List
                    continue
                elif f.name == "block":
                    # Masukkan sebagai Virtual Node
                    children_map.append(("Block", val)) # val is Node
                    continue

            if isinstance(val, ASTNode):
                children_map.append((None, val)) # None label means direct child
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, ASTNode):
                        children_map.append((None, item))
            elif val is not None:
                # Primitif (String, Int, Bool)
                val_str = f"'{val}'" if isinstance(val, str) else str(val)
                attrs.append(f"{f.name}: {val_str}")

        # Format string atribut: (name: 'Hello', ...)
        attr_str = f"({', '.join(attrs)})" if attrs else ""
        
        # 2. Print Node Saat Ini
        connector = "\-- " if is_last else "+-- "
        if prefix == "": # Root Node
            result = f"{node_name}{attr_str}\n"
            child_prefix = "    " # Indentasi awal untuk anak-anak root
        else:
            result = f"{prefix}{connector}{node_name}{attr_str}\n"
            child_prefix = prefix + ("    " if is_last else "|   ")

        # 3. Print Children
        count = len(children_map)
        for i, (label, child) in enumerate(children_map):
            is_last_child = (i == count - 1)
            
            if label: 
                # --- HANDLER UNTUK VIRTUAL NODE (Declarations/Block) ---
                sub_connector = "\-- " if is_last_child else "+-- "
                result += f"{child_prefix}{sub_connector}{label}\n"
                
                # Setup prefix untuk anak-anak dari Virtual Node ini
                virtual_prefix = child_prefix + ("    " if is_last_child else "|   ")
                
                # Jika isi Virtual Node adalah List (Declarations)
                if isinstance(child, list):
                    for j, item in enumerate(child):
                        is_last_item = (j == len(child) - 1)
                        result += item._print_tree(virtual_prefix, is_last_item)
                # Jika isi Virtual Node adalah Single Node (Block)
                elif isinstance(child, ASTNode):
                    result += child._print_tree(virtual_prefix, True) # Selalu last karena 1 on 1
            
            else:
                # --- HANDLER UNTUK DIRECT CHILD BIASA ---
                result += child._print_tree(child_prefix, is_last_child)

        return result

# -----------------------------------------------------------
# Program
# -----------------------------------------------------------
@dataclass
class ProgramNode(ASTNode):
    name: str
    declarations: list
    block: ASTNode

# -----------------------------------------------------------
# Declarations
# -----------------------------------------------------------
@dataclass
class ConstDeclNode(ASTNode):
    const_name: str
    value: ASTNode


@dataclass
class TypeDeclNode(ASTNode):
    type_name: str
    value: ASTNode

@dataclass
class VarDeclNode(ASTNode):
    var_name: str
    type_node: 'TypeNode'


# -----------------------------------------------------------
# Types
# -----------------------------------------------------------
@dataclass
class TypeNode(ASTNode):
    type_name: str


@dataclass
class ArrayTypeNode(ASTNode):
    lower: ASTNode
    upper: ASTNode
    element_type: ASTNode


@dataclass
class RecordTypeNode(ASTNode):
    fields: List[VarDeclNode]


# -----------------------------------------------------------
# Subprograms
# -----------------------------------------------------------
@dataclass
class ParameterNode(ASTNode):
    names: List[str]
    type_node: ASTNode
    is_ref: bool = False


@dataclass
class ProcedureDeclNode(ASTNode):
    name: str
    params: List[ParameterNode]
    block: ASTNode


@dataclass
class FunctionDeclNode(ASTNode):
    name: str
    return_type: TypeNode
    params: List[ParameterNode]
    block: ASTNode


# -----------------------------------------------------------
# Statements
# -----------------------------------------------------------
@dataclass
class CompoundNode(ASTNode):
    children: list


@dataclass
class AssignNode(ASTNode):
    target: ASTNode
    value: ASTNode


@dataclass
class ProcedureCallNode(ASTNode):
    proc_name: str
    arguments: List[ASTNode]


@dataclass
class IfNode(ASTNode):
    condition: ASTNode
    true_block: ASTNode
    else_block: Optional[ASTNode] = None


@dataclass
class WhileNode(ASTNode):
    condition: ASTNode
    body: ASTNode


@dataclass
class RepeatNode(ASTNode):
    body: List[ASTNode]
    condition: ASTNode


@dataclass
class ForNode(ASTNode):
    variable: str
    start_expr: ASTNode
    direction: str
    end_expr: ASTNode
    body: ASTNode


@dataclass
class CaseElementNode(ASTNode):
    value: ASTNode
    statement: ASTNode


@dataclass
class CaseNode(ASTNode):
    expr: ASTNode
    cases: List[CaseElementNode]


# -----------------------------------------------------------
# Expressions & Factors
# -----------------------------------------------------------
@dataclass
class BinOpNode(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode


@dataclass
class UnaryOpNode(ASTNode):
    op: str
    expr: ASTNode


@dataclass
class VarNode(ASTNode):
    name: str


@dataclass
class ArrayAccessNode(ASTNode):
    array: ASTNode
    index: ASTNode


@dataclass
class FieldAccessNode(ASTNode):
    record: ASTNode
    field_name: str


@dataclass
class NumNode(ASTNode):
    value: int | float


@dataclass
class StringNode(ASTNode):
    value: str


@dataclass
class CharNode(ASTNode):
    value: str


@dataclass
class BoolNode(ASTNode):
    value: bool


@dataclass
class NoOpNode(ASTNode):
    pass