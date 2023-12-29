from abc import ABC, abstractmethod

from utils.logger import logger
from config.rules import rules
from utils.util import matching_data_type, converted_type


class DocValidation(ABC):

    @abstractmethod
    def validate(self, key, schema, doc, path, index, doc_is_dynamic):
        pass


class DetectInvalidKeys(DocValidation):

    def validate(self, key, schema, doc, path, index, doc_is_dynamic):

        if schema.get(key) is not None and schema.get(key).can_bypass:
            return False

        if schema.get(key) is None:

            logger.error(
                f"unknown key (bold){key}(end) found in (bold)(blue){path}(end) remove it or add it in schema.")


class DataTypeEqualityCheck(DocValidation):

    def validate(self, key, schema, doc, path, index, doc_is_dynamic):
        value = schema.get(key)

        if value is not None:

            data_type = schema.get(key).data_type
            binding = schema.get(key).binding
            bypass = schema.get(key).can_bypass

            if binding is None and not bypass and key in doc.keys() and not matching_data_type(key, data_type, doc):
                target_data_type = converted_type(doc[key])
                valid_data_type = " or ".join([f"(bold){i}(end)" for i in data_type.split("|")])
                logger.error(rules.get_not_match_data_type_message(path, valid_data_type, target_data_type))


