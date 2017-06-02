
from abc import ABCMeta

from ir.irexpression import IRPhi


class IRStatement(metaclass=ABCMeta):
    pass


class IRInput(IRStatement):
    def __init__(self, target):
        self.target = target

    def __repr__(self):
        return "input {}".format(self.target)


class IRArg(IRStatement):
    def __init__(self, cfg, target):
        self.target = target

    def __repr__(self):
        return "arg {}".format(self.target)


class IRUndef(IRStatement):
    def __repr__(self):
        return "Undef"


class IRAssignment(IRStatement):
    def __init__(self, target, exp):
        self.target = target
        self.exp = exp
        if isinstance(exp, IRPhi):
            exp.users.append(self)

    def __repr__(self):
        return "{} = {}".format(self.target, self.exp)

    def replace(self, phi, same):
        if isinstance(same, IRPhi):
            same.users.append(self)
        if self.exp == phi:
            self.exp = same


class IRArrayAssignment(IRStatement):
    def __init__(self, arr, index, exp):
        self.arr = arr
        self.index = index
        self.exp = exp
        if isinstance(index, IRPhi):
            index.users.append(self)
        if isinstance(exp, IRPhi):
            exp.users.append(self)

    def __repr__(self):
        return "{}[{}] = {}".format(self.arr, self.index, self.exp)

    def replace(self, phi, same):
        if isinstance(same, IRPhi):
            same.users.append(self)
        if self.index == phi:
            self.index = same
        if self.exp == phi:
            self.exp = same


class IRPointAssignment(IRStatement):
    def __init__(self, target, exp):
        self.target = target
        self.exp = exp
        if isinstance(exp, IRPhi):
            exp.users.append(self)

    def __repr__(self):
        return "*{} = {}".format(self.target, self.exp)

    def replace(self, phi, same):
        if isinstance(same, IRPhi):
            same.users.append(self)
        if self.exp == phi:
            self.exp = same


class IRStructRefAssignment(IRStatement):
    def __init__(self, receiver, field, exp):
        self.receiver = receiver
        self.field = field
        self.exp = exp
        if isinstance(exp, IRPhi):
            exp.users.append(self)

    def __repr__(self):
        return "{}.{} = {}".format(self.receiver, self.field, self.exp)

    def replace(self, phi, same):
        if isinstance(same, IRPhi):
            same.users.append(self)
        if self.field == phi:
            self.field = same
        if self.exp == phi:
            self.exp = same


class IRFuncCall(IRStatement):
    def __init__(self, cfg, name, args):
        self.target = cfg.create_temp_var()
        self.name = name
        self.args = args
        for arg in args:
            if isinstance(arg, IRPhi):
                arg.users.append(self)

    def __repr__(self):
        return "{} = {}({})".format(self.target, self.name, self.args)

    def replace(self, phi, same):
        if isinstance(same, IRPhi):
            same.users.append(self)
        for i, arg in enumerate(self.args):
            if arg == phi:
                self.args[i] = same


class IRFieldAccess(IRStatement):
    def __init__(self, cfg, receiver, field):
        self.target = cfg.create_temp_var()
        self.receiver = receiver
        self.field = field
        if isinstance(receiver, IRPhi):
            receiver.users.append(self)

    def __repr__(self):
        return "{} = {}.{}".format(self.target, self.receiver, self.field)

    def replace(self, phi, same):
        if isinstance(same, IRPhi):
            same.users.append(self)
        if self.receiver == phi:
            self.receiver = same


class IRAddr(IRStatement):
    def __init__(self, cfg, ope):
        self.target = cfg.create_temp_var()
        self.ope = ope
        if isinstance(ope, IRPhi):
            ope.users.append(self)

    def __repr__(self):
        return "{} = &{}".format(self.target, self.ope)

    def replace(self, phi, same):
        if isinstance(same, IRPhi):
            same.users.append(self)
        if self.ope == phi:
            self.ope = same


class IRPoint(IRStatement):
    def __init__(self, cfg, ope):
        self.target = cfg.create_temp_var()
        self.ope = ope
        if isinstance(ope, IRPhi):
            ope.users.append(self)

    def __repr__(self):
        return "{} = *{}".format(self.target, self.ope)

    def replace(self, phi, same):
        if isinstance(same, IRPhi):
            same.users.append(self)
        if self.ope == phi:
            self.ope = same


class IRReturn(IRStatement):
    def __init__(self, cfg, exp):
        self.exp = exp
        if isinstance(exp, IRPhi):
            exp.users.append(self)

    def __repr__(self):
        return "return {}".format(self.exp)

    def replace(self, phi, same):
        if isinstance(same, IRPhi):
            same.users.append(self)
        if self.exp == phi:
            self.exp = same


class IRBinaryOp(IRStatement):
    def __init__(self, cfg, op, left, right):
        self.target = cfg.create_temp_var()
        self.op = op
        self.left = left
        self.right = right
        if isinstance(left, IRPhi):
            left.users.append(self)
        if isinstance(right, IRPhi):
            right.users.append(self)

    def __repr__(self):
        return "{} = {} {} {}".format(self.target, self.left, self.op, self.right)


    def replace(self, phi, same):
        if isinstance(same, IRPhi):
            same.users.append(self)
        if self.left == phi:
            self.left = same
        if self.right == phi:
            self.right = same


class IRUnaryOp(IRStatement):
    def __init__(self, cfg, op, ope):
        self.target = cfg.create_temp_var()
        self.op = op
        self.ope = ope
        if isinstance(ope, IRPhi):
            ope.users.append(self)

    def __repr__(self):
        return "{} = {}{}".format(self.target, self.op, self.ope)

    def replace(self, phi, same):
        if isinstance(same, IRPhi):
            same.users.append(self)
        if self.ope == phi:
            self.ope = same


class IRArrayRef(IRStatement):
    def __init__(self, cfg, arr, index):
        self.target = cfg.create_temp_var()
        self.arr = arr
        self.index = index
        if isinstance(arr, IRPhi):
            arr.users.append(self)
        if isinstance(index, IRPhi):
            index.users.append(self)

    def replace(self, phi, same):
        if isinstance(same, IRPhi):
            same.users.append(self)
        if self.arr == phi:
            self.arr = same
        if self.index == phi:
            self.index = same

    def __repr__(self):
        return "{} = {}[{}]".format(self.target, self.arr, self.index)