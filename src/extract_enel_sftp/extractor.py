import logging
import os
from dataclasses import dataclass
from typing import Dict, List

from .config import ExtractorConfig, SshKeyHostConfig
from .sftp_client import (
    close_sftp_connection,
    create_sftp_connection,
    download_files,
    load_private_key,
)
from .vpn import connect_vpn, disconnect_vpn

logger = logging.getLogger(__name__)


@dataclass
class HostResult:
    success: bool
    downloaded: List[str]
    failed: List[str]


def process_host(config: ExtractorConfig, host_config: SshKeyHostConfig) -> HostResult:
    logger.info("%s", "=" * 50)
    logger.info("Processando %s (%s)", host_config.name, host_config.host)
    logger.info("%s", "=" * 50)

    private_key = load_private_key(host_config.key_path)
    if not private_key:
        logger.error(
            "Nao foi possivel carregar a chave para %s. Pulando.", host_config.name
        )
        return HostResult(False, [], config.files)

    local_dir = config.download_base_dir
    if host_config.name.startswith("HOST_"):
        local_dir = os.path.join(
            config.download_base_dir, host_config.name.replace("HOST_", "")
        )

    sftp, transport = create_sftp_connection(
        host_config.host, host_config.user, private_key
    )
    if not sftp:
        logger.error("Nao foi possivel conectar ao %s. Pulando.", host_config.name)
        return HostResult(False, [], config.files)

    try:
        downloaded, failed = download_files(
            sftp, config.remote_path, config.files, local_dir
        )
        logger.info(
            "%s: %s arquivos baixados, %s falhas",
            host_config.name,
            len(downloaded),
            len(failed),
        )
        return HostResult(True, downloaded, failed)
    finally:
        close_sftp_connection(sftp, transport)


def run_extraction(config: ExtractorConfig) -> Dict[str, HostResult]:
    logger.info("%s", "=" * 60)
    logger.info("INICIANDO EXTRACAO DE ARQUIVOS VIA SFTP")
    logger.info("%s", "=" * 60)

    if not connect_vpn(config.globalprotect_path):
        logger.error("Nao foi possivel conectar a VPN. Abortando.")
        return {}

    results: Dict[str, HostResult] = {}
    try:
        for host_config in config.hosts:
            result = process_host(config, host_config)
            results[host_config.name] = result

        logger.info("%s", "=" * 60)
        logger.info("RESUMO DA EXTRACAO")
        logger.info("%s", "=" * 60)
        for name, result in results.items():
            status = "OK" if result.success else "FALHA"
            logger.info(
                "%s: %s | Baixados: %s | Falhas: %s",
                name,
                status,
                len(result.downloaded),
                len(result.failed),
            )
    finally:
        disconnect_vpn(config.globalprotect_path)

    logger.info("%s", "=" * 60)
    logger.info("EXTRACAO FINALIZADA")
    logger.info("%s", "=" * 60)
    return results
