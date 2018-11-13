DROP TABLE IF EXISTS concl_types;
DROP TABLE IF EXISTS concls;
DROP TABLE IF EXISTS file_names;
DROP TABLE IF EXISTS act_found;
DROP TABLE IF EXISTS key_words_act;
DROP TABLE IF EXISTS key_words_concl_man;
DROP TABLE IF EXISTS key_words_concl_machine;
DROP TABLE IF EXISTS concl_to_key_words_man;
DROP TABLE IF EXISTS concl_to_key_words_machine;
DROP TABLE IF EXISTS file_to_act_data;


CREATE TABLE concl_types(
    [id] INTEGER PRIMARY KEY NOT NULL,
    [category] TEXT NOT NULL
);

CREATE TABLE concls(
    [id] INTEGER PRIMARY KEY NOT NULL,
    [txt] TEXT NOT NULL,
    [concl_type] INTEGER NOT NULL,
    FOREIGN KEY (concl_type) REFERENCES concl_types (id)
);

CREATE TABLE file_names(
    [id] INTEGER PRIMARY KEY NOT NULL,
    [txt] TEXT NOT NULL,
    [concl_id] INTEGER NOT NULL,
    FOREIGN KEY (concl_id) REFERENCES concls (id)
);

CREATE TABLE act_found(
    [id] INTEGER PRIMARY KEY NOT NULL,
    [reqs] TEXT NOT NULL,
    [key_words] TEXT NOT NULL,
    [descr] TEXT NOT NULL
);

CREATE TABLE key_words_act(
    [id] INTEGER PRIMARY KEY NOT NULL,
    [txt] TEXT NOT NULL
);

CREATE TABLE key_words_concl_man(
    [id] INTEGER PRIMARY KEY NOT NULL,
    [txt] TEXT NOT NULL
);

CREATE TABLE key_words_concl_machine(
    [id] INTEGER PRIMARY KEY NOT NULL,
    [txt] TEXT NOT NULL
);

CREATE TABLE act_to_key_words(
    [act_id] INTEGER NOT NULL,
    [key_word_id] INTEGER NOT NULL,
    PRIMARY KEY (act_id, key_word_id),
    FOREIGN KEY (act_id) REFERENCES act_found (id),
    FOREIGN KEY (key_word_id) REFERENCES key_words_act (id)
);

CREATE TABLE concl_to_key_words_man(
    [concl_id] INTEGER NOT NULL,
    [key_word_id] INTEGER NOT NULL,
    PRIMARY KEY (concl_id, key_word_id),
    FOREIGN KEY (concl_id) REFERENCES concls (id),
    FOREIGN KEY (key_word_id) REFERENCES key_words_concl_man (id)
);

CREATE TABLE concl_to_key_words_machine(
    [concl_id] INTEGER NOT NULL,
    [key_word_id] INTEGER NOT NULL,
    PRIMARY KEY (concl_id, key_word_id),
    FOREIGN KEY (concl_id) REFERENCES concls (id),
    FOREIGN KEY (key_word_id) REFERENCES key_words_concl_machine (id)
);

CREATE TABLE file_to_act_data(
    [file_ind] INTEGER NOT NULL,
    [act_id] INTEGER NOT NULL,
    [correspond_to_concl] INTEGER NOT NULL,
    PRIMARY KEY (file_ind, act_id),
    FOREIGN KEY (file_ind) REFERENCES file_names (id),
    FOREIGN KEY (act_id) REFERENCES act_found (id)
);

