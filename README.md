# JSON Validator

[![GitHub license](https://img.shields.io/github/license/syedowaisali/json-validator-python)](https://github.com/syedowaisali/json-validator-python/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/syedowaisali/json-validator-python)](https://github.com/syedowaisali/json-validator-python/issues)
[![GitHub stars](https://img.shields.io/github/stars/syedowaisali/json-validator-python)](https://github.com/syedowaisali/json-validator-python/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/syedowaisali/json-validator-python)](https://github.com/syedowaisali/json-validator-python/network)

**JSON Validator** is a feature-rich Python library designed to elevate the validation of JSON documents by offering an extensive schema-based validation system. It empowers developers to define custom schemas, providing fine-grained control over the structure, data types, and constraints of their JSON data.

## Outline

- [Overview](#overview)
- [Key Features](#key-features)
   - [Schema Definition](#1-schema-definition)
   - [Flexible Data Type Validation](#2-flexible-data-type-validation)
   - [Key Presence Validation](#3-key-presence-validation)
   - [Required and Optional Fields](#4-required-and-optional-fields)
   - [Child Value Bypass](#5-child-value-bypass)
   - [Value Bindings](#6-value-bindings)
   - [String Value Constraints](#7-string-value-constraints)
   - [Numeric Value Constraints](#8-numeric-value-constraints)
   - [Case Constraints](#9-case-constraints)
   - [Spacing in String Values](#10-spacing-in-string-values)
   - [Custom Extension Library](#11-custom-extension-library)
- [Installation](#installation)
- [Command line guide](#command-line-guide)
- [How to use](#how-to-use)
- [Use in Project](#use-in-project)
- [Control Configs](#control-configs)
- [Register Custom Validation Filters](#register-custom-validation-filters)
- [User guide](#user-guide)
- [Available Keywords](#available-keywords)
- [Support Data Types](#support-data-types)
- [License](#license)

## Overview

**JSON Validator** is a feature-rich Python library designed to elevate the validation of JSON documents by offering an extensive schema-based validation system. It empowers developers to define custom schemas, providing fine-grained control over the structure, data types, and constraints of their JSON data.

## Key Features

### 1. Schema Definition

Define a schema for your JSON documents, specifying keys, data types, and constraints. The schema acts as a blueprint for validation.

### 2. Flexible Data Type Validation

Control the data types of each key in your JSON document. Enforce strict typing or allow flexibility based on your requirements.

### 3. Key Presence Validation

Detect and handle invalid keys in your JSON document that are not defined in the schema, ensuring data integrity.

### 4. Required and Optional Fields

Designate which fields are required and which are optional, guiding users in creating valid JSON documents.

### 5. Child Value Bypass

Allow bypassing the validation of child values, providing flexibility when certain sections of the JSON document don't require strict validation.

### 6. Value Bindings

Support value bindings to establish relationships between different parts of the JSON document, enhancing the expressiveness of your schemas.

### 7. String Value Constraints

Control the minimum and maximum length of string values, applying constraints to ensure data meets specific length requirements.

### 8. Numeric Value Constraints

Define minimum and maximum values for integer and float types, allowing precise control over the numeric range of your data.

### 9. Case Constraints

Apply case constraints to string types, specifying whether they should be in lower, upper, or mixed case.

### 10. Spacing in String Values

Optionally allow spacing in string data types, enhancing readability in scenarios where formatted text is essential.

### 11. Custom Extension Library

Extend the functionality of the library by creating custom extensions, tailoring the validation process to your unique needs.

### Installation
```commandline
install pip jsvl
```
### Command line guide
List of available commands

| Command                  | Definition                                                                                                                                                                                                                            |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| -h or --help             | for help.                                                                                                                                                                                                                             |
| -s or --schema           | provide a schema file path or URL that will be used to analyze the input json<br />Note. if the provided input is a directory then you can also provide the schema path as a directory. All schema files should have _schema postfix. | 
| -i or --input            | provide a directory or a single json file path that you want to analyze.<br/>Note: if the input source is a directory then provided schema should be in a directory and should have the same name with _schema postfix.               |
| --disable-tags           | pass this flag to disable the informative tags from the output log.                                                                                                                                                                   |
| --plain-output           | pass this flag to disable the formatted output.                                                                                                                                                                                       |
| --schema-file-postfix    | provide a schema file postfix if schema source is directory default is "_schema".                                                                                                                                                     |
| --show-validation-source | pass this flag will show the actual source of validation to end of the each log.                                                                                                                                                      |

### How to use
**Command line**

Validate a single json document.
```commandline
~$ python jsvl -s /path/to/schema.json -i /path/to/document.json
```
Validate multiple documents with a single schema.
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

### Use in Project:

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
### Control Configs:

```python
from jsvl.config import configs, enable_output_tags, formatted_output

# disable output tags. default is True
configs[enable_output_tags] = False

# disable formatted output. default is True
configs[formatted_output] = False
```
### Register Custom Validation Filters:

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
### User guide
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

|        Keyword         | Description                                                                                                                                                                                                                                                                                                                                                                                                                                             |   Default    |                           Scope                           |
|:----------------------:|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------:|:---------------------------------------------------------:|
|        <b>*</b>        | Add an asterisk keyword to the end of the key to mark it as required.                                                                                                                                                                                                                                                                                                                                                                                   | ```false```  | Could be add on any keyword. Excluded `reserved keywords` |
|         **~**          | Add a tilde keyword to the start of the key to bypass all the validation of the immediate child.                                                                                                                                                                                                                                                                                                                                                        |  ```none```  | Could be add on any keyword. Excluded `reserved keywords` |
| **\_\_data_type\_\_**  | Set data type on field, multiple data types could be supplied using pipe \| for example. ```string\|object```.                                                                                                                                                                                                                                                                                                                                          | ```string``` |                         `object`                          |
| **\_\_alow_space\_\_** | Allow space on text.                                                                                                                                                                                                                                                                                                                                                                                                                                    |  ```true```  |                         `string`                          |
| **\_\_min_length\_\_** | Set the minimum length.                                                                                                                                                                                                                                                                                                                                                                                                                                 |   ```0```    |             `string` and any type of `array`              |
| **\_\_max_length\_\_** | Set the maximum length.                                                                                                                                                                                                                                                                                                                                                                                                                                 |  ```none```  |             `string` and any type of `array`              |
| **\_\_min_value\_\_**  | Set the minimum value.                                                                                                                                                                                                                                                                                                                                                                                                                                  |   ```0```    |                   `integer` and `float`                   |
| **\_\_max_value\_\_**  | Set the maximum value.                                                                                                                                                                                                                                                                                                                                                                                                                                  |  ```none```  |                   `integer` and `float`                   |
|    **\_\_case\_\_**    | Apply case constraint on value.<br /><br />**Available case constraints:**<ol><li><code>\_\_upper\_\_</code></li><li><code>\_\_lower\_\_</code></li><li><code>\_\_title\_\_</code></li></ol>                                                                                                                                                                                                                                                            |  ```none```  |                         `string`                          |
| **\_\_bind_regex\_\_** | Apply custom regular expression or use some pre-define. <code>Note:</code> **\_\_bind_regex\_\_** will take higher precedence over **\_\_bind\_\_** if both are defined.<br /><br />**Some pre-defined expressions:**<ol><li><code>\_\_email\_\_</code></li><li><code>\_\_alpha\_\_</code></li><li><code>\_\_numeric\_\_</code></li><li><code>\_\_alphanumeric\_\_</code></li><li><code>\_\_ipv4\_\_</code></li><li><code>\_\_ipv6\_\_</code></li></ol> | ```false```  |                         `string`                          |
|    **\_\_rem\_\_**     | Proivde custom error when regex gets failed.                                                                                                                                                                                                                                                                                                                                                                                                            | ```false```  |                         `string`                          |
|    **\_\_bind\_\_**    | Bind value from defined valueset.                                                                                                                                                                                                                                                                                                                                                                                                                       |  ```none```  |                   ignore the data type                    |
|   **\_\_binder\_\_**   | This is a special keyword and that will be used only root object of the schema where you can define binding valueset.                                                                                                                                                                                                                                                                                                                                   |  ```none```  |                    only root `object`                     |
|  **\_\_defaults\_\_**  | This is a special keyword and that will be used to apply the defined constraints globally on the document.<br /><br />**Available properties that could be set globally:**<br /><ol><li><code>\_\_allow_space\_\_</code></li><li><code>\_\_min_length\_\_</code></li><li><code>\_\_max_length\_\_</code></li><li><code>\_\_min_value\_\_</code></li><li><code>\_\_max_value\_\_</code></li><li><code>\_\_case\_\_</code></li></ol>                      |  ```none```  |                     only root `object`                     |

### Support Data Types

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