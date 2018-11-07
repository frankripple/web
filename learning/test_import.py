import unittest
import data_import

class TestImportDevice(unittest.TestCase):

    def test_import_error(self):
        with self.assertRaises(FileNotFoundError):
            data_import.import_devices('NoExistPath')

        with self.assertRaises(NotADirectoryError):
            data_import.import_devices('data_import.py')

if __name__ == '__main__':
    unittest.main()