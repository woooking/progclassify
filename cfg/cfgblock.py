from abc import ABCMeta, abstractmethod

class CFGBlock(metaclass=ABCMeta):
    def __init__(self):
        self.preds = []

    @abstractmethod
    def set_next(self, next_block):
        pass

    @abstractmethod
    def print(self):
        pass


class Statements(CFGBlock):
    def __init__(self, id):
        CFGBlock.__init__(self)
        self.id = id
        self.statements = []

    def __repr__(self):
        return "[Statements {}]".format(self.id)

    def add_statement(self, statement):
        self.statements.append(statement)

    def set_next(self, next_block):
        self.next = next_block
        next_block.preds.append(self)

    def print(self):
        for s in self.statements:
            print(s)
        print("{} -> {}".format(self, self.next))


class Branch(CFGBlock):
    def __init__(self, id, var, true_block, false_block):
        CFGBlock.__init__(self)
        self.id = id
        self.var = var
        self.true_block = true_block
        self.false_block = false_block
        true_block.preds.append(self)
        false_block.preds.append(self)

    def __repr__(self):
        return "[Branch {}] {}".format(self.id, self.var)

    def set_next(self, next_block):
        raise RuntimeError()

    def print(self):
        print("{} (true)-> {}".format(self, self.true_block))
        print("{} (false)-> {}".format(self, self.false_block))


class Entry(CFGBlock):
    def __repr__(self):
        return "[Entry]"

    def set_next(self, next_block):
        self.next = next_block
        next_block.preds.append(self)

    def print(self):
        print("{} -> {}".format(self, self.next))


class Exit(CFGBlock):
    def __repr__(self):
        return "[Exit]"

    def set_next(self, next_block):
        raise RuntimeError()

    def print(self):
        pass


class Switch(CFGBlock):
    def __init__(self, id, var):
        CFGBlock.__init__(self)
        self.id = id
        self.var = var
        self.blocks = []

    def __repr__(self):
        return "[Switch {}] {}".format(self.id, self.var)

    def set_next(self, next_block):
        raise RuntimeError()

    def print(self):
        for cond, body in self.blocks:
            print("{} ({})-> {}".format(self, cond, body))



