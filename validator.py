import re

from config import root_object_path
from formatter import normalize_path
from logger import logger
from rules import rules
import schema_map
from doc_validations import doc_validation_set
from schema_validations import schema_validation_set
from util import remove_reserved_keys, reserved_key


def filter_key(key):
    return key[:-1] if key.endswith("*") else key


def filter_schema_keys(schema):
    if type(schema) is not dict:
        return schema

    return {filter_key(k): v for k, v in schema.items()}


def analyze_schema(schema, loc):
    schema = filter_schema_keys(remove_reserved_keys(schema))

    if type(schema) is not dict:
        logger.error("schema should be valid json object")
        return

    for key in schema.keys():
        path = normalize_path(f"{loc}.{key}")

        # checking if the value is an object
        if type(schema.get(key)) is dict:

            for check_key in schema.get(key).keys():
                check_value = schema.get(key).get(check_key)

                # key must have an object type value if it's not a reserved one
                if type(check_value) is not dict and check_key not in reserved_key.all_keys().keys():
                    logger.error(f"key (bold)(blue){check_key}(end) should have object value in (bold){path}(end).")

                # data-type must be defined in parent object when the immediate child is an object
                elif type(check_value) is dict and not {"object", "object_array", "string_array"}.intersection(
                        rules.get_data_type(schema.get(key)).split("|")):
                    logger.error(
                        f"(bold)(blue){path}(end) should have one of the following data type: (bold)object, object_array, string_array, integer_array, float_array, bool_array(end)")

        # when binding is enable then the source object can't have any sibling keys
        if type(schema.get(key)) is dict and schema.get(key) is not None and schema.get(key).get(
                "__bind__") is not None:
            schema_path = re.sub(r"[\[0-9\]]", "", path)
            for invalid_key in [found_key for found_key in schema.get(key).keys() if found_key != "__bind__"]:
                logger.error(rules.get_invalid_sibling_message(invalid_key, schema_path))

        if type(schema[key]) is dict:
            child_schema = schema[key] if key in schema else schema

            # schema has __bind__ key then ignore the field check
            if child_schema.get("__bind__") is None:
                analyze_schema(child_schema, f"{loc}.{key}")

        # if type(schema[key]) is list:
        #   for index, item in enumerate(schema[key]):
        #      child_schema = schema[key] if type(item) is dict and key in schema else schema
        #      analyze_schema(child_schema, item, f"{loc}.{key}[{index}]")


def is_valid_json(doc) -> bool:
    return True


def apply_validation(key, schema, target, path):
    path = normalize_path(path)
    tgt_value = target.get(key)
    sch_value = schema.get(key) if schema is not None else None

    if key is None:
        for tgt_key in target.keys():
            apply_validation(tgt_key, schema, target, path)
        return

    for validation in doc_validation_set:
        if schema is not None and validation.validate(key, schema, target, normalize_path(f"{path}.{key}")) is not None:
            return

    if type(tgt_value) is dict:
        for child_key in tgt_value.keys():
            apply_validation(child_key, sch_value, tgt_value, normalize_path(f"{path}.{key}"))

    if type(tgt_value) is list:
        for index, item in enumerate(tgt_value):
            if type(item) is dict:
                for child_key in item.keys():
                    apply_validation(child_key, sch_value, item, f"{path}.{key}[{index}]")


def apply_schema_validation(key, schema, path):
    path = normalize_path(path)
    obj = schema.get(key)

    if key is None:
        for child_key in schema.keys():
            if child_key != "__binder__":
                apply_schema_validation(child_key, schema, path)
        return

    for validation in schema_validation_set:
        if validation.validate(key, schema, normalize_path(f"{path}.{key}")) is not None:
            return

    if type(obj.val) is dict:
        for child_key in remove_reserved_keys(obj.val):
            apply_schema_validation(child_key, obj.child_schema, f"{path}.{key}")


def update_schema(schema: dict, updated_schema: dict, key=None):
    if key is None:
        for s_key in schema.keys():
            update_schema(schema, updated_schema, s_key)
        return

    if type(schema.get(key)) is dict:
        field = schema[key].copy()

        data_type = "string" if field.get("__data_type__") is None else field.get("__data_type__")
        is_required = True if key.endswith("*") else False
        bypass = True if key.startswith("~") else False

        field["__data_type__"] = data_type
        field["__required__"] = is_required
        field["__bypass__"] = bypass

        updated_key = key[:-1] if key.endswith("*") else key
        updated_key = updated_key[1:] if updated_key.startswith("~") else updated_key

        updated_schema[updated_key] = field
        if (key.startswith("~") or key.endswith("*")) and key in updated_schema.keys():
            del updated_schema[key]

        for child_key in schema.get(key).keys():
            update_schema(schema.get(key), updated_schema.get(updated_key), child_key)
    else:
        updated_schema[key] = schema.get(key)


def validate(schema, target):
    # checking schema is valid json document
    is_valid_json(schema)

    # checking target is a valid json document
    is_valid_json(target)

    # remove * from keys and add __required__ key in field object
    updated_schema = {}
    update_schema(schema, updated_schema)

    for key in {key: val for (key, val) in updated_schema.items()}:
        schema_map.schema_map[key] = schema_map.Schema(key, updated_schema[key])

    # adding separator and initial info
    logger.line_separator()
    logger.info("(bold)Validating... schema.(end)", line_separator=True)

    # validating schema first then document
    apply_schema_validation(None, schema_map.schema_map, root_object_path)

    # if schema has no error then validate the target document with schema
    if len(logger.error_set) == 0:

        logger.success("(bold)(green)Schema validated.(end)", line_separator=True)
        logger.info("(bold)Validating... document.(end)", line_separator=True)

        apply_validation(None, schema_map.schema_map, target, root_object_path)

        if logger.has_no_error():
            logger.success("Document validated.")

    logger.line_separator()

    # analyze_schema(schema, "")

    # if len(logger.error_list) == 0:
    # detect_invalid_keys(schema, impl, "")
    # for key in schema.keys():
    # validate_key(key, schema, impl, "")
