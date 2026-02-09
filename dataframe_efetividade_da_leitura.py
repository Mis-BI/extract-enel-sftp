import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from extract_enel_sftp.config import default_efetividade_config
from extract_enel_sftp.etl.efetividade import run_efetividade_etl


def main() -> None:
    run_efetividade_etl(default_efetividade_config())


if __name__ == "__main__":
    main()
