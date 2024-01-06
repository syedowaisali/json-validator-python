from jsvl.core.validator import validate
from jsvl.utils.util import reserved_key, data_type_cls, is_valid_regex
from jsvl.utils.message_list import ml
from jsvl.validations.schema_validations import ValidateKeysCombinations, ValidateValueType, ValidateSchemaBindings, \
    ValidateDataType, ValidateMinMaxValue, ValidateTextCase


class TestSchemaValidation:

    def test_validate_data_type(self):
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

        actual_logs = self.__validate(schema, validation=ValidateDataType)
        expected_logs = [
            ml.empty_value_in_data_type(f"cart.primary.{reserved_key.data_type}"),
            ml.found_invalid_data_type(f"cart.location.{reserved_key.data_type}", "s"),
            ml.found_invalid_data_type(f"cart.secondary.{reserved_key.data_type}", "j"),
            ml.found_invalid_data_type(f"cart.secondary.{reserved_key.data_type}", "9"),
            ml.found_invalid_data_type(reserved_key.data_type, "number"),
        ]

        self.__assert_result(actual_logs, expected_logs, 5)

    def test_validate_binder_object(self):
        schema = {
            "type": {
                reserved_key.bind: "roles"
            }
        }

        actual_logs = self.__validate(schema, validation=ValidateSchemaBindings)
        expected_logs = [ml.missing_binder_object()]

        self.__assert_result(actual_logs, expected_logs, 1)

    def test_validate_binding(self):
        schema = {
            "type": {
                reserved_key.bind: "roles"
            },
            "event": {
                reserved_key.bind: "location"
            },
            "email": {
                reserved_key.bind_regex: "[0-9]\\"
            },
            "__binder__": 4
        }

        actual_logs = self.__validate(schema, validation=ValidateSchemaBindings)
        expected_logs = [
            ml.missing_binding("roles"),
            ml.missing_binding("location"),
            ml.invalid_regex_binding(f"email.{reserved_key.bind_regex}", is_valid_regex(schema.get('email').get(reserved_key.bind_regex))),
        ]

        self.__assert_result(actual_logs, expected_logs, 3)

    def test_validate_value_type(self):
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

        actual_logs = self.__validate(schema, validation=ValidateValueType)
        expected_logs = [
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

        self.__assert_result(actual_logs, expected_logs, 10)

    def test_validate_keys_combinations(self):
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
                "__case__": "__lower__"
            },
            "__defaults__": {
                "__allow_space__": False,
                "__min_length__": 2,
                "__max_length__": 10,
                "__min_value__": 1,
                "__max_value__": 5,
                "__case__": "__upper__",
                "hello": {}
            }
        }

        actual_logs = self.__validate(schema, validation=ValidateKeysCombinations)
        expected_logs = [
            ml.key_support_with_object_and_array("name"),
            ml.key_support_with_object_and_array("age"),
            ml.key_support_with_number(f"name.{reserved_key.min_value}"),
            ml.key_support_with_number(f"name.{reserved_key.max_value}"),
            ml.key_support_with_string(f"age.{reserved_key.allow_space}"),
            ml.key_support_with_string(f"age.{reserved_key.min_length}"),
            ml.key_support_with_string(f"age.{reserved_key.max_length}"),
            ml.key_support_with_string(f"age.{reserved_key.case}"),
            ml.key_support_for_defaults(f"{reserved_key.defaults}.hello"),
        ]

        self.__assert_result(actual_logs, expected_logs, 9)

    def test_validate_min_max_value(self):
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

        actual_logs = self.__validate(schema, validation=ValidateMinMaxValue)
        expected_logs = [
            ml.invalid_min_max_value_or_length(reserved_key.min_length, reserved_key.max_length),
            ml.negative_min_length(f"id.{reserved_key.min_length}"),
            ml.invalid_min_max_value_or_length(f"age.{reserved_key.min_value}", f"age.{reserved_key.max_value}"),
            ml.negative_min_length(f"{reserved_key.defaults}.{reserved_key.min_length}"),
            ml.negative_or_zero_max_length(f"{reserved_key.defaults}.{reserved_key.max_length}"),
            ml.invalid_min_max_value_or_length(f"{reserved_key.defaults}.{reserved_key.min_length}", f"{reserved_key.defaults}.{reserved_key.max_length}"),
            ml.invalid_min_max_value_or_length(f"{reserved_key.defaults}.{reserved_key.min_value}", f"{reserved_key.defaults}.{reserved_key.max_value}"),
        ]

        self.__assert_result(actual_logs, expected_logs, 7)

    def test_validate_text_case(self):
        schema = {
            "first_name": {
                "__case__": "upper"
            },
            "last_name": {
                "__case__": "lower"
            },
            "full_name": {
                "__case__": "title"
            },
            "location": {
                "__data_type__": "object",
                "address": {
                    "__data_type__": "object",
                    "country": {
                        "__case__": "bad"
                    }
                }
            },
            "__defaults__": {
                "__case__": "unknown"
            }
        }

        actual_logs = self.__validate(schema, validation=ValidateTextCase)
        expected_logs = [
            ml.invalid_text_case(f"first_name.{reserved_key.case}", "upper"),
            ml.invalid_text_case(f"last_name.{reserved_key.case}", "lower"),
            ml.invalid_text_case(f"full_name.{reserved_key.case}", "title"),
            ml.invalid_text_case(f"location.address.country.{reserved_key.case}", "bad"),
            ml.invalid_text_case(f"{reserved_key.defaults}.{reserved_key.case}", "unknown"),
        ]

        self.__assert_result(actual_logs, expected_logs, 5)

    def __assert_result(self, actual_logs: list, expected_logs: list, expected_size: int = -1):

        if expected_size > -1:
            assert len(actual_logs) == expected_size

        for log in expected_logs:
            assert log in actual_logs

    def __validate(self, schema, document=None, validation: object = None):

        if document is None:
            document = {}

        output = validate(schema, document)[0].schema_result

        if validation is not None:
            output = [result for result in output if type(result.validation) is validation]

        logs = [result.message for result in output]
        return logs
