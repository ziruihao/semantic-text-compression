import os
from engine import Engine
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-i', '--input', required = True, help="Input file or directory path")
    parser.add_argument('-o', '--output', required = True, help="Output file or directory path")
    parser.add_argument('-l', '--lossless', action = 'store_true', help="Whether to use lossless compression")
    parser.add_argument('-v', '--verbose', action = 'store_true', help="Whether to log output")

    args = parser.parse_args()

    engine = Engine('data/shorthand_dict.json')

    if os.path.isdir(args.input):
        if not os.path.isdir(args.output):
            os.mkdir(args.output)
        print('Compressing', args.input, 'to', args.output)
        print()
        print('orig. size\tcomp. size\tcomp. ratio\thit rate\tfile name')
        print('----------\t----------\t----------\t----------\t----------')
        for root, dirs, files in os.walk(args.input):
            for file in files:
                input_file_path = os.path.join(root, file)
                output_file_path = os.path.join(args.output, file)
                compressed_words, total_words, compressed_file_size, original_file_size = engine.compress(input_file_path, output_file_path, {'lossless': args.lossless, 'verbose': args.verbose })
                print('{} bytes\t{} bytes\t{:.2f}%\t\t{:.2f}%\t\t{}'.format(original_file_size, compressed_file_size, compressed_file_size / original_file_size * 100, compressed_words / total_words * 100, file))
    else:
        print('Compressing', args.input)
        compressed_words, total_words, compressed_file_size, original_file_size = engine.compress(args.input, args.output, {'lossless': args.lossless, 'verbose': args.verbose })
        print('Compressed', str(round(compressed_words / total_words * 100, 1)) + '% of words, reducing file size from', original_file_size, 'bytes to', compressed_file_size, 'bytes at a', str(round(compressed_file_size / original_file_size * 100, 1)) + '% compression rate.')
    
    
