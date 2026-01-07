CREATE TABLE IF NOT EXISTS users (
    id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username   TEXT NOT NULL,
    email      TEXT NOT NULL,
    pw_hash    CHARACTER[256] NOT NULL
);

CREATE TABLE IF NOT EXISTS stories (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    creator_id  UUID NOT NULL REFERENCES users(id),
    created_at  TIMESTAMPTZ DEFAULT now(),
    title       TEXT NOT NULL,
    contents    TEXT NOT NULL
);