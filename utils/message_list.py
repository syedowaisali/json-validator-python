
class MessageList:

    # schema validation errors ----------------------------------------------------------------------

    def unmatched_data_type(self, expected_type, actual_type):
        return f"Expected {expected_type} type but found {actual_type} type."

    def min_length_item(self, expected_min_length):
        return f"The document should contain minimum {expected_min_length} item(s)."

    def max_length_item(self, expected_max_length):
        return f"The document should contain maximum {expected_max_length} item(s)."

    def empty_document(self):
        return "The document couldn't be empty."

    def validating_schema(self):
        return "Validating... schema."

    def validating_document(self):
        return "Validating... document."

    def schema_successfully_validated(self):
        return "Schema validated."

    def document_successfully_validated(self):
        return "Document validated."

    def validation_failed(self):
        return "Validation failed."

    def invalid_provided_schema(self):
        return "Provided schema is not valid."

    def invalid_provided_document(self):
        return "Provided document is not valid."

    def schema_root_object(self):
        return "In schema root object should be a json object."

    def schema_file_loaded(self, schema_file):
        return f"Loaded schema from: {schema_file}"

    def invalid_schema_file(self, schema_file):
        return f"Schema: {schema_file} is not a valid json file."

    def doc_file_loaded(self, doc_file):
        return f"Loaded document from: {doc_file}."

    def invalid_doc_file(self, doc_file):
        return f"Document: {doc_file} is not a valid json file."

    def file_not_found(self, dir):
        return f"No json file found in {dir}."

    def no_schema_found(self, schema_file_name):
        return f"{schema_file_name}.json not found."

    def unmatch_provided_schema_and_doc(self):
        return "if the provided document is a json content then the provided schema should also be json content or a single schema file."

    def empty_value_in_data_type(self, path):
        return f"{path} should not be empty."

    def found_invalid_data_type(self, path, invalid_data_type = ""):
        return f"{path} has invalid data type {invalid_data_type}. See the available data types here https://github.com/syedowaisali/json-validator-python?tab=readme-ov-file#support-data-types"

    def missing_binder_object(self):
        return "__binder__ object is missing from schema."

    def empty_schema(self):
        return "Schema couldn't be empty."

    def missing_binding(self, binding):
        return f"{binding} binding is missing."

    def invalid_binder_type(self):
        return "__binder__ type should be object."

    def invalid_value_type(self, path, expected_type, actual_type):
        return f"{path} should be {expected_type} value, but found {actual_type} value."

    def key_support_with_string(self, path):
        return f"{path} can be used only with string data type."

    def key_support_with_number(self, path):
        return f"{path} can be used only with integer or float data type."

    def key_support_with_object_and_array(self, path):
        return f"{path} can be used only with object or object_array data type."

    def key_support_for_defaults(self, path):
        return f"{path} cannot be used in defaults. See the available keywords here https://github.com/syedowaisali/json-validator-python?tab=readme-ov-file#available-keywords"

    def root_key_support(self):
        return "root object data type could be object, object_array, string_array, integer_array, float_array or bool_array data type."

    def invalid_min_max_value_or_length(self, min_value_path, max_value_path):
        return f"{min_value_path} should be less than {max_value_path} value."

    def negative_min_length(self, path):
        return f"{path} cannot be negative."

    def negative_or_zero_max_length(self, path):
        return f"{path} cannot be negative or 0."

    # document validation errors ----------------------------------------------------------------------


ml = MessageList()