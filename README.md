## Features

### Features
- Detect invalid keys that are not defined in the schema.
- Control data type on each key.
- Allow required and optional fields.
- Allow bypass of the child value.
- Support value bindings.
- Allow spacing in value. note: this will work only **string** data-type, default is false.
- Control minimum and maximum length in **string** and **array** type.
- Control minimum and maximum value in **integer** and **float** type.
- Apply lower and upper case constraint on **string** type.
- Allow to create a custom extension library.

### Installation
```commandline
install pip jsvl
```
#### How to use
List of available commands

| Command        | Definition                                                                                                                                                                                                                           |
|----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| -h or --help   | for help                                                                                                                                                                                                                             |
| -s or --schema | provide a schema file path or url that will be used to analyze the input json<br />Note. if the provided input is a directory then you can also provide the schema path as a directory. All schema file should have _schema postfix. | 
| -i or --input  | provide a directory or a single json file path that you want to analyze.<br/>Note: if the input source is a directory then provided schema should be in a directory and should have the same name with _schema postfix.              |
| --disable-tags | pass this flag to disable the informative tags from output log.                                                                                                                                                                      |
| --plain-output | pass this flag to disable the formatted output.                                                                                                                                                                                      |

### How to use
**Command line**

Validate a single json document.
```commandline
~$ python jsvl -s /path/to/schema.json -i /path/to/document.json
```
Validate multiple documents with single schema.
```commandline
~$ python jsvl -s /path/to/schema.json -i /path/to/documents/
```
Validate multiple documents with multiple schema.
```commandline
~$ python jsvl -s /path/to/schema/ -i /path/to/documents/
```
Validate single or multiple documents with remote schema.
```commandline
~$ python jsvl -s http://www.yourdomain.com/schema.json -i /path/to/document.json
```
Disable informative tags from the output.
```commandline
~$ python jsvl -s path/to/schema.json -i /path/to/document.json --disable-tags
```
Remove formatting from the output.
```commandline
~$ python jsvl -s path/to/schema.json -i /path/to/document.json --plain-output
```

### In Project:

Import **validator** function from **jsvl.core** module and validate the document with multiple options.
```python
from jsvl.core import validator

# schema json
schema = "path/to/schema.json" or "path/to/all_schema_dir/" or "http://www.yourdomain.com/schema.json" or {}

# schema json
document = "path/to/document.json" or "path/to/all_documents_dir/" or {} or []

# perform validation
validator.validate(schema, document)
```
#### Control Configs:

```python
from jsvl.config import configs, enable_output_tags, formatted_output

# disable output tags. default is True
configs[enable_output_tags] = False

# disable formatted output. default is True
configs[formatted_output] = False
```
#### Register Custom Validation Filters:

You can register two types of validation filter.
1. **Schema Validation**

```python
from jsvl.validations import schema_validation_set, SchemaValidation

# creating custom filter class for schema validation
class CustomSchemaValidation(SchemaValidation):

    def validate(self, key, schema, path):
        print(key)

# register filter in schema validation set
schema_validation_set.add(CustomCheckForSchemaValidation())
```
2. **Document Validation**
```python
from jsvl.validations import doc_validation_set, DocValidation

# creating custom filter class for document validation
class CustomDocValidation(DocValidation):

    def validate(self, key, schema, doc, path, index, doc_is_dynamic):
        pass

# register filter in document validation set
doc_validation_set.add(CustomCheckForDocValidation())

```
#### User guide
Validating a sample document.

> **schema.json**
```json
{
    "cart": {
        "__data_type__": "object",
        "items*": {
            "__data_type__": "object_array",
            "title*": {},
            "description": {},
            "category*": {
              "__bind__": "category"
            },
            "provider*": {
              "__bind__": "company"
            },
            "quantity*": {
                "__data_type__": "integer",
                "__min_value__": 1
            },
            "discount*": {
                "__data_type__": "float",
                "__max_value__": 45.5
            }
        }
    },
    "__binder__": {
        "category": ["Health", "Fashion", "Lifestyle"],
        "company": "Uniliver"
    }
}
```

> **document.json**

```json
{
    "cart": {
      "items": [
        {
          "title": "Product 1",
          "description": "",
          "quantity": 1,
          "category": "Fashion",
          "provider": "Uniliver",
          "discount": 30.0
        },
        {
          "title": "Product 2",
          "quantity": 4,
          "category": "Health",
          "provider": "Uniliver",
          "discount": 0.0
        }
      ]
    }
}
```
### Available keywords:

|       Keyword        | Description                                                                                                                                                                                                         |   Default    |
|:--------------------:|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------:|
|       <b>*</b>       | Add asterisk keyword to end of the key to mark it as required.                                                                                                                                                      | ```false```  |
|        **~**         | Add tilde keyword to start of the key to ignore all the validation of immediate child.                                                                                                                              |  ```none```  |
| **\__data_type\__**  | Set data type on field, multiple data type could be supply using \| for example. ```string```\|  ```object```                                                                                                       | ```string``` |
| **\__alow_space\__** | Allow space on value, this keyword only applicable on ```string``` data type                                                                                                                                        |  ```true```  |
| **\__min_length\__** | Set minimum length of ```string``` and any type of ```array``` data type.                                                                                                                                           |  ```none```  |
| **\__max_length\__** | set maximum length of ```string``` and and type of ```array``` data type                                                                                                                                            |  ```none```  |
| **\__min_value\__**  | Set minimum value of ```integer``` and ```float``` data type.                                                                                                                                                       |  ```none```  |
| **\__max_value\__**  | Set maximum value of ```integer``` and ```float``` data type.                                                                                                                                                       |  ```none```  |
|   **\__upper\__**    | Apply uppercase constraint on value, applicable only ```string``` data type, and if both ```__upper__``` and ```__lower__``` constraints are defined then ```__upper__``` will take precedence over ```__lower__``` | ```false```  |
|   **\__lower\__**    | Apply lowercase constraint on value, applicable only ```string``` data type.                                                                                                                                        | ```false```  |
|   **\__bypass\__**   | Ignore the validation of imediate child.                                                                                                                                                                            |  ```none```  |
|    **\__bind\__**    | Bind value from defined set                                                                                                                                                                                         |  ```none```  |
|   **\__binder\__**   | This is a special keyword and will be used only root object of schema and where you can define binding valueset.                                                                                                    |   ```none```    |

### Data Types

- ```string```
- ```integer```
- ```float```
- ```bool```
- ```object```
- ```string_array```
- ```integer_array```
- ```float_array```
- ```bool_array```
- ```array```

# License

[Apache License 2.0](https://github.com/syedowaisali/json-validator-python/blob/main/LICENSE)