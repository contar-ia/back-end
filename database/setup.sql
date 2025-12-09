CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- Habilita extensao de criacao de uuid auto generated

CREATE TABLE IF NOT EXISTS "historias" (
    "id" UUID DEFAULT uuid_generate_v4() PRIMARY KEY
);