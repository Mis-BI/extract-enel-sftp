# Extract ENEL SFTP

Automacao para baixar arquivos operacionais via SFTP (ambiente ENEL), extrair ZIPs e, opcionalmente, processar a "Efetividade de Leitura" para carga em SQL Server.

## Visao Geral do Fluxo

1. `sftp_extractor.py` conecta na VPN, acessa o SFTP e baixa ZIPs diarios.
2. Os ZIPs sao extraidos em `./archives/<UF>` e removidos apos a extracao.
3. `dataframe_efetividade_da_leitura.py` consolida arquivos `.txt` e insere no SQL Server.

## Requisitos

- Python 3.8+
- Acesso a VPN da ENEL
- GlobalProtect instalado (PanGPA.exe) para uso da conexao automatica no Windows
- Chaves SSH OpenSSH sem senha (passphrase nao suportada no script)
- ODBC Driver 18 for SQL Server

## Instalacao

```bash
pip install -r requirements.txt
```

Para executar a carga no SQL Server:

```bash
pip install sqlalchemy pyodbc
```

## Estrutura do Projeto

```text
extract-enel-sftp/
├── sftp_extractor.py
├── dataframe_efetividade_da_leitura.py
├── Base_mes_Efetividade.py
├── sftp_teste.py
├── sftp_teste_2.py
└── requirements.txt
```

## Scripts e Configuracoes

### `sftp_extractor.py` (Extracao principal)

- Verifica VPN via interface `PANGP` e abre o GlobalProtect.
- Conecta por chave SSH no host configurado.
- Baixa e extrai:
  - `COELCE_elaazisysd00_grandesclientes.txt.zip`
  - `COELCE_elaazisysd00_maecartas.txt.zip`
  - `COELCE_elaazisysd00_ordemfilhas.txt.zip`

Configurar no topo do arquivo:

- `GLOBALPROTECT_PATH`
- `KEYS_BASE_PATH`
- `HOSTS`, `REMOTE_PATH`, `FILES`
- `DOWNLOAD_BASE_DIR`

### `dataframe_efetividade_da_leitura.py` (ETL SQL Server)

- Le todos os `.txt` em `./archives/EfetividadeLeitura - Copia`
- Normaliza colunas conforme `EXPECTED_COLUMNS`
- Carrega na tabela `EfetividadeLeitura`

Configurar no topo do arquivo:

- `DOWNLOAD_BASE_DIR`
- `SQL_SERVER_*`
- `EXPECTED_COLUMNS`

### `Base_mes_Efetividade.py` (Regra de negocio)

Funcao `processar_ordens_filhas` para tratar o arquivo de ordens filhas. Ajuste o mapeamento de colunas caso o layout mude.

### `sftp_teste.py` e `sftp_teste_2.py` (Testes)

Scripts auxiliares com autenticacao por senha para baixar arquivos por prefixo e mes. Edite `FILE_PREFIX`, `FILE_MONTH` e `REMOTE_PATH` para o periodo desejado.

## Como Executar

```bash
python sftp_extractor.py
```

```bash
python dataframe_efetividade_da_leitura.py
```

Para testes:

```bash
python sftp_teste.py
python sftp_teste_2.py
```

## Observacoes Importantes

- O fluxo principal foi desenhado para Windows (checagem da VPN e caminho do GlobalProtect). Em outros sistemas, conecte a VPN manualmente e ajuste o script.
- Credenciais de banco e SFTP estao hardcoded nos scripts de ETL e testes. Recomenda-se mover para variaveis de ambiente ou um vault.
- Caminhos de rede e IPs sao internos. Garanta acesso antes de executar.
