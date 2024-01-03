import json
import os.path

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
        self.allow_space = "__allow_space__"
        self.min_length = "__min_length__"
        self.max_length = "__max_length__"
        self.min_value = "__min_value__"
        self.max_value = "__max_value__"
        self.upper = "__upper__"
        self.lower = "__lower__"
        self.bypass = "__bypass__"
        self.binder = "__binder__"
        self.defaults = "__defaults__"

    def all_keys(self) -> dict:
        return {self.required: bool,
                self.data_type: str,
                self.bind: str,
                self.allow_space: bool,
                self.min_length: int,
                self.max_length: int,
                self.min_value: float,
                self.max_value: float,
                self.upper: bool,
                self.lower: bool,
                self.bypass: bool,
                self.binder: dict,
                self.defaults: dict}


reserved_key = ReservedKey()


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
        return "array"


def remove_reserved_keys(doc):
    return [k for k in doc.keys() if k not in reserved_key.all_keys().keys()]


def is_find_data_type(source: str, target: list) -> bool:
    if type(source) is str:
        for dt in source.split("|"):
            if dt in target:
                return True

    return False


def is_exact_match_data_type(source: str, target: list) -> bool:
    for dt in source.split("|"):
        if dt not in target:
            return False

    return True


def matching_data_type(key, dt, target):
    return dt == data_type_cls.array and dt in converted_type(target[key]) or {
        converted_type(target[key])}.intersection(dt.split("|"))


def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read()


def read_rules(file_path="config/rules.json"):
    return read_file(file_path)


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