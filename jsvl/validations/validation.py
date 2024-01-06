from abc import ABC

from jsvl.models.object_set import ObjectSet
from jsvl.models.result import Error, Warn, Info, Success


class Validation(ABC):

    def __init__(self):
        self.__results = ObjectSet()

    def create_error(self, message):
        self.__results.add(Error(message, self))

    def create_warn(self, message):
        self.__results.add(Warn(message, self))

    def create_info(self, message):
        self.__results.add(Info(message, self))

    def create_success(self, message):
        self.__results.add(Success(message, self))

    def init_log_set(self):
        self.__results.ini()

    def get_set(self):
        return self.__results.item_set()


