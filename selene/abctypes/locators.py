from abc import ABCMeta, abstractmethod, abstractproperty

from future.utils import with_metaclass


class ISeleneWebElementLocator(with_metaclass(ABCMeta, object)):

    @abstractmethod
    def find(self):
        # type: () -> WebElement
        pass

    @abstractproperty
    def description(self):
        # type: () -> str
        pass

    def __str__(self):
        return self.description


class ISeleneListWebElementLocator(with_metaclass(ABCMeta, object)):

    @abstractmethod
    def find(self):
        # type: () -> List[WebElement]
        pass

    @abstractproperty
    def description(self):
        # type: () -> str
        pass

    def __str__(self):
        return self.description


