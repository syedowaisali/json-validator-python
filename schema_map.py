from util import reserved_key


class Schema:

    def __init__(self, key, val):
        self.child_schema = {}
        self.val = val
        self.key = key
        self.is_required = key.endswith("*")
        self.keys = ""

        if type(val) is dict:
            self.data_type = val.get("__data_type__") #"string" if "__data_type__" not in val else val.get("__data_type__")
            self.can_bypass = val.get("__bypass__") #False if "__bypass__" not in val else val.get("__bypass__")
            self.binding = val.get("__bind__")

            keys = {k: v for (k, v) in val.items() if k not in reserved_key.all_keys().keys()}
            for new_key in keys:
                self.child_schema[new_key] = Schema(new_key, val.get(new_key))

    def get(self, key):
        return self.child_schema.get(key)


schema_map = {}
