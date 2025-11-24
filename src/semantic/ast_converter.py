from typing import List, Optional, Union
from syntax.parsetree import Node 
from lexical.token import Token
from syntax.cfg import NonTerminal 
from .ast_nodes import *

class ASTConverter:
    def convert(self, parse_tree_root: Node) -> ASTNode:
        """Entry point untuk konversi Parse Tree ke AST"""
        if parse_tree_root.value == NonTerminal("<S>"):
            return self.convert(parse_tree_root.children[0])
        
        if parse_tree_root.value == NonTerminal("<Program>"):
            return self._convert_Program(parse_tree_root)
        
        raise ValueError(f"Root bukan <Program> atau <S>, tapi {parse_tree_root.value}")

    def visit(self, node):
        """Helper untuk menavigasi node secara dinamis."""
        if isinstance(node, Node):
            clean_name = str(node.value).replace('<', '').replace('>', '').replace('-', '_')
            
            # --- MAPPING MANUAL ---
            if clean_name == "VarDeclOpt": method_name = "_convert_VarDeclarationPart"
            elif clean_name == "ConstDeclOpt": method_name = "_convert_ConstDeclarationPart"
            elif clean_name == "TypeDeclOpt": method_name = "_convert_TypeDeclarationPart"
            elif clean_name == "SubprogDeclList": method_name = "_convert_SubprogDeclList"
            elif clean_name == "StatementPart": method_name = "_convert_StatementPart"
            else: method_name = '_convert_' + clean_name
            
            method = getattr(self, method_name, self._generic_visit)
            return method(node)
        return node

    def _generic_visit(self, node):
        return None

    # --- HELPERS ---
    def _get_lexeme(self, node_or_token) -> str:
        token = self._get_token(node_or_token)
        return token.lexeme if token else ""
    
    def _get_token(self, node_or_token) -> Optional[Token]:
        if isinstance(node_or_token, Token): return node_or_token
        if isinstance(node_or_token, Node):
            if isinstance(node_or_token.value, Token): return node_or_token.value
            if str(node_or_token.value) == "EPSILON": return None
            if node_or_token.children:
                for child in node_or_token.children:
                    found = self._get_token(child)
                    if found: return found
        return None

    def _get_operator_lexeme(self, node: Node) -> str:
        return self._get_lexeme(node)

    # ==================== PROGRAM STRUCTURE ====================
    def _convert_Program(self, node: Node) -> ProgramNode:
        header = node.children[0] 
        prog_name = self._get_lexeme(header.children[1]) 
        
        child_1 = node.children[1]
        if str(child_1.value) == "<Block>":
            decl_node = child_1.children[0]
            stmt_part = child_1.children[1]
            declarations = self._convert_DeclarationPart(decl_node)
            compound = self.visit(stmt_part)
        else:
            declarations = self._convert_DeclarationPart(child_1)
            compound = self._convert_CompoundStatement(node.children[2])
        
        return ProgramNode(name=prog_name, declarations=declarations, block=compound)

    def _convert_StatementPart(self, node: Node) -> CompoundNode:
        return self._convert_CompoundStatement(node.children[0])

    def _convert_DeclarationPart(self, node: Node) -> List[ASTNode]:
        decls = []
        if not node.children: return decls
        for child in node.children:
            if isinstance(child, Node) and str(child.value) == "EPSILON": continue
            res = self.visit(child)
            if isinstance(res, list): decls.extend(res)
            elif res and not isinstance(res, NoOpNode): decls.append(res)
        return decls

    # ==================== DECLARATIONS ====================
    def _convert_ConstDeclarationPart(self, node: Node) -> List[ConstDeclNode]:
        if not node.children or str(node.children[0].value) == "EPSILON": return []
        if len(node.children) > 1: return self.visit(node.children[1])
        return []

    def _convert_ConstList(self, node: Node) -> List[ConstDeclNode]:
        if not node.children or str(node.children[0].value) == "EPSILON": return []
        consts = []
        const_name = self._get_lexeme(node.children[0])
        val_node = self.visit(node.children[2])
        consts.append(ConstDeclNode(const_name=const_name, value=val_node))
        if len(node.children) > 4:
            rest = self.visit(node.children[4])
            if rest: consts.extend(rest)
        return consts

    def _convert_TypeDeclarationPart(self, node: Node) -> List[TypeDeclNode]:
        if not node.children or str(node.children[0].value) == "EPSILON": return []
        return self.visit(node.children[1])

    def _convert_TypeList(self, node: Node) -> List[TypeDeclNode]:
        if not node.children or str(node.children[0].value) == "EPSILON": return []
        types = []
        type_name = self._get_lexeme(node.children[0])
        type_val = self.visit(node.children[2])
        types.append(TypeDeclNode(type_name=type_name, value=type_val))
        if len(node.children) > 4:
            rest = self.visit(node.children[4])
            if rest: types.extend(rest)
        return types

    def _convert_VarDeclarationPart(self, node: Node) -> List[VarDeclNode]:
        if not node.children or str(node.children[0].value) == "EPSILON": return []
        if len(node.children) > 1:
            if "List" in str(node.children[1].value): return self.visit(node.children[1])
            vars_list = []
            res = self.visit(node.children[1])
            if res: vars_list.extend(res)
            if len(node.children) > 2: self._collect_var_prime(node.children[2], vars_list)
            return vars_list
        return []

    def _convert_VarDeclList(self, node: Node) -> List[VarDeclNode]:
        if not node.children or str(node.children[0].value) == "EPSILON": return []
        vars_list = []
        curr = self.visit(node.children[0])
        if curr: vars_list.extend(curr)
        if len(node.children) > 2:
            vars_list.extend(self._convert_VarDeclList(node.children[2]))
        return vars_list

    def _collect_var_prime(self, node, vars_list):
        if not node.children or str(node.children[0].value) == "EPSILON": return
        vars_list.extend(self.visit(node.children[0]))
        if len(node.children) > 1: self._collect_var_prime(node.children[1], vars_list)

    def _convert_VarDeclaration(self, node: Node) -> List[VarDeclNode]:
        ids = self.visit(node.children[0]) 
        type_node = self.visit(node.children[2]) 
        return [VarDeclNode(var_name=name, type_node=type_node) for name in ids]

    def _convert_IdentifierList(self, node: Node) -> List[str]:
        ids = [self._get_lexeme(node.children[0])]
        if len(node.children) > 1: self._collect_ids(node.children[1], ids)
        return ids

    def _collect_ids(self, node, ids):
        if not node.children or str(node.children[0].value) == "EPSILON": return
        ids.append(self._get_lexeme(node.children[1]))
        if len(node.children) > 2: self._collect_ids(node.children[2], ids)

    # ==================== TYPES & SUBPROGRAMS ====================
    def _convert_Type(self, node: Node) -> ASTNode:
        return self.visit(node.children[0]) 

    def _convert_SimpleType(self, node: Node) -> TypeNode:
        return TypeNode(type_name=self._get_lexeme(node))

    def _convert_ArrayType(self, node: Node) -> ArrayTypeNode:
        range_node = node.children[2] 
        elem_type = self.visit(node.children[5]) 
        lower = self.visit(range_node.children[0])
        upper = self.visit(range_node.children[2])
        return ArrayTypeNode(lower=lower, upper=upper, element_type=elem_type)

    def _convert_RecordType(self, node: Node) -> RecordTypeNode:
        fields = []
        if len(node.children) > 1: fields = self.visit(node.children[1])
        return RecordTypeNode(fields=fields)

    def _convert_FieldList(self, node: Node) -> List[VarDeclNode]:
        fields = []
        self._collect_fields(node, fields)
        return fields

    def _collect_fields(self, node, fields):
        if not node.children or str(node.children[0].value) == "EPSILON": return
        f = self.visit(node.children[0])
        if f: fields.extend(f)
        if len(node.children) > 1: self._collect_fields(node.children[1], fields)

    def _convert_SubprogDeclList(self, node: Node) -> List[ASTNode]:
        if not node.children or str(node.children[0].value) == "EPSILON": return []
        subs = []
        sub = self.visit(node.children[0])
        if sub: subs.append(sub)
        if len(node.children) > 2: subs.extend(self.visit(node.children[2]))
        return subs

    def _convert_SubprogramDeclaration(self, node: Node):
        return self.visit(node.children[0])

    def _convert_ProcedureDeclaration(self, node: Node) -> ProcedureDeclNode:
        name = self._get_lexeme(node.children[1])
        params = []
        block = None
        for child in node.children:
            val = str(child.value)
            if "FormalParam" in val:
                res = self.visit(child)
                if res: params = res
            elif "Block" in val:
                # Unpack Block
                decl_part = child.children[0]
                stmt_part = child.children[1]
                decls = self._convert_DeclarationPart(decl_part)
                body = self.visit(stmt_part)
                block = CompoundNode(children=body.children) # Simplified for now
                # Idealnya simpan decls di ProcDeclNode
        return ProcedureDeclNode(name=name, params=params, block=block)

    def _convert_FunctionDeclaration(self, node: Node) -> FunctionDeclNode:
        name = self._get_lexeme(node.children[1])
        params = []
        return_type = None
        block = None
        for child in node.children:
            val = str(child.value)
            if "FormalParam" in val:
                res = self.visit(child)
                if res: params = res
            elif "Type" in val and "Decl" not in val:
                return_type = self.visit(child)
            elif "Block" in val:
                block = self.visit(child.children[1])
        return FunctionDeclNode(name=name, return_type=return_type, params=params, block=block)

    def _convert_FormalParamOpt(self, node: Node):
        if not node.children or str(node.children[0].value) == "EPSILON": return []
        return self.visit(node.children[0])

    def _convert_FormalParameterList(self, node: Node):
        return self.visit(node.children[1]) 

    def _convert_ParamSectionList(self, node: Node) -> List[ParameterNode]:
        params = []
        p = self.visit(node.children[0])
        if p: params.extend(p)
        if len(node.children) > 1:
            self._collect_param_section_prime(node.children[1], params)
        return params

    def _collect_param_section_prime(self, node, params):
        if not node.children or str(node.children[0].value) == "EPSILON": return
        p = self.visit(node.children[1])
        if p: params.extend(p)
        if len(node.children) > 2:
            self._collect_param_section_prime(node.children[2], params)

    def _convert_ParamSection(self, node: Node) -> List[ParameterNode]:
        """Handle: VAR? <IdentifierList> : <Type>"""
        is_ref = False
        start_idx = 0
        
        # 1. Cek Keyword VAR/VARIABEL
        # Anak ke-0 bisa berupa Node VarKeywordOpt atau Token langsung
        first_child = node.children[0]
        first_lex = self._get_lexeme(first_child).lower()
        
        # Jika node VarKeywordOpt punya anak (bukan Epsilon)
        if isinstance(first_child, Node) and "VarKeywordOpt" in str(first_child.value):
            if first_child.children and str(first_child.children[0].value) != "EPSILON":
                is_ref = True
            # Jika ada VarKeywordOpt, IdentifierList biasanya geser ke index 1
            start_idx = 1
            
        # Jika struktur flat (langsung keyword 'variabel')
        elif first_lex in ["var", "variabel"]:
            is_ref = True
            start_idx = 1
            
        # 2. Ambil Identifier List
        # Pastikan kita mengambil node yang benar
        id_list_node = node.children[start_idx]
        names = self.visit(id_list_node)
        
        # SAFETY CHECK: Jika names None, inisialisasi list kosong untuk mencegah crash
        if names is None:
            print(f"[WARN] Identifier list parsing failed for node: {id_list_node.value}")
            names = []
            
        # 3. Ambil Type
        # Type ada setelah COLON.
        # Struktur: [VarOpt, IdList, Colon, Type] -> index Type = start_idx + 2
        type_idx = start_idx + 2
        type_node = None
        
        if len(node.children) > type_idx:
             type_node = self.visit(node.children[type_idx])
        
        # Buat ParameterNode
        return [ParameterNode(names=[n], type_node=type_node, is_ref=is_ref) for n in names]

    # ==================== STATEMENTS ====================
    def _convert_CompoundStatement(self, node: Node) -> CompoundNode:
        if len(node.children) > 1:
            stmts = self.visit(node.children[1])
            return CompoundNode(children=stmts if stmts else [])
        return CompoundNode(children=[])

    def _convert_StatementList(self, node: Node) -> List[ASTNode]:
        stmts = []
        if not node.children or str(node.children[0].value) == "EPSILON": return stmts
        
        first = self.visit(node.children[0])
        if first and not isinstance(first, NoOpNode): stmts.append(first)
        
        if len(node.children) > 1: self._collect_stmt_prime(node.children[1], stmts)
        return stmts

    def _collect_stmt_prime(self, node, stmts):
        if not node.children or str(node.children[0].value) == "EPSILON": return
        s = self.visit(node.children[1]) 
        if s and not isinstance(s, NoOpNode): stmts.append(s)
        if len(node.children) > 2: self._collect_stmt_prime(node.children[2], stmts)

    def _convert_Statement(self, node: Node):
        if not node.children or str(node.children[0].value) == "EPSILON": return NoOpNode()
        return self.visit(node.children[0])

    def _convert_AssignmentStatement(self, node: Node) -> AssignNode:
        """Handle: IDENTIFIER <VariableTail>? := <Expression>"""
        
        # 1. Ambil Target Dasar
        target_name = self._get_lexeme(node.children[0])
        target = VarNode(name=target_name)
        
        expr = NoOpNode()
        
        # 2. Deteksi Struktur berdasarkan Anak
        # Cari posisi token ASSIGN (:=)
        assign_idx = -1
        for i, child in enumerate(node.children):
            # Cek lexeme token langsung atau bungkusannya
            lex = self._get_lexeme(child)
            if lex == ":=":
                assign_idx = i
                break
        
        # Jika ketemu :=
        if assign_idx != -1:
            # 3. Handle Bagian Kiri (Target)
            # Jika ada node di antara ID (index 0) dan := (assign_idx)
            # Itu adalah VariableTail (Array Index / Record Access)
            if assign_idx > 1:
                # Ada tail, misalnya di index 1
                # Kita asumsikan node.children[1] adalah VariableTail atau LBRACKET dkk
                # Panggil _handle_variable_tail untuk membungkus target
                target = self._handle_variable_tail(target, node.children[1])
            
            # 4. Handle Bagian Kanan (Expression)
            # Expression ada setelah :=
            if len(node.children) > assign_idx + 1:
                res = self.visit(node.children[assign_idx + 1])
                if res is not None:
                    expr = res
                else:
                    # Debugging bantu: Kenapa None?
                    # print(f"[WARN] Expr conversion returned None for {node.children[assign_idx+1].value}")
                    pass

        return AssignNode(target=target, value=expr)

    # --- PARAMETER LIST FIX ---
    def _convert_ParameterList(self, node: Node) -> List[ASTNode]:
        # <ParameterList> -> <Expression> , <ParameterList> | <Expression>
        # Parse Tree structure:
        # Index 0: Expression
        # Index 2: ParameterList (Recursive) IF comma exists
        
        params = [self.visit(node.children[0])] # First Expression
        
        if len(node.children) > 2:
            # Ada koma dan recursive list
            rest = self.visit(node.children[2])
            if rest: params.extend(rest)
            
        return params

    def _convert_ProcedureCall(self, node: Node) -> ProcedureCallNode:
        """Handle: IDENTIFIER (<ParameterList>?)"""
        name = self._get_lexeme(node.children[0])
        params = []
        
        # Cek jumlah anak untuk menentukan struktur
        # Struktur 1: ID ( Params ) -> Minimal 3 anak (ID, Lparen, Rparen)
        if len(node.children) >= 3:
            child_2 = node.children[2]
            # Cek apakah anak ke-2 bukan RPAREN (berarti ada parameter list)
            val_2 = str(child_2.value) if isinstance(child_2, Node) else str(child_2)
            if "RPAREN" not in val_2 and val_2 != ")":
                res = self.visit(child_2)
                if res: params = res
                
        # Struktur 2: ID <ParamOpt> -> 2 anak
        elif len(node.children) == 2:
            # Visit anak kedua (ParamOpt atau sejenisnya)
            res = self.visit(node.children[1])
            if res: params = res
            
        return ProcedureCallNode(proc_name=name, arguments=params)

    def _convert_ExpressionList(self, node: Node) -> List[ASTNode]:
        # Fallback if grammar uses ExpressionList
        return self._convert_ParameterList(node)

    def _convert_IfStatement(self, node: Node) -> IfNode:
        cond = self.visit(node.children[1])
        true_blk = self.visit(node.children[3])
        else_blk = None
        
        # Scan for ElsePart or SELAIN-ITU
        if len(node.children) > 4:
            for child in node.children[4:]:
                if str(child.value) == "<ElsePart>":
                    else_blk = self.visit(child)
                    break
                if self._get_lexeme(child).lower() == "selain-itu":
                    # Next child is Statement
                    else_blk = self.visit(node.children[-1])
                    break
        return IfNode(condition=cond, true_block=true_blk, else_block=else_blk)

    def _convert_ElsePart(self, node: Node):
        if not node.children or str(node.children[0].value) == "EPSILON": return None
        return self.visit(node.children[1])
    
    def _convert_WhileStatement(self, node: Node) -> WhileNode:
        cond = self.visit(node.children[1])
        body = self.visit(node.children[3])
        return WhileNode(condition=cond, body=body)

    def _convert_ForStatement(self, node: Node) -> ForNode:
        var = self._get_lexeme(node.children[1])
        start = self.visit(node.children[3])
        direct = self._get_lexeme(node.children[4])
        if not isinstance(direct, str): direct = self._get_lexeme(node.children[4].children[0])
        end = self.visit(node.children[5])
        body = self.visit(node.children[7])
        return ForNode(variable=var, start_expr=start, direction=direct, end_expr=end, body=body)

    # ==================== EXPRESSIONS ====================
    def _convert_Expression(self, node: Node):
        left = self.visit(node.children[0])
        if len(node.children) > 1: return self._visit_expr_prime(node.children[1], left)
        return left

    def _visit_expr_prime(self, node, left):
        if not node.children or str(node.children[0].value) == "EPSILON": return left
        op = self._get_operator_lexeme(node.children[0])
        right = self.visit(node.children[1])
        return BinOpNode(op=op, left=left, right=right)

    def _convert_SimpleExpression(self, node: Node):
        left = self.visit(node.children[0])
        if len(node.children) > 1: return self._visit_simple_prime(node.children[1], left)
        return left

    def _visit_simple_prime(self, node, left):
        if not node.children or str(node.children[0].value) == "EPSILON": return left
        op = self._get_operator_lexeme(node.children[0])
        right = self.visit(node.children[1])
        new_left = BinOpNode(op=op, left=left, right=right)
        if len(node.children) > 2: return self._visit_simple_prime(node.children[2], new_left)
        return new_left

    def _convert_SignedTerm(self, node: Node):
        sign_node = node.children[0]
        unary = None
        if sign_node.children and str(sign_node.children[0].value) != "EPSILON":
             unary = self._get_lexeme(sign_node.children[0].children[0])
        term = self.visit(node.children[1])
        if unary == "-": return UnaryOpNode(op="-", expr=term)
        return term

    def _convert_Term(self, node: Node):
        left = self.visit(node.children[0])
        if len(node.children) > 1: return self._visit_term_prime(node.children[1], left)
        return left

    def _visit_term_prime(self, node, left):
        if not node.children or str(node.children[0].value) == "EPSILON": return left
        op = self._get_operator_lexeme(node.children[0])
        right = self.visit(node.children[1])
        new_left = BinOpNode(op=op, left=left, right=right)
        if len(node.children) > 2: return self._visit_term_prime(node.children[2], new_left)
        return new_left

    def _convert_Factor(self, node: Node):
        first = node.children[0]
        val_str = str(first.value)
        
        if val_str == "<Variable>": return self._convert_Variable(first)
        if val_str == "<Constant>": return self._convert_Constant(first)
        
        # Parenthesis ( Expr )
        if self._get_lexeme(first) == "(":
             return self.visit(node.children[1])

        token = self._get_token(first)
        if token:
            lex = token.lexeme
            if token.token_type == "LOGICAL_OPERATOR" and lex.lower() == "tidak":
                 return UnaryOpNode(op="tidak", expr=self.visit(node.children[1]))
            if token.token_type == "NUMBER":
                try: val = float(lex) if '.' in lex else int(lex)
                except: val = 0
                return NumNode(value=val)
            if token.token_type == "IDENTIFIER":
                 if len(node.children) > 1 and self._get_lexeme(node.children[1]) == "(":
                     params = []
                     if len(node.children) > 2:
                          res = self.visit(node.children[2])
                          if res: params = res
                     return ProcedureCallNode(proc_name=lex, arguments=params)
                 return VarNode(name=lex)
        
        return NoOpNode()

    def _convert_Variable(self, node: Node):
        name = self._get_lexeme(node.children[0])
        base = VarNode(name=name)
        if len(node.children) > 1: return self._handle_variable_tail(base, node.children[1])
        return base

    def _handle_variable_tail(self, base, node):
        if not node.children or str(node.children[0].value) == "EPSILON": return base
        first = self._get_lexeme(node.children[0])
        if first == "[":
             idx = self.visit(node.children[1])
             new_base = ArrayAccessNode(array=base, index=idx)
             if len(node.children) > 3: return self._handle_variable_tail(new_base, node.children[3])
             return new_base
        if first == ".":
             field = self._get_lexeme(node.children[1])
             new_base = FieldAccessNode(record=base, field_name=field)
             if len(node.children) > 2: return self._handle_variable_tail(new_base, node.children[2])
             return new_base
        return base
    
    def _convert_Constant(self, node: Node):
        first = node.children[0]
        if str(first.value) == "<SignOpt>":
             sign = None
             if first.children and str(first.children[0].value) != "EPSILON":
                 sign = self._get_lexeme(first.children[0].children[0])
             val = self.visit(node.children[1])
             if sign == "-" and isinstance(val, NumNode): val.value = -val.value
             return val
        token = self._get_token(first)
        if token:
             if token.token_type == "STRING_LITERAL": return StringNode(value=token.lexeme)
             if token.token_type == "CHAR_LITERAL": return CharNode(value=token.lexeme)
             if token.lexeme.lower() == "true": return BoolNode(value=True)
             if token.lexeme.lower() == "false": return BoolNode(value=False)
        return NoOpNode()

    def _convert_UnsignedConstant(self, node: Node):
        token = self._get_token(node.children[0])
        if token:
             if token.token_type == "NUMBER":
                 try: val = float(token.lexeme) if '.' in token.lexeme else int(token.lexeme)
                 except: val = 0
                 return NumNode(value=val)
             if token.token_type == "IDENTIFIER": return VarNode(name=token.lexeme)
        return NoOpNode()