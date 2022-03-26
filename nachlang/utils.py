from rply import Token


def _filter_parens(iterable):
    def filter_fn(item):
        if type(item) == Token and item.name in ["CLOSE_PAREN", "OPEN_PAREN"]:
            return False
        return True

    return list(filter(filter_fn, iterable))
