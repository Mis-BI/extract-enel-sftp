import os
import paramiko
import re

# =========================
# CONFIGURAÇÕES SFTP
# =========================

SFTP_CONFIG = {
    "host": "10.152.153.33",
    "port": 22,
    "username": "EXPLOTACAO",
    "password": "Explota@2023"
}

REMOTE_PATH = "/D:/LOGS/Coelce/ExtratorEfetividadeLeitura"
FILE_PREFIX = "BaseMes"
FILE_MONTH = "202601"
DOWNLOAD_BASE_DIR = "./archives/EfetividadeLeitura"

# Regex para filtrar arquivos diretamente
FILE_PATTERN = re.compile(f"{FILE_PREFIX}.*{FILE_MONTH}.*\\.txt$", re.IGNORECASE)

# =========================
# CONEXÃO SFTP
# =========================

def create_sftp_connection():
    print("🔗 Tentando conectar ao SFTP...")
    try:
        transport = paramiko.Transport((SFTP_CONFIG["host"], SFTP_CONFIG["port"]))
        transport.connect(username=SFTP_CONFIG["username"], password=SFTP_CONFIG["password"])
        sftp = paramiko.SFTPClient.from_transport(transport)
        print("✅ Conexão estabelecida com sucesso!")
        return sftp, transport
    except Exception as e:
        print(f"❌ Falha na conexão SFTP: {e}")
        return None, None

def close_sftp_connection(sftp, transport):
    print("🔒 Fechando conexão SFTP...")
    if sftp:
        sftp.close()
    if transport:
        transport.close()
    print("✅ Conexão encerrada.")

# =========================
# DOWNLOAD DE ARQUIVOS POR PREFIXO E MÊS
# =========================

def download_files_by_prefix_and_month(sftp, remote_path, local_dir):
    os.makedirs(local_dir, exist_ok=True)
    downloaded_files = []

    print(f"📂 Listando arquivos no diretório remoto: {remote_path}")

    try:
        for attr in sftp.listdir_attr(remote_path):
            file = attr.filename

            # Filtra usando regex
            if FILE_PATTERN.match(file):
                remote_file = f"{remote_path}/{file}"
                local_file = os.path.join(local_dir, file)

                try:
                    sftp.get(remote_file, local_file)
                    downloaded_files.append(file)
                    print(f"✅ Arquivo baixado: {file}")
                except Exception as e:
                    print(f"❌ Erro ao baixar {file}: {e}")

    except Exception as e:
        print(f"❌ Falha ao listar arquivos no diretório remoto: {e}")
        return downloaded_files

    if not downloaded_files:
        print("⚠️ Nenhum arquivo encontrado com os critérios informados.")
    else:
        print(f"📥 Total de arquivos baixados: {len(downloaded_files)}")

    return downloaded_files

# =========================
# MAIN
# =========================

def main():
    sftp, transport = None, None
    try:
        sftp, transport = create_sftp_connection()
        if not sftp:
            print("🚫 Encerrando script devido a falha na conexão.")
            return

        downloaded = download_files_by_prefix_and_month(
            sftp,
            REMOTE_PATH,
            DOWNLOAD_BASE_DIR
        )
        print("🎯 Processo finalizado. Arquivos baixados:", downloaded)
    finally:
        close_sftp_connection(sftp, transport)

if __name__ == "__main__":
    main()
