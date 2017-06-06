
from abc import ABCMeta

class IRExpression(metaclass=ABCMeta):
    def __init__(self):
        pass


class IRConstant(IRExpression):
    def __init__(self, type, value):
        IRExpression.__init__(self)
        self.type = type
        self.value = value

    def __repr__(self):
        return "{}".format(self.value)


class IRTemp(IRExpression):
    def __init__(self, num):
        IRExpression.__init__(self)
        self.id = num

    def __repr__(self):
        return "#{}".format(self.id)


class IRPhiVar(IRExpression):
    def __init__(self, num):
        IRExpression.__init__(self)
        self.id = num

    def __repr__(self):
        return "${}".format(self.id)


class IRUndef(IRExpression):
    def __repr__(self):
        return "Undef"


class IRExpPhi(IRExpression):
    def __init__(self, id, block):
        IRExpression.__init__(self)
        self.block = block
        self.operands = []
        self.users = []
        self.id = id

        self.replaced = False

    def replace(self, phi, same):
        if isinstance(same, IRExpPhi):
            same.users.append(self)
        for i, ope in enumerate(self.operands):
            if ope == phi:
                self.operands[i] = same

    def add_operand(self, ope):
        self.operands.append(ope)
        if isinstance(ope, IRExpPhi) and ope != self:
            ope.users.append(self)

    def __repr__(self):
        return "[Phi {}] {}".format(self.id, self.operands)