-- Initialize the database.
-- Drop any existing data and create empty tables.

-- Database has users and tweet tables

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS tweet;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL
);

CREATE TABLE tweet (
  tweet_id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  body TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (author_id) REFERENCES user (id)
);