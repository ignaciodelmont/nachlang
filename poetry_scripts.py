import subprocess


def run_cmd(cmd: str):
    return subprocess.run(cmd.split(" "), shell=False, check=False).returncode


def format_code():
    return run_cmd("poetry run black nachlang/") and run_cmd(
        "poetry run isort nachlang/"
    )
