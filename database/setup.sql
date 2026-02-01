-- Tabela de Usuários (Adicionei UNIQUE para garantir integridade)
CREATE TABLE IF NOT EXISTS users (
    id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username   TEXT NOT NULL UNIQUE,
    email      TEXT NOT NULL UNIQUE,
    pw_hash    TEXT NOT NULL
);

-- Tabela de Histórias
CREATE TABLE IF NOT EXISTS stories (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    creator_id  UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ DEFAULT now(),
    title       TEXT NOT NULL,
    contents    TEXT NOT NULL
);

-- Nova Tabela de Sessões
CREATE TABLE IF NOT EXISTS sessions (
    session_token UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at    TIMESTAMPTZ NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT now()
);