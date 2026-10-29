import subprocess


def run_cmd(cmd: str):
    return subprocess.run(cmd.split(" "), shell=False, check=False).returncode


def format_code():
    """
    Run black and then isort over the package and the tests.

    Both always run. This used to be `run_cmd(black) and run_cmd(isort)`,
    which short-circuits on black's return code -- 0 on success -- so isort
    only ever ran when black had failed.
    """
    black = run_cmd("poetry run black nachlang/ tests/")
    isort = run_cmd("poetry run isort nachlang/ tests/")
    return black or isort
