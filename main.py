
from core import validator
from core.arg_parser import setup_arg_parser, parse


def run_validation():

    parser = setup_arg_parser()
    args = parse(parser)
    validator.validate(args.schema, args.doc)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_validation()
