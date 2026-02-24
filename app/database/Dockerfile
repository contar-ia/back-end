# ============================================================================
# IMAGEM BASE
# ============================================================================
# Utiliza a imagem oficial do PostgreSQL versão 17.2 baseada em Alpine 3.20.
# ============================================================================
FROM postgres:17.2-alpine3.20

# ============================================================================
# VARIÁVEIS DE AMBIENTE
# ============================================================================
# Estas variáveis são utilizadas pelo entrypoint oficial do PostgreSQL
# para configurar automaticamente o banco na primeira inicialização.
# ============================================================================

ENV POSTGRES_DB=contaria
# Nome do banco de dados que será criado automaticamente
# na primeira execução do container.

ENV POSTGRES_USER=contaria
# Usuário administrador inicial do banco.

ENV POSTGRES_PASSWORD=contaria
# Senha do usuário administrador.
# Em ambiente de produção, esta senha deve ser substituída
# por uma variável segura.

# ============================================================================
# SCRIPT DE INICIALIZAÇÃO
# ============================================================================
# Copia o arquivo setup.sql para o diretório especial:
#
#   /docker-entrypoint-initdb.d/
#
# Todo arquivo .sql ou .sh presente neste diretório será
# executado automaticamente na primeira inicialização do banco.
#
# Isso permite:
# - Criar tabelas
# - Inserir dados iniciais
# - Criar extensões
# - Configurar permissões
#
# O script só roda se o diretório de dados ainda não existir.
# ============================================================================
COPY setup.sql /docker-entrypoint-initdb.d/

# ============================================================================
# EXPOSIÇÃO DE PORTA
# ============================================================================
# Informa que o container utiliza a porta 5432,
# que é a porta padrão do PostgreSQL.
# ============================================================================
EXPOSE 5432
