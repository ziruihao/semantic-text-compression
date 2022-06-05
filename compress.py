from engine import Engine
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-i', '--input', required = True, help="Input file path")
    parser.add_argument('-o', '--output', required = True, help="Output file path")

    args = parser.parse_args()

    engine = Engine('../data/shorthand_dict.json')
    engine.compress(args.input, args.output, None)
    
