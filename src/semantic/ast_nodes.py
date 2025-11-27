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
        """Universal print tree function untuk semua node"""
        node_name = self.__class__.__name__
        
        # Special handling untuk ProgramNode
        if node_name == "ProgramNode":
            return self._print_program_node()
        
        # Special handling untuk CompoundNode (tidak print header)
        if node_name == "CompoundNode":
            return self._print_compound_node(prefix, is_last)
        
        # Remove "Node" suffix
        if node_name.endswith("Node"):
            node_name = node_name[:-4]
        
        # Get inline attributes
        inline_attrs = self._format_inline_attrs()
        
        # Build node line
        connector = "\\-- " if is_last else "+-- "
        line = f"{prefix}{connector}{node_name}{inline_attrs}\n"
        
        # Get children
        children = self._get_printable_children()
        
        if not children:
            return line
        
        # Print children
        child_prefix = prefix + ("    " if is_last else "|   ")
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            line += child._print_tree(child_prefix, is_last_child)
        return line

    def _print_program_node(self):
        """Special formatting untuk ProgramNode"""
        result = f"ProgramNode(name: '{self.name}')\n"
        result += "  |\n"
        result += "  +-- Declarations\n"
        
        if self.declarations:
            for i, decl in enumerate(self.declarations):
                is_last = (i == len(self.declarations) - 1)
                connector = "\\-- " if is_last else "+-- "
                result += "  |     |\n"
                result += f"  |     {connector}{decl._format_decl_inline()}\n"
        
        result += "  |\n"
        result += "  \\-- Block\n"
        
        if isinstance(self.block, ASTNode):
            # Assume block is CompoundNode
            block_children = getattr(self.block, 'children', [])
            for i, stmt in enumerate(block_children):
                is_last = (i == len(block_children) - 1)
                result += stmt._print_tree("        ", is_last)
        return result

    def _print_compound_node(self, prefix, is_last):
        """CompoundNode tidak print header, langsung print children"""
        result = ""
        children = getattr(self, 'children', [])
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            result += child._print_tree(prefix, is_last_child)
        return result

    def _format_inline_attrs(self) -> str:
        """Format inline attributes untuk node"""
        node_name = self.__class__.__name__
        if node_name == "VarNode":
            return f"('{self.name}')"
        if node_name == "NumNode":
            return f"({self.value})"
        if node_name == "StringNode":
            return f"('{self.value}')"
        if node_name == "CharNode":
            return f"('{self.value}')"
        if node_name == "BoolNode":
            return f"({self.value})"
        if node_name == "BinOpNode":
            return f"(op: '{self.op}')"
        if node_name == "UnaryOpNode":
            return f"(op: '{self.op}')"
        
        # AssignNode - dengan multi-line support
        if node_name == "AssignNode":
            return self._format_assign_inline()
        
        # ProcedureCallNode
        if node_name == "ProcedureCallNode":
            return self._format_proc_call_inline()
        return ""

    def _format_assign_inline(self) -> str:
        """Format AssignNode dengan deteksi multi-line"""
        target_str = self._format_node_compact(self.target)
        
        # Check if value is simple
        if isinstance(self.value, (NumNode, VarNode, StringNode, CharNode, BoolNode)):
            value_str = self._format_node_compact(self.value)
            return f"(target: {target_str}, value: {value_str})"
        
        # For complex values, we need multi-line (handled in _print_tree)
        # Return partial for now
        return f"(target: {target_str},"

    def _format_proc_call_inline(self) -> str:
        """Format ProcedureCallNode inline"""
        if not self.arguments:
            return f"(name: '{self.proc_name}', args: [])"
        
        args = []
        for arg in self.arguments:
            args.append(self._format_node_compact(arg))
        
        args_str = ", ".join(args)
        return f"(name: '{self.proc_name}', args: [{args_str}])"

    def _format_node_compact(self, node) -> str:
        """Format node dalam bentuk compact string"""
        if isinstance(node, VarNode):
            return f"Var('{node.name}')"
        elif isinstance(node, NumNode):
            return f"Num({node.value})"
        elif isinstance(node, StringNode):
            return f"String('{node.value}')"
        elif isinstance(node, CharNode):
            return f"Char('{node.value}')"
        elif isinstance(node, BoolNode):
            return f"Bool({node.value})"
        return str(node)

    def _format_decl_inline(self) -> str:
        """Format declaration untuk Declarations section"""
        node_name = self.__class__.__name__
        
        if node_name == "VarDeclNode":
            type_name = self.type_node.type_name if hasattr(self.type_node, 'type_name') else str(self.type_node)
            return f"VarDecl(name: '{self.var_name}', type: '{type_name}')"
        
        if node_name == "ConstDeclNode":
            value_str = self._format_node_compact(self.value)
            return f"ConstDecl(name: '{self.const_name}', value: {value_str})"
        
        if node_name == "TypeDeclNode":
            return f"TypeDecl(name: '{self.type_name}')"
        
        if node_name == "ProcedureDeclNode":
            return f"ProcedureDecl(name: '{self.name}')"
        
        if node_name == "FunctionDeclNode":
            return f"FunctionDecl(name: '{self.name}')"
        
        return str(self)

    def _get_printable_children(self) -> List['ASTNode']:
        """Get child nodes untuk printing"""
        children = []
        
        for f in fields(self):
            # Skip metadata fields
            if f.name in ['type', 'symbol_entry', 'name', 'var_name', 'const_name', 
                          'type_name', 'proc_name', 'op', 'value', 'variable', 
                          'direction', 'field_name', 'is_ref', 'names']:
                continue
            
            # Skip fields yang sudah di-handle di inline
            if self.__class__.__name__ == "AssignNode" and f.name in ['target', 'value']:
                continue
            
            if self.__class__.__name__ == "ProcedureCallNode" and f.name == "arguments":
                continue
            
            val = getattr(self, f.name, None)
            
            if isinstance(val, ASTNode):
                children.append(val)
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, ASTNode):
                        children.append(item)
        
        return children

    def _print_tree_multiline(self, prefix, is_last):
        """Special print untuk AssignNode dengan complex value"""
        if self.__class__.__name__ != "AssignNode":
            return self._print_tree(prefix, is_last)
        
        connector = "\\-- " if is_last else "+-- "
        target_str = self._format_node_compact(self.target)
        
        # Check if simple
        if isinstance(self.value, (NumNode, VarNode, StringNode, CharNode, BoolNode)):
            value_str = self._format_node_compact(self.value)
            return f"{prefix}{connector}Assign(target: {target_str}, value: {value_str})\n"
        
        # Multi-line
        result = f"{prefix}{connector}Assign(target: {target_str},\n"
        continuation = "    " if is_last else "|   "
        
        # Format value dengan indentasi
        if isinstance(self.value, BinOpNode):
            value_lines = self._format_binop_multiline(self.value)
            for i, line in enumerate(value_lines):
                if i == 0:
                    result += f"{prefix}{continuation}       value: {line}\n"
                else:
                    result += f"{prefix}{continuation}              {line}\n"
        else:
            value_str = self._format_node_compact(self.value)
            result += f"{prefix}{continuation}       value: {value_str})\n"
        
        return result

    def _format_binop_multiline(self, node) -> List[str]:
        """Format BinOp untuk multi-line display"""
        left_str = self._format_node_compact(node.left)
        right_str = self._format_node_compact(node.right)
        
        return [
            f"BinOp(op: '{node.op}',",
            f"       left: {left_str},",
            f"       right: {right_str})"
        ]
    
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