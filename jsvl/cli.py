
from jsvl.core import validator
from jsvl.core.arg_parser import setup_arg_parser, parse


def run_validation():

    parser = setup_arg_parser()
    args = parse(parser)
    if args.doc is not None:
        validator.validate(args.schema, args.doc)
    else:
        out = []
        validator.apply_only_validation(args.schema, out)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_validation()
