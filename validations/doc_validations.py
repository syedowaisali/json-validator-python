from abc import ABC, abstractmethod


from models.result import Error
from utils.util import matching_data_type, converted_type
from validations.validation import Validation


class DocValidation(Validation):

    @abstractmethod
    def validate(self, key, schema, doc, path, index, doc_is_dynamic):
        pass


class DetectInvalidKeys(DocValidation):

    def validate(self, key, schema, doc, path, index, doc_is_dynamic):

        if schema.get(key) is not None and schema.get(key).can_bypass:
            return False

        if schema.get(key) is None:

            self.create_error(
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
                self.create_error(f"(bold)(blue){path}(end) expect {valid_data_type} value, but found (bold)(red){target_data_type}(end) value.")



# create validation set
doc_validation_set = {
    DetectInvalidKeys(),
    DataTypeEqualityCheck()
}
