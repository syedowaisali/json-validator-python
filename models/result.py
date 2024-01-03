from abc import ABC, abstractmethod

from ordered_set import OrderedSet

class Result(ABC):

    def __init__(self, message, validation: object = None):
        self.message = message
        self.validation = validation


class Success(Result):
    pass


class Info(Result):
    pass


class Warn(Result):
    pass


class Error(Result):
    pass


class Output:

    def __init__(self, schema_result: OrderedSet, document_result: OrderedSet):
        self.schema_result = schema_result
        self.document_result = document_result
