/*
===============================================================================
SCHEMA DO BANCO DE DADOS
===============================================================================

Este arquivo define a estrutura principal do banco de dados da aplicação.
O modelo foi projetado para suportar:

- Cadastro e autenticação de usuários
- Criação e armazenamento de histórias
- Gerenciamento de sessões autenticadas
- Controle de leitura de histórias
- Controle de histórias salvas/favoritas

===============================================================================
*/

-- ============================================================================
-- TABELA: users
-- ============================================================================
-- Responsável por armazenar os dados dos usuários cadastrados.
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id           UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    -- Identificador único do usuário.
    -- Gerado automaticamente usando gen_random_uuid().

    username     TEXT NOT NULL UNIQUE,
    -- Nome de usuário único no sistema.
    -- Restrição UNIQUE evita duplicidade.

    email        TEXT NOT NULL UNIQUE,
    -- Email do usuário.
    -- Também possui restrição UNIQUE para evitar múltiplos cadastros.

    pw_hash      TEXT NOT NULL,
    -- Hash da senha do usuário.
    -- Nunca armazenar senha em texto puro.

    institution  TEXT,
    -- Instituição associada ao usuário (opcional).
    -- Pode ser utilizada para contexto educacional.

    bio          TEXT
    -- Biografia curta do usuário (opcional).
);

-- ============================================================================
-- TABELA: stories
-- ============================================================================
-- Armazena as histórias criadas pelos usuários.
-- Cada história pertence a um criador (creator_id).
-- ============================================================================
CREATE TABLE IF NOT EXISTS stories (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    -- Identificador único da história.

    creator_id  UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    -- Usuário que criou a história.
    -- ON DELETE CASCADE garante que, ao deletar um usuário,
    -- todas as suas histórias também sejam removidas automaticamente.

    created_at  TIMESTAMPTZ DEFAULT now(),
    -- Data e hora de criação da história.
    -- Usa timezone para evitar inconsistências globais.

    title       TEXT NOT NULL,
    -- Título da história.

    contents    TEXT NOT NULL
    -- Conteúdo completo da história.
);

-- ============================================================================
-- TABELA: sessions
-- ============================================================================
-- Controla sessões ativas de usuários autenticados.
-- Utilizada para autenticação baseada em token.
-- ============================================================================
CREATE TABLE IF NOT EXISTS sessions (
    session_token UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    -- Token único da sessão.
    -- Funciona como identificador da sessão autenticada.

    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    -- Usuário dono da sessão.
    -- Se o usuário for deletado, suas sessões também são removidas.

    expires_at    TIMESTAMPTZ NOT NULL,
    -- Data e hora de expiração da sessão.
    -- Utilizada para invalidar sessões automaticamente.

    created_at    TIMESTAMPTZ DEFAULT now()
    -- Momento em que a sessão foi criada.
);

-- ============================================================================
-- TABELA: story_reads
-- ============================================================================
-- Registra quais histórias foram lidas por quais usuários.
-- Permite métricas de engajamento e histórico de leitura.
-- ============================================================================
CREATE TABLE IF NOT EXISTS story_reads (
    id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    -- Identificador único do registro de leitura.

    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    -- Usuário que realizou a leitura.

    story_id   UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    -- História que foi lida.

    read_at    TIMESTAMPTZ DEFAULT now(),
    -- Data e hora em que a leitura ocorreu.

    UNIQUE (user_id, story_id)
    -- Garante que um usuário não registre múltiplas leituras
    -- da mesma história (evita duplicidade).
);

-- ============================================================================
-- TABELA: story_saves
-- ============================================================================
-- Registra histórias salvas/favoritadas por usuários.
-- Permite funcionalidade de favoritos ou biblioteca pessoal.
-- ============================================================================
CREATE TABLE IF NOT EXISTS story_saves (
    id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    -- Identificador único do registro de salvamento.

    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    -- Usuário que salvou a história.

    story_id   UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    -- História que foi salva.

    saved_at   TIMESTAMPTZ DEFAULT now(),
    -- Data e hora em que a história foi salva.

    UNIQUE (user_id, story_id)
    -- Garante que um usuário não salve a mesma história mais de uma vez.
);
