import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from extract_enel_sftp.config import default_password_sftp_regex_config
from extract_enel_sftp.tools.sftp_password_regex import run_password_regex_test


def main() -> None:
    run_password_regex_test(default_password_sftp_regex_config())


if __name__ == "__main__":
    main()
