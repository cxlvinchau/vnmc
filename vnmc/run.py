import argparse
from pathlib import Path

from vnmc.timp.parser import imp_parser, IMPTransformer
from vnmc.timp.preprocessing import Simplifier

parser = argparse.ArgumentParser(description='Parsing IMP')
parser.add_argument("source")

args = parser.parse_args()

source = Path(args.source)

if source.exists():
    with open(source, "r") as f:
        program_str = "".join(f.readlines())
        tree = imp_parser.parse(program_str)
        module = IMPTransformer().transform(tree)
        module.transform(Simplifier())
        print(module.pretty())
else:
    raise ValueError(f"Source file {args.source} does not exist")