import json
import re
from abc import abstractmethod

from jsvl.utils.message_list import ml
from jsvl.utils.util import converted_type, combine, reserved_key, regex_keys
from jsvl.validations.validation import Validation
import jsvl.models.schema as schema_model


class DocValidation(Validation):

    def __init__(self):
        super().__init__()
        self.full_path = None

    def run(self, key, schema, doc, path, index, doc_is_dynamic):

        if type(doc) is None:
            return

        if schema.get(key).can_bypass:
            return

        self.full_path = combine(path, key)
        self.validate(key, schema, doc, path, index, doc_is_dynamic)

    @abstractmethod
    def validate(self, key, schema, doc, path, index, doc_is_dynamic):
        pass


class ValidateUnknownKeys(DocValidation):

    def validate(self, key, schema, doc, path, index, doc_is_dynamic):
        obj = schema.get(key)

        if obj is not None and obj.can_bypass:
            return False

        if obj is None:
            self.create_error(ml.unknown_key(path))


class ValidateRequiredFields(DocValidation):

    def validate(self, key, schema, doc, path, index, doc_is_dynamic):
        obj = schema.get(key)

        if obj.is_required and key not in doc.keys():
            self.create_error(ml.missing_required_key(self.full_path))


class ValidateDataEquality(DocValidation):

    def validate(self, key, schema, doc, path, index, doc_is_dynamic):

        obj = schema.get(key)

        if obj.binding is not None:
            return

        doc_val = doc.get(key)

        if doc_val is not None:
            expected_type_list = obj.data_type.split("|")
            actual_type = converted_type(doc_val)
            if actual_type not in expected_type_list:
                expected_types = " or ".join(expected_type_list)
                self.create_error(ml.data_inequality(self.full_path, expected_types, actual_type))


class ValidateDocBinding(DocValidation):

    def validate(self, key, schema, doc, path, index, doc_is_dynamic):

        # if __bind_regex__ is defined then ignore the __bind__ because __bind_regex__ has higher precedence
        if schema.get(key).regex_binding is not None:
            return

        binding = schema.get(key).binding
        actual_value = doc.get(key)

        if binding is None or actual_value is None:
            return

        binder = schema_model.schema_doc.get(reserved_key.binder)
        expected_value = binder.get(binding).val
        expected_type = type(expected_value)
        actual_type = type(actual_value)

        if expected_type in [str, int, float, bool]:
            self.__validate_str_binding(expected_value, actual_value, expected_type, actual_type)

        elif expected_type is dict:
            if str(expected_value) != str(actual_value):
                self.create_error(ml.invalid_binding_object(self.full_path, expected_value))

        elif expected_type is list:

            if len(expected_value) == 0:
                if actual_type is not list or len(actual_value) > 0:
                    self.create_error(ml.empty_array_binding(self.full_path))

            elif str(actual_value) not in [str(item) for item in expected_value]:
                fields = json.dumps(expected_value, indent=4)
                self.create_error(ml.invalid_binding_array_item(self.full_path, binding, fields))

    def __validate_str_binding(self, expected_value, actual_value, expected_type, actual_type):

        if actual_type is not expected_type:
            self.create_error(ml.invalid_data_type_with_bind(self.full_path, converted_type(expected_type),
                                                             converted_type(actual_type)))

        elif len(str(expected_value)) == 0 and len(str(actual_value)) > 0:
            self.create_error(ml.empty_binding(self.full_path))

        elif actual_value != expected_value:
            self.create_error(ml.invalid_data_type_with_bind(self.full_path, expected_value, actual_value))


class ValidateDocRegexBinding(DocValidation):

    def validate(self, key, schema, doc, path, index, doc_is_dynamic):
        regex_pattern = schema.get(key).regex_binding
        regex_error = schema.get(key).regex_error_message
        actual_value = doc.get(key)

        if regex_pattern is None or actual_value is None:
            return

        regex_pattern = str(regex_pattern)
        regex_pattern = regex_pattern if regex_keys.get(regex_pattern) is None else regex_keys.get(regex_pattern)

        if not re.match(regex_pattern, str(actual_value)):
            self.create_error(ml.regex_binding_error(self.full_path, regex_error))


class ValidateDocTextCase(DocValidation):

    def validate(self, key, schema, doc, path, index, doc_is_dynamic):
        actual_value = doc.get(key)
        case = schema.get(key).case

        if case is None or actual_value is None:
            return

        if case == reserved_key.upper and not str(actual_value).isupper():
            self.create_error(ml.uppercase_error(self.full_path))

        elif case == reserved_key.lower and not str(actual_value).islower():
            self.create_error(ml.lowercase_error(self.full_path))

        elif case == reserved_key.title and not str(actual_value).istitle():
            self.create_error(ml.titlecase_error(self.full_path))


class ValidateTextSpace(DocValidation):

    def validate(self, key, schema, doc, path, index, doc_is_dynamic):
        actual_value = doc.get(key)
        allow_space = schema.get(key).allow_space

        if allow_space is not None and actual_value is not None:
            if not bool(allow_space) and " " in actual_value:
                self.create_error(ml.space_error(self.full_path))


# create validation set
doc_validation_set = {
    ValidateRequiredFields(),
    ValidateDataEquality(),
    ValidateDocBinding(),
    ValidateDocRegexBinding(),
    ValidateDocTextCase(),
    ValidateTextSpace()
}

validate_unknown_keys = ValidateUnknownKeys()
