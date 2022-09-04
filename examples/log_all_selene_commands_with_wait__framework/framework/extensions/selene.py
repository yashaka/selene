import logging
from typing import Tuple, List

from examples.log_all_selene_commands_with_wait__framework.framework.extensions.python.logging import (
    TranslatingFormatter,
)


def log_with(
    logger,
    *,
    added_handler_translations: List[Tuple[str, str]] = (),
):
    """
    returns decorator factory with logging to specified logger
    with added list of translations
    to decorate Selene's waiting via config._wait_decorator.
    Example:
        from selene.support.shared import browser
        from framework.extensions.selene import log_with
        import logging

        logger = logging.getLogger('SE')
        browser.config._wait_decorator = log_with(
            logger,
            added_handler_translations = [
                ('browser.element', 'element'),
                ('browser.all', 'all'),
            ]
        )

        ...
    """

    TranslatingFormatter.translations = added_handler_translations

    handler = logging.StreamHandler()
    formatter = TranslatingFormatter("[%(name)s] - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    def decorator_factory(wait):
        def decorator(for_):
            def decorated(fn):
                entity = wait.entity
                logger.info('step: %s > %s: STARTED', entity, fn)
                try:
                    res = for_(fn)
                    logger.info('step: %s > %s: ENDED', entity, fn)
                    return res
                except Exception as error:
                    logger.info('step: %s > %s: FAILED: %s', entity, fn, error)
                    raise error

            return decorated

        return decorator

    return decorator_factory
