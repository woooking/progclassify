
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


class IRVar(IRExpression):
    def __init__(self, name):
        IRExpression.__init__(self)
        self.name = name

    def __repr__(self):
        return "{}".format(self.name)

