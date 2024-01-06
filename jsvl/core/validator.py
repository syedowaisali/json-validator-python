import json
import os.path
from glob import iglob
from typing import List

from ordered_set import OrderedSet

from jsvl.models.result import Output, Info, Error, Success, Warn

import jsvl.config as cfg
import jsvl.models.schema as schema_model
from jsvl.utils.message_list import ml
import jsvl.utils.util as util
from jsvl.validations.doc_validations import doc_validation_set, validate_unknown_keys
from jsvl.validations.schema_validations import schema_validation_set


def normalize_path(path: str, index: int = 0, doc_is_dynamic: bool = False) -> str:
    path = path.replace(cfg.root_object_path, "") if len(path) > len(cfg.root_object_path) else path
    path = path[1:] if path.startswith(".") else path
    return f"root[{index}]{path}" if doc_is_dynamic and "root" not in path else path


def apply_doc_unknown_keys_validation(key, schema, doc, path, index, doc_is_dynamic, output: OrderedSet):
    path = normalize_path(path, index, doc_is_dynamic)
    doc_value = doc.get(key)
    sch_value = schema.get(key) if schema is not None else None

    if key is None:
        for tgt_key in doc.keys():
            apply_doc_unknown_keys_validation(tgt_key, schema, doc, path, index, doc_is_dynamic, output)
        return

    if schema is not None and validate_unknown_keys.validate(key, schema, doc,
                                                  normalize_path(f"{path}.{key}", index, doc_is_dynamic), index,
                                                  doc_is_dynamic) is not None:
        return
    output.update(validate_unknown_keys.get_set())

    if type(doc_value) is dict:
        for child_key in doc_value.keys():
            apply_doc_unknown_keys_validation(child_key, sch_value, doc_value,
                                 normalize_path(f"{path}.{key}", index, doc_is_dynamic), index, doc_is_dynamic,
                                 output)

    if type(doc_value) is list:
        for i, item in enumerate(doc_value):
            if type(item) is dict:
                for child_key in item.keys():
                    apply_doc_unknown_keys_validation(child_key, sch_value, item, f"{path}.{key}[{i}]", index, doc_is_dynamic,
                                         output)

def apply_doc_validation(key, schema, doc, path, index, doc_is_dynamic, output: OrderedSet):
    path = f"root[{index}]{path}" if doc_is_dynamic and "root" not in path else path
    obj = schema.get(key)

    if key is None:
        for child_key in util.remove_reserved_keys(schema):
            apply_doc_validation(child_key, schema, doc, path, index, doc_is_dynamic, output)
        return

    #if type(doc) is list:
    #    for i, item in enumerate(doc):
    #        if type(item) is dict:
    #            apply_doc_validation(key, obj, item, f"{path}.{key}[{i}]", index, doc_is_dynamic, output)
    #    return

    for validation in doc_validation_set:
        if validation.run(key, schema, doc,
                          path, index,
                          doc_is_dynamic) is not None:
            return
        output.update(validation.get_set())

    if type(doc) is dict and obj.val_is_dict:

        for child_key in util.remove_reserved_keys(obj.val):

            doc_obj = doc.get(key)
            if type(doc_obj) is dict:
                apply_doc_validation(child_key, obj, doc_obj, f"{path}.{key}", index, doc_is_dynamic, output)

            if type(doc_obj) is list:
                for i, item in enumerate(doc_obj):
                    if type(item) is dict:
                        apply_doc_validation(child_key, obj, item, f"{path}.{key}[{i}]", index, doc_is_dynamic, output)


def apply_schema_validation(key, schema, path, output: OrderedSet):
    path = normalize_path(path)
    obj = schema.get(key)

    if key is None:
        for child_key in schema.keys():
            if child_key != util.reserved_key.binder:
                apply_schema_validation(child_key, schema, path, output)
        return

    for validation in schema_validation_set:
        if validation.validate(key, schema, normalize_path(f"{path}.{key}")) is not None:
            return

        output.update(validation.get_set())

    if type(obj.val) is dict:
        for child_key in util.remove_reserved_keys(obj.val):
            apply_schema_validation(child_key, obj.child_schema, f"{path}.{key}", output)


