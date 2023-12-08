import argparse
import os
from functools import partial
from pathlib import Path


def check_number(number: int, value_limit: int = (2**64) - 1) -> None:
    if number > value_limit or number < 0:
        raise ValueError(
            f'Number cannot exceed the value: {value_limit} '
            'or cannot be less than zero'
        )


def check_file_exist(filename: str) -> None:
    try:
        os.path.getsize(filename)
    except FileNotFoundError:
        raise ValueError((f'No such file or directory: {filename}'))


def vlq_convertor(
        number: int, filter: int = 0b1111111, msb: int = 0b10000000
) -> list[int]:
    """
    The function converts the input number into VLQ format,
    in the output is a list of byte partitions of the number.
    """
    if number == 0:
        return [0]

    result = []
    while number:
        byte = number & filter
        if not result:
            result.append(byte)
            number >>= 7
            continue
        byte += msb
        result.append(byte)
        number >>= 7
    return(result[::-1])


def transfer_data_to_original_file(
        original: str, copy: str = 'copy.bin'
) -> None:
    """
    Transfer data from the copy to the original file,
    then deleting the copy file.
    """
    original_file = open(original, 'wb')
    copy_file = open(copy, 'rb')
    copy_data = copy_file.read()
    original_file.write(copy_data)
    original_file.close()
    copy_file.close()
    os.remove(os.path.abspath(copy))


def add_new_number_in_file(
        filename: str, new_number: list[int], position: int
) -> None:
    """
    The function creates a new file and adds to it all the data from
    the original file and a new number.
    """
    Path('copy.bin').touch()
    copy_file = open('copy.bin', 'wb')
    counter = 0

    if position == 0:
        file = open(filename, 'rb')
        file_data = file.read()
        for new_byte in new_number:
            copy_file.write(new_byte.to_bytes(1, byteorder='big'))
        copy_file.write(file_data)
        file.close()
        copy_file.close()
        return transfer_data_to_original_file(filename)

    with open(filename, 'rb') as file:
        for byte in iter(partial(file.read, 1), b''):
            number = int.from_bytes(byte, 'big')
            if number < 128:
                counter += 1
                copy_file.write(byte)
            else:
                copy_file.write(byte)
            if counter == position:
                for new_byte in new_number:
                    copy_file.write(new_byte.to_bytes(1, byteorder='big'))
                file_data = file.read()
                copy_file.write(file_data)
                copy_file.close()
                return transfer_data_to_original_file(filename)

    if os.path.getsize('copy.bin') == 0:
        copy_file.close()
        os.remove(os.path.abspath('copy.bin'))
        raise ValueError('Position value out of range.')


def main():
    parser = argparse.ArgumentParser(
        prog='VLQ convertor',
        description=(
            'Script for adding a number to a given position '
            'of a number sequence in VLQ format in a binary file.'
        ),
        epilog=(
            'Be sure to provide the following arguments: '
            'File name: (absolute path to the bin file). '
            'Number: Which needs to be added '
            '(must be positive and less than 2**64 - 1. '
            'Position: The position that needs to be added '
            'in the numerical sequence recorded in the file.'
        )
    )
    parser.add_argument('filename')
    parser.add_argument('number', type=int)
    parser.add_argument('position', type=int)
    args = parser.parse_args()

    check_number(args.number)
    check_file_exist(args.filename)
    number_in_vlq_format = vlq_convertor(args.number)
    add_new_number_in_file(args.filename, number_in_vlq_format, args.position)
    print(
        f'Number {args.number} in VQL format successfully added '
        f'to position {args.position} in file {args.filename}'
    )


if __name__ == '__main__':
    main()
