from validations.schema_validations import *
from validations.doc_validations import *

# create validation set
doc_validation_set = {
    DetectInvalidKeys(),
    DataTypeEqualityCheck()
}

# schema validation set
schema_validation_set = {
    CheckInvalidDateType(),
    CheckBindings(),
    CheckInvalidValueType(),
    IrrelevantKeysCombinations(),
    CheckMinMaxValue()
}

