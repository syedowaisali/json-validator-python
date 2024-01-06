
root_object_path = "root_object_path"
schema_file_postfix = "schema_file_postfix"
enable_output_tags = "enable_output_tags"
formatted_output = "formatted_output"
enable_output_logs = "enable_output_logs"
enable_validation_source = "enable_validation_source"
allow_space = "allow_space"
min_length = "min_length"
max_length = "max_length"
min_value = "min_value"
max_value = "max_value"
case = "case"

configs = {

    # root object path
    root_object_path: "root object",

    # schema file postfix
    schema_file_postfix: "_schema",

    # control output tags
    enable_output_tags: True,

    # control output formatting
    formatted_output: True,

    # control output logs
    enable_output_logs: True,

    # show the source filter name at end of on each log
    enable_validation_source: False,

    # set default value of allow space on any text
    allow_space: True,

    # set default minimum length
    min_length: 0,

    # set default maximum length
    max_length: None,

    # set default minimum value
    min_value: 0,

    # set default maximum value
    max_value: None,

    # set default uppercase constraint
    case: None
}
