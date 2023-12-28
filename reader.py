import json

from logger import logger


def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read()


def read_rules(file_path="configs/rules.json"):
    return read_file(file_path)


def read_profile_schema():
    return json.loads(read_file("configs/profile_schema.json"))


def read_profile_config_sample():
    return json.loads(read_file("samples/profile_config.json"))
