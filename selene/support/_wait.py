import functools
from typing import ContextManager


# TODO: consider adding examples to docstring
# TODO: should we also accept a context_factory?
# TODO: should we name it as decorated_with?
def with_(
    *,
    context: ContextManager,
):
    """
    :return:
        Decorator factory to pass to Selene's config._wait_decorator
        to wrap functions (to be waited for) into passed context manager
    :param context:
        a normal context manager under each function to be waited for
    """

    def decorator_factory(wait):  # noqa
        def decorator(for_):
            @functools.wraps(for_)
            def wrapper(fn):
                with context:
                    return for_(fn)

            return wrapper

        return decorator

    return decorator_factory


# TODO: consider adding alias to _logging.wait_with
#       so that usage is
#       support._wait.with_logging(context=allure_commons._allure.StepContext)
#       instead of or in addition to
#       support._logging.wait_with_(context=allure_commons._allure.StepContext)
