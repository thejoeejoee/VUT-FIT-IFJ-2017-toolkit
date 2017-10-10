# coding=utf-8
from ifj2017.interpreter.interpreter import Interpreter
import logging
code = """\
.IFJcode17
jump scope

label function
write string@\\nfunction\\040called\\n
return


label scope
CREATEFRAME
PUSHFRAME
DEFVAR LF@a
DEFVAR GF@bar
MOVE LF@a int@42
write LF@a
POPFRAME
move TF@a   float@42.78
write string@\\nfoobar\\n
write TF@a

call function
call function
call function

jump test
write string@\\n\\t\\t\\tDO\\040NOT\\040WRITE\\t\\t\\t
label test

pushs int@58
pops GF@bar
write string@\\n
write GF@bar
"""

# logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    print(Interpreter(code).run())
