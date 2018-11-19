'''
    Test for function in import devices
'''
import unittest
import data_import
import os

class TestImportDevice(unittest.TestCase):

    def test_import_error(self):
        '''Test only error situation for import device'''
        with self.assertRaises(FileNotFoundError):
            data_import.import_device_interface_from_file('NoExistPath')

        with self.assertRaises(NotADirectoryError):
            data_import.import_device_interface_from_file('data_import.py')

    def test_read_ldp_information(self):
        '''Test test for read ldp information'''
        debug_prefix = r''
        test_path = r'ut\01normal_brief'
        expected = {
            '6/1':('A-XXXX-ZZZ-CS02', 'Eth6/1'),
            '6/9':('A_XXYY_UUU_DS01', 'Ten4/1')
        }
        self.assertEqual(
            expected, data_import.get_cdp_information(os.path.join(debug_prefix, test_path))
        )

        test_path = r'ut\02detail_test'
        expected = {
            'FastEthernet1':('B-XXX4A-ZZZ-DS01', 'mgmt0')
        }
        self.assertEqual(
            expected, data_import.get_cdp_information(os.path.join(debug_prefix, test_path))
        )

        test_path = r'ut\03detail2'
        expected = {
            'FastEthernet1':('B-XXX4A-ZZZ-DS01', 'mgmt0')
        }
        self.assertEqual(
            expected, data_import.get_cdp_information(os.path.join(debug_prefix, test_path))
        )
if __name__ == '__main__':
    unittest.main()
