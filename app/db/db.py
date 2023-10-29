import sqlite3
import os
from flask import current_app, g

def get_db():
    # L'objet g est un objet créé par le framework Flask à chaque requête.
    # Il agit comme une variable globale pour chaque requête
    # Dans notre cas, si l'objet g n'a pas d'attribut 'db', on lui ajoute une connexion à la base de données
    if 'db' not in g:
        #g.db = sqlite3.connect(os.path.join(current_app.root_path, "db","app.db" ), detect_types=sqlite3.PARSE_DECLTYPES)
        g.db = sqlite3.connect(os.path.join(current_app.root_path, "db", current_app.config['DATABASE']), detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db():
    # Suppression de l'attribut 'db' dans l'objet g
    db = g.pop('db', None)

    # Au cas où la suppression n'aurait pas fonctionné, on ferme la connexion.
    if db is not None:
        db.close()