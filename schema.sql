DROP TABLE IF EXISTS acts;
DROP TABLE IF EXISTS wordraw;
DROp TABLE IF EXISTS wordnorm;
DROP TABLE IF EXISTS wordmapping;
DROP TABLE IF EXISTS docindraw;
DROP TABLE IF EXISTS docindnorm;
DROP TABLE IF EXISTS innerdocindraw;
DROP TABLE IF EXISTS innerdocindnorm;

CREATE TABLE acts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL
);

CREATE TABLE wordraw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL
);

CREATE TABLE wordnorm (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL
);

CREATE TABLE wordmapping(
    rawid INTEGER NOT NULL,
    norm INTEGER NOT NULL
        FOREIGN KEY (rawid) REFERENCES wordraw(id)
);

CREATE TABLE docindraw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word INTEGER NOT NULL,
    postinglist TEXT NOT NULL,
        FOREIGN KEY (word) REFERENCES wordraw(id)
);

CREATE TABLE docindnorm (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word INTEGER NOT NULL,
    postinglist TEXT NOT NULL,
        FOREIGN KEY (word) REFERENCES wordnorm(id)
);

CREATE TABLE innerdocindraw(
    word INTEGER NOT NULL,
    act INTEGER NOT NULL,
    postinglist TEXT NOT NULL,
        FOREIGN KEY (word) REFERENCES wordraw(id)
        FOREIGN KEY (act) REFERENCES acts(id)

);

CREATE TABLE innerdocindnorm(
    word INTEGER NOT NULL,
    act INTEGER NOT NULL,
    postinglist TEXT NOT NULL,
        FOREIGN KEY (word) REFERENCES wordnorm(id)
        FOREIGN KEY (act) REFERENCES acts(id)
);