from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db.db import get_db
import os

# Création d'un blueprint contenant les routes ayant le préfixe /auth/...
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# Route /auth/register
@auth_bp.route('/register_student', methods=('GET', 'POST'))
def register():
    # Si des données de formulaire sont envoyées vers la route /register (ce qui est le cas lorsque le formulaire d'inscription est envoyé)
    if request.method == 'POST':

        # On récupère les champs 'username' et 'password' de la requête HTTP
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        telephone = request.form['phone']

        # On récupère la base de donnée
        db = get_db()

        # Si le nom d'utilisateur et le mot de passe ont bien une valeur
        # on essaie d'insérer l'utilisateur dans la base de données
        if username and password:
            try:
                user_with_email = db.execute("SELECT * FROM users WHERE mail = ?", (email,)).fetchone()
                user_with_telephone = db.execute("SELECT * FROM users WHERE telephone = ?", (telephone,)).fetchone()

                if user_with_email:
                    flash("Cet e-mail existe déjà.")
                    return redirect(url_for("auth.register"))

                if user_with_telephone:
                    flash("Ce numéro de téléphone existe déjà.")
                    return redirect(url_for("auth.register"))

                db.execute("INSERT INTO users (username, password, mail,telephone, role_id) VALUES (?, ?, ?, ?, ?)",
                           (username, generate_password_hash(password), email, telephone, '1'))
                # db.commit() permet de valider une modification de la base de données
                db.commit()
            except db.IntegrityError as e:
                print(e)

                # La fonction flash dans Flask est utilisée pour stocker un message dans la session de l'utilisateur
                # dans le but de l'afficher ultérieurement, généralement sur la page suivante après une redirection
                error = f"User {username} is already registered."
                flash(error)
                return redirect(url_for("auth.register"))

            return redirect(url_for("auth.login"))

        else:
            error = "Username or password invalid"
            flash(error)
            return redirect(url_for("auth.login"))
    else:
        # Si aucune donnée de formulaire n'est envoyée, on affiche le formulaire d'inscription
        return render_template('auth/register.html')


@auth_bp.route('/register_student', methods=('GET', 'POST'))
def register_student():
    # Si des données de formulaire sont envoyées vers la route /register (ce qui est le cas lorsque le formulaire d'inscription est envoyé)
    if request.method == 'POST':

        # On récupère les champs 'username' et 'password' de la requête HTTP
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        telephone = request.form['phone']

        # On récupère la base de donnée
        db = get_db()

        # Si le nom d'utilisateur et le mot de passe ont bien une valeur
        # on essaie d'insérer l'utilisateur dans la base de données
        if username and password:
            try:
                user_with_email = db.execute("SELECT * FROM users WHERE mail = ?", (email,)).fetchone()
                user_with_telephone = db.execute("SELECT * FROM users WHERE telephone = ?", (telephone,)).fetchone()

                if user_with_email:
                    flash("Cet e-mail existe déjà.")
                    return redirect(url_for("auth.register_student"))

                if user_with_telephone:
                    flash("Ce numéro de téléphone existe déjà.")
                    return redirect(url_for("auth.register_student"))

                db.execute("INSERT INTO users (username, password, mail,telephone, role_id) VALUES (?, ?, ?, ?, ?)",
                           (username, generate_password_hash(password), email, telephone, '2'))
                # db.commit() permet de valider une modification de la base de données
                db.commit()
            
            except db.IntegrityError as e:
                print(e)

                # La fonction flash dans Flask est utilisée pour stocker un message dans la session de l'utilisateur
                # dans le but de l'afficher ultérieurement, généralement sur la page suivante après une redirection
                error = f"User {username} is already registered."
                flash(error)
                return redirect(url_for("auth.register_student"))

            return redirect(url_for("auth.login"))

        else:
            error = "Username or password invalid"
            flash(error)
            return redirect(url_for("auth.login"))
    else:
        # Si aucune donnée de formulaire n'est envoyée, on affiche le formulaire d'inscription
        return render_template('auth/register_student.html')


# Route /auth/login

@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    # Si des données de formulaire sont envoyées vers la route /login (ce qui est le cas lorsque le formulaire de login est envoyé)
    if request.method == 'POST':

        # On récupère les champs 'username' et 'password' de la requête HTTP
        username = request.form['username']
        password = request.form['password']

        # On récupère la base de données
        db = get_db()

        # On récupère l'utilisateur avec le username spécifié (une contrainte dans la db indique que le nom d'utilisateur est unique)
        # La virgule après username est utilisée pour créer un tuple contenant une valeur unique
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        # Si aucun utilisateur n'est trouve ou si le mot de passe est incorrect
        # on crée une variable error
        error = None
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # S'il n'y pas d'erreur, on ajoute l'id de l'utilisateur dans une variable de session
        # De cette manière, à chaque requête de l'utilisateur, on pourra récupérer l'id dans le cookie session
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            # On redirige l'utilisateur vers la page principale une fois qu'il s'est connecté
            return redirect("/")

        else:
            # En cas d'erreur, on ajoute l'erreur dans la session et on redirige l'utilisateur vers le formulaire de login
            flash(error)
            return redirect(url_for("auth.login"))
    else:
        return render_template('auth/login.html')


# Route /auth/logout
@auth_bp.route('/logout')
def logout():
    # Se déconnecter consiste simplement à supprimer le cookie session
    session.clear()

    # On redirige l'utilisateur vers la page principale une fois qu'il s'est déconnecté
    return redirect("/")


# Fonction automatiquement appelée à chaque requête (avant d'entrer dans la route) sur une route appartenant au blueprint 'auth_bp'
# La fonction permet d'ajouter un attribut 'user' représentant l'utilisateur connecté dans l'objet 'g'
@auth_bp.before_app_request
def load_logged_in_user():
    # On récupère l'id de l'utilisateur stocké dans le cookie session
    user_id = session.get('user_id')

    # Si l'id de l'utilisateur dans le cookie session est nul, cela signifie que l'utilisateur n'est pas connecté
    # On met donc l'attribut 'user' de l'objet 'g' à None
    if user_id is None:
        g.user = None

    # Si l'id de l'utilisateur dans le cookie session n'est pas nul, on récupère l'utilisateur correspondant et on stocke
    # l'utilisateur comme un attribut de l'objet 'g'
    else:
        # On récupère la base de données et on récupère l'utilisateur correspondant à l'id stocké dans le cookie session
        db = get_db()
        g.user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()


@auth_bp.route('/select_role', methods=('GET', 'POST'))
def select_role():
    # Affichage de la page principale de l'application
    return render_template('auth/select_role.html')

@auth_bp.route('/password_change', methods=('GET', 'POST'))
def password_change():

    db = get_db()

    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['nouveau_mot_de_passe']
        confirm_password = request.form['confirmer_nouveau_mot_de_passe']
        token = request.form['jeton']

        if new_password == confirm_password:
            db.execute("UPDATE users SET password = ? WHERE email = ?", (generate_password_hash(new_password), email))
            db.commit() 
            flash('Mot de passe mis à jour avec succès.', 'success')
            return redirect(url_for('login'))  
        else:
            flash('Les mots de passe ne correspondent pas.', 'error')

    return render_template('auth/password_change.html')