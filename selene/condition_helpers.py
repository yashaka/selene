def satisfied(it, *condtions):
    return all(map(lambda cond: cond(it), condtions))