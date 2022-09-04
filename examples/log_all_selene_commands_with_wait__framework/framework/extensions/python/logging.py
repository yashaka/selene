import logging
from functools import reduce
from typing import Tuple, List


class TranslatingFormatter(logging.Formatter):
    translations: List[Tuple[str, str]] = ()

    def formatMessage(self, record: logging.LogRecord) -> str:
        original = super().formatMessage(record)

        def translate(initial: str, item: Tuple[str, str]):
            old, new = item
            return initial.replace(old, new)

        return reduce(
            translate,
            self.translations,
            original,
        )
