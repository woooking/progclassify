from abc import ABCMeta, abstractmethod

from graph_cnn.ir.irexpression import IRExpPhi


class IRStatement(metaclass=ABCMeta):
    @abstractmethod
    def def_var(self):
        pass

    @abstractmethod
    def use_var(self):
        pass


class IRPhi(IRStatement):
    def __init__(self, target, args):
        self.target = target
        self.args = args

    def __repr__(self):
        return "{} = phi({})".format(self.target, self.args)

    def def_var(self):
        return self.target

    def use_var(self):
        return self.args


class IRInput(IRStatement):
    def __init__(self, target):
        self.target = target

    def __repr__(self):
        return "input {}".format(self.target)

    def def_var(self):
        return self.target

    def use_var(self):
        return []


class IRArg(IRStatement):
    def __init__(self, cfg, target):
        self.target = target

    def __repr__(self):
        return "arg {}".format(self.target)

    def def_var(self):
        return self.target

    def use_var(self):
        return []


class IRAssignment(IRStatement):
    def __init__(self, target, exp):
        self.target = target
        self.exp = exp
        if isinstance(exp, IRExpPhi):
            exp.users.append(self)

    def __repr__(self):
        return "{} = {}".format(self.target, self.exp)

    def replace(self, phi, same):
        if isinstance(same, IRExpPhi):
            same.users.append(self)
        if self.exp == phi:
            self.exp = same

    def def_var(self):
        return self.target

    def use_var(self):
        return [self.exp]


class IRArrayAssignment(IRStatement):
    def __init__(self, arr, index, exp):
        self.arr = arr
        self.index = index
        self.exp = exp
        if isinstance(index, IRExpPhi):
            index.users.append(self)
        if isinstance(exp, IRExpPhi):
            exp.users.append(self)

    def __repr__(self):
        return "{}[{}] = {}".format(self.arr, self.index, self.exp)

    def replace(self, phi, same):
        if isinstance(same, IRExpPhi):
            same.users.append(self)
        if self.index == phi:
            self.index = same
        if self.exp == phi:
            self.exp = same

    def def_var(self):
        return self.arr

    def use_var(self):
        return [self.index, self.exp]


class IRPointAssignment(IRStatement):
    def __init__(self, target, exp):
        self.target = target
        self.exp = exp
        if isinstance(exp, IRExpPhi):
            exp.users.append(self)

    def __repr__(self):
        return "*{} = {}".format(self.target, self.exp)

    def replace(self, phi, same):
        if isinstance(same, IRExpPhi):
            same.users.append(self)
        if self.exp == phi:
            self.exp = same

    def def_var(self):
        return self.target

    def use_var(self):
        return [self.exp]


class IRStructRefAssignment(IRStatement):
    def __init__(self, receiver, field, exp):
        self.receiver = receiver
        self.field = field
        self.exp = exp
        if isinstance(receiver, IRExpPhi):
            receiver.users.append(self)
        if isinstance(exp, IRExpPhi):
            exp.users.append(self)

    def __repr__(self):
        return "{}.{} = {}".format(self.receiver, self.field, self.exp)

    def replace(self, phi, same):
        if isinstance(same, IRExpPhi):
            same.users.append(self)
        if self.receiver == phi:
            self.receiver = same
        if self.exp == phi:
            self.exp = same

    def def_var(self):
        return None

    def use_var(self):
        return [self.receiver, self.exp]


class IRFuncCall(IRStatement):
    def __init__(self, cfg, name, args):
        self.target = cfg.create_temp_var()
        self.name = name
        self.args = args
        for arg in args:
            if isinstance(arg, IRExpPhi):
                arg.users.append(self)

    def __repr__(self):
        return "{} = {}({})".format(self.target, self.name, self.args)

    def replace(self, phi, same):
        if isinstance(same, IRExpPhi):
            same.users.append(self)
        for i, arg in enumerate(self.args):
            if arg == phi:
                self.args[i] = same

    def def_var(self):
        return self.target

    def use_var(self):
        return self.args


class IRFieldAccess(IRStatement):
    def __init__(self, cfg, receiver, field):
        self.target = cfg.create_temp_var()
        self.receiver = receiver
        self.field = field
        if isinstance(receiver, IRExpPhi):
            receiver.users.append(self)

    def __repr__(self):
        return "{} = {}.{}".format(self.target, self.receiver, self.field)

    def replace(self, phi, same):
        if isinstance(same, IRExpPhi):
            same.users.append(self)
        if self.receiver == phi:
            self.receiver = same

    def def_var(self):
        return self.target

    def use_var(self):
        return [self.receiver]


