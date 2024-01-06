import json
import os.path
import re

from config import enable_validation_source, configs
from models.result import Success, Info, Warn, Error
from utils.logger import logger


class __DataType:
    def __init__(self):
        self.string = "string"
        self.integer = "integer"
        self.float = "float"
        self.bool = "bool"
        self.object = "object"
        self.object_array = "object_array"
        self.string_array = "string_array"
        self.integer_array = "integer_array"
        self.float_array = "float_array"
        self.bool_array = "bool_array"
        self.array = "array"

    def available_types(self) -> set:
        return {self.string,
                self.integer,
                self.float,
                self.bool,
                self.object,
                self.object_array,
                self.string_array,
                self.integer_array,
                self.float_array,
                self.bool_array,
                self.array}


data_type_cls = __DataType()


class ReservedKey:

    def __init__(self):
        self.required = "__required__"
        self.data_type = "__data_type__"
        self.bind = "__bind__"
        self.bind_regex = "__bind_regex__"
        self.regex_error_message = "__rem__"
        self.allow_space = "__allow_space__"
        self.min_length = "__min_length__"
        self.max_length = "__max_length__"
        self.min_value = "__min_value__"
        self.max_value = "__max_value__"
        self.case = "__case__"
        self.upper = "__upper__"
        self.lower = "__lower__"
        self.title = "__title__"
        self.bypass = "__bypass__"
        self.binder = "__binder__"
        self.defaults = "__defaults__"

    def all_keys(self) -> dict:
        return {self.required: bool,
                self.data_type: str,
                self.bind: str,
                self.bind_regex: str,
                self.regex_error_message: str,
                self.allow_space: bool,
                self.min_length: int,
                self.max_length: int,
                self.min_value: float,
                self.max_value: float,
                self.case: str,
                self.bypass: bool,
                self.binder: dict,
                self.defaults: dict}


reserved_key = ReservedKey()

regex_keys = {
    "__email__": "[^@]+@[^@]+\.[^@]+",
    "__alpha__": "^[a-zA-Z]+$",
    "__numeric__": "^([\d]+)$",
    "__alphanumeric__": "[^A-Za-z0-9]+",
    "__ipv4__": "^(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
    "__ipv6__": "^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$"
}

def converted_type(field):
    field_type = field if type(field) is type else type(field)
    if field_type is str:
        return data_type_cls.string
    elif field_type is int:
        return data_type_cls.integer
    elif field_type is float:
        return data_type_cls.float
    elif field_type is bool:
        return data_type_cls.bool
    elif field_type is dict:
        return data_type_cls.object
    elif field_type is list and len(field) > 0:
        first_item_type = type(field[0])

        if first_item_type is list:
            return data_type_cls.array

        for i in field:
            if type(i) is not first_item_type:
                return data_type_cls.array

        if first_item_type is dict:
            return data_type_cls.object_array
        elif first_item_type is str:
            return data_type_cls.string_array
        elif first_item_type is int:
            return data_type_cls.integer_array
        elif first_item_type is float:
            return data_type_cls.float_array
        elif first_item_type is bool:
            return data_type_cls.bool_array
    elif field_type is list:
        return data_type_cls.array


def remove_reserved_keys(obj):
    return [k for k in obj.keys() if k not in reserved_key.all_keys().keys()]


def is_find_data_type(source: str, target: list) -> bool:
    if type(source) is str:
        for dt in source.split("|"):
            if dt in target:
                return True

    return False

def combine(path: str, key: str) -> str:
    full_path = f"{path}.{key}"
    full_path = full_path if len(path) > 0 else full_path[1:]
    return full_path[1:] if full_path.startswith(".") else full_path

def is_exact_match_data_type(source: str, target: list) -> bool:
    for dt in source.split("|"):
        if dt not in target:
            return False

    return True


def is_valid_regex(value: str):
    try:
        re.compile(value)
        return None
    except re.error as e:
        return e

def matching_data_type(key, dt, target):
    return dt == data_type_cls.array and dt in converted_type(target[key]) or {
        converted_type(target[key])}.intersection(dt.split("|"))


def is_valid_text_case(case) -> bool:
    return case in [reserved_key.upper, reserved_key.lower, reserved_key.title, None]

def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read()

def is_valid_file(file_path: str) -> bool:
    return os.path.isfile(str(file_path))


def is_valid_dir(dir_path: str) -> bool:
    return os.path.isdir(str(dir_path))


def is_valid_json(source) -> bool:
    try:
        if type(source) is not dict and type(source) is not list:
            json.loads(source)
        return True
    except:
        return False


def get_as_json(source):
    if type(source) is dict or type(source) is list:
        return source
    else:
        return json.loads(source)


def dump_log(output_list: list):

    for output in output_list:
        print()

        results = []
        results.extend(output.schema_result)
        results.extend(output.document_result)

        for result in results:
            msg = result.message
            if configs.get(enable_validation_source) is True:
                msg = f"{msg} (bold)(black){type(result.validation).__name__}(end)"

            result_type = type(result)

            if result_type is Success:
                logger.success(msg)

            elif result_type is Info:
                logger.info(msg)

            elif result_type is Warn:
                logger.warn(msg)

            elif result_type is Error:
                logger.error(msg)

        print()
        print("=-" * 50)