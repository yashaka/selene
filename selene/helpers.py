import contextlib


@contextlib.contextmanager
def suppress(*exceptions):
    try:
        yield
    except exceptions:
        pass


def merge(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


import os


def take_screenshot(driver, name, save_location='./'):
    """ saves screenshot of the current page via driver, with name, to the save_location """
    # Make sure the path exists.
    path = os.path.abspath(save_location)
    if not os.path.exists(path):
        os.makedirs(path)
    full_path = '%s/%s' % (path, name)
    driver.get_screenshot_as_file(full_path)
    return full_path

    # todo: sometimes screenshooting fails at httplib with CannotSendRequest... consider handling this somehow...
    # todo: and of course find the reason - why... it may depend on browser version...