import os
from typing import List, Tuple

import paramiko

from ..config import PasswordSftpConfig


def create_sftp_connection(config: PasswordSftpConfig):
    print("Tentando conectar ao SFTP...")
    try:
        transport = paramiko.Transport((config.host, config.port))
        transport.connect(username=config.username, password=config.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print("Conexao estabelecida com sucesso!")
        return sftp, transport
    except Exception as exc:
        print(f"Falha na conexao SFTP: {exc}")
        return None, None


def close_sftp_connection(sftp, transport) -> None:
    print("Fechando conexao SFTP...")
    if sftp:
        sftp.close()
    if transport:
        transport.close()
    print("Conexao encerrada.")


def download_files_by_prefix_and_month(
    sftp, config: PasswordSftpConfig
) -> List[str]:
    os.makedirs(config.download_base_dir, exist_ok=True)
    print(f"Listando arquivos no diretorio remoto: {config.remote_path}")
    downloaded_files: List[str] = []

    try:
        files = sftp.listdir(config.remote_path)
        print(f"{len(files)} arquivos encontrados no diretorio remoto.")
    except Exception as exc:
        print(f"Falha ao listar arquivos no diretorio remoto: {exc}")
        return downloaded_files

    for file_name in files:
        if (
            config.file_prefix in file_name
            and config.file_month in file_name
            and file_name.lower().endswith(".txt")
        ):
            remote_file = f"{config.remote_path}/{file_name}"
            local_file = os.path.join(config.download_base_dir, file_name)

            try:
                sftp.get(remote_file, local_file)
                downloaded_files.append(file_name)
                print(f"Arquivo baixado com sucesso: {file_name}")
            except Exception as exc:
                print(f"Erro ao baixar {file_name}: {exc}")

    if not downloaded_files:
        print("Nenhum arquivo encontrado com os criterios informados.")
    else:
        print(f"Total de arquivos baixados: {len(downloaded_files)}")

    return downloaded_files


def run_password_test(config: PasswordSftpConfig) -> Tuple[str, List[str]]:
    sftp, transport = None, None
    try:
        sftp, transport = create_sftp_connection(config)
        if not sftp:
            print("Encerrando script devido a falha na conexao.")
            return "error", []

        downloaded = download_files_by_prefix_and_month(sftp, config)
        print("Processo finalizado. Arquivos baixados:", downloaded)
        return "ok", downloaded
    finally:
        close_sftp_connection(sftp, transport)
