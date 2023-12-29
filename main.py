import json

from utils.util import read_file
from core import validator


def run_validation():
    schema = json.loads(read_file("./samples/sample_schema.json"))
    document = json.loads(read_file("./samples/sample.json"))
    validator.validate(schema, document)


def is_valid_json(json_doc) -> bool:
    try:
        # json.loads(json_doc)
        pass
    except ValueError as err:
        # logger.error(err)
        return False
    return True


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_validation()
