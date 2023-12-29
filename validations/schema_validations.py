from abc import ABC, abstractmethod
from utils.logger import logger
from config.rules import rules
from utils.util import reserved_key, data_type_cls, converted_type, is_find_data_type, is_exact_match_data_type
from models.schema import schema_doc


class SchemaValidation(ABC):

    @abstractmethod
    def validate(self, key, schema, path):
        pass


class CheckInvalidDateType(SchemaValidation):

    def validate(self, key, schema, path):

        # hold the constraint that needs to performed
        value = schema.get(key)

        if type(value.val) is dict:
            self.__apply_validation(value.data_type, path)

        if key in reserved_key.all_keys().keys():
            self.__apply_validation(value.val, path)

    def __apply_validation(self, data_type, path):
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
                binder = schema_doc.get("__binder__")

                if binder is None:
                    logger.error("(bold)(blue)__binder__(end) object is missing from schema.")
                    return

                if type(binder.val) is not dict:
                    logger.error("(bold)(blue)__binder__(end) type should be object.")
                    return

                if binder.get(binding) is None:
                    logger.error(f"(bold)(blue){binding}(end) binding is missing.")


class CheckInvalidValueType(SchemaValidation):

    def validate(self, key, schema, path):
        schema_obj = schema.get(key)

        if key not in reserved_key.all_keys().keys() and type(schema_obj.val) is not dict:
            logger.error(f"(blue)(bold){path}(end) type should be (bold){{object}}(end) type")

        if type(schema_obj.val) is dict:
            for child_key in schema_obj.val.keys():
                if child_key in reserved_key.all_keys().keys():

                    value_type = type(schema_obj.val.get(child_key))
                    if value_type is not int and child_key != reserved_key.min_value and child_key != reserved_key.max_value:
                        if value_type is not reserved_key.all_keys().get(child_key):
                            logger.error(f"(bold){path}.{child_key}(end) should be (bold){converted_type(reserved_key.all_keys().get(child_key))}(end) type, but found (bold){converted_type(schema_obj.val.get(child_key))}(end) type.")

                    if value_type is float and not is_find_data_type(schema_obj.data_type, [data_type_cls.float]):
                        logger.error(
                             f"(bold){path}.{child_key}(end) should be (bold){schema_obj.data_type}(end) type, but found (bold){converted_type(value_type)}(end) type.")

                    if value_type is int and not is_find_data_type(schema_obj.data_type, [data_type_cls.integer]):
                        logger.error(
                            f"(bold){path}.{child_key}(end) should be (bold){schema_obj.data_type}(end) type, but found (bold){converted_type(value_type)}(end) type.")

        if key in reserved_key.all_keys().keys():
            if type(schema_obj.val) is not reserved_key.all_keys().get(key):
                logger.error(f"(bold){key}(end) should be (bold){converted_type(reserved_key.all_keys().get(key))}(end) type, but found (bold){converted_type(schema_obj.val)}(end) type.")


