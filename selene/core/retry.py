import random
from abc import ABC, abstractmethod
from typing import Iterator

class RetryStrategy(ABC):
    @abstractmethod
    def __iter__(self) -> Iterator[float]:
        pass

class FixedDelay(RetryStrategy):
    def __init__(self, delay: float = 0.1):
        self.delay = delay
        
    def __iter__(self) -> Iterator[float]:
        while True:
            yield self.delay

class ExponentialBackoff(RetryStrategy):
    def __init__(self, initial_delay: float = 0.1, multiplier: float = 2.0, max_delay: float = 5.0):
        self.initial_delay = initial_delay
        self.multiplier = multiplier
        self.max_delay = max_delay
        
    def __iter__(self) -> Iterator[float]:
        delay = self.initial_delay
        while True:
            yield delay
            delay = min(delay * self.multiplier, self.max_delay)

class LinearBackoff(RetryStrategy):
    def __init__(self, initial_delay: float = 0.1, step: float = 0.1, max_delay: float = 5.0):
        self.initial_delay = initial_delay
        self.step = step
        self.max_delay = max_delay
        
    def __iter__(self) -> Iterator[float]:
        delay = self.initial_delay
        while True:
            yield delay
            delay = min(delay + self.step, self.max_delay)

class FibonacciBackoff(RetryStrategy):
    def __init__(self, initial_delay: float = 0.1, max_delay: float = 5.0):
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        
    def __iter__(self) -> Iterator[float]:
        a, b = 1, 1
        while True:
            delay = min(self.initial_delay * a, self.max_delay)
            yield delay
            a, b = b, a + b

class JitteredBackoff(RetryStrategy):
    def __init__(self, initial_delay: float = 0.1, max_delay: float = 5.0, factor: float = 2.0):
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.factor = factor
        
    def __iter__(self) -> Iterator[float]:
        delay = self.initial_delay
        while True:
            yield random.uniform(0, delay)
            delay = min(delay * self.factor, self.max_delay)
