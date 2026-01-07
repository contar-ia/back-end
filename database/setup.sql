CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- Habilita extensao de criacao de uuid auto generated

CREATE TABLE IF NOT EXISTS users (
    id   UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    username   TEXT NOT NULL,
    email      TEXT NOT NULL,
    pw_hash    CHARACTER[256] NOT NULL
);

CREATE TABLE IF NOT EXISTS stories (
    id          UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    creator_id  BIGINT NOT NULL REFERENCES users(id),
    created_at  TIMESTAMPTZ DEFAULT now(),
    title       TEXT NOT NULL,
    contents    TEXT NOT NULL
);
