import logging
from typing import Tuple, List

from examples.log_all_selene_commands_with_wait__framework.framework.assist.python.logging import (
    TranslatingFormatter,
)


def log_with(
    *,
    logger,
    added_handler_translations: List[Tuple[str, str]] = (),
):
    """
    returns decorator factory with logging to specified logger
    with added list of translations
    to decorate Selene's waiting via config._wait_decorator
    """

    TranslatingFormatter.translations = added_handler_translations

    handler = logging.StreamHandler()
    formatter = TranslatingFormatter("[%(name)s] - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    def log_on_wait(wait):
        def log_on_wait_decorator(for_):
            def decorated(fn):
                entity = wait._entity
                logger.info('step: %s > %s: STARTED', entity, fn)
                try:
                    res = for_(fn)
                    logger.info('step: %s > %s: ENDED', entity, fn)
                    return res
                except Exception as error:
                    logger.info('step: %s > %s: FAILED: %s', entity, fn, error)
                    raise error

            return decorated

        return log_on_wait_decorator

    return log_on_wait
