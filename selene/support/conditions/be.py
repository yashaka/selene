from selene import conditions


# *** Condition builders ***


def not_(condition_to_be_inverted):
    return conditions.not_(condition_to_be_inverted)


# *** SeleneElement conditions ***


visible = conditions.visible
in_dom = conditions.in_dom
enabled = conditions.enabled
existing = conditions.exist
clickable = conditions.clickable
hidden = conditions.hidden
blank = conditions.blank


# *** SeleneCollection conditions ***


empty = conditions.empty


# *** Other conditions ***

or_not_to_be = conditions.or_not_to_be
