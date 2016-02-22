import time


def time_spent(function, *args, **kwargs):

    start_time = time.time()
    function(*args, **kwargs)
    end_time = time.time()

    return end_time - start_time
