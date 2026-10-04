import copy
import unittest
from capacity import remaining_capacity

class CapacityTests(unittest.TestCase):
    def test_cancelled_reservations_release_places(self):
        rows = [{'status': 'confirmed', 'places': 3}, {'status': 'cancelled', 'places': 4}]
        original = copy.deepcopy(rows)
        self.assertEqual(remaining_capacity(10, rows), 7)
        self.assertEqual(rows, original)

    def test_full_and_empty(self):
        self.assertEqual(remaining_capacity(10, []), 10)
        self.assertEqual(remaining_capacity(2, [{'status': 'confirmed', 'places': 3}]), 0)

if __name__ == '__main__':
    unittest.main()
