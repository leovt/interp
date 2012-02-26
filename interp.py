# Copyright (c) 2012, Leonhard Vogt (name.surname@gmx.ch)
# This code is provided "as is" without any warranties.
# Redistribution of this code and use in derivative works are permitted.

def test():
    return square(4) + square(3)

def square(n):
    return n * n

# define constants for the byte-codes
import dis
LOAD_CONST = dis.opmap['LOAD_CONST']
LOAD_FAST = dis.opmap['LOAD_FAST']
LOAD_GLOBAL = dis.opmap['LOAD_GLOBAL']
STORE_FAST = dis.opmap['STORE_FAST']
RETURN_VALUE = dis.opmap['RETURN_VALUE']
BINARY_ADD = dis.opmap['BINARY_ADD']
BINARY_SUBTRACT = dis.opmap['BINARY_SUBTRACT']
BINARY_MULTIPLY = dis.opmap['BINARY_MULTIPLY']
CALL_FUNCTION = dis.opmap['CALL_FUNCTION']

SETUP_LOOP = dis.opmap['SETUP_LOOP']
POP_BLOCK = dis.opmap['POP_BLOCK']
GET_ITER = dis.opmap['GET_ITER']
FOR_ITER = dis.opmap['FOR_ITER']
JUMP_ABSOLUTE = dis.opmap['JUMP_ABSOLUTE']

PRINT_ITEM = dis.opmap['PRINT_ITEM']
PRINT_NEWLINE = dis.opmap['PRINT_NEWLINE']

import types

class Frame(object):
    def __init__(self, code, globals, caller):
        self.locals = [None] * code.co_nlocals
        self.PC = 0
        self.stack = []
        self.globals = globals
        self.code = code
        self.caller = caller

def execute(code, globals):
    f = Frame(code, globals, None)

    while True:
        bc = ord(f.code.co_code[f.PC])

        #print f.PC, dis.opname[bc], f.stack, f.locals
        
        if bc==LOAD_FAST:
            arg = ord(f.code.co_code[f.PC+1]) + 256*ord(f.code.co_code[f.PC+2])
            f.stack.append(f.locals[arg])
            f.PC += 3

        elif bc==LOAD_CONST:
            arg = ord(f.code.co_code[f.PC+1]) + 256*ord(f.code.co_code[f.PC+2])
            f.stack.append(f.code.co_consts[arg])
            f.PC += 3

        elif bc==LOAD_GLOBAL:
            arg = ord(f.code.co_code[f.PC+1]) + 256*ord(f.code.co_code[f.PC+2])
            f.stack.append(f.globals[f.code.co_names[arg]])
            f.PC += 3            

        elif bc==BINARY_ADD:
            b = f.stack.pop()
            a = f.stack.pop()
            f.stack.append(a+b)
            f.PC += 1

        elif bc==BINARY_SUBTRACT:
            b = f.stack.pop()
            a = f.stack.pop()
            f.stack.append(a-b)
            f.PC += 1

        elif bc==BINARY_MULTIPLY:
            b = f.stack.pop()
            a = f.stack.pop()
            f.stack.append(a*b)
            f.PC += 1

        elif bc==STORE_FAST:
            arg = ord(f.code.co_code[f.PC+1]) + 256*ord(f.code.co_code[f.PC+2])
            f.locals[arg] = f.stack.pop()
            f.PC += 3

        elif bc==RETURN_VALUE:
            if f.caller is None:
                return f.stack.pop()
            else:
                ret = f.stack.pop()
                f = f.caller
                f.stack.append(ret)

        elif bc==SETUP_LOOP:
            f.PC += 3
        
        elif bc==POP_BLOCK:
            f.PC += 1

        elif bc==GET_ITER:
            f.stack.append(iter(f.stack.pop()))
            f.PC += 1

        elif bc==JUMP_ABSOLUTE:
            arg = ord(f.code.co_code[f.PC+1]) + 256*ord(f.code.co_code[f.PC+2])
            f.PC = arg

        elif bc==CALL_FUNCTION:
            arg = ord(f.code.co_code[f.PC+1])

            call_args = [None] * arg
            for i in range(arg-1, -1, -1):
                call_args[i] = f.stack.pop()
            
            callee = f.stack.pop()
            if type(callee) is types.BuiltinFunctionType:
                f.stack.append(callee(*call_args))
                f.PC += 3
            elif type(callee) is types.FunctionType:
                subframe = Frame(callee.func_code, callee.func_globals, f)
                subframe.locals[:arg] = call_args
                f.PC += 3
                f = subframe

        elif bc==FOR_ITER:
            arg = ord(f.code.co_code[f.PC+1]) + 256*ord(f.code.co_code[f.PC+2])
            try:
                nx = next(f.stack[-1])
            except StopIteration:
                f.stack.pop()
                f.PC += arg + 3
            else:
                f.stack.append(nx)
                f.PC += 3

        elif bc==PRINT_ITEM:
            print f.stack.pop(),
            f.PC += 1

        elif bc==PRINT_NEWLINE:
            print
            f.PC += 1

        else:
            raise Exception('Unknown Opcode %d (%s)' % (bc, dis.opname[bc]))

print 'normal Python call:', test()
print 'own execute function:', execute(test.func_code, test.func_globals)
        
        
        
