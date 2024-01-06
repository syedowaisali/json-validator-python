import json

from core.validator import validate
from utils.util import reserved_key, data_type_cls
from utils.message_list import ml
from validations.doc_validations import ValidateRequiredFields, ValidateUnknownKeys, ValidateDataEquality, \
    ValidateDocBinding, ValidateDocRegexBinding, ValidateDocTextCase, ValidateTextSpace


class TestDocValidation:

    def test_validate_unknown_keys(self):
        schema = {
            "id": {},
            "location": {
                "__data_type__": "object"
            },
            "orders": {
                "__data_type__": "object_array",
                "origin": {
                    "__data_type__": "object",
                    "use": {}
                }
            }
        }

        doc = {
           "id": "12345",
            "name": "Michael",
            "age": 23,
            "location": {
                "address": {
                    "street": "11-B"
                }
            },
            "orders": [
                {
                    "origin": {
                        "source": "invy",
                        "use": "system"
                    }
                },
                {
                    "origin": {
                        "source": "sinvy"
                    }
                }
            ]
        }

        actual_logs = self.__validate(schema, doc, validation=ValidateUnknownKeys)
        expected_logs = [
            ml.unknown_key("name"),
            ml.unknown_key("age"),
            ml.unknown_key("location.address"),
            ml.unknown_key("orders[0].origin.source"),
            ml.unknown_key("orders[1].origin.source"),
        ]

        self.__assert_result(actual_logs, expected_logs, 5)

    def test_validate_required_fields(self):
        schema = {
            "id*": {},
            "address*": {
                "__data_type__": "object",
                "city*": {}
            },
            "orders*": {
                "__data_type__": "object_array",
                "id*": {},
                "title*": {},
                "detail": {},
                "location*": {
                    "__data_type__": "object",
                    "address*": {}
                }
            }
        }

        doc = {
            "style": "new",
            "orders": [
                {},
                {}
            ]
        }

        actual_logs = self.__validate(schema, doc, validation=ValidateRequiredFields)
        expected_logs = [
            ml.missing_required_key("id"),
            ml.missing_required_key("address"),
            ml.missing_required_key("orders[0].id"),
            ml.missing_required_key("orders[1].id"),
            ml.missing_required_key("orders[0].title"),
            ml.missing_required_key("orders[1].title"),
            ml.missing_required_key("orders[0].location"),
            ml.missing_required_key("orders[1].location"),
        ]

        self.__assert_result(actual_logs, expected_logs, 8)

    def test_validate_data_equality(self):
        schema = {
            "type": {},
            "info": {
                "__data_type__": "object",
                "serial": {
                    "__data_type__": "integer|float"
                },
                "can_use": {
                    "__data_type__": "bool"
                }
            },
            "records": {
                "__data_type__": "object_array",
                "id": {
                    "__data_type__": "integer",
                },
                "rating": {
                    "__data_type__": "float"
                }
            }
        }

        doc = {
            "type": 0,
            "info": {
                "serial": "one",
                "can_use": []
            },
            "records": [
                {
                    "id": True,
                    "rating": False
                },
                {
                    "id": 0.3,
                    "rating": "high"
                },
                {
                    "id": 2,
                    "rating": 3.0
                }
            ]
        }

        actual_logs = self.__validate(schema, doc, validation=ValidateDataEquality)
        expected_logs = [
            ml.data_inequality("type", data_type_cls.string, data_type_cls.integer),
            ml.data_inequality("info.serial", f"{data_type_cls.integer} or {data_type_cls.float}", data_type_cls.string),
            ml.data_inequality("info.can_use", data_type_cls.bool, data_type_cls.array),
            ml.data_inequality("records[0].id", data_type_cls.integer, data_type_cls.bool),
            ml.data_inequality("records[1].id", data_type_cls.integer, data_type_cls.float),
            ml.data_inequality("records[0].rating", data_type_cls.float, data_type_cls.bool),
            ml.data_inequality("records[1].rating", data_type_cls.float, data_type_cls.string),
        ]

        self.__assert_result(actual_logs, expected_logs, 7)

    def test_validate_binding(self):
        schema = {
            "country": {
                "__bind__": "countries"
            },
            "region": {
                "__bind__": "regions"
            },
            "board": {
                "__data_type__": "object",
                "score": {
                    "__bind__": "score"
                }
            },
            "model": {
                "__bind__": "structure"
            },
            "location": {
                "__bind__": "locations"
            },
            "pick": {
                "__bind__": "can_pick"
            },
            "__binder__": {
                "countries": "Pakistan",
                "score": 3,
                "structure": {
                    "floor": 4
                },
                "locations": ["KHI", "LHR", "ISB"],
                "regions": [],
                "can_pick": True
            }
        }

        doc = {
            "country": "Japan",
            "board": {
                "score": 1
            },
            "model": {
                "root": "low"
            },
            "location": "RWP",
            "region": "",
            "pick": 10
        }

        actual_logs = self.__validate(schema, doc, validation=ValidateDocBinding)
        fields = json.dumps(schema.get(reserved_key.binder).get("locations"), indent=4)
        expected_logs = [
            ml.invalid_data_type_with_bind("country", "Pakistan", "Japan"),
            ml.empty_array_binding("region"),
            ml.invalid_data_type_with_bind("board.score", 3, 1),
            ml.invalid_binding_object("model", "{'floor': 4}"),
            ml.invalid_data_type_with_bind("pick", "bool", "integer"),
            ml.invalid_binding_array_item("location", "locations", fields),
        ]

        self.__assert_result(actual_logs, expected_logs, 6)

    def test_validate_regex_bind(self):
        schema = {
            "id": {
                "__bind_regex__": "__numeric__",
                "__rem__": "should be contains only number"
            },
            "name": {
                "__data_type__": "object",
                "first_name": {
                    "__bind_regex__": "__alpha__",
                    "__rem__": "should contains only alphabets"
                },
                "last_name": {
                    "__bind_regex__": "__alpha_numeric__"
                }
            },
            "email": {
                "__bind_regex__": "__email__",
                "__rem__": "is not valid"
            },
            "parent_email": {
                "__bind_regex__": "__email__"
            },
            "ipv4": {
                "__bind_regex__": "__ipv4__",
            },
            "ipv6": {
                "__bind_regex__": "__ipv6__",
                "__rem__": "should be a valid IPV6"
            },
            "date": {
                "__bind_regex__": "^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}$",
                "__rem__": "should be like this DD/MM/YYYY"
            },
            "last_date": {
                "__bind_regex__": "^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}$"
            }
        }

        doc = {
            "id": "dash",
            "name": {
                "first_name": "Rocky 15",
                "last_name": "@"
            },
            "email": "rock@@gamil.com",
            "parent_email": "dev@gmail.com",
            "ipv4": "192.168.1",
            "ipv6": "3.223.4.5",
            "date": "05-01-2023",
            "last_date": "05/01/2023"
        }

        actual_logs = self.__validate(schema, doc, validation=ValidateDocRegexBinding)
        expected_logs = [
            ml.regex_binding_error("id", "should be contains only number"),
            ml.regex_binding_error("name.first_name", "should contains only alphabets"),
            ml.regex_binding_error("name.last_name"),
            ml.regex_binding_error("email", "is not valid"),
            ml.regex_binding_error("ipv4"),
            ml.regex_binding_error("ipv6", "should be a valid IPV6"),
            ml.regex_binding_error("date", "should be like this DD/MM/YYYY"),
        ]

        self.__assert_result(actual_logs, expected_logs, 7)

    def test_validate_text_case(self):
        schema = {
            "name": {
                "__case__": "__upper__"
            },
            "username": {
                "__case__": "__lower__"
            },
            "address": {
                "__data_type__": "object",
                "city": {
                    "__case__": "__title__"
                },
                "country": {
                    "__case__": "__title__"
                }
            }
        }

        doc = {
            "name": "owais",
            "username": "SyedOwaisAli",
            "address": {
                "city": "Karachi",
                "country": "pakistan"
            }
        }

        actual_logs = self.__validate(schema, doc, validation=ValidateDocTextCase)
        expected_logs = [
            ml.uppercase_error("name"),
            ml.lowercase_error("username"),
            ml.titlecase_error("address.country"),
        ]

        self.__assert_result(actual_logs, expected_logs, 3)

    def test_validate_text_space(self):
        schema = {
            "full_name": {
                "__allow_space__": False
            },
            "interest": {}
        }

        doc = {
            "full_name": "Bill G.",
            "interest": "Learn Engineering",
        }

        actual_logs = self.__validate(schema, doc, validation=ValidateTextSpace)
        expected_logs = [
            ml.space_error("full_name"),
        ]

        self.__assert_result(actual_logs, expected_logs, 1)

    def __assert_result(self, actual_logs: list, expected_logs: list, expected_size: int = -1):

        if expected_size > -1:
            assert len(actual_logs) == expected_size

        for log in expected_logs:
            assert log in actual_logs

    def __validate(self, schema, document, validation: object = None):

        output = validate(schema, document)[0].document_result

        if validation is not None:
            output = [result for result in output if type(result.validation) is validation]

        logs = [result.message for result in output]
        return logs
