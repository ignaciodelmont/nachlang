def get_raw_tokens(tokens):
        tokens_as_dicts = [t.__dict__ for t in tokens]
        print(tokens_as_dicts)
        [t.pop("source_pos") for t in tokens_as_dicts]
        return tokens_as_dicts