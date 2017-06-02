from pycparser import c_ast
from pycparser.c_ast import *
from cfg.cfg import CFG
from ir.irstatement import *
from ir.irexpression import IRConstant


def transform_assignment(node: Assignment):
    if node.op == "=":
        return node
    elif node.op in ["+=", "-=", "*=", "/=", "%=", "^=", "|=", "&=", ">>=", "<<="]:
        return Assignment("=", node.lvalue, BinaryOp(node.op[:-1], node.lvalue, node.rvalue, node.coord), node.coord)
    else:
        print(node.op)
        raise NotImplementedError()


def transform_decl(node: Decl):
    if not node.init is None:
        return Assignment("=", ID(node.name, node.coord), node.init, node.coord)
    return node


def transform_unary_op(node: UnaryOp):
    if node.op == "p++":
        return Assignment("=", node.expr, BinaryOp("+", node.expr, Constant(int, 1)), node.coord)
    elif node.op == "p--":
        return Assignment("=", node.expr, BinaryOp("-", node.expr, Constant(int, 1)), node.coord)
    elif node.op == "++":
        return Assignment("=", node.expr, BinaryOp("+", node.expr, Constant(int, 1)), node.coord)
    elif node.op == "--":
        return Assignment("=", node.expr, BinaryOp("-", node.expr, Constant(int, 1)), node.coord)
    else:
        raise RuntimeError()


class ASTVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.graphs = []
        self.cfg = None  # type: CFG

    def visit_ArrayDecl(self, node):
        raise NotImplementedError()

    def visit_ArrayRef(self, node):
        arr = self.visit(node.name)
        index = self.visit(node.subscript)
        s = IRArrayRef(self.cfg, arr, index)
        self.cfg.current_block.add_statement(s)
        return s.target

    def visit_Assignment(self, node):
        if self.cfg.current_block is None:
            return

        node = transform_assignment(node)

        if isinstance(node.lvalue, ID):  # x = ...
            r = self.visit(node.rvalue)
            temp = self.cfg.create_temp_var()
            self.cfg.write_var(node.lvalue.name, self.cfg.current_block, temp)
            self.cfg.current_block.add_statement(IRAssignment(temp, r))
        elif isinstance(node.lvalue, ArrayRef):  # x[i] = ...
            r = self.visit(node.rvalue)
            subscript = self.visit(node.lvalue.subscript)
            temp = self.cfg.create_temp_var()
            self.cfg.write_var(node.lvalue.name.name, self.cfg.current_block, temp)
            self.cfg.current_block.add_statement(IRArrayAssignment(temp, subscript, r))
        elif isinstance(node.lvalue, StructRef):  # x.f = ...
            rec = self.visit(node.lvalue.name)
            if node.lvalue.type == "->":
                point = IRPoint(self.cfg, rec)
                self.cfg.current_block.add_statement(point)
                rec = point.target
            r = self.visit(node.rvalue)
            self.cfg.current_block.add_statement(IRStructRefAssignment(rec, node.lvalue.field, r))
        elif isinstance(node.lvalue, UnaryOp):  # *... = ...
            l = self.visit(node.lvalue.expr)
            r = self.visit(node.rvalue)
            self.cfg.current_block.add_statement(IRPointAssignment(l, r))
        else:
            node.show()
            raise NotImplementedError()

    def visit_BinaryOp(self, node):
        l = self.visit(node.left)
        r = self.visit(node.right)
        s = IRBinaryOp(self.cfg, node.op, l, r)
        self.cfg.current_block.add_statement(s)
        return s.target

    def visit_Break(self, node):
        if self.cfg.current_block is None:
            return

        self.cfg.seal_block(self.cfg.current_block)
        self.cfg.current_block.set_next(self.break_blocks[-1])
        self.cfg.current_block = None

    def visit_Case(self, node):
        raise NotImplementedError()

    def visit_Cast(self, node):
        self.visit(node.expr)

    def visit_Compound(self, node):
        if node.block_items is not None:
            for item in node.block_items:
                self.visit(item)

    def visit_CompoundLiteral(self, node):
        raise NotImplementedError()

    def visit_Constant(self, node):
        return IRConstant(node.type, node.value)

    def visit_Countinue(self, node):
        raise NotImplementedError()

    def visit_Decl(self, node):
        if self.cfg is None:
            return

        if not node.init is None:
            node = transform_decl(node)
            return self.visit(node)

    def visit_Declist(self, node):
        raise NotImplementedError()

    def visit_Default(self, node):
        raise NotImplementedError()

    def visit_DoWhile(self, node):
        cond_block = self.cfg.create_basic_block()
        true_block = self.cfg.create_basic_block()
        body_block = self.cfg.create_basic_block()
        false_block = self.cfg.create_basic_block()
        self.cfg.seal_block(self.cfg.current_block)
        self.cfg.add_block(true_block)
        self.cfg.add_block(body_block)
        self.break_blocks.append(false_block)
        self.continue_blocks.append(cond_block)
        self.visit(node.stmt)
        self.break_blocks.pop()
        self.continue_blocks.pop()
        if self.cfg.current_block is not None:
            self.cfg.current_block.set_next(cond_block)
        self.cfg.current_block = cond_block
        cond_exp = self.visit(node.cond)
        self.cfg.seal_block(cond_block)
        branch = self.cfg.create_branch_block(cond_exp, true_block, false_block)
        self.cfg.seal_block(branch)
        self.cfg.add_block(branch)
        self.cfg.seal_block(true_block)
        self.cfg.current_block = false_block

    def visit_EllipsisParam(self, node):
        raise NotImplementedError()

    def visit_EmptyStatement(self, node):
        pass

    def visit_Enum(self, node):
        raise NotImplementedError()

    def visit_Enumerator(self, node):
        raise NotImplementedError()

    def visit_EnumeratorList(self, node):
        raise NotImplementedError()

    def visit_ExprList(self, node):
        return [self.visit(c) for c in node.exprs]

    def visit_FileAST(self, node):
        self.generic_visit(node)
        return self.graphs

    def visit_For(self, node):
        if self.cfg.current_block is None:
            return

        if node.init is not None:
            self.visit(node.init)
        self.cfg.seal_block(self.cfg.current_block)
        entry_block = self.cfg.create_basic_block()
        self.cfg.add_block(entry_block)
        cond_block = self.cfg.create_basic_block()
        self.cfg.add_block(cond_block)
        cond_exp = None
        if node.cond is not None:
            cond_exp = self.visit(node.cond)

        true_block = self.cfg.create_basic_block()
        false_block = self.cfg.create_basic_block()
        update_block = self.cfg.create_basic_block()
        branch = self.cfg.create_branch_block(cond_exp, true_block, false_block)
        self.cfg.seal_block(branch)
        self.cfg.current_block.set_next(branch)
        self.cfg.current_block = true_block
        self.break_blocks.append(false_block)
        self.continue_blocks.append(update_block)
        self.visit(node.stmt)

        if self.cfg.current_block is not None:
            self.cfg.seal_block(self.cfg.current_block)
            self.cfg.current_block.set_next(update_block)

        self.cfg.current_block = update_block
        if node.next is not None:
            self.visit(node.next)
        self.break_blocks.pop()
        self.continue_blocks.pop()
        self.cfg.seal_block(update_block)
        self.cfg.current_block.set_next(cond_block)
        self.cfg.seal_block(entry_block)
        self.cfg.current_block = false_block

    def visit_FuncCall(self, node):
        if self.cfg.current_block is None:
            return

        if isinstance(node.name, ID) and node.name.name == "scanf":
            return self.visit_Scanf(node)

        args = []
        if node.args is not None:
            args = self.visit(node.args)
        if isinstance(node.name, ID):
            s = IRFuncCall(self.cfg, node.name.name, args)
        elif isinstance(node.name, UnaryOp):
            e = self.visit(node.name)
            s = IRFuncCall(self.cfg, e, args)
        elif isinstance(node.name, StructRef):
            e = self.visit(node.name)
            s = IRFuncCall(self.cfg, e, args)
        else:
            node.show()
            raise NotImplementedError()
        self.cfg.current_block.add_statement(s)
        return s.target

    def visit_FuncDecl(self, node):
        raise NotImplementedError()

    def visit_FuncDef(self, node):
        self.cfg = CFG()
        self.break_blocks = []
        self.continue_blocks = []

        # print("{} Started.".format(node.decl.name))
        args = node.decl.type.args
        if args is not None:
            for arg in args.params:
                temp = self.cfg.create_temp_var()
                self.cfg.write_var(arg.name, self.cfg.current_block, temp)
                self.cfg.current_block.add_statement(IRArg(self.cfg, temp))

        self.generic_visit(node)

        if self.cfg.current_block is not None:
            self.cfg.seal_block(self.cfg.current_block)
            self.cfg.current_block.set_next(self.cfg.exit)

        self.cfg.post_traverse()
        self.graphs.append((node.decl.name, self.cfg))
        self.cfg = None

        # print("{} Ended.".format(node.decl.name))



        # self.returns = []
        # self.jump = []
        # for r in self.returns:
        #     r.set_next(self.current_cfg.exit)
        # for s, t in self.jump:
        #     s.set_next(t)

    def visit_Goto(self, node):
        if self.cfg.current_block is None:
            return

        self.cfg.gotos.append((self.cfg.current_block, node.name))
        self.cfg.current_block = None

    def visit_ID(self, node):
        return self.cfg.read_var(node.name, self.cfg.current_block)

    def visit_IdentifierType(self, node):
        raise NotImplementedError()

    def visit_If(self, node):
        cond_exp = self.visit(node.cond)
        true_block = self.cfg.create_basic_block()
        false_block = self.cfg.create_basic_block()
        end_block = self.cfg.create_basic_block()
        branch = self.cfg.create_branch_block(cond_exp, true_block, false_block)
        self.cfg.seal_block(self.cfg.current_block)
        self.cfg.seal_block(branch)
        self.cfg.current_block.set_next(branch)
        self.cfg.current_block = true_block
        if node.iftrue is not None:
            self.visit(node.iftrue)
        if self.cfg.current_block is not None:
            self.cfg.seal_block(self.cfg.current_block)
            self.cfg.current_block.set_next(end_block)
        self.cfg.current_block = false_block
        if node.iffalse is not None:
            self.visit(node.iffalse)
        if self.cfg.current_block is not None:
            self.cfg.seal_block(self.cfg.current_block)
            self.cfg.current_block.set_next(end_block)
        self.cfg.current_block = end_block

    def visit_InitList(self, node):
        pass  # todo

    def visit_Label(self, node):
        block = self.cfg.create_basic_block()
        if self.cfg.current_block is not None:
            self.cfg.current_block.set_next(block)
        self.cfg.current_block = block
        self.cfg.labels[node.name] = block
        self.visit(node.stmt)

    def visit_NamedInitializer(self, node):
        raise NotImplementedError()

    def visit_ParamList(self, node):
        raise NotImplementedError()

    def visit_PtrDecl(self, node):
        raise NotImplementedError()

    def visit_Return(self, node):
        if self.cfg.current_block is None:
            return

        e = None
        if node.expr is not None:
            e = self.visit(node.expr)
        s = IRReturn(self.cfg, e)
        self.cfg.current_block.add_statement(s)
        self.cfg.current_block.set_next(self.cfg.exit)
        self.cfg.seal_block(self.cfg.current_block)
        self.cfg.current_block = None

    def visit_Struct(self, node):
        raise NotImplementedError()

    def visit_StructRef(self, node):
        rec = self.visit(node.name)
        if node.type == '->':
            point = IRPoint(self.cfg, rec)
            self.cfg.current_block.add_statement(point)
            rec = point.target
        s = IRFieldAccess(self.cfg, rec, node.field.name)
        self.cfg.current_block.add_statement(s)
        return s.target

    def visit_Switch(self, node):
        cond_exp = self.visit(node.cond)
        assert isinstance(node.stmt, Compound)
        switch = self.cfg.create_switch_block(cond_exp)
        self.cfg.seal_block(self.cfg.current_block)
        self.cfg.seal_block(switch)
        self.cfg.current_block.set_next(switch)
        end_block = self.cfg.create_basic_block()
        self.break_blocks.append(end_block)
        last_block = None
        for stmt in node.stmt.block_items:
            body = self.cfg.create_basic_block()
            if isinstance(stmt, Case):
                switch.blocks.append((stmt.expr, body))
            elif isinstance(stmt, Default):
                switch.blocks.append((None, body))
            else:
                raise RuntimeError()
            if last_block is not None:
                self.cfg.seal_block(last_block)
                last_block.set_next(body)

            self.cfg.current_block = body
            for body_stmt in stmt.stmts:
                self.visit(body_stmt)
            last_block = self.cfg.current_block
        self.break_blocks.pop()
        if last_block is not None:
            self.cfg.seal_block(last_block)
            last_block.set_next(end_block)
        self.cfg.current_block = end_block

    def visit_TernaryOp(self, node):
        cond = self.visit(node.cond)
        iftrue = self.visit(node.iftrue)
        iffalse = self.visit(node.iffalse)
        temp = self.cfg.create_temp_var()
        true_block = self.cfg.create_basic_block()
        true_block.add_statement(IRAssignment(temp, iftrue))
        false_block = self.cfg.create_basic_block()
        false_block.add_statement(IRAssignment(temp, iffalse))
        end_block = self.cfg.create_basic_block()
        branch = self.cfg.create_branch_block(cond, true_block, false_block)
        self.cfg.seal_block(self.cfg.current_block)
        self.cfg.add_block(branch)
        self.cfg.seal_block(branch)
        self.cfg.seal_block(true_block)
        self.cfg.seal_block(false_block)
        true_block.set_next(end_block)
        false_block.set_next(end_block)
        self.cfg.current_block = end_block
        return temp

    def visit_TypeDecl(self, node):
        raise NotImplementedError()

    def visit_Typedef(self, node):
        pass

    def visit_Typename(self, node):
        pass

    def visit_UnaryOp(self, node):
        if node.op in ['+', '-', '!', '~', 'sizeof']:
            e = self.visit(node.expr)
            s = IRUnaryOp(self.cfg, node.op, e)
        elif node.op == '&':
            e = self.visit(node.expr)
            s = IRAddr(self.cfg, e)
        elif node.op == '*':
            e = self.visit(node.expr)
            s = IRPoint(self.cfg, e)
        elif node.op in ['p++', 'p--', '++', '--']:
            return self.visit(transform_unary_op(node))
        else:
            print(node.op)
            raise NotImplementedError()

    def visit_Union(self, node):
        raise NotImplementedError()

    def visit_While(self, node):
        self.cfg.seal_block(self.cfg.current_block)
        cond_block = self.cfg.create_basic_block()
        self.cfg.add_block(cond_block)
        cond_exp = self.visit(node.cond)

        true_block = self.cfg.create_basic_block()
        false_block = self.cfg.create_basic_block()
        branch = self.cfg.create_branch_block(cond_exp, true_block, false_block)
        self.cfg.seal_block(branch)
        self.cfg.current_block.set_next(branch)
        self.cfg.current_block = true_block
        self.break_blocks.append(false_block)
        self.continue_blocks.append(cond_block)
        self.visit(node.stmt)
        self.break_blocks.pop()
        self.continue_blocks.pop()
        if self.cfg.current_block is not None:
            self.cfg.seal_block(self.cfg.current_block)
            self.cfg.current_block.set_next(cond_block)
        self.cfg.seal_block(cond_block)
        self.cfg.current_block = false_block

    def visit_Pragma(self, node):
        raise NotImplementedError()

    def visit_Scanf(self, node):
        for arg in node.args.exprs[1:]:
            temp = self.cfg.create_temp_var()
            self.cfg.write_var(self.extract_var(arg), self.cfg.current_block, temp)
            self.cfg.current_block.add_statement(IRInput(temp))

    def extract_var(self, node):
        if isinstance(node, ID):
            return node.name
        elif isinstance(node, UnaryOp):
            return self.extract_var(node.expr)
        elif isinstance(node, StructRef):
            return self.extract_var(node.name)
        elif isinstance(node, ArrayRef):
            return self.extract_var(node.name)
        elif isinstance(node, BinaryOp):  # a + i
            if node.op in ["+", "-"]:
                return self.extract_var(node.left)
            else:
                raise RuntimeError()
        else:
            node.show()
            raise RuntimeError()
