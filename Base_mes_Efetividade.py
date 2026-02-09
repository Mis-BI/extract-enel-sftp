import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from extract_enel_sftp.processing.ordens_filhas import processar_ordens_filhas

__all__ = ["processar_ordens_filhas"]
