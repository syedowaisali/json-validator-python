import re

from validations.validation import Validation
from config.rules import rules
from utils.logger import logger


class RequiredFieldValidation(Validation):

    def validate(self, key, filtered_key, schema, impl, loc, schema_map):

        # when key is required but not found in target implementation then simply log the error and return
        if self.__is_required(f"{loc}.{filtered_key}"[1:], schema_map) and filtered_key not in impl:
            target = "main object." if loc == "" else loc[1:]
            logger.error(rules.get_required_message(filtered_key, target))

    def __is_required(self, path, schema_map):
        path = re.sub(r"[\[0-9\]]", "", path).split(".")
        return self.__check_required_chain(0, path, schema_map)

    def __check_required_chain(self, index, path_list, schema_dict):
        obj = schema_dict.get(path_list[index])

        if obj is None:
            obj = schema_dict.get(path_list[index] + "*")

        if not obj.is_required:
            return False

        index += 1

        return self.__check_required_chain(index, path_list, obj.child_schema) if index < len(path_list) else True
