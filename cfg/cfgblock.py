from abc import ABCMeta, abstractmethod


class CFGBLock(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def optimize(self):
        pass

    @abstractmethod
    def set_next(self, next_block):
        pass

    @abstractmethod
    def print(self):
        pass


class Statement(CFGBLock):
    def __init__(self, id, statement):
        CFGBLock.__init__(self)
        self.id = id
        self.statement = statement

    def __repr__(self):
        return "[Statement {}] {}".format(self.id, self.statement)

    def optimize(self):
        n = self.next
        while isinstance(n, Empty):
            n = n.next
        self.next = n

    def set_next(self, next_block):
        self.next = next_block

    def print(self):
        print("{} -> {}".format(self, self.next))


class Branch(CFGBLock):
    def __init__(self, id, var, true_block, false_block):
        CFGBLock.__init__(self)
        self.id = id
        self.var = var
        self.true_block = true_block
        self.false_block = false_block

    def __repr__(self):
        return "[Branch {}] {}".format(self.id, self.var)

    def optimize(self):
        n = self.true_block
        while isinstance(n, Empty):
            n = n.next
        self.true_block = n

        n = self.false_block
        while isinstance(n, Empty):
            n = n.next
        self.false_block = n

    def set_next(self, next_block):
        raise RuntimeError()

    def print(self):
        print("{} (true)-> {}".format(self, self.true_block))
        print("{} (false)-> {}".format(self, self.false_block))


class Entry(CFGBLock):
    def __repr__(self):
        return "[Entry]"

    def optimize(self):
        n = self.next
        while isinstance(n, Empty):
            n = n.next
        self.next = n

    def set_next(self, next_block):
        self.next = next_block

    def print(self):
        print("{} -> {}".format(self, self.next))


class Exit(CFGBLock):
    def __repr__(self):
        return "[Exit]"

    def optimize(self):
        pass

    def set_next(self, next_block):
        raise RuntimeError()

    def print(self):
        pass


class Empty(CFGBLock):
    def __init__(self, id):
        CFGBLock.__init__(self)
        self.id = id

    def __repr__(self):
        return "[Empty {}]".format(self.id)

    def optimize(self):
        pass

    def set_next(self, next_block):
        self.next = next_block

    def print(self):
        print("{} -> {}".format(self, self.next))


class Switch(CFGBLock):
    def __init__(self, id, var, blocks):
        CFGBLock.__init__(self)
        self.id = id
        self.var = var
        self.blocks = blocks

    def __repr__(self):
        return "[Switch {}] {}".format(self.id, self.var)

    def optimize(self):
        for index, (_, n) in enumerate(self.blocks):
            while isinstance(n, Empty):
                n = n.next
            self.blocks[index] = n

    def set_next(self, next_block):
        raise RuntimeError()

    def print(self):
        for cond, body in self.blocks:
            print("{} ({})-> {}".format(self, cond, body))
