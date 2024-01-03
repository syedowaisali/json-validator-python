import re

from formatter import normalize_path
from validations.validation import Validation
from config.rules import rules
from utils.logger import logger


def converted_type(field):
    field_type = type(field)
    if field_type is str:
        return "string"
    elif field_type is int:
        return "integer"
    elif field_type is float:
        return "float"
    elif field_type is bool:
        return "bool"
    elif field_type is dict:
        return "object"
    elif field_type is list and len(field) > 0:
        first_item_type = type(field[0])
        if first_item_type is dict:
            return "object_array"
        elif first_item_type is str:
            return "string_array"


def valid_data_types():
    return ["string", "integer", "float", "bool", "object", "object_array", "string_array"]


def empty_list_check(filtered_key, impl):
    if filtered_key in impl.keys():
        return converted_type(impl[filtered_key]) is None
    return False


def matching_data_type(filtered_key, data_type, impl):
    return {converted_type(impl[filtered_key])}.intersection(data_type.split("|"))


class DetectInvalidTypeValidation():

    def validate(self, key, filtered_key, schema, impl, loc, schema_map):

        path = normalize_path(f"{loc}.{filtered_key}")

        # hold the constraint that needs to performed
        value = schema[key]

        # get the data-type from source value
        data_type = rules.get_data_type(value)

        # get binding from source value
        binding = rules.get_binding(value)

        # checking invalid data-type in schema
        for dt in data_type.split("|"):
            if dt not in valid_data_types():
                path = re.sub(r"[\[0-9\]]", "", path)
                logger.error(rules.get_invalid_data_type_message(path, dt))
                return

        # when object is array then it should have at least one child if binding is not enabled
        if not binding and empty_list_check(filtered_key, impl):
            logger.error(rules.get_at_least_one_message(path))
            return

        # checking target data-type should match with source data-type when binding is not enabled
        if not binding and filtered_key in impl.keys() and not matching_data_type(filtered_key, data_type, impl):
            target_data_type = converted_type(impl[filtered_key])
            valid_data_type = " or ".join([f"(bold){i}(end)" for i in data_type.split("|")])
            logger.error(rules.get_not_match_data_type_message(path, valid_data_type, target_data_type))
