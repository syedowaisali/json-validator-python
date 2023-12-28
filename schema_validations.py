from abc import ABC, abstractmethod
from logger import logger
from rules import rules
from util import reserved_key, data_type as data_type_cls, converted_type
import schema_map


class SchemaValidation(ABC):

    @abstractmethod
    def validate(self, key, schema, path):
        pass


class CheckInvalidDateType(SchemaValidation):

    def validate(self, key, schema, path):

        # hold the constraint that needs to performed
        value = schema.get(key)

        if type(value.val) is dict:

            # get the data-type from source value
            data_type = value.data_type

            if type(data_type) is str:
                for dt in data_type.split("|"):
                    if dt not in data_type_cls.available_types():
                        logger.error(rules.get_invalid_data_type_message(path, dt))


class CheckBindings(SchemaValidation):

    def validate(self, key, schema, path):

        value = schema.get(key)

        if type(value.val) is dict:

            binding = value.binding

            if binding and type(binding) is str:
                binder = schema_map.schema_map.get("__binder__")

                if binder is None:
                    logger.error("(bold)(blue)__binder__(end) object is missing from schema.")
                    return

                if type(binder.val) is not dict:
                    logger.error("(bold)(blue)__binder__(end) type should be object.")
                    return

                if binder.get(binding) is None:
                    logger.error(f"(bold)(blue){binding}(end) binding is missing.")


class CheckKeyType(SchemaValidation):

    def validate(self, key, schema, path):
        schema_obj = schema.get(key)

        if key not in reserved_key.all_keys().keys() and type(schema_obj.val) is not dict:
            logger.error(f"(blue)(bold){path}(end) type should be (bold){{object}}(end) type")

        for child_key in schema_obj.val.keys():
            if child_key in reserved_key.all_keys().keys():
                if type(schema_obj.val.get(child_key)) is not reserved_key.all_keys().get(child_key):
                    logger.error(f"(bold){path}.{child_key}(end) should be (bold){converted_type(reserved_key.all_keys().get(child_key))}(end) type, but found (bold){converted_type(schema_obj.val.get(child_key))}(end) type.")


class AnalyzeKeys(SchemaValidation):

    def validate(self, key, schema, path):
        schema_obj = schema.get(key)

        if schema_obj.data_type != data_type_cls.string:

            string_type_support_keys = [reserved_key.min_length, reserved_key.max_length, reserved_key.allow_space,
                                        reserved_key.upper, reserved_key.lower]

            for support_support_key in string_type_support_keys:
                if support_support_key in schema_obj.val.keys():
                    logger.warn(f"(bold){path}.{support_support_key}(end) can be used only with (bold)string(end) data type.")


schema_validation_set = {
    CheckInvalidDateType(),
    CheckBindings(),
    CheckKeyType(),
    AnalyzeKeys()
}
