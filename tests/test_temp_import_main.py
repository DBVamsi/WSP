import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestImportMain(unittest.TestCase):
    def test_can_import_main(self):
        print("Attempting to import main module...")
        try:
            import main as main_module
            print("Successfully imported main module.")
            self.assertIsNotNone(main_module, "main_module should not be None")
        except Exception as e:
            print(f"Failed to import main module: {e}")
            self.fail(f"Importing main module failed: {e}")

if __name__ == '__main__':
    unittest.main()
