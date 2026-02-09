import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from extract_enel_sftp.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
