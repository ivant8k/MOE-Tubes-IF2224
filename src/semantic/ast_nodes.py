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
        node_name = self.__class__.__name__.replace("Node", "")
        if node_name == "Program": node_name = "ProgramNode"
        
        attrs = []
        children_map = [] 

        # FIX: Special handling for ProcedureCallNode arguments
        is_proc_call = self.__class__.__name__ == "ProcedureCallNode"

        for f in fields(self):
            if f.name in ['type', 'symbol_entry']: continue
            
            val = getattr(self, f.name)
            
            if self.__class__.__name__ == "ProgramNode":
                if f.name in ["declarations", "block"]:
                    if f.name == "declarations": children_map.append(("Declarations", val)) 
                    else: children_map.append(("Block", val)) 
                    continue

            # IF ProcedureCall, format args inline!
            if is_proc_call and f.name == "arguments":
                if isinstance(val, list):
                    # Create a string representation like [String('...'), Var('b')]
                    args_str = ", ".join([str(arg).split('(')[0] + "(" + str(arg).split('(')[1].strip()[:-1] + ")" for arg in val if hasattr(arg, '__class__')])
                    # Simplified inline repr for readability
                    nice_args = []
                    for arg in val:
                        if isinstance(arg, StringNode): nice_args.append(f"String('{arg.value}')")
                        elif isinstance(arg, VarNode): nice_args.append(f"Var('{arg.name}')")
                        elif isinstance(arg, NumNode): nice_args.append(f"Num({arg.value})")
                        else: nice_args.append(arg.__class__.__name__.replace("Node",""))
                    
                    attrs.append(f"args: [{', '.join(nice_args)}]")
                continue

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
        
        if prefix == "": 
            result = f"{node_name}{attr_str}\n"
            child_prefix = "    "
        else:
            result = f"{prefix}{connector}{node_name}{attr_str}\n"
            child_prefix = prefix + ("    " if is_last else "|   ")

        count = len(children_map)
        for i, (label, child) in enumerate(children_map):
            is_last_child = (i == count - 1)
            
            if label: 
                sub_connector = "\\-- " if is_last_child else "+-- "
                result += f"{child_prefix}{sub_connector}{label}\n"
                virtual_prefix = child_prefix + ("    " if is_last_child else "|   ")
                
                if label == "Block" and type(child).__name__ == "CompoundNode":
                    statements = getattr(child, 'children', [])
                    for k, stmt in enumerate(statements):
                        is_last_stmt = (k == len(statements) - 1)
                        result += stmt._print_tree(virtual_prefix, is_last_stmt)
                elif isinstance(child, list):
                    for j, item in enumerate(child):
                        is_last_item = (j == len(child) - 1)
                        result += item._print_tree(virtual_prefix, is_last_item)
                elif isinstance(child, ASTNode):
                    result += child._print_tree(virtual_prefix, True)
            else:
                result += child._print_tree(child_prefix, is_last_child)
        return result

# ... (REST OF THE FILE IS SAME AS BEFORE - Copy all Node classes below) ...
@dataclass
class ProgramNode(ASTNode):
    name: str
    declarations: List[ASTNode] = field(repr=False) 
    block: ASTNode = field(repr=False)

@dataclass
class VarDeclNode(ASTNode):
    var_name: str
    type_node: 'TypeNode'
    # Override str agar ringkas: VarDecl(var_name: 'a', type_node: 'integer')
    # We want type_node to print as 'integer', not TypeNode(...)
    # But fields() iteration will handle it if we adjust.
    # However, user wants VarDecl(name: 'a', type: 'integer')
    # We can achieve this by having type_node.__repr__ return the string.
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
    # Important: This makes it print 'integer' inside VarDecl attr list
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
