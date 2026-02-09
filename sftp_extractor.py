import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from extract_enel_sftp.config import default_extractor_config
from extract_enel_sftp.extractor import run_extraction
from extract_enel_sftp.logging_config import setup_logging


def main() -> None:
    setup_logging()
    run_extraction(default_extractor_config())


if __name__ == "__main__":
    main()
