-- This is a sample SQL schema if you’re using SQLite/MySQL

CREATE TABLE property (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    location TEXT NOT NULL
);
