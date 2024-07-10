from libs.simple_logger import log, exc
import os

abs_path_executed_file = os.getcwd()


def contentv2(input_file, output):
    content = bytearray()
    xor_key = [0x61, 0x23, 0x21, 0x73, 0x43, 0x30, 0x2c, 0x2e]
    content_idx = 0
    try:
        with open(input_file, 'rb') as input_file:
            while byte := input_file.read(1):
                content += bytes([ord(byte) ^ xor_key[content_idx % (len(xor_key))]])
                content_idx += 1
    except (IOError, OSError) as exception:
        exc(f'Could not read input file {exception}')
        return

    os.chdir(abs_path_executed_file + "/Data")  # change working dir to /Data
  
    try:
        with open(output, 'wb') as output_file:  # if output is full path, it will be saved by path, not the working dir
            output_file.write(content)
            log(f"Successfully saved {output}")
            abs_output_file_path = os.path.abspath(output)
            os.chdir(abs_path_executed_file)
            return abs_output_file_path
    except (IOError, OSError) as exception:
        exc(f'Could not create output file {exception}')
        return