class IRAddr(IRStatement):
    def __init__(self, cfg, ope):
        self.target = cfg.create_temp_var()
        self.ope = ope
        if isinstance(ope, IRExpPhi):
            ope.users.append(self)

    def __repr__(self):
        return "{} = &{}".format(self.target, self.ope)

    def replace(self, phi, same):
        if isinstance(same, IRExpPhi):
            same.users.append(self)
        if self.ope == phi:
            self.ope = same

    def def_var(self):
        return self.target

    def use_var(self):
        return [self.ope]


class IRPoint(IRStatement):
    def __init__(self, cfg, ope):
        self.target = cfg.create_temp_var()
        self.ope = ope
        if isinstance(ope, IRExpPhi):
            ope.users.append(self)

    def __repr__(self):
        return "{} = *{}".format(self.target, self.ope)

    def replace(self, phi, same):
        if isinstance(same, IRExpPhi):
            same.users.append(self)
        if self.ope == phi:
            self.ope = same

    def def_var(self):
        return self.target

    def use_var(self):
        return [self.ope]


class IRReturn(IRStatement):
    def __init__(self, cfg, exp):
        self.exp = exp
        if isinstance(exp, IRExpPhi):
            exp.users.append(self)

    def __repr__(self):
        return "return {}".format(self.exp)

    def replace(self, phi, same):
        if isinstance(same, IRExpPhi):
            same.users.append(self)
        if self.exp == phi:
            self.exp = same

    def def_var(self):
        return None

    def use_var(self):
        return [self.exp]


class IRBinaryOp(IRStatement):
    def __init__(self, cfg, op, left, right):
        self.target = cfg.create_temp_var()
        self.op = op
        self.left = left
        self.right = right
        if isinstance(left, IRExpPhi):
            left.users.append(self)
        if isinstance(right, IRExpPhi):
            right.users.append(self)

    def __repr__(self):
        return "{} = {} {} {}".format(self.target, self.left, self.op, self.right)


    def replace(self, phi, same):
        if isinstance(same, IRExpPhi):
            same.users.append(self)
        if self.left == phi:
            self.left = same
        if self.right == phi:
            self.right = same

    def def_var(self):
        return self.target

    def use_var(self):
        return [self.left, self.right]


class IRTernaryOp(IRStatement):
    def __init__(self, cfg, cond, iftrue, iffalse):
        self.target = cfg.create_temp_var()
        self.cond = cond
        self.iftrue = iftrue
        self.iffalse = iffalse
        if isinstance(cond, IRExpPhi):
            cond.users.append(self)
        if isinstance(iftrue, IRExpPhi):
            iftrue.users.append(self)
        if isinstance(iffalse, IRExpPhi):
            iffalse.users.append(self)

    def __repr__(self):
        return "{} = {} ? {} : {}".format(self.target, self.cond, self.iftrue, self.iffalse)

    def replace(self, phi, same):
        if isinstance(same, IRExpPhi):
            same.users.append(self)
        if self.cond == phi:
            self.cond = same
        if self.iftrue == phi:
            self.iftrue = same
        if self.iffalse == phi:
            self.iffalse = same

    def def_var(self):
        return self.target

    def use_var(self):
        return [self.cond, self.iftrue, self.iffalse]


class IRUnaryOp(IRStatement):
    def __init__(self, cfg, op, ope):
        self.target = cfg.create_temp_var()
        self.op = op
        self.ope = ope
        if isinstance(ope, IRExpPhi):
            ope.users.append(self)

    def __repr__(self):
        return "{} = {}{}".format(self.target, self.op, self.ope)

    def replace(self, phi, same):
        if isinstance(same, IRExpPhi):
            same.users.append(self)
        if self.ope == phi:
            self.ope = same

    def def_var(self):
        return self.target

    def use_var(self):
        return [self.ope]


class IRArrayRef(IRStatement):
    def __init__(self, cfg, arr, index):
        self.target = cfg.create_temp_var()
        self.arr = arr
        self.index = index
        if isinstance(arr, IRExpPhi):
            arr.users.append(self)
        if isinstance(index, IRExpPhi):
            index.users.append(self)

    def __repr__(self):
        return "{} = {}[{}]".format(self.target, self.arr, self.index)

    def replace(self, phi, same):
        if isinstance(same, IRExpPhi):
            same.users.append(self)
        if self.arr == phi:
            self.arr = same
        if self.index == phi:
            self.index = same

    def def_var(self):
        return self.target

    def use_var(self):
        return [self.arr, self.index]

