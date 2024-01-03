import json

from formatter import normalize_path
from validations.validation import Validation
from config.rules import rules
from utils.logger import logger


class BindingValidation():

    def validate(self, key, filtered_key, schema, impl, loc, schema_map):

        path = normalize_path(f"{loc}.{filtered_key}")
        binding = rules.get_binding(schema[key])

        if binding:
            boundary_map = schema_map.get("__binder__")
            if boundary_map is None:
                logger.error(rules.get_main_boundary_not_found_message())
                return

            elif boundary_map.val.get(binding) is None:
                logger.error(rules.get_missing_boundary_message(binding))
                return

            elif filtered_key not in impl.keys():
                logger.error(f"{loc}.{filtered_key} not found")
                return

            bind_value = boundary_map.val.get(binding)
            bind_type = type(bind_value)

            if bind_type is str:
                self.__check_string_binding(bind_value, filtered_key, impl, path)

            elif bind_type is dict:
                self.__check_object_binding(binding, bind_value, filtered_key, impl, path)

            elif bind_type is list:
                self.__check_list_binding(binding, bind_value, filtered_key, impl, path)

    def __check_string_binding(self, bind_value, filtered_key, impl, path):

        target_value = impl[filtered_key]

        if type(target_value) is not str:
            logger.error(f"{path} should be string type.")

        elif len(bind_value) == 0 and len(target_value) != 0:
            logger.error(f"{path} should be empty.")

        elif bind_value != target_value:
            logger.error(f"{path} value should be (bold)(blue){bind_value}(end).")

    def __check_object_binding(self, binding, bind_value, filtered_key, impl, path):
        target_value = impl[filtered_key]

        if str(target_value) != str(bind_value):
            field = json.dumps(bind_value, indent=4)
            logger.error(f"(bold)(blue){path}(end) should be the same as the following object:\n{field}")

    def __check_list_binding(self, binding, bind_value, filtered_key, impl, path):
        target_value = impl[filtered_key]

        if len(bind_value) == 0:
            logger.error(f"{path} should be empty array")
            return

        if str(target_value) not in [str(json_str) for json_str in bind_value]:
            fields = json.dumps(bind_value, indent=4)
            logger.error(f"(bold)(blue){path}(end) should have one of the following value from (bold){binding}(end) array:\n \"{binding}\":{fields}")

