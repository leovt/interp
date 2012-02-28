import unittest
import interp

class TestRetrunValues(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
