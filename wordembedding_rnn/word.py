__author__ = 'woooking'

from enum import Enum


class KeyWord(Enum):
    FILE_START = "FILE_START"
    FILE_END = "FILE_END"

    FUNC_START = "FUNC_START"
    FUNC_PARAM = "FUNC_PARAM"
    FUNC_BODY = "FUNC_BODY"
    FUNC_END = "FUNC_END"

    FOR_START = "FOR_START"
    FOR_INIT = "FOR_INIT"
    FOR_COND = "FOR_COND"
    FOR_UPDATE = "FOR_UPDATE"
    FOR_STMT = "FOR_STMT"
    FOR_END = "FOR_END"

    WHILE_START = "WHILE_START"
    WHILE_COND = "WHILE_COND"
    WHILE_STMT = "WHILE_STMT"
    WHILE_END = "WHILE_END"

    DO_START = "DO_START"
    DO_COND = "DO_COND"
    DO_STMT = "DO_STMT"
    DO_END = "DO_END"

    FUNC_CALL = "FUNC_CALL"
    FUNC_ARG = "FUNC_ARG"
    FUNC_CALL_END = "FUNC_CALL_END"

    TYPE = "TYPE"

    RETURN = "RETURN"

    BREAK = "BREAK"

    TERNARY_COND = "TERNARY_COND"
    TERNARY_TRUE = "TERNARY_TRUE"
    TERNARY_FALSE = "TERNARY_FALSE"
    TERNARY_END = "TERNARY_END"

    IF_COND = "IF_COND"
    IF_TRUE = "IF_TRUE"
    IF_FALSE = "IF_FALSE"
    IF_END = "IF_END"

    SWITCH_START = "SWITCH_START"
    SWITCH_CASE = "SWITCH_CASE"
    SWITCH_CASE_STMT = "SWITCH_CASE"
    SWITCH_DEFAULT = "SWITCH_DEFAULT"
    SWITCH_END = "SWITCH_END"

    ARRAY_DECL = "ARRAY_DECL"
    ARRAY_DIM = "ARRAY_DIM"

    ARRAY_REF = "ARRAY_REF"
    ARRAY_INDEX = "ARRAY_INDEX"

    VARIABLE_DECL = "VARIABLE_DECL"
    VARIABLE_INIT = "VARIABLE_INIT"

    PTR_DECL = "PTR_DECL"
    PTR_INIT = "PTR_INIT"

    STRUCT_DECL = "STRUCT_DECL"

    ENUM_DECL = "ENUM_DECL"
    ENUM_NAME = "ENUM_NAME"
    ENUM_MEMBER = "ENUM_MEMBER"
    ENUM_VALUE = "ENUM_VALUE"

    CAST = "CAST"

    INIT_LIST = "INIT_LIST"
    INIT_ITEM = "INIT_ITEM"

    STRUCT_REF = "STRUCT_REF"
    STRUCT_POINT_REF = "STRUCT_POINT_REF"
    STRUCT_FIELD = "STRUCT_FIELD"

    TYPEDEF = "TYPEDEF"

    GOTO = "GOTO"
    LABEL = "LABEL"


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
