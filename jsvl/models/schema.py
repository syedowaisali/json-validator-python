from jsvl.utils.util import reserved_key


class Schema:

    def __init__(self, key, val):
        self.child_schema = {}
        self.val = val
        self.key = key

        self.is_required = False
        self.data_type = None
        self.allow_space = None
        self.min_value = None
        self.max_value = None
        self.min_length = None
        self.max_length = None
        self.case = None
        self.can_bypass = None
        self.binding = None
        self.regex_binding = None
        self.regex_error_message = None

        if type(val) is dict:
            self.is_required = val.get(reserved_key.required)
            self.data_type = val.get(reserved_key.data_type)
            self.allow_space = val.get(reserved_key.allow_space)
            self.min_value = val.get(reserved_key.min_value)
            self.max_value = val.get(reserved_key.max_value)
            self.min_length = val.get(reserved_key.min_length)
            self.max_length = val.get(reserved_key.max_length)
            self.case = val.get(reserved_key.case)
            self.can_bypass = val.get(reserved_key.bypass)
            self.binding = val.get(reserved_key.bind)
            self.regex_binding = val.get(reserved_key.bind_regex)
            self.regex_error_message = val.get(reserved_key.regex_error_message)

            keys = {k: v for (k, v) in val.items() if k not in reserved_key.all_keys().keys()}
            for new_key in keys:
                self.child_schema[new_key] = Schema(new_key, val.get(new_key))

    def get(self, key):
        return self.child_schema.get(key)

    def val_is_dict(self):
        return type(self.val) is dict


schema_doc = {}
