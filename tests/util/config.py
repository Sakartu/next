import unittest
import os
from next.util import config

class ConfigTest(unittest.TestCase):
    def test_parse_locations(self):
        f = config.parse_locations

        self.assertEqual(f([]), {})

        data = [("/series", "unstructured"), ("~/test", "structured")]
        expected = {"/series": True, os.path.expanduser("~/test"): False}
        self.assertEqual(f(data), expected)

if __name__ == "__main__":
    unittest.main()
