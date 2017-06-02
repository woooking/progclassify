from ir.irexpression import IRTemp, IRPhi
from ir.irstatement import IRUndef
from cfg.cfgblock import *


class CFG:
    def __init__(self):
        self.num = 0
        self.temp = 0
        self.phi = 0
        self.entry = Entry()
        self.exit = Exit()
        self.phis = []
        self.blocks = [self.entry, self.exit]
        self.sealed_blocks = [self.entry]
        self.incomplete_phis = {self.entry: {}, self.exit: {}}
        block = self.create_basic_block()
        self.current_block = block
        self.entry.set_next(block)
        self.cur_def = {}
        self.traverse_end = False
        self.gotos = []
        self.labels = {}

    def post_traverse(self):
        self.traverse_end = True
        for s, t in self.gotos:
            s.set_next(self.labels[t])
        for block in self.labels.values():
            self.seal_block(block)

    def replace(self, phi, same):
        if phi.replaced:
            return
        phi.replaced = True
        self.phis.remove(phi)
        for var in self.cur_def:
            for block in self.cur_def[var]:
                if self.cur_def[var][block] == phi:
                    self.cur_def[var][block] = same
        for block in self.incomplete_phis:
            for var in self.incomplete_phis[block]:
                if self.incomplete_phis[block][var] == phi:
                    self.incomplete_phis[block][var] = same

    def write_var(self, var: str, block: CFGBlock, value):
        if var in self.cur_def:
            self.cur_def[var][block] = value
        else:
            self.cur_def[var] = {block: value}

    def read_var(self, var: str, block: CFGBlock):
        if var in self.cur_def:
            if block in self.cur_def[var]:
                return self.cur_def[var][block]
        return self.read_var_rec(var, block)

    def read_var_rec(self, var: str, block: CFGBlock):
        if not block in self.sealed_blocks:
            val = self.create_phi(block)
            self.incomplete_phis[block][var] = val
        elif len(block.preds) == 1:
            val = self.read_var(var, block.preds[0])
        else:
            val = self.create_phi(block)
            self.write_var(var, block, val)
            val = self.add_phi_operands(var, val)
        self.write_var(var, block, val)
        return val

    def add_phi_operands(self, var, phi):
        for pred in phi.block.preds:
            phi.add_operand(self.read_var(var, pred))
        return self.try_remove(phi)

    def try_remove(self, phi):
        same = None
        for op in phi.operands:
            if op == same or op == phi:
                continue
            if same is not None:
                return phi
            same = op
        if same is None:
            same = IRUndef()

        if phi in phi.users:
            phi.users.remove(phi)

        self.replace(phi, same)
        for use in phi.users:
            use.replace(phi, same)

        for use in phi.users:
            if isinstance(use, IRPhi):
                self.try_remove(use)

        return same

    def seal_block(self, block):
        if not self.traverse_end and block in self.labels.values():
            return
        # print("Block {} sealed".format(block.id))
        for var in self.incomplete_phis[block]:
            self.add_phi_operands(var, self.incomplete_phis[block][var])
        self.sealed_blocks.append(block)

    def create_basic_block(self):
        block = Statements(self.num)
        self.incomplete_phis[block] = {}
        self.num += 1
        self.blocks.append(block)
        return block

    def create_branch_block(self, var, true_block, false_block):
        block = Branch(self.num, var, true_block, false_block)
        self.incomplete_phis[block] = {}
        self.num += 1
        self.blocks.append(block)
        return block

    def create_switch_block(self, var):
        block = Switch(self.num, var)
        self.incomplete_phis[block] = {}
        self.num += 1
        self.blocks.append(block)
        return block

    def create_temp_var(self):
        num = self.temp
        self.temp += 1
        return IRTemp(num)

    def create_phi(self, block):
        num = self.phi
        self.phi += 1
        phi = IRPhi(num, block)
        self.phis.append(phi)
        return phi

    def add_block(self, block: CFGBlock):
        self.current_block.set_next(block)
        self.current_block = block

    def print(self):
        for block in self.blocks:
            block.print()

        for phi in self.phis:
            print("{} defined in block {}".format(phi, phi.block.id))


