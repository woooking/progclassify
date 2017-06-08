from pycparser.c_ast import *
from wordembedding_rnn.word import KeyWord, Word, ConstantValue, Op


class ASTVisitor(NodeVisitor):
    def __init__(self):
        self.pre_order = []
        self.in_funcdef = False

    def visit_ArrayDecl(self, node):
        node.show()
        raise NotImplementedError()

    def visit_ArrayRef(self, node):
        node.show()
        raise NotImplementedError()

    def visit_Assignment(self, node):
        self.pre_order.append(Op(node.op))
        self.generic_visit(node)

    def visit_BinaryOp(self, node):
        self.pre_order.append(Op(node.op))
        self.generic_visit(node)

    def visit_Break(self, node):
        node.show()
        raise NotImplementedError()

    def visit_Case(self, node):
        node.show()
        raise NotImplementedError()

    def visit_Cast(self, node):
        node.show()
        raise NotImplementedError()

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
        if not self.in_funcdef and isinstance(node.type, FuncDecl):
            return

        # todo: ?

        if node.quals:
            node.show()
            raise NotImplementedError()
        if node.storage:
            node.show()
            raise NotImplementedError()
        if node.funcspec:
            node.show()
            raise NotImplementedError()
        self.generic_visit(node)

    def visit_Declist(self, node):
        node.show()
        raise NotImplementedError()

    def visit_Default(self, node):
        node.show()
        raise NotImplementedError()

    def visit_DoWhile(self, node):
        node.show()
        raise NotImplementedError()

    def visit_EllipsisParam(self, node):
        node.show()
        raise NotImplementedError()

    def visit_EmptyStatement(self, node):
        node.show()
        raise NotImplementedError()

    def visit_Enum(self, node):
        node.show()
        raise NotImplementedError()

    def visit_Enumerator(self, node):
        node.show()
        raise NotImplementedError()

    def visit_EnumeratorList(self, node):
        node.show()
        raise NotImplementedError()

    def visit_ExprList(self, node):
        self.generic_visit(node)

    def visit_FileAST(self, node):
        self.pre_order.append(KeyWord.FILE_START)
        self.generic_visit(node)
        self.pre_order.append(KeyWord.FILE_END)

    def visit_For(self, node):
        self.pre_order.append(KeyWord.FOR_INIT)
        self.visit(node.init)
        self.pre_order.append(KeyWord.FOR_COND)
        self.visit(node.cond)
        self.pre_order.append(KeyWord.FOR_UPDATE)
        self.visit(node.next)
        self.pre_order.append(KeyWord.FOR_STMT)
        self.visit(node.stmt)
        self.pre_order.append(KeyWord.FOR_END)

    def visit_FuncCall(self, node):
        self.pre_order.append(KeyWord.FUNC_CALL)
        self.generic_visit(node)

    def visit_FuncDecl(self, node):
        self.generic_visit(node)

    def visit_FuncDef(self, node):
        self.pre_order.append(KeyWord.FUNC_START)
        assert not self.in_funcdef
        self.in_funcdef = True
        self.generic_visit(node)
        assert self.in_funcdef
        self.in_funcdef = False
        self.pre_order.append(KeyWord.FUNC_END)

    def visit_Goto(self, node):
        node.show()
        raise NotImplementedError()

    def visit_ID(self, node):
        self.pre_order.append(Word(node.name))

    def visit_IdentifierType(self, node):
        for name in node.names:
            self.pre_order.append(Word(name))
        if len(node.names) != 1:
            node.show(showcoord=True)
            raise RuntimeError()

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
        node.show()
        raise NotImplementedError()

    def visit_Label(self, node):
        node.show()
        raise NotImplementedError()

    def visit_NamedInitializer(self, node):
        node.show()
        raise NotImplementedError()

    def visit_ParamList(self, node):
        self.generic_visit(node)

    def visit_PtrDecl(self, node):
        node.show()
        raise NotImplementedError()

    def visit_Return(self, node):
        self.pre_order.append(KeyWord.RETURN)
        self.generic_visit(node)

    def visit_Struct(self, node):
        node.show()
        raise NotImplementedError()

    def visit_StructRef(self, node):
        node.show()
        raise NotImplementedError()

    def visit_Switch(self, node):
        node.show()
        raise NotImplementedError()

    def visit_TernaryOp(self, node):
        node.show()
        raise NotImplementedError()

    def visit_TypeDecl(self, node):
        self.visit(node.type)
        self.pre_order.append(Word(node.declname))
        if node.quals:
            node.show()
            raise NotImplementedError()

    def visit_Typedef(self, node):
        node.show()
        raise NotImplementedError()

    def visit_Typename(self, node):
        node.show()
        raise NotImplementedError()

    def visit_UnaryOp(self, node):
        self.pre_order.append(Op(node.op))
        self.generic_visit(node)

    def visit_Union(self, node):
        node.show()
        raise NotImplementedError()

    def visit_While(self, node):
        node.show()
        raise NotImplementedError()

    def visit_Pragma(self, node):
        node.show()
        raise NotImplementedError()
