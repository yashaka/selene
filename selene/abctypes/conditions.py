from abc import ABCMeta, abstractmethod


class IEntityCondition(object):
    __metaclass__ = ABCMeta

    # todo: consider using __call__ instead
    @abstractmethod
    def fn(self, entity):
        # type: (object) -> any
        pass

    def __call__(self, entity):
        return self.fn(entity)

    @abstractmethod
    def description(self):
        # type: () -> str
        pass