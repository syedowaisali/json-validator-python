import json

from utils.util import read_file
from core import validator


def run_validation():
    #schema = "invalid json content"
    schema = "./samples/sample_schema.json"
    #schema = json.loads(read_file("./samples/sample_schema.json"))
    #document = json.loads(read_file("./samples/sample.json"))
    document = "./samples/sample.json"
    validator.validate(schema, document)





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_validation()