class IrrelevantKeysCombinations(SchemaValidation):

    def validate(self, key, schema, path):
        schema_obj = schema.get(key)
        val = schema_obj.val

        if type(val) is dict:

            data_type = schema_obj.data_type

            # check irrelevant keys when data type is not string
            if not is_find_data_type(data_type, [data_type_cls.string, data_type_cls.array, data_type_cls.string_array, data_type_cls.integer_array, data_type_cls.float_array, data_type_cls.bool_array, data_type_cls.object_array]):

                string_type_support_keys = [reserved_key.min_length, reserved_key.max_length, reserved_key.allow_space,
                                            reserved_key.upper, reserved_key.lower]

                for string_support_key in string_type_support_keys:
                    if string_support_key in val.keys():
                        logger.error(f"(bold){path}.{string_support_key}(end) can be used only with (bold)string(end) data type.")

            # check irrelevant keys when data type is not integer or float
            if not is_find_data_type(data_type, [data_type_cls.integer, data_type_cls.float]):
                number_type_support_keys = [reserved_key.min_value, reserved_key.max_value]
                for number_support_key in number_type_support_keys:
                    if number_support_key in val.keys():
                        logger.error(f"(bold){path}.{number_support_key}(end) can be used only with (bold)integer(end) or (bold)float(end) data type.")

            # check irrelevant keys when data type is not object or object_array
            if not is_find_data_type(data_type, [data_type_cls.object, data_type_cls.object_array, data_type_cls.array]):
                for i_key in val.keys():
                    if i_key not in reserved_key.all_keys().keys():
                        logger.error(f"(bold){path}.{i_key}(end) can be used only with (bold)object(end) or (bold)object_array(end) data type.")

        # check irrelevant keys when data type is not object or object_array
        if key == reserved_key.data_type and type(val) is str:
            array_and_object_data_types = [data_type_cls.object, data_type_cls.object_array, data_type_cls.array]
            if not is_exact_match_data_type(val, array_and_object_data_types):
                for i_key in schema.keys():
                    if i_key not in reserved_key.all_keys().keys():
                        logger.warn(f"(bold){i_key}(end) can be used only with (bold)object(end) or (bold)object_array(end) data type.")

            single_data_types = [data_type_cls.string, data_type_cls.integer, data_type_cls.float, data_type_cls.bool]
            if is_find_data_type(val, single_data_types):
                logger.error(
                    f"(bold)root object(end) data type can have (bold)object(end), (bold)object_array(end), (bold)string_array(end), (bold)integer_array(end), (bold)float_array(end) or (bold)bool_array(end) data type.")


class CheckMinMaxValue(SchemaValidation):

    def validate(self, key, schema, path):
        schema_obj = schema.get(key)
        val = schema_obj.val

        # checking on schema root object
        # __min_length__ cannot be negative
        if key == reserved_key.min_length:
            if type(schema_obj.val) is int and schema_obj.val < 0:
                logger.error(f"(bold)(blue){reserved_key.min_length}(end) cannot be negative.")

        # __max_length__ cannot be negative
        if key == reserved_key.max_length:
            if type(schema_obj.val) is int and schema_obj.val <= 0:
                logger.error(f"(bold)(blue){reserved_key.max_length}(end) cannot be negative or 0.")

        # checking __min_length__ and __max_length__
        if reserved_key.min_length in schema.keys() and reserved_key.max_length in schema.keys():
            if schema.get(reserved_key.min_length).val >= schema.get(reserved_key.max_length).val:
                logger.error(
                    f"(bold)(blue){reserved_key.min_length}(end) should be less than (blue)(bold){reserved_key.max_length}(end) value.")

        # checking on schema child object and nested child object
        if type(val) is dict:

            # __min_length__ cannot be negative
            if reserved_key.min_length in val.keys():
                if schema_obj.min_length < 0:
                    logger.error(f"(bold)(blue){path}.{reserved_key.min_length}(end) cannot be negative.")

            # __max_length__ cannot be negative
            if reserved_key.max_length in val.keys():
                if schema_obj.max_length <= 0:
                    logger.error(f"(bold)(blue){path}.{reserved_key.max_length}(end) cannot be negative or 0.")

            # checking __min_length__ and __max_length__
            if reserved_key.min_length in val.keys() and reserved_key.max_length in val.keys():
                if schema_obj.min_length >= schema_obj.max_length:
                    logger.error(f"(bold)(blue){path}.{reserved_key.min_length}(end) should be less than (blue)(bold){path}.{reserved_key.max_length}(end) value.")

            # checking __min_value and __max_value__
            if reserved_key.min_value in val.keys() and reserved_key.max_value in val.keys():
                if schema_obj.min_value >= schema_obj.max_value:
                    logger.error(f"(bold)(blue){path}.{reserved_key.min_value}(end) should be less than (blue)(bold){path}.{reserved_key.max_value}(end) value.")



