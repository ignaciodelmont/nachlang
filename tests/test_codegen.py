from nachlang.codegen.ast import generate_llvm_ir
from nachlang.parser import parse


def test_codegen(code_samples, snapshot):
    def test_sample(code_sample):
        snapshot.assert_match(
            "\n".join((generate_llvm_ir(parse(code_sample["code"]))._get_body_lines())),
            f"LLVM IR for: {code_sample['name']}",
        )

    list(map(test_sample, code_samples))
