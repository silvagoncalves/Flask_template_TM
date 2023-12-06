from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)

# Routes /...
home_bp = Blueprint('home', __name__)



# Route /
@home_bp.route('/', methods=('GET', 'POST'))
def landing_page():
    # Affichage de la page principale de l'application
    return render_template('home/index.html')

@home_bp.route('/research_teacher', methods=('GET', 'POST'))
def research_teacher():
    # Affichage de la page principale de l'application
    return render_template('home/research.html')

@home_bp.route('/list_teacher', methods=('GET', 'POST'))
def list_teacher():


    if request.method == 'POST':
        level = request.form['level']
        course = request.form['course_type']
        subject = request.form.getlist('subjects[]')

        query = "SELECT * FROM teachers WHERE level = ? AND course_type = ? AND subject IN ({})".format(','.join(['?'] * len(subject)))

        db = get_db()
        teacher = get_db().execute(query, (level, course) + tuple(subject)).fetchall()

        return render_template('home/list_teacher.html', teacher=teacher)

    return render_template('home/list_teacher.html', teachers=None)
 

@home_bp.route('/<path:text>', methods=['GET', 'POST'])
def not_found_error(text):
    return render_template('home/404.html'), 404