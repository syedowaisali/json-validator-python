from abc import abstractmethod

from utils.util import reserved_key, data_type_cls, converted_type, is_find_data_type, is_exact_match_data_type, \
    is_valid_text_case, is_valid_regex, regex_keys
import models.schema as schema_model
from utils.message_list import ml
from validations.validation import Validation


class SchemaValidation(Validation):

    @abstractmethod
    def validate(self, key, schema, path):
        pass

    def is_default_object(self, key, schema, path):
        return path == reserved_key.defaults and key == reserved_key.defaults and type(schema.get(key).val) is dict

class ValidateDataType(SchemaValidation):

    def validate(self, key, schema, path):

        # hold the constraint that needs to performed
        value = schema.get(key)

        if type(value.val) is dict and key not in [reserved_key.defaults, reserved_key.binder]:
            self.__apply_validation(value.data_type, f"{path}.{reserved_key.data_type}")

        if key == reserved_key.data_type:
            self.__apply_validation(value.val, path)

    def __apply_validation(self, data_type, path):
        if type(data_type) is str:
            for dt in data_type.split("|"):
                if len(dt) == 0:
                    msg = ml.empty_value_in_data_type(path)
                    self.create_error(msg)
                elif dt not in data_type_cls.available_types():
                    msg = ml.found_invalid_data_type(path, dt)
                    self.create_error(msg)
        else:
            msg = ml.found_invalid_data_type(path)
            self.create_error(msg)


class ValidateSchemaBindings(SchemaValidation):

    def validate(self, key, schema, path):

        value = schema.get(key)
        binding = value.binding
        regex_binding = value.regex_binding

        if type(binding) is str:
            binder = schema_model.schema_doc.get("__binder__")

            if binder is None:
                self.create_error(ml.missing_binder_object())
                return

            if binder.get(binding) is None:
                self.create_error(ml.missing_binding(binding))

        if type(regex_binding) is str:
            regex_binding = self.resolve_pattern(regex_binding)
            regex_result = is_valid_regex(regex_binding)
            if regex_result is not None:
                self.create_error(ml.invalid_regex_binding(f"{path}.{reserved_key.bind_regex}", regex_result))

    def resolve_pattern(self, regex):
        return regex_keys.get(regex) if regex in regex_keys.keys() else regex


class ValidateValueType(SchemaValidation):

    def validate(self, key, schema, path):
        schema_obj = schema.get(key)

        if key not in reserved_key.all_keys().keys() and type(schema_obj.val) is not dict:
            self.create_error(f"{path} type should be {object} type")

        if type(schema_obj.val) is dict and type(schema_obj.val.get(reserved_key.data_type)) is str:
            for child_key in schema_obj.val.keys():

                if child_key in reserved_key.all_keys().keys():

                    value = schema_obj.val.get(child_key)

                    if child_key in [reserved_key.max_length, reserved_key.max_value, reserved_key.case] and value is None:
                        continue

                    if child_key in [reserved_key.min_value, reserved_key.max_value] and type(value) is int:
                        value = float(value)

                    if type(value) is not reserved_key.all_keys().get(child_key):
                        self.create_error(ml.invalid_value_type(f"{path}.{child_key}", converted_type(
                            reserved_key.all_keys().get(child_key)), converted_type(value)))

                    """
                     if value_type is not int and child_key != reserved_key.min_value and child_key != reserved_key.max_value:
                        if value_type is not reserved_key.all_keys().get(child_key):
                            self.create_error(ml.invalid_value_type(f"{path}.{child_key}", converted_type(
                                reserved_key.all_keys().get(child_key)), converted_type(schema_obj.val.get(child_key))))

                    if value_type is float and not is_find_data_type(schema_obj.data_type, [data_type_cls.float]):
                        self.create_error(ml.invalid_value_type(f"{path}.{child_key}", schema_obj.data_type,
                                                                converted_type(value_type)))

                    if value_type is int and not is_find_data_type(schema_obj.data_type, [data_type_cls.integer]):
                        self.create_error(ml.invalid_value_type(f"{path}.{child_key}", schema_obj.data_type,
                                                                converted_type(value_type)))
                    """

        if key in [reserved_key.max_length, reserved_key.max_value] and schema_obj.val is None:
            return

        if key in reserved_key.all_keys().keys():
            if type(schema_obj.val) is not reserved_key.all_keys().get(key):
                self.create_error(ml.invalid_value_type(f"{path}", converted_type(
                    reserved_key.all_keys().get(key)), converted_type(schema_obj.val)))

        if key == reserved_key.defaults and type(schema_obj.val) is dict:
            for child_key in schema_obj.val.keys():
                if child_key in [reserved_key.allow_space, reserved_key.min_length, reserved_key.max_length, reserved_key.min_value, reserved_key.max_value, reserved_key.case]:
                    value = schema_obj.val.get(child_key)

                    if child_key in [reserved_key.max_length, reserved_key.max_value] and value is None:
                        return

                    if child_key in [reserved_key.min_value, reserved_key.max_value] and type(value) is int:
                        value = float(value)

                    if type(value) is not reserved_key.all_keys().get(child_key):
                        self.create_error(ml.invalid_value_type(f"{path}.{child_key}", converted_type(
                            reserved_key.all_keys().get(child_key)), converted_type(value)))


