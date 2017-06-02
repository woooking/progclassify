
from abc import ABCMeta
from cfg.cfgblock import CFGBlock

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


class IRPhi(IRExpression):
    def __init__(self, id, block: CFGBlock):
        IRExpression.__init__(self)
        self.block = block
        self.operands = []
        self.users = []
        self.id = id

        self.replaced = False

    def replace(self, phi, same):
        if isinstance(same, IRPhi):
            same.users.append(self)
        for i, ope in enumerate(self.operands):
            if ope == phi:
                self.operands[i] = same

    def add_operand(self, ope):
        self.operands.append(ope)
        if isinstance(ope, IRPhi) and ope != self:
            ope.users.append(self)

    def __repr__(self):
        return "[Phi {}] {}".format(self.id, self.operands)