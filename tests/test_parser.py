from nachlang.parser import parse

def test_ast_building(code_samples, snapshot):
    def test_sample(code_sample):
        snapshot.assert_match(parse(code_sample["code"]), f"Build AST for: {code_sample['name']}")

    list(map(test_sample, code_samples))
