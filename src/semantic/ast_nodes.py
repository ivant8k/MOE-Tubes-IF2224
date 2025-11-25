from dataclasses import dataclass, field, fields
from typing import List, Optional, Any, Union
from lexical.token import Token 

@dataclass
class ASTNode:
    type: Optional[str] = field(default=None, init=False, repr=False)
    symbol_entry: Optional[dict] = field(default=None, init=False, repr=False)

    def __str__(self):
        return self._print_tree()

    def _print_tree(self, prefix="", is_last=True):
        # Nama node
        node_name = self.__class__.__name__
        if node_name.endswith("Node"):
            node_name = node_name[:-4]

        # Ambil atribut tampilan
        attrs = []
        if getattr(self, "type", None):
            attrs.append(f"type:{self.type}")

        if getattr(self, "symbol_entry", None):
            se = self.symbol_entry
            extras = []
            if isinstance(se, dict):
                if "tab_index" in se: extras.append(f"tab_index:{se['tab_index']}")
                if "lev" in se:       extras.append(f"lev:{se['lev']}")
            if extras:
                attrs.append(", ".join(extras))

        # Buat row output node saat ini
        connector = "└─ " if is_last else "├─ "
        line_prefix = "" if prefix == "" else prefix + connector

        # Format atribut ( → )
        attr_str = ""
        if attrs:
            attr_str = "  →  " + ", ".join(attrs)

        result = f"{line_prefix}{node_name}{attr_str}\n"

        # Padding untuk anak node berikutnya
        child_prefix = prefix + ("   " if is_last else "│  ")

        # Kumpulkan child AST
        children = []

        for f in fields(self):
            if f.name in ["type", "symbol_entry"]:
                continue

            val = getattr(self, f.name)

            # child single node
            if isinstance(val, ASTNode):
                children.append((f.name, val))

            # list child
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, ASTNode):
                        children.append((f.name, item))

            # field value biasa
            elif val is not None:
                # tampilkan di parent sebagai inline
                if isinstance(val, str):
                    result = result.rstrip() + f"(name: '{val}')\n"
                else:
                    result = result.rstrip() + f"({f.name}: {val})\n"

        # Cetak child
        for i, (label, child) in enumerate(children):
            is_last_child = (i == len(children) - 1)

            # Nama field seperti target / value
            next_prefix = child_prefix

            child_label = None
            if child.__class__.__name__ in ["Var", "Num", "String", "BinOp"]:
                child_label = f"{label} "

            # Rekursi
            result += child._print_tree(next_prefix, is_last_child)

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
    pass 

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
    block: ASTNode

@dataclass
class FunctionDeclNode(ASTNode):
    name: str
    return_type: TypeNode
    params: List[ParameterNode]
    block: ASTNode
