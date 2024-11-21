CREATE TABLE users
(
    id            SERIAL PRIMARY KEY,
    username      TEXT UNIQUE NOT NULL,
    password_hash BYTEA       NOT NULL
);

CREATE TABLE files
(
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users (id),
    filename    TEXT    NOT NULL,
    file_size   INTEGER NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE uptime
(
    id         SERIAL PRIMARY KEY,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