class ValidateKeysCombinations(SchemaValidation):

    def validate(self, key, schema, path):
        schema_obj = schema.get(key)
        val = schema_obj.val

        if type(val) is dict and key != reserved_key.defaults:

            data_type = schema_obj.data_type

            # check irrelevant keys when data type is not string
            if not is_find_data_type(data_type, [data_type_cls.string, data_type_cls.array, data_type_cls.string_array,
                                                 data_type_cls.integer_array, data_type_cls.float_array,
                                                 data_type_cls.bool_array, data_type_cls.object_array]):

                string_type_support_keys = [reserved_key.min_length, reserved_key.max_length, reserved_key.allow_space,
                                            reserved_key.case]

                for string_support_key in string_type_support_keys:
                    if string_support_key in val.keys():
                        self.create_error(ml.key_support_with_string(f"{path}.{string_support_key}"))

            # check irrelevant keys when data type is not integer or float
            if not is_find_data_type(data_type, [data_type_cls.integer, data_type_cls.float]):
                number_type_support_keys = [reserved_key.min_value, reserved_key.max_value]
                for number_support_key in number_type_support_keys:
                    if number_support_key in val.keys():
                        self.create_error(ml.key_support_with_number(f"{path}.{number_support_key}"))

            # check irrelevant keys when data type is not object or object_array
            if not is_find_data_type(data_type,
                                     [data_type_cls.object, data_type_cls.object_array, data_type_cls.array]):
                for i_key in val.keys():
                    if i_key not in reserved_key.all_keys().keys():
                        self.create_error(ml.key_support_with_object_and_array(f"{path}.{i_key}"))

        # check irrelevant keys when data type is not object or object_array
        if key == reserved_key.data_type and type(val) is str:
            array_and_object_data_types = [data_type_cls.object, data_type_cls.object_array, data_type_cls.array]
            if not is_exact_match_data_type(val, array_and_object_data_types):
                for i_key in schema.keys():
                    if i_key not in reserved_key.all_keys().keys():
                        self.create_warn(ml.key_support_with_object_and_array(f"{i_key}"))

        # check if keys is default then check irrelevant keys
        if type(val) is dict and key == reserved_key.defaults:
            for child_key in val.keys():
                if child_key not in [reserved_key.allow_space, reserved_key.min_length, reserved_key.max_length, reserved_key.min_value, reserved_key.max_value, reserved_key.case]:
                    self.create_error(ml.key_support_for_defaults(f"{path}.{child_key}"))


class ValidateMinMaxValue(SchemaValidation):

    def validate(self, key, schema, path):

        schema_obj = schema.get(key)
        val = schema_obj.val

        # checking on schema root object
        # __min_length__ cannot be negative
        if key == reserved_key.min_length:
            if type(schema_obj.val) is int and schema_obj.val < 0:
                self.create_error(ml.negative_min_length(f"{reserved_key.min_length}"))

        # __max_length__ cannot be negative
        if key == reserved_key.max_length:
            if type(schema_obj.val) is int and schema_obj.val <= 0:
                self.create_error(ml.negative_or_zero_max_length(f"{reserved_key.max_length}"))

        # checking __min_length__ and __max_length__
        if reserved_key.min_length in schema.keys() and reserved_key.max_length in schema.keys():
            if type(schema_obj.val) is int and type(schema_obj.val) is int:
                if schema.get(reserved_key.min_length).val >= schema.get(reserved_key.max_length).val:
                    self.create_error(
                        ml.invalid_min_max_value_or_length(f"{reserved_key.min_length}", f"{reserved_key.max_length}"))

        # checking on schema child object and nested child object
        if type(val) is dict:

            # __min_length__ cannot be negative
            if reserved_key.min_length in val.keys():
                if type(schema_obj.min_length) is int and schema_obj.min_length < 0:
                    self.create_error(ml.negative_min_length(f"{path}.{reserved_key.min_length}"))

            # __max_length__ cannot be negative
            if reserved_key.max_length in val.keys():
                if type(schema_obj.max_length) is int and schema_obj.max_length <= 0:
                    self.create_error(ml.negative_or_zero_max_length(f"{path}.{reserved_key.max_length}"))

            # checking __min_length__ and __max_length__
            if reserved_key.min_length in val.keys() and reserved_key.max_length in val.keys():
                if type(schema_obj.min_length) is int and type(schema_obj.max_length) is int:
                    if schema_obj.min_length >= schema_obj.max_length:
                        self.create_error(ml.invalid_min_max_value_or_length(f"{path}.{reserved_key.min_length}",
                                                                             f"{path}.{reserved_key.max_length}"))

            # checking __min_value and __max_value__
            if reserved_key.min_value in val.keys() and reserved_key.max_value in val.keys():
                if type(schema_obj.min_value) is int and type(schema_obj.max_value) is int:
                    if schema_obj.min_value >= schema_obj.max_value:
                        self.create_error(ml.invalid_min_max_value_or_length(f"{path}.{reserved_key.min_value}",
                                                                             f"{path}.{reserved_key.max_value}"))


class ValidateTextCase(SchemaValidation):

    def validate(self, key, schema, path):

        obj = schema.get(key)

        if self.is_default_object(key, schema, path):
            if not is_valid_text_case(obj.case):
                self.create_error(ml.invalid_text_case(f"{path}.{reserved_key.case}", obj.case))
        elif not is_valid_text_case(obj.case):
            self.create_error(ml.invalid_text_case(f"{path}.{reserved_key.case}", obj.case))


# schema validation set
schema_validation_set = {
    ValidateDataType(),
    ValidateSchemaBindings(),
    ValidateValueType(),
    ValidateKeysCombinations(),
    ValidateMinMaxValue(),
    ValidateTextCase()
}
