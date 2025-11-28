from dataclasses import dataclass, field, fields
from typing import List, Optional, Any, Union
from lexical.token import Token 

@dataclass
class ASTNode:
    type: Optional[str] = field(default=None, init=False, repr=False)
    symbol_entry: Optional[dict] = field(default=None, init=False, repr=False)

    def __str__(self):
        # return self._print_tree()
        return self._print_ast_decorated()

    # =========================================================================
    # METHOD FOR AST DECORATED PRINT
    # =========================================================================

    def _get_inline_details(self) -> str:
        """
        Helper untuk mengambil nilai primitif penting agar ditampilkan 
        di sebelah nama Node (misal: nama variabel, nilai angka, operator).
        """
        details = []
        # List atribut yang ingin ditampilkan 'inline' (bukan sebagai child node)
        important_attrs = ['name', 'var_name', 'proc_name', 'const_name', 
                           'type_name', 'op', 'value', 'variable', 'field_name']
        
        for f in fields(self):
            # Skip atribut internal/semantic
            if f.name in ['type', 'symbol_entry', 'children']: 
                continue
            if self.__class__.__name__ == "ParameterNode" and f.name == "names":
                if self.names:
                    details.append(f"'{self.names[0]}'")
                continue
                
            val = getattr(self, f.name)
            
            # Jika atribut ada di list penting dan tipenya primitif (str/int/float/bool)
            if f.name in important_attrs and isinstance(val, (str, int, float, bool)):
                # Khusus string, kasih tanda kutip biar jelas
                if isinstance(val, str):
                    details.append(f"'{val}'")
                else:
                    details.append(str(val))
                    
        return f"({', '.join(details)})" if details else ""

    def _get_annotations(self) -> str:
        """
        Helper untuk memformat string anotasi semantik.
        """
        parts = []
        
        # 1. Type
        if self.type:
            parts.append(f"type:{self.type}")
        
        # 2. Symbol Entry Info 
        if self.symbol_entry and isinstance(self.symbol_entry, dict):
            se = self.symbol_entry
            # Key Map untuk tab_index, b_index, a_index (ref)
            key_map = {
                'tab_index': 't_idx', # tab index
                'block_index': 'b_idx', # block index
                'ref': 'a_idx',       # array index (ref di tab entry)
                'lev': 'lev',
                'adr': 'adr'
            }
            
            # Prioritaskan urutan print agar rapi
            priority_keys = ['tab_index', 'block_index', 'ref', 'lev', 'adr']
            
            for key in priority_keys:
                if key in se:
                    # Khusus ref/a_idx, hanya print jika nilainya > 0
                    if key == 'ref' and se[key] == 0:
                        continue
                        
                    label = key_map.get(key, key)
                    parts.append(f"{label}:{se[key]}")

        if not parts:
            return ""
            
        return ", ".join(parts)

    def _print_ast_decorated(self, prefix="", is_last=True):
        """
        Fungsi rekursif utama untuk mencetak AST yang sudah didekorasi.
        """
        # --- KONFIGURASI LEBAR KOLOM ---
        ALIGN_WIDTH = 40 
        
        # 1. Siapkan komponen visual
        connector = "└─ " if is_last else "├─ "
        
        # 2. Ambil Nama Node
        node_name = self.__class__.__name__.replace("Node", "")
        
        # 3. Ambil Detail Inline
        inline = self._get_inline_details()
        
        # 4. Bangun Bagian Kiri (Tree Structure)
        line_prefix = "" if prefix == "" else prefix + connector
        left_part = f"{line_prefix}{node_name}{inline}"
        
        # 5. Ambil Anotasi (Kanan)
        annotations = self._get_annotations()

        # 6. Gabungkan dengan Alignment
        if annotations:
            # ljust akan menambahkan spasi di kanan sampai panjang string mencapai ALIGN_WIDTH
            # Jika string lebih panjang dari ALIGN_WIDTH, panah akan terdorong otomatis (aman)
            padded_left = left_part.ljust(ALIGN_WIDTH)
            result = f"{padded_left}  →  {annotations}\n"
        else:
            # Jika tidak ada anotasi, tidak perlu panah
            result = f"{left_part}\n"

        # 7. Siapkan Children untuk Rekursi
        children = []
        for f in fields(self):
            if f.name in ['type', 'symbol_entry']: continue
            
            # Skip logic khusus
            if f.name == "type_node":
                if self.__class__.__name__ in ["VarDeclNode", "ParameterNode"]:
                    continue
            
            val = getattr(self, f.name)
            
            if isinstance(val, ASTNode):
                children.append(val)
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, ASTNode):
                        children.append(item)

        # 8. Rekursi ke setiap Child
        child_prefix = prefix + ("   " if is_last else "│  ")
        count = len(children)
        
        for i, child in enumerate(children):
            is_last_child = (i == count - 1)
            result += child._print_ast_decorated(child_prefix, is_last_child)

        return result
    
@dataclass
class ProgramNode(ASTNode):
    name: str
    declarations: List[ASTNode] = field(repr=False) 
    block: ASTNode = field(repr=False)


@dataclass
class VarDeclNode(ASTNode):
    var_name: str
    type_node: 'TypeNode'

@dataclass
class ConstDeclNode(ASTNode):
    const_name: str
    value: ASTNode

@dataclass
class TypeDeclNode(ASTNode):
    type_name: str
    value: ASTNode

@dataclass
class TypeNode(ASTNode):
    type_name: str
    def __repr__(self): return f"'{self.type_name}'"
    def __str__(self): return f"'{self.type_name}'"

@dataclass
class ArrayTypeNode(ASTNode):
    lower: ASTNode
    upper: ASTNode
    element_type: ASTNode

@dataclass
class RecordTypeNode(ASTNode):
    fields: List['VarDeclNode']

@dataclass
class CompoundNode(ASTNode):
    children: List[ASTNode]

@dataclass
class AssignNode(ASTNode):
    target: ASTNode
    value: ASTNode    
    def _print_tree(self, prefix="", is_last=True):
        """Override untuk handle multi-line assignment"""
        return self._print_tree_multiline(prefix, is_last)

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
    def __repr__(self): return f"Var('{self.name}')"

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
    value: Union[int, float]
    def __repr__(self): return f"Num({self.value})"

@dataclass
class StringNode(ASTNode):
    value: str
    def __repr__(self): return f"String({self.value})"

@dataclass
class CharNode(ASTNode):
    value: str

@dataclass
class BoolNode(ASTNode):
    value: bool

@dataclass
class NoOpNode(ASTNode):
    pass

@dataclass
class ParameterNode(ASTNode):
    names: List[str]
    type_node: ASTNode
    is_ref: bool = False

@dataclass
class ProcedureDeclNode(ASTNode):
    name: str
    params: List[ParameterNode]
    local_vars: List[ASTNode]
    block: ASTNode

@dataclass
class FunctionDeclNode(ASTNode):
    name: str
    return_type: TypeNode
    params: List[ParameterNode]
    local_vars: List[ASTNode]
    block: ASTNode