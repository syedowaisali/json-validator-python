class __DataType:
    def __init__(self):
        self.string = "string"
        self.integer = "integer"
        self.float = "float"
        self.bool = "bool"
        self.object = "object"
        self.object_array = "object_array"
        self.string_array = "string_array"
        self.integer_array = "integer_array"
        self.float_array = "float_array"
        self.bool_array = "bool_array"
        self.array = "array"

    def available_types(self) -> set:
        return {self.string,
                self.integer,
                self.float,
                self.bool,
                self.object,
                self.object_array,
                self.string_array,
                self.integer_array,
                self.float_array,
                self.bool_array,
                self.array}


data_type = __DataType()


class ReservedKey:

    def __init__(self):
        self.required = "__required__"
        self.data_type = "__data_type__"
        self.bind = "__bind__"
        self.allow_space = "__allow_space__"
        self.min_length = "__min_length__"
        self.max_length = "__max_length__"
        self.upper = "__upper__"
        self.lower = "__lower__"
        self.bypass = "__bypass__"
        self.depend_on = "__depend_on__"

    def all_keys(self) -> dict:
        return {self.required: bool,
                self.data_type: str,
                self.bind: str,
                self.allow_space: bool,
                self.min_length: int,
                self.max_length: int,
                self.upper: bool,
                self.lower: bool,
                self.bypass: bool,
                self.depend_on: str}


reserved_key = ReservedKey()


def remove_reserved_keys(doc):
    return [k for k in doc.keys() if k not in reserved_key.all_keys().keys()]


def matching_data_type(key, dt, target):
    return {converted_type(target[key])}.intersection(dt.split("|"))


def converted_type(field):
    field_type = field if type(field) is type else type(field)
    if field_type is str:
        return data_type.string
    elif field_type is int:
        return data_type.integer
    elif field_type is float:
        return data_type.float
    elif field_type is bool:
        return data_type.bool
    elif field_type is dict:
        return data_type.object
    elif field_type is list and len(field) > 0:
        first_item_type = type(field[0])

        for i in field:
            if type(i) is not first_item_type:
                return data_type.array

        if first_item_type is dict:
            return data_type.object_array
        elif first_item_type is str:
            return data_type.string_array
        elif first_item_type is int:
            return data_type.integer_array
        elif first_item_type is float:
            return data_type.float_array
        elif first_item_type is bool:
            return data_type.bool_array
