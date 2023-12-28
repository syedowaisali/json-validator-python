
import reader
from validator import validate


def run_validation():
    schema = reader.read_profile_schema()
    implementation = reader.read_profile_config_sample()
    validate(schema, implementation)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_validation()

