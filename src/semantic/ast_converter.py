from typing import List
# FIX IMPORT: Sesuaikan dengan struktur project Anda
from syntax.parsetree import Node 
from lexical.token import Token
from syntax.cfg import NonTerminal 

# Import lokal node AST
from .ast_nodes import *

class ASTConverter:
    def convert(self, parse_tree_root: Node) -> ASTNode:
        # Handle wrapper <S> jika ada
        if parse_tree_root.value == NonTerminal("<S>"):
            return self.convert(parse_tree_root.children[0])
        
        if parse_tree_root.value == NonTerminal("<Program>"):
            return self._convert_Program(parse_tree_root)
        
        raise ValueError(f"Root bukan <Program> atau <S>, tapi {parse_tree_root.value}")

    def visit(self, node):
        """Helper untuk menavigasi node secara dinamis."""
        if isinstance(node, Node):
            # Ubah <Nama-Node> menjadi _convert_Nama_Node
            clean_name = str(node.value).replace('<', '').replace('>', '').replace('-', '_')
            method_name = '_convert_' + clean_name
            method = getattr(self, method_name, self._generic_visit)
            return method(node)
        return node

    def _generic_visit(self, node):
        return None

    # --- HELPER: Ambil Lexeme Aman ---
    def _get_lexeme(self, node_or_token) -> str:
        if isinstance(node_or_token, Token):
            return node_or_token.lexeme
        if isinstance(node_or_token, Node):
            if isinstance(node_or_token.value, Token):
                return node_or_token.value.lexeme
            return str(node_or_token.value)
        return str(node_or_token)

    # --- Program Structure ---
    def _convert_Program(self, node: Node) -> ProgramNode:
        # Cek struktur: Apakah <ProgramHeader> <Block> DOT ?
        # Atau <ProgramHeader> <DeclarationPart> <CompoundStatement> DOT ?
        
        header = node.children[0] 
        prog_name = self._get_lexeme(header.children[1]) 
        
        child_1 = node.children[1]
        
        declarations = []
        compound = CompoundNode(children=[])

        # KASUS 1: Program -> Header Block DOT
        if str(child_1.value) == "<Block>":
            # Block -> DeclarationPart StatementPart
            decl_node = child_1.children[0]
            stmt_part = child_1.children[1] # StatementPart -> CompoundStatement
            
            declarations = self._convert_DeclarationPart(decl_node)
            compound = self.visit(stmt_part) # Visit StatementPart
            
        # KASUS 2: Program -> Header DeclarationPart CompoundStatement DOT
        else:
            declarations = self._convert_DeclarationPart(child_1)
            compound = self._convert_CompoundStatement(node.children[2])
        
        return ProgramNode(name=prog_name, declarations=declarations, block=compound)

    def _convert_StatementPart(self, node: Node) -> CompoundNode:
        # <StatementPart> -> <CompoundStatement>
        return self._convert_CompoundStatement(node.children[0])

    def _convert_DeclarationPart(self, node: Node) -> List[ASTNode]:
        decls = []
        self._collect_decls(node, decls)
        return decls

    def _collect_decls(self, node, decl_list):
        if not node.children or str(node.children[0].value) == "EPSILON":
            return
        
        # Child 0: ConstDecl, VarDeclPart, etc.
        res = self.visit(node.children[0])
        if isinstance(res, list):
            decl_list.extend(res)
        elif res:
            decl_list.append(res)
            
        # Child 1: DeclarationPart (recursive)
        if len(node.children) > 1:
            # Pastikan anak kedua benar-benar DeclarationPart sebelum recurse
            # untuk menghindari memakan StatementPart jika struktur Block tercampur
            if str(node.children[1].value) == "<DeclarationPart>":
                self._collect_decls(node.children[1], decl_list)

    # --- Variables ---
    def _convert_VarDeclarationPart(self, node: Node) -> List[VarDeclNode]:
        if not node.children or str(node.children[0].value) == "EPSILON": return []
        
        vars_list = []
        if len(node.children) > 1:
            vars_list.extend(self.visit(node.children[1]))
        
        if len(node.children) > 2:
            self._collect_var_prime(node.children[2], vars_list)
        return vars_list

    def _collect_var_prime(self, node, vars_list):
        if not node.children or str(node.children[0].value) == "EPSILON": return
        vars_list.extend(self.visit(node.children[0]))
        if len(node.children) > 1:
            self._collect_var_prime(node.children[1], vars_list)

    def _convert_VarDeclaration(self, node: Node) -> List[VarDeclNode]:
        ids = self.visit(node.children[0]) 
        type_node = self.visit(node.children[2]) 
        return [VarDeclNode(var_name=name, type_node=type_node) for name in ids]

    def _convert_IdentifierList(self, node: Node) -> List[str]:
        ids = [self._get_lexeme(node.children[0])]
        if len(node.children) > 1:
            self._collect_ids(node.children[1], ids)
        return ids

    def _collect_ids(self, node, ids):
        if not node.children or str(node.children[0].value) == "EPSILON": return
        ids.append(self._get_lexeme(node.children[1]))
        if len(node.children) > 2:
            self._collect_ids(node.children[2], ids)

    def _convert_Type(self, node: Node) -> TypeNode:
        token_node = node.children[0]
        if isinstance(token_node, Node) and "ArrayType" in str(token_node.value):
             return TypeNode(type_name="array")
        return TypeNode(type_name=self._get_lexeme(token_node))

    # --- Statements ---
    def _convert_CompoundStatement(self, node: Node) -> CompoundNode:
        # mulai <StmtList> selesai
        if len(node.children) > 1:
            stmts = self.visit(node.children[1])
        else:
            stmts = []
        return CompoundNode(children=stmts)

    def _convert_StatementList(self, node: Node) -> List[ASTNode]:
        stmts = []
        if not node.children or str(node.children[0].value) == "EPSILON": return stmts
        
        first = self.visit(node.children[0])
        if first and not isinstance(first, NoOpNode): 
            stmts.append(first)
        
        if len(node.children) > 1:
            self._collect_stmt_prime(node.children[1], stmts)
        return stmts

    def _collect_stmt_prime(self, node, stmts):
        if not node.children or str(node.children[0].value) == "EPSILON": return
        s = self.visit(node.children[1]) 
        if s and not isinstance(s, NoOpNode): 
            stmts.append(s)
        if len(node.children) > 2:
            self._collect_stmt_prime(node.children[2], stmts)

    def _convert_Statement(self, node: Node):
        if not node.children: return NoOpNode()
        child = node.children[0]
        if str(child.value) == "EPSILON": return NoOpNode()
        return self.visit(child)

    def _convert_AssignmentStatement(self, node: Node) -> AssignNode:
        target_name = self._get_lexeme(node.children[0])
        target = VarNode(name=target_name)
        
        num_children = len(node.children)
        
        if num_children >= 6:
             expr = self.visit(node.children[5])
        elif num_children >= 3:
             expr = self.visit(node.children[2])
        else:
             expr = NoOpNode()
        
        return AssignNode(target=target, value=expr)
    
    def _convert_ProcedureCall(self, node: Node) -> ProcedureCallNode:
        name = self._get_lexeme(node.children[0])
        params = []
        if len(node.children) >= 3:
            child_2 = node.children[2]
            child_2_val = str(child_2.value) if isinstance(child_2, Node) else ""
            if "RPAREN" not in child_2_val and child_2_val != ")":
                 res = self.visit(child_2)
                 if res: params = res
        return ProcedureCallNode(proc_name=name, arguments=params)

    def _convert_ParameterList(self, node: Node) -> List[ASTNode]:
        if not node.children or str(node.children[0].value) == "EPSILON": return []
        params = [self.visit(node.children[0])]
        if len(node.children) > 1:
            self._collect_params_prime(node.children[1], params)
        return params
    
    def _collect_params_prime(self, node, params):
        if not node.children or str(node.children[0].value) == "EPSILON": return
        params.append(self.visit(node.children[1])) 
        if len(node.children) > 2:
            self._collect_params_prime(node.children[2], params)
    
    def _convert_IfStatement(self, node: Node) -> IfNode:
        cond = self.visit(node.children[1])
        true_blk = self.visit(node.children[3])
        else_blk = None
        if len(node.children) > 5: 
             else_blk = self.visit(node.children[5])
        return IfNode(condition=cond, true_block=true_blk, else_block=else_blk)

    def _convert_WhileStatement(self, node: Node) -> WhileNode:
        cond = self.visit(node.children[1])
        body = self.visit(node.children[3])
        return WhileNode(condition=cond, body=body)

    def _convert_ForStatement(self, node: Node) -> ForNode:
        var = self._get_lexeme(node.children[1])
        start = self.visit(node.children[3])
        direct = self._get_lexeme(node.children[4])
        end = self.visit(node.children[5])
        body = self.visit(node.children[7])
        return ForNode(variable=var, start_expr=start, direction=direct, end_expr=end, body=body)

    # --- Expressions ---
    def _convert_Expression(self, node: Node):
        left = self.visit(node.children[0])
        if len(node.children) > 1:
            return self._visit_expr_prime(node.children[1], left)
        return left

    def _visit_expr_prime(self, node, left):
        if not node.children or str(node.children[0].value) == "EPSILON": return left
        op_node = node.children[0]
        op = self._get_lexeme(op_node.children[0]) 
        right = self.visit(node.children[1])
        return BinOpNode(op=op, left=left, right=right)

    def _convert_SimpleExpression(self, node: Node):
        left = self.visit(node.children[0])
        if len(node.children) > 1:
            return self._visit_simple_prime(node.children[1], left)
        return left

    def _visit_simple_prime(self, node, left):
        if not node.children or str(node.children[0].value) == "EPSILON": return left
        op = self._get_lexeme(node.children[0].children[0])
        right = self.visit(node.children[1])
        new_left = BinOpNode(op=op, left=left, right=right)
        if len(node.children) > 2:
            return self._visit_simple_prime(node.children[2], new_left)
        return new_left

    def _convert_Term(self, node: Node):
        left = self.visit(node.children[0])
        if len(node.children) > 1:
            return self._visit_term_prime(node.children[1], left)
        return left

    def _visit_term_prime(self, node, left):
        if not node.children or str(node.children[0].value) == "EPSILON": return left
        op = self._get_lexeme(node.children[0].children[0])
        right = self.visit(node.children[1])
        new_left = BinOpNode(op=op, left=left, right=right)
        if len(node.children) > 2:
            return self._visit_term_prime(node.children[2], new_left)
        return new_left

    def _convert_Factor(self, node: Node):
        first = node.children[0]
        first_val = first.value
        
        if isinstance(first_val, Token):
            lexeme = first_val.lexeme
            token_type = first_val.token_type
            
            if token_type == "NUMBER":
                val = float(lexeme) if '.' in lexeme or 'e' in lexeme.lower() else int(lexeme)
                return NumNode(value=val)
            elif token_type == "IDENTIFIER":
                if len(node.children) > 1:
                     second = node.children[1]
                     sec_val = self._get_lexeme(second)
                     if sec_val == "(":
                         if len(node.children) > 2:
                             params = self.visit(node.children[2])
                             return ProcedureCallNode(proc_name=lexeme, arguments=params)
                         else:
                             return ProcedureCallNode(proc_name=lexeme, arguments=[])
                return VarNode(name=lexeme)
            elif token_type == "STRING_LITERAL":
                return StringNode(value=lexeme)
            elif token_type == "CHAR_LITERAL":
                return CharNode(value=lexeme)
            elif token_type == "LOGICAL_OPERATOR" and lexeme == "tidak":
                 return UnaryOpNode(op="tidak", expr=self.visit(node.children[1]))
        
        elif str(first_val) == "LPARENTHESIS":
             return self.visit(node.children[1])
        
        return NoOpNode()
    
    