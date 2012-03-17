import unittest
import interp

class TestReturnValues(unittest.TestCase):
    """
    These tests are verifying that the return values
    of some functions are the same in native Python and
    in my interpreter.
    """
    def test_basic_operations(self):
        """
        Testing the first example
        """
        def test():
            a = 2
            b = a + 4
            return (a + 1) * (b - 2)

        expected = test()
        realized = interp.execute(test.func_code, {})
        self.assertEqual(expected, realized)

    def test_loop(self):
        """
        Testing a for loop. In addition to printing build a checksum
        so that we can test a meaningful return value.
        """
        def test():
            ret = 0
            for i in range(10):
                print i
                ret = ret + i
            return ret
        
        expected = test()
        realized = interp.execute(test.func_code, {'range': range})
        self.assertEqual(expected, realized)

    @unittest.skip('closures (e.g. LOAD_DEREF) not yet implemented')
    def test_call(self):
        """
        test from third post: calling a function
        """
        def test():
            return square(4) + square(3)

        def square(n):
            return n * n

        expected = test()
        realized = interp.execute(test.func_code, test.func_globals)
        self.assertEqual(expected, realized)


    def test_call_global(self):
        """
        test from third post: calling a function, at module level
        """
        global square
        def test():
            return square(4) + square(3)

        def square(n):
            return n * n

        expected = test()
        realized = interp.execute(test.func_code, test.func_globals)
        self.assertEqual(expected, realized)

    
    def test_attribute_builtin(self):
        '''
        access and execute attributes
        '''
        def test():
            x = 'abc'.upper()
            a = [3,1,2]
            a.sort()
            return a, x
        
        expected = test()
        realized = interp.execute(test.func_code, test.func_globals)
        self.assertEqual(expected, realized)

    def test_jump_or_pop(self):
        '''
        test the two instructions JUMP_IF_FALSE_OR_POP, JUMP_IF_TRUE_OR_POP
        '''
        def test():
            return ('abc' or None, 
                    '' or 1, 
                    [] and 4, 
                    (3,) and '123')
        expected = test()
        realized = interp.execute(test.func_code, test.func_globals)
        self.assertEqual(expected, realized)

    def test_pop_jump(self):
        global helper

        def helper(a,b):
            if a:
                if not b:
                    return 1
                else:
                    return 2
            else:
                return 3

        def test():
            return helper(1,0), helper(1,1), helper(0,1)

        expected = test()
        realized = interp.execute(test.func_code, test.func_globals)
        self.assertEqual(expected, realized)

    def test_jump_forward(self):
        def test():
            if True:
                ret = 'yes'
            else:
                ret = 'no'
            return ret
        expected = test()
        realized = interp.execute(test.func_code, {'True': True})
        self.assertEqual(expected, realized)

    def test_unknown_opcode(self):
        class Mock(object):
            co_code = '\xff\x00\x00'
            co_nlocals = 0

        with self.assertRaises(interp.InterpError):
            interp.execute(Mock(), {})

    def test_corrupt_stack(self):
        from interp import LOAD_CONST, RETURN_VALUE
        class Mock(object):
            co_code = ''.join(map(chr, [
                        LOAD_CONST, 0,0,
                        LOAD_CONST, 0,0,
                        RETURN_VALUE]))
            co_nlocals = 0
            co_consts = (None,)

        with self.assertRaises(interp.InterpError):
            interp.execute(Mock(), {})

    def test_compare(self):
        def test():
            return (
                1 < 2, 1 < 1, 2 < 1,
                1 > 2, 1 > 1, 2 > 1,
                1 == 2, 1 == 1, 2 == 1,
                1 <= 2, 1 <= 1, 2 <= 1,
                1 >= 2, 1 >= 1, 2 >= 1,
                1 != 2, 1 != 1, 2 != 1,
                1 is 2, 1 is 1, 2 is 1,
                1 is not 2, 1 is not 1, 2 is not 1,
                'a' in 'ab', 'a' in 'bc',
                'a' not in 'ab', 'a' not in 'bc')
    
        expected = test()
        realized = interp.execute(test.func_code, test.func_globals)
        self.assertEqual(expected, realized)

    def test_bad_compare_op(self):
        from interp import LOAD_CONST, RETURN_VALUE, COMPARE_OP
        class Mock(object):
            co_code = ''.join(map(chr, [
                        LOAD_CONST, 0,0,
                        LOAD_CONST, 0,0,
                        COMPARE_OP, 17,17,
                        RETURN_VALUE]))
            co_nlocals = 0
            co_consts = (None,)

        with self.assertRaises(interp.InterpError):
            interp.execute(Mock(), {})
        
if __name__ == '__main__':
    unittest.main()
