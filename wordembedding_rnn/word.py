__author__ = 'woooking'

from enum import Enum


class KeyWord(Enum):
    FILE_START = "FILE_START"
    FILE_END = "FILE_END"

    FUNC_START = "FUNC_START"
    FUNC_END = "FUNC_END"

    FOR_INIT = "FOR_INIT"
    FOR_COND = "FOR_COND"
    FOR_UPDATE = "FOR_UPDATE"
    FOR_STMT = "FOR_STMT"
    FOR_END = "FOR_END"

    FUNC_CALL = "FUNC_CALL"

    RETURN = "RETURN"

    IF_COND = "IF_COND"
    IF_TRUE = "IF_TRUE"
    IF_FALSE = "IF_FALSE"
    IF_END = "IF_END"


class Word:
    _dict = {}

    def __new__(cls, value: str):
        if value in Word._dict:
            return Word._dict[value]
        obj = object.__new__(cls)
        obj.value = value
        return obj

    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return "Word({})".format(self.value)


class ConstantValue:
    _dict = {}

    def __new__(cls, value):
        if value in ConstantValue._dict:
            return ConstantValue._dict[value]
        obj = object.__new__(cls)
        obj.value = value
        return obj

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Constant({})".format(self.value)


class Op:
    _dict = {}

    def __new__(cls, value):
        if value in Op._dict:
            return Op._dict[value]
        obj = object.__new__(cls)
        obj.value = value
        return obj

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Op({})".format(self.value)
