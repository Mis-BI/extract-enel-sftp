import logging
import subprocess
import time

logger = logging.getLogger(__name__)


def check_vpn_connected() -> bool:
    try:
        result = subprocess.run(
            ["route", "print"], capture_output=True, text=True, timeout=10
        )
        return "PANGP Virtual Ethernet Adapter" in result.stdout
    except Exception:
        return False


def connect_vpn(globalprotect_path: str) -> bool:
    logger.info("Verificando conexao VPN...")

    if check_vpn_connected():
        logger.info("VPN ja esta conectada!")
        return True

    logger.info("VPN nao conectada. Abrindo GlobalProtect...")

    try:
        subprocess.Popen([globalprotect_path])
    except FileNotFoundError:
        logger.error("GlobalProtect nao encontrado em: %s", globalprotect_path)
        return False
    except Exception as exc:
        logger.error("Erro ao iniciar GlobalProtect: %s", exc)
        return False

    logger.info("=" * 50)
    logger.info("POR FAVOR, CONECTE-SE A VPN")
    logger.info("Clique em 'Conectar' na janela do GlobalProtect")
    logger.info("(Pode ser necessario autenticacao MFA)")
    logger.info("=" * 50)

    logger.info("Aguardando conexao VPN (verificando a cada 5 segundos)...")
    for i in range(36):
        time.sleep(5)
        if check_vpn_connected():
            logger.info("VPN conectada com sucesso!")
            return True
        if (i + 1) % 6 == 0:
            logger.info("Ainda aguardando VPN... (%ss)", (i + 1) * 5)

    logger.error("Timeout: VPN nao conectada apos 3 minutos")
    return False


def disconnect_vpn(globalprotect_path: str) -> bool:
    logger.info("Desconectando da VPN")
    try:
        subprocess.run([globalprotect_path, "-d"], check=True, timeout=30)
        logger.info("VPN desconectada com sucesso")
        return True
    except Exception as exc:
        logger.error("Erro ao desconectar da VPN: %s", exc)
        return False