def prepare_schema(schema: dict, updated_schema: dict, key=None, defaults=None):
    if key is None:

        if util.reserved_key.data_type not in schema.keys():
            schema[util.reserved_key.data_type] = util.data_type_cls.object

        if util.reserved_key.defaults not in schema.keys():
            schema[util.reserved_key.defaults] = {
                util.reserved_key.allow_space: cfg.configs.get(cfg.allow_space),
                util.reserved_key.min_length: cfg.configs.get(cfg.min_length),
                util.reserved_key.max_length: cfg.configs.get(cfg.max_length),
                util.reserved_key.min_value: cfg.configs.get(cfg.min_value),
                util.reserved_key.max_value: cfg.configs.get(cfg.max_value),
                util.reserved_key.case: cfg.configs.get(cfg.case),
            }

        defaults = schema.get(util.reserved_key.defaults)

        if util.reserved_key.allow_space not in defaults:
            defaults[util.reserved_key.allow_space] = cfg.configs.get(cfg.allow_space)

        if util.reserved_key.min_length not in defaults:
            defaults[util.reserved_key.min_length] = cfg.configs.get(cfg.min_length)

        if util.reserved_key.max_length not in defaults:
            defaults[util.reserved_key.max_length] = cfg.configs.get(cfg.max_length)

        if util.reserved_key.min_value not in defaults:
            defaults[util.reserved_key.min_value] = cfg.configs.get(cfg.min_value)

        if util.reserved_key.max_value not in defaults:
            defaults[util.reserved_key.max_value] = cfg.configs.get(cfg.max_value)

        if util.reserved_key.case not in defaults:
            defaults[util.reserved_key.case] = cfg.configs.get(cfg.case)

        for s_key in schema.keys():
            prepare_schema(schema, updated_schema, s_key, defaults)
        return

    if type(schema.get(key)) is dict and key not in util.reserved_key.all_keys():
        field = schema[key].copy()

        data_type = util.data_type_cls.string if field.get(util.reserved_key.data_type) is None else field.get(
            util.reserved_key.data_type)
        is_required = True if key.endswith("*") else False
        bypass = True if key.startswith("~") else False

        field[util.reserved_key.data_type] = data_type
        field[util.reserved_key.required] = is_required
        field[util.reserved_key.bypass] = bypass

        if data_type == util.data_type_cls.string:
            allow_space = defaults.get(util.reserved_key.allow_space) if field.get(
                util.reserved_key.allow_space) is None else field.get(util.reserved_key.allow_space)
            min_length = defaults.get(util.reserved_key.min_length) if field.get(
                util.reserved_key.min_length) is None else field.get(util.reserved_key.min_length)
            max_length = defaults.get(util.reserved_key.max_length) if field.get(
                util.reserved_key.max_length) is None else field.get(util.reserved_key.max_length)
            case = defaults.get(util.reserved_key.case) if field.get(util.reserved_key.case) is None else field.get(
                util.reserved_key.case)

            field[util.reserved_key.allow_space] = allow_space
            field[util.reserved_key.min_length] = min_length
            field[util.reserved_key.max_length] = max_length
            field[util.reserved_key.case] = case

        if data_type == util.data_type_cls.integer:
            min_value = defaults.get(util.reserved_key.min_value) if field.get(
                util.reserved_key.min_value) is None else field.get(util.reserved_key.min_value)
            max_value = defaults.get(util.reserved_key.max_value) if field.get(
                util.reserved_key.max_value) is None else field.get(util.reserved_key.max_value)

            field[util.reserved_key.min_value] = min_value
            field[util.reserved_key.max_value] = max_value

        updated_key = key[:-1] if key.endswith("*") else key
        updated_key = updated_key[1:] if updated_key.startswith("~") else updated_key

        updated_schema[updated_key] = field
        if (key.startswith("~") or key.endswith("*")) and key in updated_schema.keys():
            del updated_schema[key]

        for child_key in schema.get(key).keys():
            prepare_schema(schema.get(key), updated_schema.get(updated_key), child_key, defaults)
    else:
        updated_schema[key] = schema.get(key)


