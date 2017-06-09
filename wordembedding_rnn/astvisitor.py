from pycparser.c_ast import *
from wordembedding_rnn.word import KeyWord, Word, ConstantValue, Op


class ASTVisitor(NodeVisitor):
    def __init__(self):
        self.pre_order = []

    def visit_ArrayDecl(self, node):
        if node.dim_quals:
            node.show()
            raise RuntimeError()

        self.visit(node.type)
        self.pre_order.append(KeyWord.ARRAY_DIM)
        if node.dim:
            self.visit(node.dim)

    def visit_ArrayRef(self, node):
        self.pre_order.append(KeyWord.ARRAY_REF)
        self.visit(node.name)
        self.pre_order.append(KeyWord.ARRAY_INDEX)
        self.visit(node.subscript)

    def visit_Assignment(self, node):
        self.pre_order.append(Op(node.op))
        self.generic_visit(node)

    def visit_BinaryOp(self, node):
        self.pre_order.append(Op(node.op))
        self.generic_visit(node)

    def visit_Break(self, node):
        self.pre_order.append(KeyWord.BREAK)

    def visit_Case(self, node):
        self.pre_order.append(KeyWord.SWITCH_CASE)
        self.visit(node.expr)
        self.pre_order.append(KeyWord.SWITCH_CASE_STMT)
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_Cast(self, node):
        self.pre_order.append(KeyWord.CAST)
        self.visit(node.to_type)
        self.visit(node.expr)

    def visit_Compound(self, node):
        self.generic_visit(node)

    def visit_CompoundLiteral(self, node):
        node.show()
        raise NotImplementedError()

    def visit_Constant(self, node):
        self.pre_order.append(ConstantValue(node.value))

    def visit_Countinue(self, node):
        node.show()
        raise NotImplementedError()

    def visit_Decl(self, node):
        # todo: const? / extern? / inline?
        if node.bitsize:
            node.show()
            raise NotImplementedError()

        if isinstance(node.type, FuncDecl):
            pass
        elif isinstance(node.type, TypeDecl):
            self.pre_order.append(KeyWord.VARIABLE_DECL)
            self.visit(node.type)
            if node.init:
                self.pre_order.append(KeyWord.VARIABLE_INIT)
                self.visit(node.init)
        elif isinstance(node.type, PtrDecl):
            self.pre_order.append(KeyWord.PTR_DECL)
            self.visit(node.type)
            if node.init:
                self.pre_order.append(KeyWord.PTR_INIT)
                self.visit(node.init)
        elif isinstance(node.type, ArrayDecl):
            self.pre_order.append(KeyWord.ARRAY_DECL)
            self.generic_visit(node)
        elif isinstance(node.type, Struct):
            self.pre_order.append(KeyWord.STRUCT_DECL)
            self.generic_visit(node)
        elif isinstance(node.type, Enum):
            self.visit(node.type)
        else:
            node.show()
            raise RuntimeError()

    def visit_Declist(self, node):
        node.show()
        raise NotImplementedError()

    def visit_Default(self, node):
        self.pre_order.append(KeyWord.SWITCH_DEFAULT)
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_DoWhile(self, node):
        self.pre_order.append(KeyWord.DO_START)
        self.pre_order.append(KeyWord.DO_STMT)
        self.visit(node.stmt)
        self.pre_order.append(KeyWord.DO_COND)
        self.visit(node.cond)
        self.pre_order.append(KeyWord.DO_END)

    def visit_EllipsisParam(self, node):
        node.show()
        raise NotImplementedError()

    def visit_EmptyStatement(self, node):
        pass

    def visit_Enum(self, node):
        self.pre_order.append(KeyWord.ENUM_DECL)
        if node.name:
            self.pre_order.append(KeyWord.ENUM_NAME)
            self.pre_order.append(Word(node.name))
        self.visit(node.values)

    def visit_Enumerator(self, node):
        self.pre_order.append(KeyWord.ENUM_MEMBER)
        self.pre_order.append(Word(node.name))
        self.pre_order.append(KeyWord.ENUM_VALUE)
        self.visit(node.value)

    def visit_EnumeratorList(self, node):
        self.generic_visit(node)

    def visit_ExprList(self, node):
        self.generic_visit(node)

    def visit_FileAST(self, node):
        self.pre_order.append(KeyWord.FILE_START)
        self.generic_visit(node)
        self.pre_order.append(KeyWord.FILE_END)

    def visit_For(self, node):
        self.pre_order.append(KeyWord.FOR_START)

        if node.init:
            self.pre_order.append(KeyWord.FOR_INIT)
            self.visit(node.init)

        if node.cond:
            self.pre_order.append(KeyWord.FOR_COND)
            self.visit(node.cond)

        if node.next:
            self.pre_order.append(KeyWord.FOR_UPDATE)
            self.visit(node.next)
        self.pre_order.append(KeyWord.FOR_STMT)
        self.visit(node.stmt)
        self.pre_order.append(KeyWord.FOR_END)

    def visit_FuncCall(self, node):
        self.pre_order.append(KeyWord.FUNC_CALL)
        self.visit(node.name)
        if node.args:
            for arg in node.args.exprs:
                self.pre_order.append(KeyWord.FUNC_ARG)
                self.visit(arg)
        self.pre_order.append(KeyWord.FUNC_CALL_END)

    def visit_FuncDecl(self, node):
        pass

    def visit_FuncDef(self, node):
        self.pre_order.append(KeyWord.FUNC_START)
        self.visit(node.decl.type.type)

        if node.decl.type.args:
            for arg in node.decl.type.args.params:
                self.pre_order.append(KeyWord.FUNC_PARAM)
                self.visit(arg)
        if node.decl.init:
            node.show()
            raise RuntimeError()
        if node.param_decls:
            node.show()
            raise RuntimeError()
        self.pre_order.append(KeyWord.FUNC_BODY)
        self.visit(node.body)
        self.pre_order.append(KeyWord.FUNC_END)

    def visit_Goto(self, node):
        self.pre_order.append(KeyWord.GOTO)
        self.pre_order.append(Word(node.name))

    def visit_ID(self, node):
        self.pre_order.append(Word(node.name))

    def visit_IdentifierType(self, node):
        for name in node.names:
            self.pre_order.append(Word(name))

    def visit_If(self, node):
        self.pre_order.append(KeyWord.IF_COND)
        self.visit(node.cond)
        self.pre_order.append(KeyWord.IF_TRUE)
        self.visit(node.iftrue)
        self.pre_order.append(KeyWord.IF_FALSE)
        if node.iffalse:
            self.visit(node.iffalse)
        self.pre_order.append(KeyWord.IF_END)

    def visit_InitList(self, node):
        self.pre_order.append(KeyWord.INIT_LIST)
        for expr in node.exprs:
            self.pre_order.append(KeyWord.INIT_ITEM)
            self.visit(expr)

    def visit_Label(self, node):
        self.pre_order.append(KeyWord.LABEL)
        self.pre_order.append(Word(node.name))
        self.visit(node.stmt)

    def visit_NamedInitializer(self, node):
        node.show()
        raise NotImplementedError()

    def visit_ParamList(self, node):
        self.generic_visit(node)

    def visit_PtrDecl(self, node):
        if node.quals:
            node.show()
            raise NotImplementedError()
        self.pre_order.append(KeyWord.PTR_DECL)
        self.visit(node.type)

    def visit_Return(self, node):
        self.pre_order.append(KeyWord.RETURN)
        self.generic_visit(node)

    def visit_Struct(self, node):
        self.generic_visit(node)

    def visit_StructRef(self, node):
        if node.type == ".":
            self.pre_order.append(KeyWord.STRUCT_REF)
        else:
            self.pre_order.append(KeyWord.STRUCT_POINT_REF)
        self.visit(node.name)
        self.pre_order.append(KeyWord.STRUCT_FIELD)
        self.visit(node.field)

    def visit_Switch(self, node):
        self.pre_order.append(KeyWord.SWITCH_START)
        self.visit(node.cond)
        self.visit(node.stmt)
        self.pre_order.append(KeyWord.SWITCH_END)

    def visit_TernaryOp(self, node):
        self.pre_order.append(KeyWord.TERNARY_COND)
        self.visit(node.cond)
        self.pre_order.append(KeyWord.TERNARY_TRUE)
        self.visit(node.iftrue)
        self.pre_order.append(KeyWord.TERNARY_FALSE)
        self.visit(node.iffalse)
        self.pre_order.append(KeyWord.TERNARY_END)

    def visit_TypeDecl(self, node):
        # todo: const?
        self.pre_order.append(Word(node.declname))
        self.pre_order.append(KeyWord.TYPE)
        self.visit(node.type)

    def visit_Typedef(self, node):
        self.pre_order.append(KeyWord.TYPEDEF)
        self.pre_order.append(Word(node.name))
        self.visit(node.type)

    def visit_Typename(self, node):
        if node.name:
            node.show()
            raise NotImplementedError()
        self.visit(node.type)

    def visit_UnaryOp(self, node):
        self.pre_order.append(Op(node.op))
        self.generic_visit(node)

    def visit_Union(self, node):
        node.show()
        raise NotImplementedError()

    def visit_While(self, node):
        self.pre_order.append(KeyWord.WHILE_START)
        if node.cond:
            self.pre_order.append(KeyWord.WHILE_COND)
            self.visit(node.cond)
        self.pre_order.append(KeyWord.WHILE_STMT)
        self.visit(node.stmt)
        self.pre_order.append(KeyWord.WHILE_END)

    def visit_Pragma(self, node):
        node.show()
        raise NotImplementedError()
