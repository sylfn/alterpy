import datetime
import platform
import os


def system_info() -> str:
    return f"{platform.python_implementation()} {platform.python_version()} on {platform.system()} {platform.machine()}"


def argv() -> list[str]:
    pid = os.getpid()
    with open(f'/proc/{pid}/cmdline') as f:
        args = f.read().split('\0')[:-1]
    return args


