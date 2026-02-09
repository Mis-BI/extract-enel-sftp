import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from extract_enel_sftp.config import default_password_sftp_config
from extract_enel_sftp.tools.sftp_password import run_password_test


def main() -> None:
    run_password_test(default_password_sftp_config())


if __name__ == "__main__":
    main()
