DROP TABLE IF EXISTS acts;
DROP TABLE IF EXISTS wordraw;
DROp TABLE IF EXISTS wordnorm;
DROP TABLE IF EXISTS wordmapping;
DROP TABLE IF EXISTS docindraw;
DROP TABLE IF EXISTS docindnorm;
DROP TABLE IF EXISTS termfreqraw;
DROP TABLE IF EXISTS termfreqnorm;
DROP TABLE IF EXISTS tfidfraw;
DROP TABLE IF EXISTS tfidfnorm;
--DROP TABLE IF EXISTS innerdocindraw;
--DROP TABLE IF EXISTS innerdocindnorm;

CREATE TABLE acts (
    id INTEGER PRIMARY KEY,
    act TEXT NOT NULL
);

CREATE TABLE wordraw (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL
);

CREATE TABLE wordnorm (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL
);

CREATE TABLE wordmapping(
    raww TEXT NOT NULL,
    norm TEXT NOT NULL
);

CREATE TABLE docindraw (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL,
    postinglist TEXT NOT NULL,
    docfreq INTEGER NOT NULL
);
--FOREIGN KEY (word) REFERENCES wordraw(id)

CREATE TABLE docindnorm (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL,
    postinglist TEXT NOT NULL,
    docfreq INTEGER NOT NULL
);
--FOREIGN KEY (word) REFERENCES wordnorm(id)

CREATE TABLE termfreqraw(
    id INTEGER PRIMARY KEY,
    actid INTEGER NOT NULL,
    word TEXT NOT NULL,
    termfreq INTEGER NOT NULL,
        FOREIGN KEY (actid) REFERENCES acts(id)
);

CREATE TABLE termfreqnorm(
    id INTEGER PRIMARY KEY,
    actid INTEGER NOT NULL,
    word TEXT NOT NULL,
    termfreq INTEGER NOT NULL,
        FOREIGN KEY (actid) REFERENCES acts(id)
);

CREATE TABLE tfidfraw(
    actid INTEGER PRIMARY KEY,
    vector TEXT NOT NULL
);

CREATE TABLE tfidfnorm(
    actid INTEGER PRIMARY KEY,
    vector TEXT NOT NULL
);
/*
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
*/