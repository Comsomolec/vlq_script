import os
import unittest
from pathlib import Path

from vlq_script import (
    add_new_number_in_file,
    vlq_convertor,
    check_file_exist,
    check_number
)


class SquareEqSolverTestCase(unittest.TestCase):

    def test_vlq_convertor(self):
        test_data = [0, 127, 8192, 16383, 2097152, 268435455]
        result = [
            [0],
            [127],
            [192, 0],
            [255, 127],
            [129, 128, 128, 0],
            [255, 255, 255, 127]
        ]

        for i in range(len(test_data)):
            self.assertEqual(vlq_convertor(test_data[i]), result[i])

    def test_add_number_in_file(self):
        Path('test.bin').touch()
        test_data = [0, 1, 128]
        result = [0, 124, 1, 129, 0]

        for i in range(len(test_data)):
            vlq_number = vlq_convertor(test_data[i])
            add_new_number_in_file('test.bin', vlq_number, i)
        another_number = vlq_convertor(124)
        add_new_number_in_file('test.bin', another_number, 1)

        with open('test.bin', 'rb') as file:
            for element in result:
                byte = file.read(1)
                number = int.from_bytes(byte, 'big')
                self.assertEqual(number, element)

        os.remove(os.path.abspath('test.bin'))

    def test_check_number(self):
        self.assertRaises(ValueError, check_number, -1)
        self.assertRaises(ValueError, check_number, 2**64)

    def test_check_file_exist(self):
        self.assertRaises(ValueError, check_file_exist, 'test.bin')
