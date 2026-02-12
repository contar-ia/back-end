-- Tabela de Usuarios
CREATE TABLE IF NOT EXISTS users (
    id           UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username     TEXT NOT NULL UNIQUE,
    email        TEXT NOT NULL UNIQUE,
    pw_hash      TEXT NOT NULL,
    institution  TEXT,
    bio          TEXT
);

-- Tabela de Historias
CREATE TABLE IF NOT EXISTS stories (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    creator_id  UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ DEFAULT now(),
    title       TEXT NOT NULL,
    contents    TEXT NOT NULL
);

-- Nova Tabela de Sessoes
CREATE TABLE IF NOT EXISTS sessions (
    session_token UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at    TIMESTAMPTZ NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT now()
);

-- Tabela de leituras de historias
CREATE TABLE IF NOT EXISTS story_reads (
    id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    story_id   UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    read_at    TIMESTAMPTZ DEFAULT now(),
    UNIQUE (user_id, story_id)
);

-- Tabela de historias salvas
CREATE TABLE IF NOT EXISTS story_saves (
    id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    story_id   UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    saved_at   TIMESTAMPTZ DEFAULT now(),
    UNIQUE (user_id, story_id)
);
