import argparse
from dataclasses import replace
from typing import List, Optional

from .config import (
    default_efetividade_config,
    default_extractor_config,
    default_password_sftp_config,
    default_password_sftp_regex_config,
)
from .etl.efetividade import run_efetividade_etl
from .extractor import run_extraction
from .logging_config import setup_logging
from .processing.ordens_filhas import processar_ordens_filhas
from .tools.sftp_password import run_password_test
from .tools.sftp_password_regex import run_password_regex_test


def _apply_test_overrides(config, args):
    updated = config
    if args.file_month:
        updated = replace(updated, file_month=args.file_month)
    if args.file_prefix:
        updated = replace(updated, file_prefix=args.file_prefix)
    if args.download_dir:
        updated = replace(updated, download_base_dir=args.download_dir)
    if args.remote_path:
        updated = replace(updated, remote_path=args.remote_path)
    return updated


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="enel-sftp",
        description="Extracao SFTP e processamento de dados ENEL",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("extract", help="Executa a extracao via SFTP")
    subparsers.add_parser("etl", help="Executa a carga de Efetividade no SQL Server")

    ordens_parser = subparsers.add_parser(
        "ordens-filhas", help="Processa o arquivo de ordens filhas"
    )
    ordens_parser.add_argument(
        "--arquivo", help="Caminho do arquivo de ordens filhas"
    )

    test_parser = subparsers.add_parser(
        "test-sftp", help="Teste SFTP com filtro por prefixo/mes"
    )
    test_parser.add_argument("--file-month", dest="file_month")
    test_parser.add_argument("--file-prefix", dest="file_prefix")
    test_parser.add_argument("--download-dir", dest="download_dir")
    test_parser.add_argument("--remote-path", dest="remote_path")

    regex_parser = subparsers.add_parser(
        "test-sftp-regex", help="Teste SFTP com filtro regex"
    )
    regex_parser.add_argument("--file-month", dest="file_month")
    regex_parser.add_argument("--file-prefix", dest="file_prefix")
    regex_parser.add_argument("--download-dir", dest="download_dir")
    regex_parser.add_argument("--remote-path", dest="remote_path")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "extract":
        setup_logging()
        config = default_extractor_config()
        run_extraction(config)
        return 0

    if args.command == "etl":
        config = default_efetividade_config()
        run_efetividade_etl(config)
        return 0

    if args.command == "ordens-filhas":
        df = processar_ordens_filhas(args.arquivo)
        print(df.head())
        print(f"Linhas processadas: {len(df)}")
        return 0

    if args.command == "test-sftp":
        config = _apply_test_overrides(default_password_sftp_config(), args)
        run_password_test(config)
        return 0

    if args.command == "test-sftp-regex":
        config = _apply_test_overrides(default_password_sftp_regex_config(), args)
        run_password_regex_test(config)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
