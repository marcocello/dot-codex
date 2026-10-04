import unittest
from counts import format_count
class CountsTests(unittest.TestCase):
    def test_singular(self):
        self.assertEqual(format_count(1), '1 item')

    def test_plural(self):
        self.assertEqual(format_count(0), '0 items')
        self.assertEqual(format_count(2), '2 items')
if __name__ == '__main__':
    unittest.main()