def is_dynamic_document(document: list) -> bool:
    first_item_type = type(document[0])
    is_dynamic_array = False

    for item in document:
        if type(item) is not first_item_type:
            is_dynamic_array = True

    return is_dynamic_array


def check_root_data_type(schema: dict, expected_type: str, output_validation: OrderedSet):
    data_type = schema.get(util.reserved_key.data_type)

    if data_type != expected_type:
        output_validation.add(Error(ml.unmatched_data_type(expected_type, data_type)))


def validate_min_length(schema: dict, document: list, output_validation: OrderedSet):
    min_length = schema.get(util.reserved_key.min_length)
    if min_length is not None and len(document) < int(min_length):
        output_validation.add(Error(ml.min_length_item(min_length)))


def validate_max_length(schema: dict, document: list, output_validation: OrderedSet):
    max_length = schema.get(util.reserved_key.max_length)
    if max_length is not None and len(document) > int(max_length):
        output_validation.add(Error(ml.max_length_item(max_length)))


def run_doc_validations(schema: dict, document, doc_validation_output: OrderedSet):
    # target document comprises on a single object
    if type(document) is dict and len(document.keys()) > 0:
        apply_doc_validation(None, schema_model.schema_doc, document, "", 0, False,
                             doc_validation_output)

        apply_doc_unknown_keys_validation(None, schema_model.schema_doc, document, "", 0, False,
                             doc_validation_output)

    # target document comprises on a array
    elif len(document) > 0:

        # when document is dynamic
        if is_dynamic_document(document):
            check_root_data_type(schema, "array", doc_validation_output)

        # when document is not dynamic
        elif type(document[0]) is dict:
            for index, doc in enumerate(document):
                apply_doc_validation(None, schema_model.schema_doc, doc, "", index, True,
                                     doc_validation_output)
                apply_doc_unknown_keys_validation(None, schema_model.schema_doc, doc, "", index, True,
                                     doc_validation_output)

        elif type(document[0]) is str:
            check_root_data_type(schema, util.data_type_cls.string_array, doc_validation_output)

        elif type(document[0]) is int:
            check_root_data_type(schema, util.data_type_cls.integer_array, doc_validation_output)

        elif type(document[0]) is float:
            check_root_data_type(schema, util.data_type_cls.float_array, doc_validation_output)

        elif type(document[0]) is bool:
            check_root_data_type(schema, util.data_type_cls.bool_array, doc_validation_output)

        validate_min_length(schema, document, doc_validation_output)
        validate_max_length(schema, document, doc_validation_output)

    else:
        doc_validation_output.add(Error(ml.empty_document_object()))


def start_validation_process(schema: dict, document, schema_validation_output: OrderedSet,
                             doc_validation_output: OrderedSet):
    updated_schema = {}

    # remove * from keys and add __required__ key in field object
    # remove ~ from keys and add __bypass__ key in field object
    prepare_schema(schema, updated_schema)

    schema_model.schema_doc = {}
    for key in {key: val for (key, val) in updated_schema.items()}:
        schema_model.schema_doc[key] = schema_model.Schema(key, updated_schema[key])

    # adding separator and initial info
    schema_validation_output.add(Info(ml.validating_schema()))

    # validating schema first then document
    apply_schema_validation(None, schema_model.schema_doc, cfg.root_object_path, schema_validation_output)

    # if schema has no error then validate the target document with schema
    if len([result for result in schema_validation_output if type(result) is Error]) == 0:

        schema_validation_output.add(Success(ml.schema_successfully_validated()))
        schema_validation_output.add(Info(ml.validating_document()))

        run_doc_validations(schema, document, doc_validation_output)

        if len([result for result in doc_validation_output if type(result) is Error]) == 0:
            doc_validation_output.add(Success(ml.document_successfully_validated()))


