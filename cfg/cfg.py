
from ir.irexpression import IRTemp
from cfg.cfgblock import Entry, Exit, Branch, Empty, Switch, Statement

class CFG:
    def __init__(self):
        self.num = 0
        self.temp = 0
        self.entry = Entry()
        self.blocks = []
        self.exit = Exit()

    def create_temp_var(self):
        num = self.temp
        self.temp += 1
        return IRTemp(num)

    def create_empty_block(self):
        block = Empty(self.num)
        self.num += 1
        self.blocks.append(block)
        return block

    def create_branch_block(self, var, true_block, false_block):
        block = Branch(self.num, var, true_block, false_block)
        self.num += 1
        self.blocks.append(block)
        return block

    def create_switch_block(self, var):
        block = Switch(self.num, var, [])
        self.num += 1
        self.blocks.append(block)
        return block

    def create_statement_block(self, statement):
        block = Statement(self.num, statement)
        self.num += 1
        self.blocks.append(block)
        return block

    def optimize(self):
        for block in self.blocks:
            block.optimize()
        self.blocks = list(filter(lambda b: not isinstance(b, Empty),self.blocks))

    def print(self):
        for block in self.blocks:
            block.print()