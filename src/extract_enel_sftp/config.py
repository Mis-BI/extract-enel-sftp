from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


@dataclass(frozen=True)
class SshKeyHostConfig:
    host: str
    user: str
    name: str
    key_path: str


@dataclass(frozen=True)
class ExtractorConfig:
    vpn_portal: str
    globalprotect_path: str
    keys_base_path: str
    hosts: List[SshKeyHostConfig]
    remote_path: str
    files: List[str]
    download_base_dir: str


@dataclass(frozen=True)
class SqlServerConfig:
    user: str
    password: str
    host: str
    port: str
    database: str
    table: str


@dataclass(frozen=True)
class EfetividadeConfig:
    download_base_dir: str
    expected_columns: List[str]
    sql_server: SqlServerConfig


@dataclass(frozen=True)
class PasswordSftpConfig:
    host: str
    port: int
    username: str
    password: str
    remote_path: str
    file_prefix: str
    file_month: str
    download_base_dir: str


EXPECTED_COLUMNS = [
    "CO",
    "REFERENCIA",
    "NUMERO_CLIENTE",
    "MATRICULA_LEITURISTA",
    "SECTOR",
    "LOCALIDADE",
    "ZONA",
    "MUNICIPIO",
    "BAIRRO",
    "IRREG_LIDA",
    "IRREG_OPERADOR",
    "NUMERO_MEDIDOR",
    "DESC_IRREG_LIDA",
    "DESC_IRREG_OPERADOR",
    "DX",
    "TELEMEDIDO",
    "UNIDADE_LEITURA",
    "CODIGO_MUNICIPIO",
    "FAT_BIMESTRAL",
    "LATITUDE",
    "LONGITUDE",
]


def default_extractor_config() -> ExtractorConfig:
    vpn_portal = _env("ENEL_VPN_PORTAL", "vpn.enel.com")
    globalprotect_path = _env(
        "ENEL_GLOBALPROTECT_PATH",
        r"C:\Program Files\Palo Alto Networks\GlobalProtect\PanGPA.exe",
    )
    keys_base_path = _env(
        "ENEL_KEYS_BASE_PATH",
        r"\\10.71.201.243\mis$\DADOS OPERACOES\ENEL\INDUSTRIA ON DEMAND\CHAVES",
    )
    hosts = [
        SshKeyHostConfig(
            host=_env("ENEL_HOST_CE", "10.154.78.75"),
            user=_env("ENEL_HOST_CE_USER", "sftpce"),
            name="HOST_CE",
            key_path=f"{keys_base_path}\\CE\\id_rsa_22052020_204527",
        )
    ]
    remote_path = _env("ENEL_REMOTE_PATH", "/synergia/archivos/batch/lst/diarios/")
    files = [
        "COELCE_elaazisysd00_grandesclientes.txt.zip",
        "COELCE_elaazisysd00_maecartas.txt.zip",
        "COELCE_elaazisysd00_ordemfilhas.txt.zip",
    ]
    download_base_dir = _env("ENEL_DOWNLOAD_BASE_DIR", "./archives")

    return ExtractorConfig(
        vpn_portal=vpn_portal,
        globalprotect_path=globalprotect_path,
        keys_base_path=keys_base_path,
        hosts=hosts,
        remote_path=remote_path,
        files=files,
        download_base_dir=download_base_dir,
    )


def default_efetividade_config() -> EfetividadeConfig:
    sql_server = SqlServerConfig(
        user=_env("ENEL_SQL_SERVER_USER", "FSABA/jmoreira"),
        password=_env("ENEL_SQL_SERVER_PASSWORD", "Tel*2025@!"),
        host=_env("ENEL_SQL_SERVER_HOST", "172.26.0.37"),
        port=_env("ENEL_SQL_SERVER_PORT", "1433"),
        database=_env("ENEL_SQL_SERVER_DB", "ENEL"),
        table=_env("ENEL_SQL_SERVER_TABLE", "EfetividadeLeitura"),
    )

    return EfetividadeConfig(
        download_base_dir=_env(
            "ENEL_EFETIVIDADE_DIR", "./archives/EfetividadeLeitura - Copia"
        ),
        expected_columns=EXPECTED_COLUMNS,
        sql_server=sql_server,
    )


def default_password_sftp_config() -> PasswordSftpConfig:
    return PasswordSftpConfig(
        host=_env("ENEL_TEST_SFTP_HOST", "10.152.153.33"),
        port=int(_env("ENEL_TEST_SFTP_PORT", "22")),
        username=_env("ENEL_TEST_SFTP_USER", "EXPLOTACAO"),
        password=_env("ENEL_TEST_SFTP_PASSWORD", "Explota@2023"),
        remote_path=_env(
            "ENEL_TEST_SFTP_REMOTE_PATH", "/D:/LOGS/Coelce/ExtratorEfetividadeLeitura"
        ),
        file_prefix=_env("ENEL_TEST_FILE_PREFIX", "BaseMes"),
        file_month=_env("ENEL_TEST_FILE_MONTH", "202602"),
        download_base_dir=_env("ENEL_TEST_DOWNLOAD_BASE_DIR", "./archives"),
    )


def default_password_sftp_regex_config() -> PasswordSftpConfig:
    return PasswordSftpConfig(
        host=_env("ENEL_TEST_SFTP_HOST", "10.152.153.33"),
        port=int(_env("ENEL_TEST_SFTP_PORT", "22")),
        username=_env("ENEL_TEST_SFTP_USER", "EXPLOTACAO"),
        password=_env("ENEL_TEST_SFTP_PASSWORD", "Explota@2023"),
        remote_path=_env(
            "ENEL_TEST_SFTP_REMOTE_PATH", "/D:/LOGS/Coelce/ExtratorEfetividadeLeitura"
        ),
        file_prefix=_env("ENEL_TEST_FILE_PREFIX", "BaseMes"),
        file_month=_env("ENEL_TEST_FILE_MONTH", "202601"),
        download_base_dir=_env(
            "ENEL_TEST_DOWNLOAD_BASE_DIR", "./archives/EfetividadeLeitura"
        ),
    )
