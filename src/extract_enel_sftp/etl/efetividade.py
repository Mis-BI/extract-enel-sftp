import os
from typing import List, Optional

import pandas as pd
from sqlalchemy import create_engine, inspect
from urllib.parse import quote_plus

from ..config import EfetividadeConfig, SqlServerConfig


def create_dataframe_from_txt(
    base_dir: str, expected_columns: List[str]
) -> Optional[pd.DataFrame]:
    all_files = []
    for root, _, files in os.walk(base_dir):
        for file_name in files:
            if file_name.lower().endswith(".txt"):
                all_files.append(os.path.join(root, file_name))

    if not all_files:
        print("Nenhum arquivo encontrado.")
        return None

    dataframes = []
    for file_path in all_files:
        file_name = os.path.basename(file_path)
        try:
            df = pd.read_csv(file_path, sep="|", encoding="utf-8", dtype=str)
            df["source_file"] = file_name

            for col in expected_columns:
                if col not in df.columns:
                    df[col] = None
            df = df[expected_columns + ["source_file"]]

            dataframes.append(df)
            print(f"Arquivo carregado: {file_name}")
        except Exception as exc:
            print(f"Falha ao ler {file_name}: {exc}")

    if not dataframes:
        print("Nenhum DataFrame criado.")
        return None

    combined_df = pd.concat(dataframes, ignore_index=True)
    print(f"DataFrame combinado criado com {len(combined_df)} linhas.")
    return combined_df


def _build_connection_string(sql_config: SqlServerConfig) -> str:
    usuario = quote_plus(sql_config.user)
    senha = quote_plus(sql_config.password)

    return (
        f"mssql+pyodbc://{usuario}:{senha}@{sql_config.host},{sql_config.port}/"
        f"{sql_config.database}?driver=ODBC+Driver+18+for+SQL+Server"
        "&TrustServerCertificate=yes"
    )


def insert_dataframe_to_sqlserver(
    df: pd.DataFrame, sql_config: SqlServerConfig
) -> None:
    try:
        conn_str = _build_connection_string(sql_config)

        print("Conectando com:", conn_str)
        engine = create_engine(conn_str)

        inspector = inspect(engine)
        if sql_config.table not in inspector.get_table_names():
            print(f"Tabela {sql_config.table} nao existe. Criando...")
            df.head(0).to_sql(
                sql_config.table, con=engine, if_exists="replace", index=False
            )
            print(f"Tabela {sql_config.table} criada com sucesso.")

        df.to_sql(sql_config.table, con=engine, if_exists="append", index=False)
        print(f"{len(df)} linhas inseridas na tabela {sql_config.table}.")

    except Exception as exc:
        print(f"Falha ao inserir no SQL Server: {exc}")


def run_efetividade_etl(config: EfetividadeConfig) -> None:
    df_final = create_dataframe_from_txt(
        config.download_base_dir, config.expected_columns
    )
    if df_final is not None:
        insert_dataframe_to_sqlserver(df_final, config.sql_server)
        print("Processo concluido! Dados salvos no SQL Server.")
