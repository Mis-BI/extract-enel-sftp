# ENEL SFTP Extractor & Data Processor

Este projeto consiste em um conjunto de scripts Python para automatizar a extração de arquivos operacionais via SFTP, processamento de dados (ETL) e carga em banco de dados SQL Server. O sistema foi desenhado para interagir com a infraestrutura da ENEL (VPN, SFTP) e processar arquivos de "Efetividade de Leitura" e "Ordens Filhas".

## 📋 Pré-requisitos

- **Python 3.8+**
- **Acesso à VPN da ENEL**: O script `sftp_extractor.py` tenta conectar automaticamente via GlobalProtect (`PanGPA.exe`), mas é necessário ter o cliente instalado.
- **Drivers ODBC**: Para conexão com SQL Server (`ODBC Driver 18 for SQL Server`).
- **Credenciais**: Chaves SSH para conexão SFTP e credenciais de banco de dados.

## 📦 Instalação

1. Clone o repositório.
2. Instale as dependências listadas:

```bash
pip install -r requirements.txt
```

> **Nota:** O script `dataframe_efetividade_da_leitura.py` requer adicionalmente `sqlalchemy` e `pyodbc`, que podem não estar no `requirements.txt` original. Caso necessário, instale com:
> `pip install sqlalchemy pyodbc`

## 🚀 Estrutura do Projeto

```text
extract-enel-sftp/
├── sftp_extractor.py                 # Script Principal: Gerencia VPN e download SFTP (Chave SSH)
├── dataframe_efetividade_da_leitura.py # ETL: Lê TXT baixados e insere no SQL Server
├── Base_mes_Efetividade.py           # Módulo: Lógica de processamento para 'Ordens Filhas'
├── sftp_teste.py                     # Teste: Download SFTP alternativo (Autenticação por Senha)
├── sftp_teste_2.py                   # Teste: Variação do teste anterior com filtro Regex
└── requirements.txt                  # Dependências do projeto
```

## 🛠 Detalhamento dos Scripts

### 1. `sftp_extractor.py` (Extração Principal)
Este é o script principal para extração de dados diários.

- **Funcionalidades**:
  - **Gerenciamento de VPN**: Verifica e tenta conectar à VPN GlobalProtect antes da execução.
  - **Autenticação Segura**: Utiliza chaves SSH (RSA/Ed25519) localizadas em um caminho de rede (`\\10.71.201.243...`).
  - **Extração Automática**: Baixa arquivos ZIP específicos (`grandesclientes`, `maecartas`, `ordemfilhas`) e os extrai automaticamente.
  - **Log**: Gera logs detalhados do processo.
- **Configuração**:
  - Variáveis globais no início do arquivo definem IPs, caminhos de chaves e diretórios remotos/locais.

### 2. `dataframe_efetividade_da_leitura.py` (ETL SQL Server)
Responsável por consolidar os arquivos baixados e enviá-los para o banco de dados.

- **Funcionalidades**:
  - Varre o diretório `./archives/EfetividadeLeitura - Copia` buscando arquivos `.txt`.
  - Lê arquivos CSV (separador `|`) e normaliza colunas.
  - Insere os dados na tabela `EfetividadeLeitura` no SQL Server (`172.26.0.37`).
- **Configuração**:
  - Credenciais do banco e mapeamento de colunas (`EXPECTED_COLUMNS`) definidos no início do script.

### 3. `Base_mes_Efetividade.py` (Lógica de Negócio)
Contém a função `processar_ordens_filhas` que encapsula a regra de negócio para tratamento do arquivo de Ordens Filhas.

- **Regras**:
  - Renomeia colunas genéricas (`Column1`, etc.) para nomes de negócio (`CO`, `REFERENCIA`, etc.).
  - Filtra estados indesejados (`04`, `09`).
  - Converte strings de data para objetos `datetime`.

### 4. `sftp_teste.py` e `sftp_teste_2.py` (Scripts de Teste)
Scripts auxiliares para testar conexão com um servidor SFTP diferente (`10.152.153.33`).

- **Uso**: Úteis para validar conectividade ou baixar arquivos de logs/efetividade ("BaseMes") de um diretório diferente, usando autenticação por senha (ao contrário do script principal que usa chave).
- **Diferença**: O `sftp_teste_2.py` implementa filtros de arquivo mais avançados usando Regex.

## ⚙️ Como Executar

### Passo 1: Extração
```bash
python sftp_extractor.py
```
*Certifique-se de estar em um ambiente onde o GlobalProtect possa ser acionado ou conecte a VPN manualmente antes.*

### Passo 2: Carga no Banco
```bash
python dataframe_efetividade_da_leitura.py
```

## ⚠️ Observações Importantes

- **Caminhos de Rede**: O script `sftp_extractor.py` faz referência a caminhos de rede Windows (`\\10.71.201.243...`). Certifique-se de ter acesso a esses caminhos.
- **Chaves SSH**: Chaves no formato `.ppk` (PuTTY) não são suportadas diretamente; devem ser convertidas para formato OpenSSH.
- **Segurança**: As credenciais de banco de dados e senhas SFTP estão hardcoded nos scripts (`dataframe_...py` e `sftp_teste...py`). Em um ambiente de produção rigoroso, recomenda-se mover para variáveis de ambiente.
