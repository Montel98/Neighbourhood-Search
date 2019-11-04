import sqlite3
from flask import current_app, g

#current_app.config['DATABASE']

def get_db():
    if 'db' not in g:
        with sqlite3.connect("C:\\Users\Montel\.spyder-py3\db\db2.db", detect_types=sqlite3.PARSE_DECLTYPES) as g.db:
            g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    # remove reference to database
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    # create schema if it don't exist
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
