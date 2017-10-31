# coding=utf-8
from sys import stdout, stderr

from ifj2017.interpreter.interpreter import Interpreter

# import logging
# logging.basicConfig(level=logging.DEBUG)
code = """\
# foo bar
.IFJcode17

# foo bar
DEFVAR GF@%00000_%__temp_variable_1  
DEFVAR GF@%00000_%__temp_variable_2  
DEFVAR GF@%00000_%__temp_variable_3  
JUMP %_LABEL_000_main_scope_DEPTH_000  
LABEL %_LABEL_000_main_scope_DEPTH_000  
CREATEFRAME   
PUSHFRAME   
PUSHS int@78  
PUSHS int@2  
GTS   
PUSHS bool@false
JUMPIFEQS %_LABEL_002_if_else_DEPTH_001  
DEFVAR LF@%00001_a  
MOVE LF@%00001_a int@0 
PUSHS int@12  
POPS LF@%00001_a  
LABEL %_LABEL_003_while_start_DEPTH_002  
PUSHS LF@%00001_a  
PUSHS int@1  
LTS   
NOTS   
PUSHS bool@false  
JUMPIFEQS %_LABEL_004_while_end_DEPTH_002  
PUSHS LF@%00001_a  
PUSHS int@8  
GTS   
PUSHS bool@false  
JUMPIFEQS %_LABEL_006_if_else_DEPTH_003  
PUSHS int@69  
POPS GF@%00000_%__temp_variable_1  
WRITE GF@%00000_%__temp_variable_1  
JUMP %_LABEL_005_if_end_DEPTH_003  
JUMP %_LABEL_005_if_end_DEPTH_003  
LABEL %_LABEL_006_if_else_DEPTH_003  
PUSHS int@11  
POPS GF@%00000_%__temp_variable_1  
WRITE GF@%00000_%__temp_variable_1  
LABEL %_LABEL_007_if_else_DEPTH_003  
LABEL %_LABEL_005_if_end_DEPTH_003  
PUSHS LF@%00001_a  
PUSHS int@1  
SUBS   
POPS LF@%00001_a  
JUMP %_LABEL_003_while_start_DEPTH_002  
LABEL %_LABEL_004_while_end_DEPTH_002  
JUMP %_LABEL_001_if_end_DEPTH_001  
JUMP %_LABEL_001_if_end_DEPTH_001  
LABEL %_LABEL_002_if_else_DEPTH_001  
PUSHS int@77  
POPS GF@%00000_%__temp_variable_1  
WRITE GF@%00000_%__temp_variable_1  
LABEL %_LABEL_008_if_else_DEPTH_001  
LABEL %_LABEL_001_if_end_DEPTH_001  
POPFRAME   


"""

# logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    state_ = Interpreter(code).run()
    print(state_.stdout.getvalue(), file=stdout)
    print(state_.stderr.getvalue(), file=stderr)
