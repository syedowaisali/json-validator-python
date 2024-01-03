from ordered_set import OrderedSet

from models.result import Result


class ObjectSet:

    def __init__(self):
        self.ordered_set = OrderedSet()

    def add(self, val: Result):
        messages = [result.message for result in self.ordered_set]
        if val.message not in messages:
            self.ordered_set.add(val)

    def item_set(self):
        return self.ordered_set

    def ini(self):
        self.ordered_set = OrderedSet()
