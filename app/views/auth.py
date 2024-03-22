from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db.db import get_db
import os
from random import randint 
import base64

# Création d'un blueprint contenant les routes ayant le préfixe /auth/...
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
#extention autorisée pour les photos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

#fonction qui vérifie si l'extention du fichier est autorisée
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route /auth/register
@auth_bp.route('/register', methods=('GET', 'POST'))
def register():
    db = get_db()
    subjects = db.execute("SELECT * FROM subject").fetchall()
    levels = db.execute("SELECT * FROM level").fetchall()
    course_types = db.execute("SELECT * FROM course_type").fetchall()
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        telephone = request.form['phone']
        tarif = request.form['tarif']
        photo = request.files['photo']
        photo_data = None

        if photo and allowed_file(photo.filename):
            photo_data = base64.b64encode(photo.read()).decode('utf-8')
                
        if username and password:
            try:
                user_with_email = db.execute("SELECT * FROM users WHERE mail = ?", (email,)).fetchone()
                user_with_telephone = db.execute("SELECT * FROM users WHERE telephone = ?", (telephone,)).fetchone()
                user_with_username = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

                if user_with_email:
                    flash("Cet adresse électronique existe déjà.")
                    return redirect(url_for("auth.register"))

                if user_with_telephone:
                    flash("Ce numéro de téléphone existe déjà.")
                    return redirect(url_for("auth.register"))

                if user_with_username:
                    flash("Ce nom d'utilisateur est déjà utilisé.")
                    return redirect(url_for("auth.register"))
                
                if not request.form.getlist('matieres[]') or not request.form.getlist('niveau[]') or not request.form.getlist('course_type[]'):
                    flash("Au moins une matière, un niveau et un type de cours doivent être sélectionnés.")
                    return redirect(url_for("auth.register"))  
                
                db.execute("INSERT INTO users (username, password, mail, telephone, tarif, role_id, photo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (username, generate_password_hash(password), email, telephone, tarif,'1', photo_data))

                user_id = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()['id']

                for subject_id in request.form.getlist('matieres[]'):
                    db.execute("INSERT INTO teacher_subject (teacher_id, subject_id) VALUES (?, ?)", (user_id, subject_id))
                
                for level_id in request.form.getlist('niveau[]'):
                    db.execute("INSERT INTO teacher_level (teacher_id, level_id) VALUES (?, ?)", (user_id, level_id))

                for course_type_id in request.form.getlist('course_type[]'):
                    db.execute("INSERT INTO teacher_course_type (teacher_id, course_type_id) VALUES (?, ?)", (user_id, course_type_id))
               
                db.commit()
            
            except db.IntegrityError as e:
                print(e)
                error = f"User {username} is already registered."
                flash(error)
                return redirect(url_for("auth.register"))

            return redirect(url_for("auth.login"))

        else:
            error = "Username or password invalid"
            flash(error)
            return redirect(url_for("auth.login"))
    else:
        return render_template('auth/register.html', levels=levels, subjects=subjects, course_types=course_types)


@auth_bp.route('/register_student', methods=('GET', 'POST'))
def register_student():
    db = get_db()
    #vérifie si des données sont soumises et récupère les données 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        telephone = request.form['phone']
        photo = request.files['photo']
        photo_data = None

        #vérifie si une photo est fournie et si elle est autorisée
        if photo and allowed_file(photo.filename):
            photo_data = base64.b64encode(photo.read()).decode('utf-8')
    
        #vérifie si les données saisis n'existent pas déjà dans la base de données
        if username and password:
            try:
                #récupère les utilisateurs avec le même email, le même numéros de telephone et le même nom d'utilisateur dans la base de données
                user_with_email = db.execute("SELECT * FROM users WHERE mail = ?", (email,)).fetchone()
                user_with_telephone = db.execute("SELECT * FROM users WHERE telephone = ?", (telephone,)).fetchone()
                user_with_username = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

                #si l'email est déja enregistré : flash"email existe déjà" et returne la page d'inscription
                if user_with_email:
                    flash("Cet e-mail existe déjà.")
                    return redirect(url_for("auth.register_student"))
                
                #si le numéro de téléphone est déjà enregistré : flash "numéro de téléphone existe déjà" et returne la page d'inscription
                if user_with_telephone:
                    flash("Ce numéro de téléphone existe déjà.")
                    return redirect(url_for("auth.register_student"))

                # si le nom d'utilisateur est déjà enregistré: flash "nom d'utilisateur existe déjà" et returne la page d'inscription
                if user_with_username:
                    flash("Ce nom d'utilisateur est déjà utilisé.")
                    return redirect(url_for("auth.register_student"))
                
                #si aucun utilisateur n'a les même données, insère les données du nouveau utilisateur dans la base de données
                db.execute("INSERT INTO users (username, password, mail, telephone, role_id, photo) VALUES (?, ?, ?, ?, ?, ?)",
                           (username, generate_password_hash(password), email, telephone, '2', photo_data))
                db.commit()

            #gestion des erreurs d'intégrité (utilisateur déjà enregistré)
            except db.IntegrityError as e:
                print(e)
                error = f"User {username} is already registered."
                flash(error)
                return redirect(url_for("auth.register_student"))
            #redirige vers la page de connexion si l'inscription est réussi 
            return redirect(url_for("auth.login"))

        else:
            #si les données saisies sont invalides, affiche un message d'erreur
            error = "Username or password invalid"
            flash(error)
            return redirect(url_for("auth.login"))
    else:
        #affiche le formulaire d'inscription si la méthode de la requête est GET
        return render_template('auth/register_student.html')

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
            error = "Nom d'utilisateur incorrect."
        elif not check_password_hash(user['password'], password):
            error = 'Mot de passe incorrect.'

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
    
    if request.method == 'POST':

        mail = request.form['mail']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        token = request.form['token']

        # On récupère la base de données
        db = get_db()

        # On récupère l'utilisateur avec le username spécifié (une contrainte dans la db indique que le nom d'utilisateur est unique)
        # La virgule après username est utilisée pour créer un tuple contenant une valeur unique
        user = db.execute('SELECT * FROM users WHERE mail = ?', (mail,)).fetchone()
        
        if user:
            if new_password == confirm_password:
                # Vérification du jeton

                # Mise à jour du mot de passe
                hashed_password = generate_password_hash(new_password)
                db.execute('UPDATE users SET password = ? WHERE mail = ?', (hashed_password, mail))
                db.commit()
                flash('Mot de passe mis à jour avec succès.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Les nouveaux mots de passe ne correspondent pas.', 'error')
        else:
            flash('L\'utilisateur avec cet adresse électronique n\'existe pas.', 'error')

    return render_template('auth/password_change.html')

@auth_bp.route('/count_modification', methods=('GET', 'POST'))
def count_modification():
    db = get_db()
    subjects = db.execute("SELECT * FROM subject").fetchall()
    levels = db.execute("SELECT * FROM level").fetchall()
    course_types = db.execute("SELECT * FROM course_type").fetchall()

    user_id = g.user['id']
    tarif = None
    username = None
    mail = None
    telephone = None
    photo_data= None

    if request.method == 'POST':
        # Récupération des nouvelles données du formulaire
        new_tarif = request.form['tarif']
        new_username = request.form['username']
        new_mail = request.form['mail']
        new_telephone = request.form['telephone']
        new_photo = request.files['photo']
        
        if not new_photo:
            photo_data = g.user['photo']
        else:
            photo_data = base64.b64encode(new_photo.read()).decode('utf-8')

        if not new_tarif:
            new_tarif = g.user['tarif']
        if not new_username:
            new_username = g.user['username']
        if not new_mail:
            new_mail = g.user['mail']
        if not new_telephone:
            new_telephone = g.user['telephone']
        if not new_photo: 
            new_photo = g.user['photo']


        if new_username != g.user['username'] and db.execute('SELECT id FROM users WHERE username = ?', (new_username,)).fetchone():
            flash("Ce nom d'utilisateur est déjà utilisé. Veuillez en choisir un autre.", "error")
            return redirect(url_for('auth.count_modification'))

        if new_telephone != g.user['telephone'] and db.execute('SELECT id FROM users WHERE telephone = ?', (new_telephone,)).fetchone():
            flash("Ce numéro de téléphone est déjà utilisé. Veuillez en choisir un autre.", "error")
            return redirect(url_for('auth.count_modification'))

        if new_mail != g.user['mail'] and db.execute('SELECT id FROM users WHERE mail = ?', (new_mail,)).fetchone():
            flash("Cette adresse électronique est déjà utilisée. Veuillez en choisir un autre.", "error")
            return redirect(url_for('auth.count_modification'))
        
        if 'matieres[]' in request.form:
            db.execute("DELETE FROM teacher_subject WHERE teacher_id = ?", (user_id,))
            for subject_id in request.form.getlist('matieres[]'):
                db.execute("INSERT INTO teacher_subject (teacher_id, subject_id) VALUES (?, ?)", (user_id, subject_id))

        if 'niveau[]' in request.form:
            db.execute("DELETE FROM teacher_level WHERE teacher_id = ?", (user_id,))
            for level_id in request.form.getlist('niveau[]'):
                db.execute("INSERT INTO teacher_level (teacher_id, level_id) VALUES (?, ?)", (user_id, level_id))

        if 'course_type[]' in request.form:
            db.execute("DELETE FROM teacher_course_type WHERE teacher_id = ?", (user_id,))
            for course_type_id in request.form.getlist('course_type[]'):
                db.execute("INSERT INTO teacher_course_type (teacher_id, course_type_id) VALUES (?, ?)", (user_id, course_type_id))

        db.execute('UPDATE users SET tarif = ?, username = ?, mail = ?, telephone = ?, photo = ? WHERE id = ?', (new_tarif, new_username, new_mail, new_telephone, photo_data, user_id))
        db.commit()

                
        return redirect(url_for('user.show_profile'))

    return render_template('auth/count_modification.html',  telephone=g.user['telephone'], mail=g.user['mail'], username=g.user['username'], tarif=g.user['tarif'], photo=g.user['photo'], levels=levels, subjects=subjects, course_types=course_types)


    
@auth_bp.route('/count_modification_student', methods=('GET', 'POST'))
def count_modification_student():
    db = get_db()
  

    user_id = g.user['id']

    username = None
    mail = None
    telephone = None
    photo_data = None

    if request.method == 'POST':

        new_username = request.form['username']
        new_mail = request.form['mail']
        new_telephone = request.form['telephone']
        new_photo = request.files['photo']

        if not new_photo:
            photo_data = g.user['photo']
        else:
            photo_data = base64.b64encode(new_photo.read()).decode('utf-8')

    
        if not new_username:
            new_username = g.user['username']
        if not new_mail:
            new_mail = g.user['mail']
        if not new_telephone:
            new_telephone = g.user['telephone']
        if not new_photo: 
            new_photo = g.user['photo']

        if new_username != g.user['username'] and db.execute('SELECT id FROM users WHERE username = ?', (new_username,)).fetchone():
            flash("Ce nom d'utilisateur est déjà utilisé. Veuillez en choisir un autre.", "error")
            return redirect(url_for('auth.count_modification_student'))

        if new_telephone != g.user['telephone'] and db.execute('SELECT id FROM users WHERE telephone = ?', (new_telephone,)).fetchone():
            flash("Ce numéro de téléphone est déjà utilisé. Veuillez en choisir un autre.", "error")
            return redirect(url_for('auth.count_modification_student'))

        if new_mail != g.user['mail'] and db.execute('SELECT id FROM users WHERE mail = ?', (new_mail,)).fetchone():
            flash("Cette adresse électronique est déjà utilisée. Veuillez en choisir un autre.", "error")
            return redirect(url_for('auth.count_modification_student'))
        
        else:
            if new_username != g.user['username'] or new_mail != g.user['mail'] or new_telephone != g.user['telephone'] or new_photo != g.user['photo']:
                db.execute('UPDATE users SET  username = ?, mail = ?, telephone = ? , photo = ? WHERE id = ?', ( new_username, new_mail, new_telephone, photo_data, user_id))
                db.commit()

    
        return redirect(url_for('user.show_profile'))

    return render_template('auth/count_modification_student.html', photo_data=photo_data, telephone=telephone, mail=mail, username=username)