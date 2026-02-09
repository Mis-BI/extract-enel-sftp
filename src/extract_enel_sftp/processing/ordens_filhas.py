import csv
from typing import Optional

import pandas as pd


def processar_ordens_filhas(arquivo: Optional[str] = None) -> pd.DataFrame:
    if arquivo is None:
        arquivo = "archives/COELCE_elaazisysd00_ordemfilhas.txt"

    df_ordens_filhas = pd.read_csv(
        arquivo,
        sep="|",
        encoding="cp1252",
        quoting=csv.QUOTE_NONE,
        engine="python",
        header=None,
    )

    df_ordens_filhas.columns = [
        f"Column{i + 1}" for i in range(len(df_ordens_filhas.columns))
    ]

    df_ordens_filhas = df_ordens_filhas.rename(
        columns={
            "Column1": "CO",
            "Column2": "REFERENCIA",
            "Column3": "NUMERO_CLIENTE",
            "Column4": "MATRICULA_LEITURISTA",
            "Column5": "SECTOR",
            "Column6": "LOCALIDADE",
            "Column7": "ZONA",
            "Column8": "MUNICIPIO",
            "Column9": "BAIRRO",
            "Column10": "IRREG_LIDA",
            "Column11": "IRREG_OPERADOR",
            "Column12": "NUMERO_MEDIDOR",
            "Column13": "DESC_IRREG_LIDA",
            "Column14": "DESC_IRREG_OPERADOR",
            "Column15": "DX",
            "Column16": "TELEMEDIDO",
            "Column17": "UNIDADE_LEITURA",
            "Column18": "CODIGO_MUNICIPIO",
            "Column19": "FAT_BIMESTRAL",
            "Column20": "LATITUDE",
            "Column21": "LONGITUDE",
        }
    )

    df_ordens_filhas = df_ordens_filhas[~df_ordens_filhas["estado"].isin(["04", "09"])]
    df_ordens_filhas["data_ingresso"] = pd.to_datetime(
        df_ordens_filhas["data_ingresso"], errors="coerce", dayfirst=True
    )
    df_ordens_filhas["data_estado"] = pd.to_datetime(
        df_ordens_filhas["data_estado"], errors="coerce", dayfirst=True
    )
    df_ordens_filhas["BASE"] = "ORDENS FILHAS"

    return df_ordens_filhas
