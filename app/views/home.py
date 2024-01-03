from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.db.db import get_db
# Routes /...
home_bp = Blueprint('home', __name__)



# Route /
@home_bp.route('/', methods=('GET', 'POST'))
def landing_page():
    # Affichage de la page principale de l'application
    return render_template('home/index.html')

@home_bp.route('/research_teacher', methods=('GET', 'POST'))
def research_teacher():
    
    if 'user_id' not in session : 
        return redirect(url_for('auth.login'))
    
    db = get_db()
    levels = db.execute("SELECT * FROM level").fetchall()
    subjects = db.execute("SELECT * FROM subject").fetchall()
    course_types = db.execute("SELECT * FROM course_type").fetchall()
    
    return render_template('home/research.html', levels=levels, subjects=subjects, course_types=course_types)

@home_bp.route('/list_teacher', methods=('GET', 'POST'))
def list_teacher():
    
    if request.method == 'POST':
        level = request.form['level']
        course_type = request.form['course_type']
        subject = request.form['subject']

        db = get_db()
        #teachers = db.execute("SELECT users.* FROM users, teacher_level WHERE role_id = 1 and teacher_level.teacher_id = users.id and teacher_level.level_id = ?", (level)).fetchall()
        #teachers = db.execute("SELECT users. *FROM users, teacher_subject WHERE role_id = 1 and teacher_subject.teacher_id = users.id and teacher_subject.id = ?", (subject)).fetchall() 
        teachers = db.execute("""
            SELECT DISTINCT users.* FROM users, teacher_level, teacher_subject, teacher_course_type WHERE role_id = 1 and teacher_level.teacher_id = users.id and teacher_level.level_id = ? and teacher_subject.teacher_id = users.id and teacher_subject.subject_id = ?
        """, (level, subject)).fetchall()
        print(level)
        print(subject)
        print(course_type)


    return render_template('home/list_teacher.html', teachers=teachers)

@home_bp.route('/teacher_account', methods=('GET', 'POST'))
def teacher_account():
    
    levels_teacher = db.execute("SELECT * FROM level").fetchall()
    
    return render_template('home/list_teacher.html', levels_teacher=levels_teacher)

@home_bp.route('/<path:text>', methods=['GET', 'POST'])
def not_found_error(text):
    return render_template('home/404.html'), 404