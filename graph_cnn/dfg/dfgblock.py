from abc import ABCMeta


class DFGBlock(metaclass=ABCMeta):
    def __init__(self, id):
        self.id = id
        self.nexts = []


class DataBlock(DFGBlock):
    def __init__(self, dfg):
        DFGBlock.__init__(self, dfg.get_next_num())


class DFGInput(DataBlock):
    def __init__(self, dfg):
        DataBlock.__init__(self, dfg)

    def __repr__(self):
        return "[Input {}]".format(self.id)


class DFGArg(DataBlock):
    def __init__(self, dfg):
        DataBlock.__init__(self, dfg)

    def __repr__(self):
        return "[Arg {}]".format(self.id)


class DFGConst(DataBlock):
    def __init__(self, dfg, value, type):
        DataBlock.__init__(self, dfg)
        self.value = value
        self.type = type

    def __repr__(self):
        return "[Const({}) {}]".format(self.value, self.id)


class DFGUndef(DataBlock):
    def __init__(self, dfg):
        DataBlock.__init__(self, dfg)

    def __repr__(self):
        return "[Undef {}]".format(self.id)


class OperationBlock(DFGBlock):
    def __init__(self, dfg):
        DFGBlock.__init__(self, dfg.get_next_num())


class DFGPhi(OperationBlock):
    def __init__(self, dfg):
        OperationBlock.__init__(self, dfg)

    def __repr__(self):
        return "[Phi {}]".format(self.id)


class DFGAssignment(OperationBlock):
    def __init__(self, dfg):
        OperationBlock.__init__(self, dfg)

    def __repr__(self):
        return "[Assignment {}]".format(self.id)


class DFGArrayAssignment(OperationBlock):
    def __init__(self, dfg):
        OperationBlock.__init__(self, dfg)

    def __repr__(self):
        return ""


class DFGPointAssignment(OperationBlock):
    def __init__(self, dfg):
        OperationBlock.__init__(self, dfg)

    def __repr__(self):
        return "[PointAssignment {}]".format(self.id)


class DFGStructRefAssignment(OperationBlock):
    def __init__(self, dfg):
        OperationBlock.__init__(self, dfg)

    def __repr__(self):
        return "[StructRefAssignment {}]".format(self.id)


class DFGFuncCall(OperationBlock):
    def __init__(self, dfg, name):
        OperationBlock.__init__(self, dfg)
        self.name = name

    def __repr__(self):
        return "[FuncCall::{} {}]".format(self.name, self.id)


class DFGFieldAccess(OperationBlock):
    def __init__(self, dfg, field):
        OperationBlock.__init__(self, dfg)
        self.field = field

    def __repr__(self):
        return "[FieldAccess::{} {}]".format(self.field, self.id)


class DFGAddr(OperationBlock):
    def __init__(self, dfg):
        OperationBlock.__init__(self, dfg)

    def __repr__(self):
        return "[Addr {}]".format(self.id)


class DFGPoint(OperationBlock):
    def __init__(self, dfg):
        OperationBlock.__init__(self, dfg)

    def __repr__(self):
        return "[Point {}]".format(self.id)


class DFGReturn(OperationBlock):
    def __init__(self, dfg):
        OperationBlock.__init__(self, dfg)

    def __repr__(self):
        return "[Return {}]".format(self.id)


class DFGBinaryOp(OperationBlock):
    def __init__(self, dfg, op):
        OperationBlock.__init__(self, dfg)
        self.op = op

    def __repr__(self):
        return "[BinaryOp({}) {}]".format(self.op, self.id)


class DFGTernaryOp(OperationBlock):
    def __init__(self, dfg):
        OperationBlock.__init__(self, dfg)

    def __repr__(self):
        return "[TernaryOp {}]".format(self.id)


class DFGUnaryOp(OperationBlock):
    def __init__(self, dfg, op):
        OperationBlock.__init__(self, dfg)
        self.op = op

    def __repr__(self):
        return "[UnaryOp({}) {}]".format(self.op, self.id)


class DFGArrayRef(OperationBlock):
    def __init__(self, dfg):
        OperationBlock.__init__(self, dfg)

    def __repr__(self):
        return "[ArrayRef {}]".format(self.id)


class DFGCondition(OperationBlock):
    def __init__(self, dfg):
        OperationBlock.__init__(self, dfg)

    def __repr__(self):
        return "[Condition {}]".format(self.id)
