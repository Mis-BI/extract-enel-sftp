import os
import subprocess
import logging
import time
import zipfile
import paramiko

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

VPN_PORTAL = "vpn.enel.com"
GLOBALPROTECT_PATH = r"C:\Program Files\Palo Alto Networks\GlobalProtect\PanGPA.exe"

KEYS_BASE_PATH = r"\\10.71.201.243\mis$\DADOS OPERACOES\ENEL\INDUSTRIA ON DEMAND\CHAVES"

HOSTS = [
    {
        "host": "10.154.78.75",
        "user": "sftpce",
        "name": "HOST_CE",
        "key_path": f"{KEYS_BASE_PATH}\\CE\\id_rsa_22052020_204527"
    }
]

REMOTE_PATH = "/synergia/archivos/batch/lst/diarios/"
FILES = [
    "COELCE_elaazisysd00_grandesclientes.txt.zip",
    "COELCE_elaazisysd00_maecartas.txt.zip",
    "COELCE_elaazisysd00_ordemfilhas.txt.zip"
]
DOWNLOAD_BASE_DIR = "./archives"


def check_vpn_connected():
    """Verifica se a VPN está conectada checando a interface PANGP"""
    try:
        result = subprocess.run(
            ["route", "print"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return "PANGP Virtual Ethernet Adapter" in result.stdout
    except Exception:
        return False


def connect_vpn():
    logger.info("Verificando conexão VPN...")
    
    if check_vpn_connected():
        logger.info("VPN já está conectada!")
        return True
    
    logger.info("VPN não conectada. Abrindo GlobalProtect...")
    
    try:
        subprocess.Popen([GLOBALPROTECT_PATH])
    except FileNotFoundError:
        logger.error(f"GlobalProtect não encontrado em: {GLOBALPROTECT_PATH}")
        return False
    except Exception as e:
        logger.error(f"Erro ao iniciar GlobalProtect: {e}")
        return False
    
    logger.info("="*50)
    logger.info("POR FAVOR, CONECTE-SE À VPN")
    logger.info("Clique em 'Conectar' na janela do GlobalProtect")
    logger.info("(Pode ser necessário autenticação MFA)")
    logger.info("="*50)
    
    logger.info("Aguardando conexão VPN (verificando a cada 5 segundos)...")
    for i in range(36):  # 3 minutos de timeout
        time.sleep(5)
        if check_vpn_connected():
            logger.info("VPN conectada com sucesso!")
            return True
        if (i + 1) % 6 == 0:  # A cada 30 segundos
            logger.info(f"Ainda aguardando VPN... ({(i+1)*5}s)")
    
    logger.error("Timeout: VPN não conectada após 3 minutos")
    return False


def disconnect_vpn():
    logger.info("Desconectando da VPN")
    try:
        subprocess.run(
            [GLOBALPROTECT_PATH, "-d"],
            check=True,
            timeout=30
        )
        logger.info("VPN desconectada com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao desconectar da VPN: {e}")
        return False


def load_private_key(key_path):
    logger.info(f"Carregando chave privada: {key_path}")
    
    if not os.path.exists(key_path):
        logger.error(f"Arquivo de chave não encontrado: {key_path}")
        return None

    key_types = [
        (paramiko.RSAKey, "RSA"),
        (paramiko.Ed25519Key, "Ed25519"),
        (paramiko.ECDSAKey, "ECDSA")
    ]

    for key_class, key_name in key_types:
        try:
            key = key_class.from_private_key_file(key_path)
            logger.info(f"Chave {key_name} carregada com sucesso")
            return key
        except paramiko.ssh_exception.PasswordRequiredException:
            logger.error(f"Chave {key_name} requer senha (não suportado)")
            continue
        except Exception as e:
            logger.debug(f"Tentativa {key_name} falhou: {e}")
            continue

    if key_path.lower().endswith('.ppk'):
        logger.error("Arquivo .ppk detectado. Este formato não é suportado diretamente pelo paramiko.")
        logger.error("Por favor, converta a chave usando PuTTYgen:")
        logger.error("  1. Abra o PuTTYgen")
        logger.error("  2. Carregue o arquivo .ppk")
        logger.error("  3. Vá em Conversions > Export OpenSSH key")
        logger.error("  4. Salve como id_ce ou id_rj (sem extensão .ppk)")
    else:
        logger.error(f"Formato de chave não reconhecido ou chave inválida: {key_path}")
        logger.error("Certifique-se de que a chave está no formato OpenSSH")
    
    return None


def create_sftp_connection(host, user, private_key):
    logger.info(f"Conectando via SFTP ao host {host} com usuário {user}")
    try:
        transport = paramiko.Transport((host, 22))
        transport.connect(username=user, pkey=private_key)
        sftp = paramiko.SFTPClient.from_transport(transport)
        logger.info(f"Conexão SFTP estabelecida com {host}")
        return sftp, transport
    except paramiko.AuthenticationException:
        logger.error(f"Falha de autenticação no host {host}")
        return None, None
    except paramiko.SSHException as e:
        logger.error(f"Erro SSH ao conectar em {host}: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Erro ao conectar via SFTP em {host}: {e}")
        return None, None


def download_files(sftp, remote_path, files, local_dir):
    os.makedirs(local_dir, exist_ok=True)
    downloaded = []
    failed = []

    for file in files:
        remote_file = os.path.join(remote_path, file).replace("\\", "/")
        local_file = os.path.join(local_dir, file)

        try:
            logger.info(f"Baixando: {remote_file}")
            sftp.get(remote_file, local_file)
            logger.info(f"Arquivo salvo em: {local_file}")
            downloaded.append(file)
            
            if file.endswith('.zip'):
                extract_zip(local_file, local_dir)
                
        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado: {remote_file}")
            failed.append(file)
        except PermissionError:
            logger.error(f"Permissão negada para: {remote_file}")
            failed.append(file)
        except Exception as e:
            logger.error(f"Erro ao baixar {file}: {e}")
            failed.append(file)

    return downloaded, failed


def extract_zip(zip_path, extract_dir):
    try:
        logger.info(f"Extraindo: {zip_path}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        logger.info(f"Arquivo extraído em: {extract_dir}")
        
        os.remove(zip_path)
        logger.info(f"Arquivo ZIP removido: {zip_path}")
    except zipfile.BadZipFile:
        logger.error(f"Arquivo ZIP corrompido: {zip_path}")
    except Exception as e:
        logger.error(f"Erro ao extrair {zip_path}: {e}")


def close_sftp_connection(sftp, transport):
    try:
        if sftp:
            sftp.close()
        if transport:
            transport.close()
        logger.info("Conexão SFTP encerrada")
    except Exception as e:
        logger.error(f"Erro ao fechar conexão SFTP: {e}")


def process_host(host_config):
    host = host_config["host"]
    user = host_config["user"]
    name = host_config["name"]
    key_path = host_config["key_path"]

    logger.info(f"{'='*50}")
    logger.info(f"Processando {name} ({host})")
    logger.info(f"{'='*50}")

    private_key = load_private_key(key_path)
    if not private_key:
        logger.error(f"Não foi possível carregar a chave para {name}. Pulando para o próximo host.")
        return False, [], FILES

    local_dir = os.path.join(DOWNLOAD_BASE_DIR, name.replace("HOST_", ""))

    sftp, transport = create_sftp_connection(host, user, private_key)
    if not sftp:
        logger.error(f"Não foi possível conectar ao {name}. Pulando para o próximo host.")
        return False, [], FILES

    try:
        downloaded, failed = download_files(sftp, REMOTE_PATH, FILES, local_dir)
        logger.info(f"{name}: {len(downloaded)} arquivos baixados, {len(failed)} falhas")
        return True, downloaded, failed
    finally:
        close_sftp_connection(sftp, transport)


def main():
    logger.info("="*60)
    logger.info("INICIANDO EXTRAÇÃO DE ARQUIVOS VIA SFTP")
    logger.info("="*60)

    if not connect_vpn():
        logger.error("Não foi possível conectar à VPN. Abortando.")
        return

    try:
        results = {}
        for host_config in HOSTS:
            success, downloaded, failed = process_host(host_config)
            results[host_config["name"]] = {
                "success": success,
                "downloaded": downloaded,
                "failed": failed
            }

        logger.info("="*60)
        logger.info("RESUMO DA EXTRAÇÃO")
        logger.info("="*60)
        for name, result in results.items():
            status = "OK" if result["success"] else "FALHA"
            logger.info(f"{name}: {status} | Baixados: {len(result['downloaded'])} | Falhas: {len(result['failed'])}")

    finally:
        disconnect_vpn()

    logger.info("="*60)
    logger.info("EXTRAÇÃO FINALIZADA")
    logger.info("="*60)


if __name__ == "__main__":
    main()
