import os
import pandas as pd
from sqlalchemy import create_engine, inspect
from urllib.parse import quote_plus

# =========================
# CONFIGURAÇÃO PASTAS
# =========================
DOWNLOAD_BASE_DIR = "./archives/EfetividadeLeitura - Copia"

# Colunas esperadas
EXPECTED_COLUMNS = [
    "CO", "REFERENCIA", "NUMERO_CLIENTE", "MATRICULA_LEITURISTA", "SECTOR",
    "LOCALIDADE", "ZONA", "MUNICIPIO", "BAIRRO", "IRREG_LIDA", "IRREG_OPERADOR",
    "NUMERO_MEDIDOR", "DESC_IRREG_LIDA", "DESC_IRREG_OPERADOR", "DX", "TELEMEDIDO",
    "UNIDADE_LEITURA", "CODIGO_MUNICIPIO", "FAT_BIMESTRAL", "LATITUDE", "LONGITUDE"
]

# =========================
# CONFIGURAÇÃO SQL SERVER
# =========================
SQL_SERVER_USER = 'FSABA/jmoreira'
SQL_SERVER_PASSWORD = 'Tel*2025@!'
SQL_SERVER_HOST = '172.26.0.37'
SQL_SERVER_PORT = '1433'
SQL_SERVER_DB = 'ENEL'
SQL_SERVER_TABLE = 'EfetividadeLeitura'

# Codificando usuário e senha
usuario = quote_plus(SQL_SERVER_USER)
senha = quote_plus(SQL_SERVER_PASSWORD)

# =========================
# FUNÇÃO PRINCIPAL: COMBINA TXT
# =========================
def create_dataframe_from_txt(base_dir):
    all_files = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith(".txt"):
                all_files.append(os.path.join(root, f))

    if not all_files:
        print("⚠️ Nenhum arquivo encontrado.")
        return None

    dataframes = []
    for file_path in all_files:
        file_name = os.path.basename(file_path)
        try:
            df = pd.read_csv(file_path, sep='|', encoding='utf-8', dtype=str)
            df['source_file'] = file_name

            # Garantir colunas esperadas
            for col in EXPECTED_COLUMNS:
                if col not in df.columns:
                    df[col] = None
            df = df[EXPECTED_COLUMNS + ['source_file']]

            dataframes.append(df)
            print(f"✅ Arquivo carregado: {file_name}")
        except Exception as e:
            print(f"❌ Falha ao ler {file_name}: {e}")

    if not dataframes:
        print("❌ Nenhum DataFrame criado.")
        return None

    combined_df = pd.concat(dataframes, ignore_index=True)
    print(f"📊 DataFrame combinado criado com {len(combined_df)} linhas.")
    return combined_df

# =========================
# FUNÇÃO PARA INSERIR NO SQL SERVER
# =========================
def insert_dataframe_to_sqlserver(df):
    try:
        conn_str = (
                    f"mssql+pyodbc://{usuario}:{senha}@{SQL_SERVER_HOST},{SQL_SERVER_PORT}/{SQL_SERVER_DB}"
                     "?driver=ODBC+Driver+18+for+SQL+Server"
                        "&TrustServerCertificate=yes"
) 

        print("🔗 Conectando com:", conn_str)
        engine = create_engine(conn_str)

        # Verifica se a tabela existe usando o inspector
        inspector = inspect(engine)
        if SQL_SERVER_TABLE not in inspector.get_table_names():
            print(f"⚙️ Tabela {SQL_SERVER_TABLE} não existe. Criando...")
            df.head(0).to_sql(SQL_SERVER_TABLE, con=engine, if_exists='replace', index=False)
            print(f"✅ Tabela {SQL_SERVER_TABLE} criada com sucesso.")

        # Insere os dados no SQL Server
        df.to_sql(SQL_SERVER_TABLE, con=engine, if_exists='append', index=False)
        print(f"✅ {len(df)} linhas inseridas na tabela {SQL_SERVER_TABLE}.")

    except Exception as e:
        print(f"❌ Falha ao inserir no SQL Server: {e}")

# =========================
# EXECUÇÃO
# =========================
if __name__ == "__main__":
    df_final = create_dataframe_from_txt(DOWNLOAD_BASE_DIR)
    if df_final is not None:
        insert_dataframe_to_sqlserver(df_final)
        print("🎯 Processo concluído! Dados salvos no SQL Server.")
