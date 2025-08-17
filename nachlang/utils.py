from rply import Token


def filter_parens(iterable):
    def filter_fn(item):
        if isinstance(item, Token) and item.name in ["CLOSE_PAREN", "OPEN_PAREN"]:
            return False
        return True

    return list(filter(filter_fn, iterable))
