# coding=utf-8
from sys import stdout, stderr

from ifj2017.interpreter.interpreter import Interpreter

# import logging
# logging.basicConfig(level=logging.DEBUG)
code = """\
.IFJcode17
jump scope

label inner
    write string@\\ninner\\040function\\040called\\n
return 

label function
    DPRINT LF@a
    write string@\\nfunction\\040called\\n
    call inner
return


label scope
    CREATEFRAME
    PUSHFRAME
    DEFVAR LF@a
    DEFVAR LF@b
    DEFVAR GF@bar
    MOVE LF@a int@42
    write LF@a
    POPFRAME
    move TF@a   float@42.78
    write string@\\nfoobar\\n
    write TF@a
    
    CREATEFRAME
    PUSHFRAME
    MOVE LF@a int@42
    MOVE LF@b int@42
    JUMPIFNEQ test LF@a LF@b
    
    
    
    call function
    call function
    TYPE LF@b int@42
    BREAK
    call function
    
    jump test
    write string@\\t\\t\\tDO\\040NOT\\040WRITE\\t\\t\\t
    label test
    
    pushs int@58
    pops GF@bar
    write string@\\n
    write GF@bar
"""

# logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    state = Interpreter(code).run()
    print(state.stdout.getvalue(), file=stdout)
    print(state.stderr.getvalue(), file=stderr)
