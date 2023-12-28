## Features

#### Features
- Detect invalid keys which are not defined in schema.
- Control data type on each key.
- Allow required and optional fields.
- Provide pre-defined value set to bound the value.
- Allow spacing in value. note this will work only **string** data-type, default is false.
- Limit the character in string data-type by provide minimum and maximum character length.

#### Installation
```commandline
install pip json-analyzer
```
#### How to use
List of available commands

| Command        | Definition                                                                                                                                                                                                          |
|----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| h or --help    | for help                                                                                                                                                                                                            |
| i or --input   | provide a directory or a single json file that you want to analyze.<br/>Note: if the input source is a directory then provided schema should be in a directory and should have the same name with _schema postfix.  |
| o or --output  | provide output directory where you want to save error log, default all logs will be printed on console.                                                                                                             |
| -s or --schema | provide a schema file that will be used to analyze the input json<br />Note. if the provided input is a directory then you can also provide the schema as a directory. All schema file should have _schema postfix. | 

#### Validate
**Command line**
```commandline
~$ jvl -i /path/to/source.json -s /path/to/schema.json
```
**In Python**
```python
from jvl import validator

# source json
source = "path/to/source.json"

# schema json
schema = "path/to/schema.json"

# perform validation
validator.validate(source, schema)
```
#### Allow additional fields

By default, you can't add any additional field in json file which is not defined in schema. Because all the fields are strictly checking from schema that means source json cannot have any additional field which is not defined in schema, If you want to disable this then pass the **--allow-additional** flag argument.<br /><br />
**Command line**
```commandline
jvl -i /path/to/source.json -s /path/to/schema.json --allow-additional
```
**In Python**
```python
from jvl import config

config.allow_additional_fields(False)
```
#### User guide

#### Data Types
#### Required & Optional Field