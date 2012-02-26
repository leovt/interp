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

if __name__ == '__main__':
    unittest.main()
