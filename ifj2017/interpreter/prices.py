# coding=utf-8


class InstructionPrices(object):
    _prices_table = {
        0: 'LABEL,BREAK,DPRINT,GROOT'.split(','),
        1: 'MOVE,DEFVAR,PUSHS,POPS,INT2FLOATS,FLOAT2INTS,FLOAT2R2EINTS,FLOAT2R2OINTS,INT2CHARS,STRI2INTS,JUMPIFEQS,'
           'JUMPIFNEQS'.split(','),
        2: 'PUSHFRAME,POPFRAME,CREATEFRAME,CLEARS,INT2FLOAT,FLOAT2INT,FLOAT2R2EINT,FLOAT2R2OINT,INT2CHAR,STRI2INT,'
           'JUMP,JUMPIFEQ,JUMPIFNEQ,TYPE'.split(','),
        3: 'ADDS,SUBS,MULS,DIVS,LTS,GTS,EQS,ANDS,ORS,NOTS'.split(','),
        4: 'ADD,SUB,MUL,DIV,LT,GT,EQ,AND,OR,NOT,READ,WRITE,CONCAT,STRLEN,GETCHAR,SETCHAR'.split(','),
        5: 'CALL,RETURN'.split(','),
    }

    INSTRUCTIONS = {
        name: value for value, names in _prices_table.items() for name in names
    }

    OPERAND_CONSTANT = 1
    OPERAND_STACK = 2
    OPERAND_VARIABLE = 4
