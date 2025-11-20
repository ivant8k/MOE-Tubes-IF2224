from typing import List, Union
from syntax.parsetree import Node 
from lexical.token import Token
from syntax.cfg import NonTerminal 

from .ast_nodes import *

class ASTConverter:
    def convert(self, parse_tree_root: Node) -> ASTNode:
        """Entry point untuk konversi Parse Tree ke AST"""
        # Handle wrapper <S> jika ada
        if parse_tree_root.value == NonTerminal("<S>"):
            return self.convert(parse_tree_root.children[0])
        
        if parse_tree_root.value == NonTerminal("<Program>"):
            return self._convert_Program(parse_tree_root)
        
        raise ValueError(f"Root bukan <Program> atau <S>, tapi {parse_tree_root.value}")

    def visit(self, node):
        if isinstance(node, Node):
            # Bersihkan nama: <VarDeclOpt> -> VarDeclOpt
            clean_name = str(node.value).replace('<', '').replace('>', '').replace('-', '_')
            
            # --- MAPPING MANUAL ---
            if clean_name == "VarDeclOpt": 
                method_name = "_convert_VarDeclarationPart"
            elif clean_name == "ConstDeclOpt":
                method_name = "_convert_ConstDeclarationPart"
            elif clean_name == "TypeDeclOpt":
                method_name = "_convert_TypeDeclarationPart"
            elif clean_name == "SubprogDeclList":
                method_name = "_convert_SubprogDeclList"
            else:
                # Default: <Program> -> _convert_Program
                method_name = '_convert_' + clean_name

            method = getattr(self, method_name, self._generic_visit)
            return method(node)
            
        return node

    def _generic_visit(self, node):
        """Fallback jika tidak ada handler spesifik"""
        return None

    # --- HELPER: Ambil Lexeme Aman ---
    def _get_lexeme(self, node_or_token) -> str:
        """Ambil string dari token terdalam"""
        token = self._get_token(node_or_token)
        return token.lexeme if token else ""
    
    def _get_token(self, node_or_token) -> Optional[Token]:
        """
        REKURSI PINTAR: Cari token daun (leaf) dengan menelusuri
        semua anak sampai ketemu yang bukan EPSILON.
        """
        # 1. Jika input sudah berupa Token, kembalikan langsung
        if isinstance(node_or_token, Token):
            return node_or_token
        
        # 2. Jika input adalah Node
        if isinstance(node_or_token, Node):
            # Cek value node itu sendiri
            if isinstance(node_or_token.value, Token):
                return node_or_token.value
            
            # Cek string value untuk EPSILON
            if str(node_or_token.value) == "EPSILON":
                return None

            # ITERASI ANAK (DFS): 
            if node_or_token.children:
                for child in node_or_token.children:
                    found = self._get_token(child)
                    if found:
                        return found
            
        return None

    # ==================== Program Structure ====================
    def _convert_Program(self, node: Node) -> ProgramNode:
        """
        Convert: <Program> -> <ProgramHeader> <Block> DOT
        atau: <Program> -> <ProgramHeader> <DeclarationPart> <CompoundStatement> DOT
        """
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
        """<StatementPart> -> <CompoundStatement>"""
        return self._convert_CompoundStatement(node.children[0])

    def _convert_DeclarationPart(self, node: Node) -> List[ASTNode]:
        decls = []
        if not node.children:
            return decls

        for child in node.children:
            # 1. Filter: Abaikan jika child adalah Token mentah (bukan Node)
            if isinstance(child, Node):
                if str(child.value) == "EPSILON":
                    continue
                
                # 2. Visit Node (Const, Type, Var, dll)
                res = self.visit(child)
                
                # 3. Safety Check: Pastikan hasil valid sebelum dimasukkan
                if isinstance(res, list):
                    decls.extend(res)
                elif isinstance(res, ASTNode) and not isinstance(res, NoOpNode):
                    decls.append(res)
            
        return decls
    # ==================== Constant Declarations ====================
    def _convert_ConstDeclarationPart(self, node: Node) -> List[ConstDeclNode]:
        """Handle: KONSTAN <ConstDeclList>"""
        if not node.children or str(node.children[0].value) == "EPSILON":
            return []
        
        const_list = []
        if len(node.children) > 1:
            self._collect_const_decls(node.children[1], const_list)
        return const_list

    def _collect_const_decls(self, node: Node, const_list: List[ConstDeclNode]):
        """Collect constant declarations recursively"""
        if not node.children or str(node.children[0].value) == "EPSILON":
            return

        const_decl = self.visit(node.children[0])
        if const_decl:
            const_list.append(const_decl)

        if len(node.children) > 1:
            self._collect_const_decls(node.children[1], const_list)

    def _convert_ConstDeclaration(self, node: Node) -> ConstDeclNode:
        """Handle: IDENTIFIER = <Expression> ;"""
        const_name = self._get_lexeme(node.children[0])
        value = self.visit(node.children[2])  # Expression
        return ConstDeclNode(const_name=const_name, value=value)

    # ==================== Type Declarations ====================
    def _convert_TypeDeclarationPart(self, node: Node) -> List[TypeDeclNode]:
        """Handle: TIPE <TypeDeclList>"""
        if not node.children or str(node.children[0].value) == "EPSILON":
            return []
        
        type_list = []
        if len(node.children) > 1:
            self._collect_type_decls(node.children[1], type_list)
        return type_list

    def _collect_type_decls(self, node: Node, type_list: List[TypeDeclNode]):
        """Collect type declarations recursively"""
        if not node.children or str(node.children[0].value) == "EPSILON":
            return
        
        type_decl = self.visit(node.children[0])
        if type_decl:
            type_list.append(type_decl)
        
        if len(node.children) > 1:
            self._collect_type_decls(node.children[1], type_list)

    def _convert_TypeDeclaration(self, node: Node) -> TypeDeclNode:
        """Handle: IDENTIFIER = <Type> ;"""
        type_name = self._get_lexeme(node.children[0])
        type_value = self.visit(node.children[2])
        return TypeDeclNode(type_name=type_name, value=type_value)

    # ==================== Variable Declarations ====================
    def _convert_VarDeclarationPart(self, node: Node) -> List[VarDeclNode]:
        # 1. Cek apakah node kosong atau Epsilon (tidak ada deklarasi variabel)
        if not node.children or str(node.children[0].value) == "EPSILON":
            return []

        # 2. Validasi anak kedua. Jika ada 'variabel', anak ke-1 (index 1) adalah <VarDeclList>
        if len(node.children) > 1:
            return self._convert_VarDeclList(node.children[1])
        
        return []
    
    def _convert_VarDeclList(self, node: Node) -> List[VarDeclNode]:
        if not node.children or str(node.children[0].value) == "EPSILON":
            return []

        vars_list = []

        # 1. Ambil deklarasi di head (VarDeclaration)
        current_decls = self.visit(node.children[0])
        if current_decls:
            vars_list.extend(current_decls)

        # 2. Rekursi ke tail (VarDeclList berikutnya)
        if len(node.children) > 2:
            next_decls = self._convert_VarDeclList(node.children[2])
            vars_list.extend(next_decls)

        return vars_list

    def _collect_var_prime(self, node: Node, vars_list: List[VarDeclNode]):
        """Recursively collect variable declarations"""
        if not node.children or str(node.children[0].value) == "EPSILON":
            return
        vars_list.extend(self.visit(node.children[0]))
        if len(node.children) > 1:
            self._collect_var_prime(node.children[1], vars_list)

    def _convert_VarDeclaration(self, node: Node) -> List[VarDeclNode]:
        """Handle: <IdentifierList> : <Type> ;"""
        ids = self.visit(node.children[0]) 
        type_node = self.visit(node.children[2]) 
        return [VarDeclNode(var_name=name, type_node=type_node) for name in ids]

    def _convert_IdentifierList(self, node: Node) -> List[str]:
        # <IdentifierList> -> ID <IdentifierListPrime>
        first_id = self._get_lexeme(node.children[0])
        ids = [first_id]
        
        if len(node.children) > 1:
            self._collect_ids(node.children[1], ids)
        return ids

    def _collect_ids(self, node: Node, ids: List[str]):
        """Recursively collect identifiers"""
        if not node.children or str(node.children[0].value) == "EPSILON":
            return

        # Ambil ID. Asumsi struktur: COMMA (0), ID (1), PRIME (2)
        if len(node.children) > 1:
            ids.append(self._get_lexeme(node.children[1]))
        
        # Rekursi
        if len(node.children) > 2:
            self._collect_ids(node.children[2], ids)

    def _convert_SimpleType(self, node: Node) -> TypeNode:
        """
        Handle: <SimpleType> -> integer | boolean | char
        """
        type_name = self._get_lexeme(node) 
        return TypeNode(type_name=type_name)

    # ==================== Types ====================
    def _convert_Type(self, node: Node) -> Union[TypeNode, ArrayTypeNode, RecordTypeNode]:
        token_node = node.children[0]
        
        # Array Type
        if isinstance(token_node, Node) and "ArrayType" in str(token_node.value):
            return self.visit(token_node)
        
        # Record Type
        if isinstance(token_node, Node) and "RecordType" in str(token_node.value):
            return self.visit(token_node)
            
        return TypeNode(type_name=self._get_lexeme(node))

    def _convert_ArrayType(self, node: Node) -> ArrayTypeNode:
        """Handle: ARRAY [ <Expression> .. <Expression> ] OF <Type>"""
        lower = self.visit(node.children[2])  # First expression
        upper = self.visit(node.children[4])  # Second expression
        elem_type = self.visit(node.children[7])  # Type after OF
        return ArrayTypeNode(lower=lower, upper=upper, element_type=elem_type)

    def _convert_RecordType(self, node: Node) -> RecordTypeNode:
        """Handle: RECORD <FieldList> END"""
        fields = []
        if len(node.children) > 1:
            fields = self.visit(node.children[1])
        return RecordTypeNode(fields=fields)

    def _convert_FieldList(self, node: Node) -> List[VarDeclNode]:
        """Collect record fields"""
        fields = []
        self._collect_fields(node, fields)
        return fields

    def _collect_fields(self, node: Node, fields):
        """Recursively collect field declarations"""
        if not node.children or str(node.children[0].value) == "EPSILON":
            return
        
        field_decls = self.visit(node.children[0])
        if isinstance(field_decls, list):
            fields.extend(field_decls)
        elif field_decls:
            fields.append(field_decls)
        
        if len(node.children) > 1:
            self._collect_fields(node.children[1], fields)

    # ==================== Subprograms ====================
    def _convert_ProcedureDeclaration(self, node: Node) -> ProcedureDeclNode:
        """Handle: PROCEDURE IDENTIFIER (<Params>) ; <Block> ;"""
        name = self._get_lexeme(node.children[1])
        params = []
        
        if len(node.children) > 3 and str(node.children[3].value) != "RPAREN":
            params = self.visit(node.children[3])

        block_idx = len(node.children) - 2
        block = self.visit(node.children[block_idx])
        
        return ProcedureDeclNode(name=name, params=params, block=block)

    def _convert_FunctionDeclaration(self, node: Node) -> FunctionDeclNode:
        """Handle: FUNCTION IDENTIFIER (<Params>) : <Type> ; <Block> ;"""
        name = self._get_lexeme(node.children[1])
        params = []
        
        # Check if there are parameters
        param_idx = 3
        if len(node.children) > param_idx and str(node.children[param_idx].value) != "RPAREN":
            params = self.visit(node.children[param_idx])
        
        # Return type
        return_type_idx = len(node.children) - 4
        return_type = self.visit(node.children[return_type_idx])
        
        # Block
        block_idx = len(node.children) - 2
        block = self.visit(node.children[block_idx])
        
        return FunctionDeclNode(name=name, return_type=return_type, params=params, block=block)

    def _convert_FormalParameters(self, node: Node) -> List[ParameterNode]:
        """Collect formal parameters"""
        params = []
        self._collect_formal_params(node, params)
        return params

    def _collect_formal_params(self, node: Node, params: List[ParameterNode]):
        """Recursively collect parameters"""
        if not node.children or str(node.children[0].value) == "EPSILON":
            return
        
        param = self.visit(node.children[0])
        if param:
            params.append(param)
        
        if len(node.children) > 1:
            self._collect_formal_params(node.children[1], params)

    def _convert_ParameterGroup(self, node: Node) -> ParameterNode:
        """Handle: VAR? <IdentifierList> : <Type>"""
        is_ref = False
        start_idx = 0
        
        # Check for VAR keyword (pass by reference)
        if self._get_lexeme(node.children[0]).lower() == "var":
            is_ref = True
            start_idx = 1
        
        names = self.visit(node.children[start_idx])
        type_node = self.visit(node.children[start_idx + 2])
        
        return ParameterNode(names=names, type_node=type_node, is_ref=is_ref)

    # ==================== Statements ====================
    def _convert_CompoundStatement(self, node: Node) -> CompoundNode:
        """Handle: MULAI <StatementList> SELESAI"""
        if len(node.children) > 1:
            stmts = self.visit(node.children[1])
        else:
            stmts = []
        return CompoundNode(children=stmts)

    def _convert_StatementList(self, node: Node) -> List[ASTNode]:
        """Collect statements separated by semicolon"""
        stmts = []
        if not node.children or str(node.children[0].value) == "EPSILON":
            return stmts
        
        first = self.visit(node.children[0])
        if first and not isinstance(first, NoOpNode): 
            stmts.append(first)
        
        if len(node.children) > 1:
            self._collect_stmt_prime(node.children[1], stmts)
        return stmts

    def _collect_stmt_prime(self, node: Node, stmts: List[ASTNode]):
        """Recursively collect statements"""
        if not node.children or str(node.children[0].value) == "EPSILON":
            return
        s = self.visit(node.children[1]) 
        if s and not isinstance(s, NoOpNode): 
            stmts.append(s)
        if len(node.children) > 2:
            self._collect_stmt_prime(node.children[2], stmts)

    def _convert_Statement(self, node: Node):
        """Dispatch to specific statement handler"""
        if not node.children:
            return NoOpNode()
        child = node.children[0]
        if str(child.value) == "EPSILON":
            return NoOpNode()
        return self.visit(child)

    def _convert_AssignmentStatement(self, node: Node) -> AssignNode:
        """Handle: IDENTIFIER := <Expression>"""
        if isinstance(node.children[0].value, Token):
            target_name = node.children[0].value.lexeme
        else:
            target_name = self._get_lexeme(node.children[0])
        
        target = VarNode(name=target_name)
        
        # Find := and expression after it
        expr = None
        for i in range(len(node.children)):
            lex = self._get_lexeme(node.children[i])
            if lex == ":=":
                if i + 1 < len(node.children):
                    expr = self.visit(node.children[i + 1])
                break
        
        if expr is None:
            expr = NoOpNode()
        
        return AssignNode(target=target, value=expr)
    
    def _convert_Variable(self, node: Node) -> Union[VarNode, ArrayAccessNode, FieldAccessNode]:
        """Handle variable which could be: IDENTIFIER | IDENTIFIER[expr] | IDENTIFIER.field"""
        base_name = self._get_lexeme(node.children[0])
        base = VarNode(name=base_name)
        
        # Check for array access or field access
        if len(node.children) > 1:
            return self._handle_variable_suffix(base, node.children[1])
        
        return base

    def _handle_variable_suffix(self, base, suffix_node):
        """Handle array indexing or field access recursively"""
        if not suffix_node.children or str(suffix_node.children[0].value) == "EPSILON":
            return base
        
        first = suffix_node.children[0]
        
        # Array access: [ <Expression> ]
        if self._get_lexeme(first) == "[":
            index_expr = self.visit(suffix_node.children[1])
            base = ArrayAccessNode(array=base, index=index_expr)
            
            # Check for more suffixes
            if len(suffix_node.children) > 3:
                return self._handle_variable_suffix(base, suffix_node.children[3])
        
        # Field access: . IDENTIFIER
        elif self._get_lexeme(first) == ".":
            field_name = self._get_lexeme(suffix_node.children[1])
            base = FieldAccessNode(record=base, field_name=field_name)
            
            # Check for more suffixes
            if len(suffix_node.children) > 2:
                return self._handle_variable_suffix(base, suffix_node.children[2])
        
        return base
    
    def _convert_ProcedureCall(self, node: Node) -> ProcedureCallNode:
        """Handle: IDENTIFIER (<ParameterList>?)"""
        name = self._get_lexeme(node.children[0])
        params = []
        
        if len(node.children) >= 3:
            child_2 = node.children[2]
            child_2_val = str(child_2.value) if isinstance(child_2, Node) else ""
            if "RPAREN" not in child_2_val and child_2_val != ")":
                res = self.visit(child_2)
                if res:
                    params = res
        
        return ProcedureCallNode(proc_name=name, arguments=params)

    def _convert_ParameterList(self, node: Node) -> List[ASTNode]:
        """Collect procedure/function call parameters"""
        if not node.children or str(node.children[0].value) == "EPSILON":
            return []
        params = [self.visit(node.children[0])]
        if len(node.children) > 1:
            self._collect_params_prime(node.children[1], params)
        return params
    
    def _collect_params_prime(self, node: Node, params: List[ASTNode]):
        """Recursively collect parameters"""
        if not node.children or str(node.children[0].value) == "EPSILON":
            return
        params.append(self.visit(node.children[1])) 
        if len(node.children) > 2:
            self._collect_params_prime(node.children[2], params)
    
    def _convert_IfStatement(self, node: Node) -> IfNode:
        """Handle: IF <Expression> THEN <Statement> (ELSE <Statement>)?"""
        cond = self.visit(node.children[1])
        true_blk = self.visit(node.children[3])
        else_blk = None
        
        if len(node.children) > 5: 
            else_blk = self.visit(node.children[5])
        
        return IfNode(condition=cond, true_block=true_blk, else_block=else_blk)

    def _convert_WhileStatement(self, node: Node) -> WhileNode:
        """Handle: WHILE <Expression> DO <Statement>"""
        cond = self.visit(node.children[1])
        body = self.visit(node.children[3])
        return WhileNode(condition=cond, body=body)

    def _convert_RepeatStatement(self, node: Node) -> RepeatNode:
        """Handle: REPEAT <StatementList> UNTIL <Expression>"""
        body_stmts = self.visit(node.children[1])
        condition = self.visit(node.children[3])
        return RepeatNode(body=body_stmts, condition=condition)

    def _convert_ForStatement(self, node: Node) -> ForNode:
        """Handle: FOR IDENTIFIER := <Expression> (TO|DOWNTO) <Expression> DO <Statement>"""
        var = self._get_lexeme(node.children[1])
        start = self.visit(node.children[3])
        direct = self._get_lexeme(node.children[4])
        end = self.visit(node.children[5])
        body = self.visit(node.children[7])
        return ForNode(variable=var, start_expr=start, direction=direct, end_expr=end, body=body)

    def _convert_CaseStatement(self, node: Node) -> CaseNode:
        """Handle: CASE <Expression> OF <CaseList> END"""
        expr = self.visit(node.children[1])
        cases = []
        
        if len(node.children) > 3:
            cases = self.visit(node.children[3])
        
        return CaseNode(expr=expr, cases=cases)

    def _convert_CaseList(self, node: Node) -> List[CaseElementNode]:
        """Collect case elements"""
        cases = []
        self._collect_case_elements(node, cases)
        return cases

    def _collect_case_elements(self, node: Node, cases: List[CaseElementNode]):
        """Recursively collect case elements"""
        if not node.children or str(node.children[0].value) == "EPSILON":
            return
        
        case_elem = self.visit(node.children[0])
        if case_elem:
            cases.append(case_elem)
        
        if len(node.children) > 1:
            self._collect_case_elements(node.children[1], cases)

    def _convert_CaseElement(self, node: Node) -> CaseElementNode:
        """Handle: <Expression> : <Statement>"""
        value = self.visit(node.children[0])
        statement = self.visit(node.children[2])
        return CaseElementNode(value=value, statement=statement)

    # ==================== Expressions ====================
    def _convert_Expression(self, node: Node):
        """Handle expression with relational operators"""
        left = self.visit(node.children[0])
        if len(node.children) > 1:
            return self._visit_expr_prime(node.children[1], left)
        return left

    def _visit_expr_prime(self, node: Node, left):
        """Handle relational operators"""
        if not node.children or str(node.children[0].value) == "EPSILON":
            return left
            
        op = self._get_operator_lexeme(node.children[0])
        right = self.visit(node.children[1])
        return BinOpNode(op=op, left=left, right=right)

    def _convert_SimpleExpression(self, node: Node):
        """
        Tree Structure: <SimpleExpression> -> <SignedTerm> <SimpleExpressionPrime>
        """
        left = self.visit(node.children[0])

        if len(node.children) > 1:
            return self._visit_simple_prime(node.children[1], left)
            
        return left

    def _visit_simple_prime(self, node: Node, left):
        """Recursively handle + and - operators"""
        if not node.children or str(node.children[0].value) == "EPSILON":
            return left
        op = self._get_operator_lexeme(node.children[0]) 
        
        right = self.visit(node.children[1])
        
        new_left = BinOpNode(op=op, left=left, right=right)
        
        if len(node.children) > 2:
            return self._visit_simple_prime(node.children[2], new_left)
        
        return new_left

    def _convert_Term(self, node: Node):
        """Handle expression with *, /, div, mod, dan operators"""
        left = self.visit(node.children[0])
        if len(node.children) > 1:
            return self._visit_term_prime(node.children[1], left)
        return left

    def _visit_term_prime(self, node: Node, left):
        """Recursively handle * and / operators"""
        if not node.children or str(node.children[0].value) == "EPSILON":
            return left
            
        op = self._get_operator_lexeme(node.children[0])
        right = self.visit(node.children[1])
        
        new_left = BinOpNode(op=op, left=left, right=right)
        
        if len(node.children) > 2:
            return self._visit_term_prime(node.children[2], new_left)
            
        return new_left
    
    def _convert_SignedTerm(self, node: Node):
        """
        Handle: <SignedTerm> -> <SignOpt> <Term>
        """
        unary_op = None
        
        # 1. Cek SignOpt
        sign_node = node.children[0]
        sign_token = self._get_token(sign_node)
        
        if sign_token and sign_token.lexeme == "-":
            unary_op = "-"
            
        # 2. Ambil Term (Anak ke-1)
        term_val = self.visit(node.children[1])

        if unary_op:
            return UnaryOpNode(op=unary_op, expr=term_val)
            
        return term_val
    
    def _get_operator_lexeme(self, node: Node) -> str:
        """Helper aman untuk mengambil operator (+, -, *, dll)"""
        lex = self._get_lexeme(node)
        if lex: return lex

        if node.children:
            return self._get_lexeme(node.children[0])
        return "?"

    def _convert_Factor(self, node: Node):
        token = self._get_token(node)
        if not token:
            # Cek ( Expression )
            if len(node.children) > 1:
                 # Cek manual lexeme anak pertama untuk '('
                 first_lex = self._get_lexeme(node.children[0])
                 if first_lex == "(":
                     return self.visit(node.children[1])
            
            # Cek Variable
            if node.children and "Variable" in str(node.children[0].value):
                return self._convert_Variable(node.children[0])
                
            return NoOpNode()

        # 2. PROSES TOKEN (Angka, String, Var)
        lexeme = token.lexeme
        
        # Deteksi Angka (Handle int dan float)
        clean_lex = lexeme.replace('.', '', 1).replace('-', '', 1)
        if clean_lex.isdigit():
            val = float(lexeme) if '.' in lexeme else int(lexeme)
            return NumNode(value=val)
            
        # Deteksi String
        if (lexeme.startswith("'") and lexeme.endswith("'")) or \
           (lexeme.startswith('"') and lexeme.endswith('"')):
            return StringNode(value=lexeme[1:-1])
            
        # Deteksi Identifier / Variable sederhana
        if lexeme[0].isalpha() or lexeme.startswith('_'):
            return VarNode(name=lexeme)
            
        # Deteksi Operator Unary (NOT / tidak)
        if lexeme.lower() == "tidak" or lexeme.lower() == "not":
             if len(node.children) > 1:
                 return UnaryOpNode(op=lexeme, expr=self.visit(node.children[1]))
            
        return NoOpNode()