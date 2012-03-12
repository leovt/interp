# Copyright (c) 2012, Leonhard Vogt (name.surname@gmx.ch)
# This code is provided "as is" without any warranties.
# Redistribution of this code and use in derivative works are permitted.

"""
This is a partial Python bytecode interpreter.
http://leovt.wordpress.com
"""

# define constants for the byte-codes
import opcode
LOAD_CONST = opcode.opmap['LOAD_CONST']
LOAD_FAST = opcode.opmap['LOAD_FAST']
LOAD_GLOBAL = opcode.opmap['LOAD_GLOBAL']
LOAD_ATTR = opcode.opmap['LOAD_ATTR']
STORE_FAST = opcode.opmap['STORE_FAST']
RETURN_VALUE = opcode.opmap['RETURN_VALUE']
BINARY_ADD = opcode.opmap['BINARY_ADD']
BINARY_SUBTRACT = opcode.opmap['BINARY_SUBTRACT']
BINARY_MULTIPLY = opcode.opmap['BINARY_MULTIPLY']
CALL_FUNCTION = opcode.opmap['CALL_FUNCTION']

SETUP_LOOP = opcode.opmap['SETUP_LOOP']
POP_BLOCK = opcode.opmap['POP_BLOCK']
GET_ITER = opcode.opmap['GET_ITER']
FOR_ITER = opcode.opmap['FOR_ITER']

JUMP_ABSOLUTE = opcode.opmap['JUMP_ABSOLUTE']
JUMP_FORWARD = opcode.opmap['JUMP_FORWARD']
JUMP_IF_FALSE_OR_POP = opcode.opmap['JUMP_IF_FALSE_OR_POP']
JUMP_IF_TRUE_OR_POP = opcode.opmap['JUMP_IF_TRUE_OR_POP']
POP_JUMP_IF_FALSE = opcode.opmap['POP_JUMP_IF_FALSE']
POP_JUMP_IF_TRUE = opcode.opmap['POP_JUMP_IF_TRUE']

PRINT_ITEM = opcode.opmap['PRINT_ITEM']
PRINT_NEWLINE = opcode.opmap['PRINT_NEWLINE']

BUILD_LIST = opcode.opmap['BUILD_LIST']
BUILD_TUPLE = opcode.opmap['BUILD_TUPLE']

POP_TOP = opcode.opmap['POP_TOP']

class InterpError(Exception):
    '''
    raised when something is wrong with the bytecode
    or the interpreter state
    '''

import types

class Frame(object):
    """
    Execution frame, holds the state of the interpreter for one function
    """
    def __init__(self, code, globs, caller):
        """
        Initialize the frame instance

        Args:
           code: code object which is executed
           globs: global namespace in which code is executed
           caller: parent frame that called this code
        """
        self.locals = [None] * code.co_nlocals
        self.pc = 0
        self.stack = []
        self.globs = globs
        self.code = code
        self.caller = caller

def execute(code, globs):
    """
    Execute a code object
    
    Args:
       code: code object which is executed
       globs: global namespace
       
    Returns:
       the return value of the executed code
    """
    f = Frame(code, globs, None)

    while True:
        bc = ord(f.code.co_code[f.pc])

        if bc >= opcode.HAVE_ARGUMENT:
            # this bytecode takes an argument
            arg = ord(f.code.co_code[f.pc+1]) + 256*ord(f.code.co_code[f.pc+2])
        else:
            arg = ''

        print f.pc, opcode.opname[bc], arg, f.stack, f.locals
        
        if bc == LOAD_FAST:
            f.stack.append(f.locals[arg])
            f.pc += 3

        elif bc == LOAD_CONST:
            f.stack.append(f.code.co_consts[arg])
            f.pc += 3

        elif bc == LOAD_GLOBAL:
            f.stack.append(f.globs[f.code.co_names[arg]])
            f.pc += 3            

        elif bc == LOAD_ATTR:
            f.stack.append(getattr(f.stack.pop(), f.code.co_names[arg]))
            f.pc += 3            

        elif bc == BINARY_ADD:
            b = f.stack.pop()
            a = f.stack.pop()
            f.stack.append(a+b)
            f.pc += 1

        elif bc == BINARY_SUBTRACT:
            b = f.stack.pop()
            a = f.stack.pop()
            f.stack.append(a-b)
            f.pc += 1

        elif bc == BINARY_MULTIPLY:
            b = f.stack.pop()
            a = f.stack.pop()
            f.stack.append(a*b)
            f.pc += 1

        elif bc == STORE_FAST:
            f.locals[arg] = f.stack.pop()
            f.pc += 3

        elif bc == RETURN_VALUE:
            ret = f.stack.pop()
            if f.stack:
                raise InterpError('stack not empty on return')
            if f.caller is None:
                return ret
            else:
                f = f.caller
                f.stack.append(ret)

        elif bc == SETUP_LOOP:
            f.pc += 3
        
        elif bc == POP_BLOCK:
            f.pc += 1

        elif bc == GET_ITER:
            f.stack.append(iter(f.stack.pop()))
            f.pc += 1

        elif bc == JUMP_ABSOLUTE:
            f.pc = arg

        elif bc == JUMP_FORWARD:
            f.pc += arg + 3

        elif bc == JUMP_IF_FALSE_OR_POP:
            if f.stack[-1]:
                f.stack.pop()
                f.pc += 3
            else:
                f.pc = arg

        elif bc == JUMP_IF_TRUE_OR_POP:
            if f.stack[-1]:
                f.pc = arg
            else:
                f.stack.pop()
                f.pc += 3

        elif bc == POP_JUMP_IF_FALSE:
            if f.stack.pop():
                f.pc += 3
            else:
                f.pc = arg

        elif bc == POP_JUMP_IF_TRUE:
            if f.stack.pop():
                f.pc = arg
            else:
                f.pc += 3

        elif bc == CALL_FUNCTION:
            nb_kwargs, nb_args = divmod(arg, 256)

            call_args = [None] * nb_args
            for i in range(arg-1, -1, -1):
                call_args[i] = f.stack.pop()
            
            callee = f.stack.pop()
            if type(callee) is types.BuiltinFunctionType:
                f.stack.append(callee(*call_args))
                f.pc += 3
            elif type(callee) is types.FunctionType:
                subframe = Frame(callee.func_code, callee.func_globals, f)
                subframe.locals[:nb_args] = call_args
                f.pc += 3
                f = subframe

        elif bc == FOR_ITER:
            try:
                nx = next(f.stack[-1])
            except StopIteration:
                f.stack.pop()
                f.pc += arg + 3
            else:
                f.stack.append(nx)
                f.pc += 3

        elif bc == PRINT_ITEM:
            print f.stack.pop(),
            f.pc += 1

        elif bc == PRINT_NEWLINE:
            print
            f.pc += 1

        elif bc == BUILD_LIST:
            if arg:
                lst = list(f.stack[-arg:])
                f.stack[-arg:] = []
                f.stack.append(lst)
            else:
                f.stack.append(list())
            f.pc += 3

        elif bc == BUILD_TUPLE:
            tup = tuple(f.stack[-arg:])
            f.stack[-arg:] = []
            f.stack.append(tup)
            f.pc += 3

        elif bc == POP_TOP:
            f.stack.pop()
            f.pc += 1

        else:
            raise InterpError('Unknown Opcode %d (%s)' % (bc, opcode.opname[bc]))


        
        
        