def execute(schema, document, out: list):
    for validation in schema_validation_set:
        validation.init_log_set()

    for validation in doc_validation_set:
        validation.init_log_set()

    schema_validation_output = OrderedSet()
    doc_validation_output = OrderedSet()

    out.append(Output(schema_validation_output, doc_validation_output))

    schema_is_valid_json = util.is_valid_json(schema)
    schema_is_file = util.is_valid_file(schema)
    schema_is_dir = util.is_valid_dir(schema)

    if not schema_is_valid_json and not schema_is_file and not schema_is_dir:
        schema_validation_output.add(Error(ml.invalid_provided_schema()))
        return

    doc_is_valid_json = util.is_valid_json(document)
    doc_is_file = util.is_valid_file(document)
    doc_is_dir = util.is_valid_dir(document)

    if not doc_is_valid_json and not doc_is_file and not doc_is_dir:
        doc_validation_output.add(Error(ml.invalid_provided_document()))
        return

    list_of_schema = []

    if schema_is_valid_json:
        schema = util.get_as_json(schema)
        if type(schema) is not dict:
            schema_validation_output.add(Error(ml.schema_root_object()))
            return
        list_of_schema.append(schema)

    if schema_is_file:
        schema_validation_output.add(Info(ml.schema_file_loaded(schema)))
        file_content = util.read_file(schema)
        if not util.is_valid_json(file_content):
            schema_validation_output.add(Error(ml.invalid_schema_file(schema)))
            return

        schema = json.loads(file_content)
        list_of_schema.append(schema)

    if schema_is_dir:
        list_of_schema.clear()
        schema = schema if schema.endswith("/") else f"{schema}/"

        for file in iglob(f"{schema}**/*.json", recursive=True):
            list_of_schema.append(file)

    list_of_doc = []
    if doc_is_valid_json:
        document = util.get_as_json(document)
        list_of_doc.append(document)

    if doc_is_file:
        schema_validation_output.add(Info(ml.doc_file_loaded(document)))
        file_content = util.read_file(document)

        if not util.is_valid_json(file_content):
            doc_validation_output.add(Error(ml.invalid_doc_file(document)))
            return

        document = json.loads(file_content)
        list_of_doc.append(document)

    if doc_is_dir:
        list_of_doc.clear()
        document = document if document.endswith("/") else f"{document}/"

        for file in iglob(f"{document}**/*.json", recursive=True):
            list_of_doc.append(file)

        if len(list_of_doc) == 0:
            doc_validation_output.add(Info(ml.file_not_found(document)))
            return

        if len(list_of_schema) == 0:
            schema_validation_output.add(Error(ml.file_not_found(schema)))
            return

        for target_doc in list_of_doc:

            if type(schema) is dict:
                execute(schema, target_doc, out)

            elif schema == list_of_schema[0]:
                execute(schema, target_doc, out)
            else:
                schema_file_name = f"{os.path.splitext(os.path.basename(target_doc))[0]}{cfg.configs.get(cfg.schema_file_postfix)}"

                found_schema_file = None
                for schema_file_path in list_of_schema:
                    if f"/{schema_file_name}.json" in schema_file_path:
                        found_schema_file = schema_file_path
                        break

                if found_schema_file is not None:
                    execute(found_schema_file, target_doc, out)
                else:
                    schema_validation_output.add(Warn(ml.no_schema_found(schema_file_name)))

        return

    if type(document) is dict and (not schema_is_valid_json and not schema_is_file):
        schema_validation_output.add(Error(ml.unmatch_provided_schema_and_doc()))
        return

    if len(schema) == 0:
        schema_validation_output.add(Error(ml.empty_schema()))
        return

    start_validation_process(schema, document, schema_validation_output, doc_validation_output)


def validate(schema, document) -> List[Output]:
    output = []
    execute(schema, document, output)

    if cfg.configs.get(cfg.enable_output_logs):
        util.dump_log(output)

    return output
