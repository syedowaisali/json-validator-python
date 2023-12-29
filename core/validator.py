import re

from config.rules import rules
from validations import doc_validation_set, schema_validation_set
from utils.logger import logger
from config import root_object_path
from models.schema import Schema, schema_doc

from utils.util import remove_reserved_keys, reserved_key, data_type_cls


def normalize_path(path: str, index: int = 0, doc_is_dynamic: bool = False) -> str:
    path = path.replace(root_object_path, "") if len(path) > len(root_object_path) else path
    path = path[1:] if path.startswith(".") else path
    return f"root[{index}]{path}" if doc_is_dynamic and "root" not in path else path


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


def apply_doc_validation(key, schema, doc, path, index, doc_is_dynamic):
    path = normalize_path(path, index, doc_is_dynamic)
    doc_value = doc.get(key)
    sch_value = schema.get(key) if schema is not None else None

    if key is None:
        for tgt_key in doc.keys():
            apply_doc_validation(tgt_key, schema, doc, path, index, doc_is_dynamic)
        return

    for validation in doc_validation_set:
        if schema is not None and validation.validate(key, schema, doc,
                                                      normalize_path(f"{path}.{key}", index, doc_is_dynamic), index,
                                                      doc_is_dynamic) is not None:
            return

    if type(doc_value) is dict:
        for child_key in doc_value.keys():
            apply_doc_validation(child_key, sch_value, doc_value,
                                 normalize_path(f"{path}.{key}", index, doc_is_dynamic), index, doc_is_dynamic)

    if type(doc_value) is list:
        for i, item in enumerate(doc_value):
            if type(item) is dict:
                for child_key in item.keys():
                    apply_doc_validation(child_key, sch_value, item, f"{path}.{key}[{i}]", index, doc_is_dynamic)


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


def is_dynamic_document(document: list) -> bool:
    first_item_type = type(document[0])
    is_dynamic_array = False

    for item in document:
        if type(item) is not first_item_type:
            is_dynamic_array = True

    return is_dynamic_array


def check_root_data_type(schema: dict, expected_type: str):
    data_type = schema.get(reserved_key.data_type)

    if data_type != expected_type:
        logger.error(
            f"expected (bold)(blue){expected_type}(end) type but found (bold)(blue){data_type}(end) type in the document.")


def validate_min_length(schema: dict, document: list):
    min_length = schema.get(reserved_key.min_length)
    if min_length is not None and len(document) < int(min_length):
        logger.error(f"the document could contain a minimum (bold){min_length}(end) item(s).")


def validate_max_length(schema: dict, document: list):
    max_length = schema.get(reserved_key.max_length)
    if max_length is not None and len(document) > int(max_length):
        logger.error(f"the document could contain a maximum (bold){max_length}(end) item(s).")


def run_doc_validations(schema: dict, document):
    # target document comprises on a single object
    if type(document) is dict:
        apply_doc_validation(None, schema_doc, document, root_object_path, 0, False)

    # target document comprises on a array
    elif len(document) > 0:

        # when document is dynamic
        if is_dynamic_document(document):
            check_root_data_type(schema, "array")

        # when document is not dynamic
        elif type(document[0]) is dict:
            for index, doc in enumerate(document):
                apply_doc_validation(None, schema_doc, doc, root_object_path, index, True)

        elif type(document[0]) is str:
            check_root_data_type(schema, data_type_cls.string_array)

        elif type(document[0]) is int:
            check_root_data_type(schema, data_type_cls.integer_array)

        elif type(document[0]) is float:
            check_root_data_type(schema, data_type_cls.float_array)

        elif type(document[0]) is bool:
            check_root_data_type(schema, data_type_cls.bool_array)

        validate_min_length(schema, document)
        validate_max_length(schema, document)

    else:
        logger.error("the document couldn't be empty.")


def validate(schema, document):
    # remove * from keys and add __required__ key in field object
    updated_schema = {}
    update_schema(schema, updated_schema)

    for key in {key: val for (key, val) in updated_schema.items()}:
        schema_doc[key] = Schema(key, updated_schema[key])

    # adding separator and initial info
    logger.line_separator()
    logger.info("(bold)Validating... schema.(end)", line_separator=True)

    # validating schema first then document
    apply_schema_validation(None, schema_doc, root_object_path)

    # if schema has no error then validate the target document with schema
    if len(logger.error_set) == 0:

        logger.success("(bold)(green)Schema validated.(end)", line_separator=True)
        logger.info("(bold)Validating... document.(end)", line_separator=True)

        run_doc_validations(schema, document)

        if logger.has_no_error():
            logger.success("Document validated.")

    if not logger.has_no_error():
        logger.error("Failed")

    logger.line_separator()


