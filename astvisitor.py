from pycparser import c_ast
from pycparser.c_ast import *
from cfg.cfg import CFG
from ir.irstatement import *
from ir.irexpression import IRConstant, IRVar


class ASTVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.graphs = []
        self.current_cfg = None # type: CFG

    def visit_ArrayDecl(self, node):
        raise NotImplementedError()

    def visit_ArrayRef(self, node):
        arr = self.visit(node.name)
        index = self.visit(node.subscript)
        s = IRArrayRef(self.current_cfg, arr, index)
        self.add_statement(s)
        return s.target

    def visit_Assignment(self, node):
        if isinstance(node.lvalue, ID):
            pass
        elif isinstance(node.lvalue, ArrayRef):
            pass
        elif isinstance(node.lvalue, StructRef):
            pass
        elif isinstance(node.lvalue, UnaryOp):
            pass
        else:
            node.show()
            raise NotImplementedError()
        l = self.visit(node.lvalue)
        r = self.visit(node.rvalue)
        if node.op == "=":
            s = IRAssignment(self.current_cfg, l, r)
        elif node.op in ["+=", "-=", "*=", "/=", "%=", "^=", "|=", "&=", ">>=", "<<="]:
            exp = IRBinaryOp(self.current_cfg, node.op[0:-2], l, r)
            self.add_statement(exp)
            s = IRAssignment(self.current_cfg, l, exp.target)
        else:
            print(node.op)
            raise NotImplementedError()
        self.add_statement(s)
        return s.target

    def visit_BinaryOp(self, node):
        l = self.visit(node.left)
        r = self.visit(node.right)
        s = IRBinaryOp(self.current_cfg, node.op, l, r)
        self.add_statement(s)
        return s.target

    def visit_Break(self, node):
        self.jump.append((self.current_block, self.break_blocks[-1]))

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
        if self.current_cfg is None:
            return
        if not node.init is None:
            init = self.visit(node.init)
            s = IRAssignment(self.current_cfg, IRVar(node.name), init)
            self.add_statement(s)
            return s.target

    def visit_Declist(self, node):
        raise NotImplementedError()

    def visit_Default(self, node):
        raise NotImplementedError()

    def visit_DoWhile(self, node):
        cond_block = self.current_cfg.create_empty_block()
        true_block = self.current_cfg.create_empty_block()
        false_block = self.current_cfg.create_empty_block()
        self.add_block(true_block)
        self.break_blocks.append(false_block)
        self.continue_blocks.append(cond_block)
        self.visit(node.stmt)
        self.break_blocks.pop()
        self.continue_blocks.pop()
        self.add_block(cond_block)
        cond_exp = self.visit(node.cond)
        branch = self.current_cfg.create_branch_block(cond_exp, true_block, false_block)
        self.add_block(branch)
        self.current_block = false_block

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
        if node.init is not None:
            self.visit(node.init)
        cond_block = self.current_cfg.create_empty_block()
        self.add_block(cond_block)
        cond_exp = None
        if node.cond is not None:
            cond_exp = self.visit(node.cond)
        true_block = self.current_cfg.create_empty_block()
        false_block = self.current_cfg.create_empty_block()
        update_block = self.current_cfg.create_empty_block()
        branch = self.current_cfg.create_branch_block(cond_exp, true_block, false_block)
        self.current_block.set_next(branch)
        self.current_block = true_block
        self.break_blocks.append(false_block)
        self.continue_blocks.append(update_block)
        self.visit(node.stmt)
        self.add_block(update_block)
        if node.next is not None:
            self.visit(node.next)
        self.break_blocks.pop()
        self.continue_blocks.pop()
        self.current_block.set_next(cond_block)
        self.current_block = false_block

    def visit_FuncCall(self, node):
        args = None
        if node.args is not None:
            args = self.visit(node.args)
        if isinstance(node.name, ID):
            s = IRFuncCall(self.current_cfg, node.name.name, args)
        elif isinstance(node.name, UnaryOp):
            e = self.visit(node.name)
            s = IRFuncCall(self.current_cfg, e, args)
        elif isinstance(node.name, StructRef):
            e = self.visit(node.name)
            s = IRFuncCall(self.current_cfg, e, args)
        else:
            node.show()
            raise NotImplementedError()
        next_block = self.current_cfg.create_statement_block(s)
        self.current_block.set_next(next_block)
        self.current_block = next_block
        return s.target

    def visit_FuncDecl(self, node):
        raise NotImplementedError()

    def visit_FuncDef(self, node):
        self.current_cfg = CFG()
        self.returns = []
        self.break_blocks = []
        self.continue_blocks = []
        self.jump = []
        self.gotos = []
        self.labels = {}
        self.graphs.append((node.decl.name, self.current_cfg))
        self.current_block = self.current_cfg.entry
        self.generic_visit(node)
        self.current_block.set_next(self.current_cfg.exit)
        for r in self.returns:
            r.set_next(self.current_cfg.exit)
        self.current_cfg = None
        for s, t in self.jump:
            s.set_next(t)
        for s, t in self.gotos:
            s.set_next(self.labels[t])

    def visit_Goto(self, node):
        self.gotos.append((self.current_block, node.name))

    def visit_ID(self, node):
        return IRVar(node.name)

    def visit_IdentifierType(self, node):
        raise NotImplementedError()

    def visit_If(self, node):
        cond_exp = self.visit(node.cond)
        true_block = self.current_cfg.create_empty_block()
        false_block = self.current_cfg.create_empty_block()
        end_block = self.current_cfg.create_empty_block()
        branch = self.current_cfg.create_branch_block(cond_exp, true_block, false_block)
        self.current_block.set_next(branch)
        self.current_block = true_block
        if node.iftrue is not None:
            self.visit(node.iftrue)
        self.current_block.set_next(end_block)
        self.current_block = false_block
        if node.iffalse is not None:
            self.visit(node.iffalse)
        self.current_block.set_next(end_block)
        self.current_block = end_block

    def visit_InitList(self, node):
        pass  # todo

    def visit_Label(self, node):
        block = self.current_cfg.create_empty_block()
        self.add_block(block)
        self.labels[node.name] = block
        self.visit(node.stmt)

    def visit_NamedInitializer(self, node):
        raise NotImplementedError()

    def visit_ParamList(self, node):
        raise NotImplementedError()

    def visit_PtrDecl(self, node):
        raise NotImplementedError()

    def visit_Return(self, node):
        e = None
        if node.expr is not None:
            e = self.visit(node.expr)
        s = IRReturn(self.current_cfg, e)
        self.add_statement(s)
        self.returns.append(self.current_block)
        return s.target

    def visit_Struct(self, node):
        raise NotImplementedError()

    def visit_StructRef(self, node):
        rec = self.visit(node.name)
        if node.type == '->':
            point = IRPoint(self.current_cfg, rec)
            self.add_statement(point)
            rec = point.target
        s = IRFieldAccess(self.current_cfg, rec, node.field.name)
        self.add_statement(s)
        return s.target

    def visit_Switch(self, node):
        # node.show()
        cond = self.visit(node.cond)
        assert isinstance(node.stmt, Compound)
        s = self.current_cfg.create_switch_block(cond)
        self.add_block(s)
        end_block = self.current_cfg.create_empty_block()
        self.break_blocks.append(end_block)
        for stmt in node.stmt.block_items:
            body = self.current_cfg.create_empty_block()
            if isinstance(stmt, Case):
                s.blocks.append((stmt.expr, body))
            elif isinstance(stmt, Default):
                s.blocks.append((None, body))
            else:
                raise RuntimeError()
            self.current_block = body
            for body_stmt in stmt.stmts:
                self.visit(body_stmt)
            self.add_block(end_block)
        self.break_blocks.pop()

    def visit_TernaryOp(self, node):
        cond = self.visit(node.cond)
        iftrue = self.visit(node.iftrue)
        iffalse = self.visit(node.iffalse)
        temp = self.current_cfg.create_temp_var()
        true_block = self.current_cfg.create_statement_block(IRAssignment(self.current_cfg, temp, iftrue))
        false_block = self.current_cfg.create_statement_block(IRAssignment(self.current_cfg, temp, iffalse))
        end_block = self.current_cfg.create_empty_block()
        branch = self.current_cfg.create_branch_block(cond, true_block, false_block)
        self.add_block(branch)
        true_block.set_next(end_block)
        false_block.set_next(end_block)
        self.current_block = end_block
        return temp

    def visit_TypeDecl(self, node):
        raise NotImplementedError()

    def visit_Typedef(self, node):
        pass

    def visit_Typename(self, node):
        pass

    def visit_UnaryOp(self, node):
        e = self.visit(node.expr)
        if node.op in ['+', '-', '!', '~', 'sizeof']:
            s = IRUnaryOp(self.current_cfg, node.op, e)
        elif node.op == '&':
            s = IRAddr(self.current_cfg, e)
        elif node.op == '*':
            s = IRPoint(self.current_cfg, e)
        elif node.op == 'p++':
            temp = self.current_cfg.create_temp_var()
            self.add_statement(IRAssignment(self.current_cfg, temp, e))
            op = IRBinaryOp(self.current_cfg, '+', e, IRConstant(int, 1))
            self.add_statement(op)
            self.add_statement(IRAssignment(self.current_cfg, e, op.target))
            return temp
        elif node.op == 'p--':
            temp = self.current_cfg.create_temp_var()
            self.add_statement(IRAssignment(self.current_cfg, temp, e))
            minus = IRBinaryOp(self.current_cfg, '-', e, IRConstant(int, 1))
            self.add_statement(minus)
            self.add_statement(IRAssignment(self.current_cfg, e, minus.target))
            return temp
        elif node.op == '++':
            op = IRBinaryOp(self.current_cfg, '+', e, IRConstant(int, 1))
            self.add_statement(op)
            self.add_statement(IRAssignment(self.current_cfg, e, op.target))
            return e
        elif node.op == '--':
            op = IRBinaryOp(self.current_cfg, '-', e, IRConstant(int, 1))
            self.add_statement(op)
            self.add_statement(IRAssignment(self.current_cfg, e, op.target))
            return e
        else:
            print(node.op)
            raise NotImplementedError()

        self.add_statement(s)
        return s.target

    def visit_Union(self, node):
        raise NotImplementedError()

    def visit_While(self, node):
        cond_block = self.current_cfg.create_empty_block()
        self.add_block(cond_block)
        cond_exp = self.visit(node.cond)
        true_block = self.current_cfg.create_empty_block()
        false_block = self.current_cfg.create_empty_block()
        branch = self.current_cfg.create_branch_block(cond_exp, true_block, false_block)
        self.current_block.set_next(branch)
        self.current_block = true_block
        self.break_blocks.append(false_block)
        self.continue_blocks.append(cond_block)
        self.visit(node.stmt)
        self.break_blocks.pop()
        self.continue_blocks.pop()
        self.current_block.set_next(cond_block)
        self.current_block = false_block

    def visit_Pragma(self, node):
        raise NotImplementedError()

    def add_statement(self, s):
        next_block = self.current_cfg.create_statement_block(s)
        self.add_block(next_block)

    def add_block(self, block):
        self.current_block.set_next(block)
        self.current_block = block
