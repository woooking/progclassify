
from abc import ABCMeta


class IRStatement(metaclass=ABCMeta):
    def __init__(self, cfg, target=None):
        self.target = cfg.create_temp_var() if target is None else target


class IRAssignment(IRStatement):
    def __init__(self, cfg, target, exp):
        IRStatement.__init__(self, cfg, target)
        self.exp = exp

    def __repr__(self):
        return "{} = {}".format(self.target, self.exp)


class IRFuncCall(IRStatement):
    def __init__(self, cfg, name, args):
        IRStatement.__init__(self, cfg)
        self.name = name
        self.args = args

    def __repr__(self):
        return "{} = {}({})".format(self.target, self.name, self.args)


class IRFieldAccess(IRStatement):
    def __init__(self, cfg, receiver, field):
        IRStatement.__init__(self, cfg)
        self.receiver = receiver
        self.field = field

    def __repr__(self):
        return "{} = {}.{}".format(self.target, self.receiver, self.field)


class IRAddr(IRStatement):
    def __init__(self, cfg, ope):
        IRStatement.__init__(self, cfg)
        self.ope = ope

    def __repr__(self):
        return "{} = &{}".format(self.target, self.ope)


class IRPoint(IRStatement):
    def __init__(self, cfg, ope):
        IRStatement.__init__(self, cfg)
        self.ope = ope

    def __repr__(self):
        return "{} = *{}".format(self.target, self.ope)


class IRReturn(IRStatement):
    def __init__(self, cfg, exp):
        IRStatement.__init__(self, cfg)
        self.exp = exp

    def __repr__(self):
        return "return {}".format(self.exp)


class IRBinaryOp(IRStatement):
    def __init__(self, cfg, op, left, right):
        IRStatement.__init__(self, cfg)
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return "{} = {} {} {}".format(self.target, self.left, self.op, self.right)


class IRUnaryOp(IRStatement):
    def __init__(self, cfg, op, ope):
        IRStatement.__init__(self, cfg)
        self.op = op
        self.ope = ope

    def __repr__(self):
        return "{} = {}{}".format(self.target, self.op, self.ope)


class IRArrayRef(IRStatement):
    def __init__(self, cfg, arr, index):
        IRStatement.__init__(self, cfg)
        self.arr = arr
        self.index = index

    def __repr__(self):
        return "{} = {}[{}]".format(self.target, self.arr, self.index)