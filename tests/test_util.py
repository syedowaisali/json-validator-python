from utils.util import converted_type


def test_converted_type():
    assert converted_type("") == "string"
    assert converted_type(1) == "integer"
    assert converted_type(1.0) == "float"
    assert converted_type(True) == "bool"
    assert converted_type({}) == "object"
    assert converted_type([""]) == "string_array"
    assert converted_type([1]) == "integer_array"
    assert converted_type([1.0]) == "float_array"
    assert converted_type([False]) == "bool_array"
    assert converted_type([{}]) == "object_array"
    assert converted_type([{}, 1]) == "array"
    assert converted_type(["", 1, False]) == "array"
    assert converted_type(["", 1, 0.2]) == "array"
    assert converted_type(["", 1, 0.2, {}, False]) == "array"
    assert converted_type(["", "", 0.2, {}, False]) == "array"
    assert converted_type([[]]) == "array"
