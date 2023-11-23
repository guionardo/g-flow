"""
g-flow - A complete and practical Gitflow implementation
Directly inspired by https://github.com/galvao-eti/g-flow

"""
import os
import subprocess
import sys
from shutil import which

from packaging.version import InvalidVersion, Version

CONFIG_FILE = ".g_flowrc"
VERSION_FILE = "VERSION"
VERSION = ""
VALID_TYPES = ()
RESULTS = []

CONFIG = {
    "INIT_VERSION": "0.1.0",
    "EPIC": "epic",
    "FEATURE": "feat",
    "FIX": "fix",
    "HOTFIX": "hfix",
    "PROD_BRANCH": "main",
    "HMG_BRANCH": "homolog",
    "DEV_BRANCH": "dev",
    "REMOTE": "origin",
}


def get_usage():
    return f"""g-flow - A complete and practical git-flow implementation
https://github.com/guionardo/g-flow

Directly inspired by bash g-flow @ https://github.com/galvao-eti/g-flow

SYNOPSIS:
g-flow COMMAND branch_name [SOURCE_BRANCH]

COMMANDS 
    {CONFIG['EPIC']}
        Creates an epic branch
    {CONFIG['FEATURE']}
        Creates an feature branch
    {CONFIG['FIX']}
        Creates a fix branch
    {CONFIG['HOTFIX']}
        Creates a hotfix branch
"""


def check_git():
    if not which("git"):
        error("git command was not found")
    if not os.path.exists(".git"):
        error("This folder doesn't seem to be the root of a git project.")


def read_config():
    global VALID_TYPES
    try:
        with open(CONFIG_FILE) as file:
            for line in file:
                line = line.strip("\n\r ")
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                if key in CONFIG:
                    if value := value.strip():
                        CONFIG[key] = value.strip()
                    else:
                        error(f"INVALID EMPTY CONFIGURATION [{key}] IN {CONFIG_FILE}")
    except FileNotFoundError:
        # Ok, this is not a problem
        pass
    except Exception as exc:
        error(f"FAILED TO READ CONFIGURATION: {exc}")

    VALID_TYPES = (CONFIG["EPIC"], CONFIG["FEATURE"], CONFIG["FIX"], CONFIG["HOTFIX"])


def parse_version():
    global VERSION
    try:
        with open(VERSION_FILE) as file:
            VERSION = Version(file.read())

    except FileNotFoundError:
        VERSION = Version(CONFIG["INIT_VERSION"])
    except InvalidVersion as exc:
        error(f"FAILED TO PARSE VERSION: {exc}")


def parse_arguments():
    if len(sys.argv) == 1:
        print(get_usage())
        sys.exit(0)

    args = sys.argv[1:]
    args.extend(["", ""])
    TYPE, NAME, MAIN = args[:3]
    if not TYPE or TYPE not in VALID_TYPES:
        error(
            f"Invalid branch type {TYPE}. Accepted types: {VALID_TYPES}\n{get_usage()}"
        )
    TYPE = CONFIG[TYPE.upper()]
    if not NAME:
        error(f"branch_name is required.\n{get_usage()}")

    MAIN = MAIN or CONFIG["PROD_BRANCH"]

    if MAIN != CONFIG["PROD_BRANCH"] and not confirm(
        f'WARNING: Your branch will be created from {MAIN}, which is different from {CONFIG["PROD_BRANCH"]}.\n'
        "Are you SURE you want to continue ( y / N )?"
    ):
        print("Aborted")
        sys.exit(0)

    return TYPE, NAME, MAIN


def run_switch_branch(branch):
    run_process(f"Error switching to {branch}", "git", "switch", branch)

    RESULTS.append(f"Switched branches to {branch};")


def run_pull_main(branch):
    run_process(f"Error updating the {branch} branch", "git", "pull")

    RESULTS.append(f"{branch} branch updated (pull);")


def run_create_main(TYPE, NAME, MAIN):
    run_process(
        f"Error creating {TYPE}/{NAME} branch",
        "git",
        "switch",
        "--create",
        f"{TYPE}/{NAME}",
    )

    RESULTS.append(f"{TYPE}/{NAME} branch created from {MAIN};")


def run_push_branch(TYPE, NAME):
    run_process(
        f"Error trying to remotely synchronize the {TYPE}/{NAME} branch",
        "git",
        "push",
        "-u",
        "origin",
        f"{TYPE}/{NAME}",
    )

    RESULTS.append(f"{TYPE}/{NAME} branch remotely synchronized.")


def finishes_process():
    print("\ng-flow executed sucessfully")
    print("Summary of the executed actions:\n", "\n".join(RESULTS))
    print("Have a good one!")


def run_process(error_message, *args):
    process = subprocess.run(args, capture_output=True)
    if process.returncode == 0:
        return True
    print("Command ", " ".join(args), "returned non-zero exit ", process.returncode)
    if process.stderr:
        print(f"STDERR={process.stderr.decode()}")
    if process.stdout:
        print(f"STDOUT={process.stdout.decode()}")
    error(error_message, 2)
    return False


def error(message, exit_code=1):
    print("ERROR:", message)
    sys.exit(exit_code)


def confirm(message):
    return f"{input(message)} ".upper()[0] == "Y"


def main():
    check_git()
    read_config()
    parse_version()
    TYPE, NAME, MAIN = parse_arguments()

    run_switch_branch(MAIN)
    run_pull_main(MAIN)
    run_create_main(TYPE, NAME, MAIN)
    run_push_branch(TYPE, NAME)

    finishes_process()


if __name__ == "__main__":
    main()
