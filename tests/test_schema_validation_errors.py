from core.validator import validate
from models.result import Error, Warn
from utils.util import reserved_key, data_type_cls
from utils.message_list import ml
from validations.schema_validations import IrrelevantKeysCombinations, CheckInvalidValueType, CheckBindings, \
    CheckInvalidDataType


class TestSchemaValidationErrors:

    def setup_method(self):
        pass

    def test_check_invalid_data_type(self):
        schema = {
            "__data_type__": "number",
            "cart": {
                "location": {
                    "__data_type__": "s"
                },
                "primary": {
                    "__data_type__": ""
                },
                "secondary": {
                    "__data_type__": "j|string|9"
                }
            }
        }

        actual_errors = self.__apply_and_get_errors(schema, validation=CheckInvalidDataType)
        expected_errors = [
            ml.empty_value_in_data_type(f"cart.primary.{reserved_key.data_type}"),
            ml.found_invalid_data_type(f"cart.location.{reserved_key.data_type}", "s"),
            ml.found_invalid_data_type(f"cart.secondary.{reserved_key.data_type}", "j"),
            ml.found_invalid_data_type(f"cart.secondary.{reserved_key.data_type}", "9"),
            ml.found_invalid_data_type(reserved_key.data_type, "number"),
        ]

        self.__assert_result(actual_errors, expected_errors, 5)

    def test_missing_binder_object(self):
        schema = {
            "type": {
                reserved_key.bind: "roles"
            }
        }

        actual_errors = self.__apply_and_get_errors(schema, validation=CheckBindings)
        expected_errors = [ml.missing_binder_object()]

        self.__assert_result(actual_errors, expected_errors, 1)

    def test_missing_binding(self):
        schema = {
            "type": {
                reserved_key.bind: "roles"
            },
            "event": {
                reserved_key.bind: "location"
            },
            "__binder__": 4
        }

        actual_errors = self.__apply_and_get_errors(schema, validation=CheckBindings)
        expected_errors = [
            ml.missing_binding("roles"),
            ml.missing_binding("location"),
        ]

        self.__assert_result(actual_errors, expected_errors, 2)

    def test_invalid_value_type(self):
        schema = {
            "__required__": {},
            "__data_type__": 0,
            "__min_length__": True,
            "__max_length__": 0.0,
            "__min_value__": {},
            "__max_value__": [],
            "__allow_space__": 0,
            "__bind__": False,
            "__bypass__": "",
            "company": {
                "__required__": []
            }
        }

        actual_errors = self.__apply_and_get_errors(schema, validation=CheckInvalidValueType)
        expected_errors = [
            ml.invalid_value_type(reserved_key.required, data_type_cls.bool, data_type_cls.object),
            ml.invalid_value_type(reserved_key.data_type, data_type_cls.string, data_type_cls.integer),
            ml.invalid_value_type(reserved_key.min_length, data_type_cls.integer, data_type_cls.bool),
            ml.invalid_value_type(reserved_key.max_length, data_type_cls.integer, data_type_cls.float),
            ml.invalid_value_type(reserved_key.min_value, data_type_cls.float, data_type_cls.object),
            ml.invalid_value_type(reserved_key.max_value, data_type_cls.float, data_type_cls.array),
            ml.invalid_value_type(reserved_key.allow_space, data_type_cls.bool, data_type_cls.integer),
            ml.invalid_value_type(reserved_key.bind, data_type_cls.string, data_type_cls.bool),
            ml.invalid_value_type(reserved_key.bypass, data_type_cls.bool, data_type_cls.string),
            ml.invalid_value_type(f"company.{reserved_key.required}", data_type_cls.bool, data_type_cls.array),
        ]

        self.__assert_result(actual_errors, expected_errors, 10)

    def test_irrelevant_keys_combinations(self):
        schema = {
            "__data_type__": "integer",
            "name": {
                "__min_value__": 4,
                "__max_value__": 10
            },
            "age": {
                "__data_type__": "integer",
                "__allow_space__": True,
                "__min_length__": 3,
                "__max_length__": 5,
                "__upper__": True,
                "__lower__": True,
            },
            "__defaults__": {
                "__allow_space__": False,
                "__min_length__": 2,
                "__max_length__": 10,
                "__min_value__": 1,
                "__max_value__": 5,
                "__upper__": True,
                "__lower__": True,
                "hello": {}
            }
        }

        actual_errors = self.__apply_and_get_errors(schema, validation=IrrelevantKeysCombinations)
        expected_errors = [
            ml.root_key_support(),
            ml.key_support_with_number(f"name.{reserved_key.min_value}"),
            ml.key_support_with_number(f"name.{reserved_key.max_value}"),
            ml.key_support_with_string(f"age.{reserved_key.allow_space}"),
            ml.key_support_with_string(f"age.{reserved_key.min_length}"),
            ml.key_support_with_string(f"age.{reserved_key.max_length}"),
            ml.key_support_with_string(f"age.{reserved_key.upper}"),
            ml.key_support_with_string(f"age.{reserved_key.upper}"),
            ml.key_support_with_string(f"age.{reserved_key.lower}"),
            ml.key_support_for_defaults(f"{reserved_key.defaults}.hello"),
        ]

        self.__assert_result(actual_errors, expected_errors, 9)

    def test_min_max_value(self):
        schema = {
            "__min_length__": 3,
            "__max_length__": 2,
            "id": {
                "__min_length__": -1,
                "__max_length__": 10
            },
            "age": {
                "__data_type__": "integer",
                "__min_value__": 5,
                "__max_value__": 1
            },
            "__defaults__": {
                "__min_length__": -2,
                "__max_length__": -4,
                "__min_value__": 10,
                "__max_value__": 4
            }
        }

        actual_errors = self.__apply_and_get_errors(schema)
        expected_errors = [
            ml.invalid_min_max_value_or_length(reserved_key.min_length, reserved_key.max_length),
            ml.negative_min_length(f"id.{reserved_key.min_length}"),
            ml.invalid_min_max_value_or_length(f"age.{reserved_key.min_value}", f"age.{reserved_key.max_value}"),
            ml.negative_min_length(f"{reserved_key.defaults}.{reserved_key.min_length}"),
            ml.negative_or_zero_max_length(f"{reserved_key.defaults}.{reserved_key.max_length}"),
            ml.invalid_min_max_value_or_length(f"{reserved_key.defaults}.{reserved_key.min_length}", f"{reserved_key.defaults}.{reserved_key.max_length}"),
            ml.invalid_min_max_value_or_length(f"{reserved_key.defaults}.{reserved_key.min_value}", f"{reserved_key.defaults}.{reserved_key.max_value}"),
        ]

        self.__assert_result(actual_errors, expected_errors, 7)

    def __assert_result(self, actual_errors: list, expected_errors: list, expected_size: int = -1):

        if expected_size > -1:
            assert len(actual_errors) == expected_size

        for error in expected_errors:
            assert error in actual_errors

    def __apply_and_get_errors(self, schema, document=None, validation: object = None):

        if document is None:
            document = {}

        output = validate(schema, document)[0].schema_result

        if validation is not None:
            output = [result for result in output if type(result.validation) is validation]

        error_list = [result.message for result in output if type(result) is Error]
        return error_list
