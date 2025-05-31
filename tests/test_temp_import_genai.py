import unittest

class TestImportGenAI(unittest.TestCase):
    def test_can_import_genai(self):
        print("Attempting to import google.generativeai...")
        try:
            import google.generativeai as genai
            print("Successfully imported google.generativeai.")
            self.assertIsNotNone(genai, "genai module should not be None")
        except Exception as e:
            print(f"Failed to import google.generativeai: {e}")
            self.fail(f"Importing google.generativeai failed: {e}")

if __name__ == '__main__':
    unittest.main()
