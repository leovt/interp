# Copyright (c) 2012, Leonhard Vogt (name.surname@gmx.ch)
# This code is provided "as is" without any warranties.
# Redistribution of this code and use in derivative works are permitted.

def test():
    a = 2
    b = a + 4
    return (a + 1) * (b - 2)

# define constants for the byte-codes
import dis
LOAD_CONST = dis.opmap['LOAD_CONST']
LOAD_FAST = dis.opmap['LOAD_FAST']
STORE_FAST = dis.opmap['STORE_FAST']
RETURN_VALUE = dis.opmap['RETURN_VALUE']
BINARY_ADD = dis.opmap['BINARY_ADD']
BINARY_SUBTRACT = dis.opmap['BINARY_SUBTRACT']
BINARY_MULTIPLY = dis.opmap['BINARY_MULTIPLY']

class Frame(object):
    def __init__(self, code):
        self.locals = [None] * code.co_nlocals
        self.PC = 0
        self.stack = []
        self.code = code

def execute(code):
    f = Frame(code)

    while True:
        bc = ord(f.code.co_code[f.PC])
        
        if bc==LOAD_FAST:
            arg = ord(f.code.co_code[f.PC+1]) + 256*ord(f.code.co_code[f.PC+2])
            f.stack.append(f.locals[arg])
            f.PC += 3

        elif bc==LOAD_CONST:
            arg = ord(f.code.co_code[f.PC+1]) + 256*ord(f.code.co_code[f.PC+2])
            f.stack.append(f.code.co_consts[arg])
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
            return f.stack.pop()

        else:
            raise Exception('Unknown Opcode %d (%s)' % (bc, dis.opname[bc]))

print 'normal Python call:', test()
print 'own execute function:', execute(test.func_code)
        
        
        
