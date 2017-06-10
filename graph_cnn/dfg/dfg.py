
from graph_cnn.cfg.cfgblock import Statements, Entry, Exit, Branch, Switch
from graph_cnn.ir.irstatement import *
from graph_cnn.ir.irexpression import *
from graph_cnn.dfg.dfgblock import *


class DFG:
    def __init__(self, cfg):
        self.cfg = cfg
        self.num = 0
        self.blocks = []
        self.def_block = {}
        self.statement_map = {}

        self.setup_def()
        self.build()

    def get_next_num(self):
        temp = self.num
        self.num += 1
        return temp

    def setup_def(self):
        for block in self.cfg.blocks:
            if not isinstance(block, Statements):
                continue

            for s in block.statements:
                if isinstance(s, IRPhi):
                    b = DFGPhi(self)
                elif isinstance(s, IRInput):
                    b = DFGInput(self)
                elif isinstance(s, IRArg):
                    b = DFGArg(self)
                elif isinstance(s, IRAssignment):
                    b = DFGAssignment(self)
                elif isinstance(s, IRArrayAssignment):
                    b = DFGArrayAssignment(self)
                elif isinstance(s, IRPointAssignment):
                    b = DFGPointAssignment(self)
                elif isinstance(s, IRStructRefAssignment):
                    b = DFGStructRefAssignment(self)
                elif isinstance(s, IRFuncCall):
                    b = DFGFuncCall(self, s.name)
                elif isinstance(s, IRFieldAccess):
                    b = DFGFieldAccess(self, s.field)
                elif isinstance(s, IRAddr):
                    b = DFGAddr(self)
                elif isinstance(s, IRPoint):
                    b = DFGPoint(self)
                elif isinstance(s, IRReturn):
                    b = DFGReturn(self)
                elif isinstance(s, IRBinaryOp):
                    b = DFGBinaryOp(self, s.op)
                elif isinstance(s, IRUnaryOp):
                    b = DFGUnaryOp(self, s.op)
                elif isinstance(s, IRArrayRef):
                    b = DFGArrayRef(self)
                elif isinstance(s, IRTernaryOp):
                    b = DFGTernaryOp(self)
                else:
                    raise RuntimeError()

                self.blocks.append(b)
                self.statement_map[s] = b
                target = s.def_var()
                if target is not None:
                    self.def_block[target] = b

    def build(self):
        for block in self.cfg.blocks:
            if isinstance(block, Entry):
                continue

            if isinstance(block, Exit):
                continue

            if isinstance(block, Branch) or isinstance(block, Switch):
                var = block.var
                cond = DFGCondition(self)
                self.blocks.append(cond)

                if isinstance(var, IRTemp) or isinstance(var, IRExpPhi):
                    self.def_block[var].nexts.append(cond)
                elif isinstance(var, IRConstant):
                    b = DFGConst(self, var.value, var.type)
                    self.blocks.append(b)
                    b.nexts.append(cond)
                elif isinstance(var, IRUndef):
                    b = DFGUndef(self)
                    self.blocks.append(b)
                    b.nexts.append(cond)

            if isinstance(block, Statements):
                for s in block.statements:
                    for use in s.use_var():
                        if isinstance(use, IRTemp) or isinstance(use, IRExpPhi):
                            self.def_block[use].nexts.append(self.statement_map[s])
                        elif isinstance(use, IRConstant):
                            b = DFGConst(self, use.value, use.type)
                            self.blocks.append(b)
                            b.nexts.append(self.statement_map[s])
                        elif isinstance(use, IRUndef):
                            b = DFGUndef(self)
                            self.blocks.append(b)
                            b.nexts.append(self.statement_map[s])

    def print(self, f=None):
        for block in self.blocks:
            for next in block.nexts:
                print("{} -> {}".format(block, next), file=f)
