from abc import ABCMeta, abstractmethod, abstractproperty


class ISeleneWebElementLocator(object):
    __metaclass__ = ABCMeta

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


class ISeleneListWebElementLocator(object):
    __metaclass__ = ABCMeta

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


