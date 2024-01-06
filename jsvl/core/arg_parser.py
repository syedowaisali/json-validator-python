import argparse

import jsvl.config as cfg
from jsvl.utils.util import reserved_key


def setup_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="JSON Validator",
        description="JSON Validator is a feature-rich Python library designed to elevate the validation of JSON documents by offering an extensive schema-based validation system.",
    )

    parser.add_argument(
        "-s", "--schema",
        action="store",
        dest="schema",
        required=True,
        type=str,
        help="Provide a schema json, file or a directory path for validating the documents."
    )
    parser.add_argument(
        "-d", "--doc",
        dest="doc",
        required=True,
        type=str,
        help="Provide a document json, file or a directory path for validation."
    )
    parser.add_argument(
        "-csfp", "--change-schema-file-postfix",
        dest="schema_file_postfix",
        default="_schema",
        type=str,
        help="This argument will be used to change the schema file postfix name."
    )
    parser.add_argument(
        "--disable-tags",
        dest="enable_output_tags",
        action="store_false",
        help="Pass this flag to disable the output tags from logs."
    )
    parser.add_argument(
        "--plain-output",
        dest="formatted_output",
        action="store_false",
        help="Pass this flag to remove the formatting from logs."
    )
    parser.add_argument(
        "--disable-logs",
        dest="enable_output_logs",
        action="store_false",
        help="Pass this flag to disable all the logs."
    )
    parser.add_argument(
        "--show-validation-source",
        dest="enable_validation_source",
        action="store_true",
        help="Pass this flag to show the validation class name with logs."
    )
    parser.add_argument(
        "--tight-space",
        dest="allow_space",
        action="store_false",
        help="Pass this flag to disable the allow_space globally."
    )
    parser.add_argument(
        "-ml", "--min-length",
        dest="min_length",
        type=int,
        default=0,
        help="Set the minimum length globally, default is 0."
    )
    parser.add_argument(
        "-xl", "--max-length",
        dest="max_length",
        type=int,
        default=None,
        help="Set the maximum length globally, default is None."
    )
    parser.add_argument(
        "-mv", "--min-value",
        dest="min_value",
        type=float,
        default=0,
        help="Set the minimum value globally, default is 0."
    )
    parser.add_argument(
        "-xv", "--max-value",
        dest="max_value",
        type=float,
        default=None,
        help="Set the maximum value globally, default is None."
    )
    parser.add_argument(
        "-c", "--case",
        dest="case",
        type=str,
        choices=[reserved_key.upper, reserved_key.lower, reserved_key.title],
        default=None,
        help="Set the text constraints globally, default is None."
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 1.0.7"
    )

    return parser


def parse(parser) -> argparse.Namespace:
    args = parser.parse_args()
    cfg.configs[cfg.schema_file_postfix] = args.schema_file_postfix
    cfg.configs[cfg.enable_output_tags] = args.enable_output_tags
    cfg.configs[cfg.formatted_output] = args.formatted_output
    cfg.configs[cfg.enable_output_logs] = args.enable_output_logs
    cfg.configs[cfg.enable_validation_source] = args.enable_validation_source
    cfg.configs[cfg.allow_space] = args.allow_space
    cfg.configs[cfg.min_length] = args.min_length
    cfg.configs[cfg.max_length] = args.max_length
    cfg.configs[cfg.min_value] = args.min_value
    cfg.configs[cfg.max_value] = args.max_value
    cfg.configs[cfg.case] = args.case

    return args
