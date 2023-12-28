from reader import read_rules
import json


class Rules:

    def __init__(self):
        self.rules = json.loads(read_rules()).get("rules")

    def get_required_message(self, source, target):
        return self.rules.get("__required__").get("missing_message").format(source=source, target=target)

    def get_at_least_one_message(self, source):
        return self.rules.get("__required__").get("at_least_one_message").format(source=source)

    def get_invalid_data_type_message(self, source, datatype):
        return self.rules.get("__data_type__").get("invalid").format(source=source, datatype=datatype)

    def get_not_match_data_type_message(self, source, valid_data_type, target_data_type):
        return self.rules.get("__data_type__").get("not_match").format(source=source, valid_data_type=valid_data_type, target_data_type=target_data_type)

    def get_invalid_key_message(self, path: str) -> str:
        return self.rules.get("invalid_key").format(path=path)

    def get_invalid_sibling_message(self, invalid_key, schema_path):
        return self.rules.get("invalid_sibling_key").format(invalid_key=invalid_key, schema_path=schema_path)

    def get_main_boundary_not_found_message(self):
        return self.rules.get("__binder__").get("not_found")

    def get_missing_boundary_message(self, binding):
        return self.rules.get("__binder__").get("missing").format(binding=binding)

    def is_required(self, key):
        return key.endswith("*")

    def get_data_type(self, field):
        return "string" if "__data_type__" not in field else field.get("__data_type__")

    def get_binding(self, field):
        return False if "__bind__" not in field else field.get("__bind__")

rules = Rules()
