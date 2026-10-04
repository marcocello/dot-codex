import unittest
from presets import save, load
class PresetTests(unittest.TestCase):
    def test_roundtrip(self):
        save('weekly', 'last_7_days')
        self.assertEqual(load('weekly'), 'last_7_days')
if __name__ == '__main__':
    unittest.main()
