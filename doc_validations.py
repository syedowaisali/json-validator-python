from abc import ABC, abstractmethod

from logger import logger
from rules import rules
from util import matching_data_type, converted_type


class Validation(ABC):

    @abstractmethod
    def validate(self, key, schema, target, path):
        pass


class DetectInvalidKeys(Validation):

    def validate(self, key, schema, target, path):

        if schema.get(key) is not None and schema.get(key).can_bypass:
            return False

        if schema.get(key) is None:
            logger.error(
                f"unknown key (bold){key}(end) found in (bold)(blue){path}(end) remove it or add it in schema.")


class DataTypeEqualityCheck(Validation):

    def validate(self, key, schema, target, path):
        value = schema.get(key)

        if value is not None:

            data_type = schema.get(key).data_type
            binding = schema.get(key).binding
            bypass = schema.get(key).can_bypass

            if binding is None and not bypass and key in target.keys() and not matching_data_type(key, data_type, target):
                target_data_type = converted_type(target[key])
                valid_data_type = " or ".join([f"(bold){i}(end)" for i in data_type.split("|")])
                logger.error(rules.get_not_match_data_type_message(path, valid_data_type, target_data_type))


# create validation set
doc_validation_set = {
    DetectInvalidKeys(),
    DataTypeEqualityCheck()
}
