import logging
import os
import zipfile
from typing import List, Tuple

import paramiko

logger = logging.getLogger(__name__)


def load_private_key(key_path: str):
    logger.info("Carregando chave privada: %s", key_path)

    if not os.path.exists(key_path):
        logger.error("Arquivo de chave nao encontrado: %s", key_path)
        return None

    key_types = [
        (paramiko.RSAKey, "RSA"),
        (paramiko.Ed25519Key, "Ed25519"),
        (paramiko.ECDSAKey, "ECDSA"),
    ]

    for key_class, key_name in key_types:
        try:
            key = key_class.from_private_key_file(key_path)
            logger.info("Chave %s carregada com sucesso", key_name)
            return key
        except paramiko.ssh_exception.PasswordRequiredException:
            logger.error("Chave %s requer senha (nao suportado)", key_name)
            continue
        except Exception as exc:
            logger.debug("Tentativa %s falhou: %s", key_name, exc)
            continue

    if key_path.lower().endswith(".ppk"):
        logger.error("Arquivo .ppk detectado. Formato nao suportado pelo paramiko.")
        logger.error("Converta a chave usando PuTTYgen:")
        logger.error("  1. Abra o PuTTYgen")
        logger.error("  2. Carregue o arquivo .ppk")
        logger.error("  3. Conversions > Export OpenSSH key")
        logger.error("  4. Salve como id_ce ou id_rj (sem extensao .ppk)")
    else:
        logger.error("Formato de chave nao reconhecido ou chave invalida: %s", key_path)
        logger.error("Certifique-se de que a chave esta no formato OpenSSH")

    return None


def create_sftp_connection(host: str, user: str, private_key):
    logger.info("Conectando via SFTP ao host %s com usuario %s", host, user)
    try:
        transport = paramiko.Transport((host, 22))
        transport.connect(username=user, pkey=private_key)
        sftp = paramiko.SFTPClient.from_transport(transport)
        logger.info("Conexao SFTP estabelecida com %s", host)
        return sftp, transport
    except paramiko.AuthenticationException:
        logger.error("Falha de autenticacao no host %s", host)
        return None, None
    except paramiko.SSHException as exc:
        logger.error("Erro SSH ao conectar em %s: %s", host, exc)
        return None, None
    except Exception as exc:
        logger.error("Erro ao conectar via SFTP em %s: %s", host, exc)
        return None, None


def download_files(
    sftp, remote_path: str, files: List[str], local_dir: str
) -> Tuple[List[str], List[str]]:
    os.makedirs(local_dir, exist_ok=True)
    downloaded: List[str] = []
    failed: List[str] = []

    for file_name in files:
        remote_file = os.path.join(remote_path, file_name).replace("\\", "/")
        local_file = os.path.join(local_dir, file_name)

        try:
            logger.info("Baixando: %s", remote_file)
            sftp.get(remote_file, local_file)
            logger.info("Arquivo salvo em: %s", local_file)
            downloaded.append(file_name)

            if file_name.endswith(".zip"):
                extract_zip(local_file, local_dir)

        except FileNotFoundError:
            logger.error("Arquivo nao encontrado: %s", remote_file)
            failed.append(file_name)
        except PermissionError:
            logger.error("Permissao negada para: %s", remote_file)
            failed.append(file_name)
        except Exception as exc:
            logger.error("Erro ao baixar %s: %s", file_name, exc)
            failed.append(file_name)

    return downloaded, failed


def extract_zip(zip_path: str, extract_dir: str) -> None:
    try:
        logger.info("Extraindo: %s", zip_path)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
        logger.info("Arquivo extraido em: %s", extract_dir)

        os.remove(zip_path)
        logger.info("Arquivo ZIP removido: %s", zip_path)
    except zipfile.BadZipFile:
        logger.error("Arquivo ZIP corrompido: %s", zip_path)
    except Exception as exc:
        logger.error("Erro ao extrair %s: %s", zip_path, exc)


def close_sftp_connection(sftp, transport) -> None:
    try:
        if sftp:
            sftp.close()
        if transport:
            transport.close()
        logger.info("Conexao SFTP encerrada")
    except Exception as exc:
        logger.error("Erro ao fechar conexao SFTP: %s", exc)
