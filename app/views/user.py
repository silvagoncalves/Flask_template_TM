from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *
from app.db.db import get_db


# Routes /user/...
user_bp = Blueprint('user', __name__, url_prefix='/user')

# Route /user/profile accessible uniquement à un utilisateur connecté grâce au décorateur @login_required
@user_bp.route('/profile', methods=('GET', 'POST'))
@login_required 
def show_profile():

    db = get_db()
 
    #user_id= g.user['id']
    #photo_profil = db.execute("SELECT DISTINCT photo FROM users WHERE id = ?",(user_id,)).fetchall()
    
    teacher_id = g.user['id']

    teachers = db.execute("SELECT DISTINCT users.* FROM users WHERE role_id = 1 AND id = ?", (teacher_id,)).fetchall()
    
    levels = db.execute("SELECT * FROM level").fetchall() 
    subjects = db.execute("SELECT * FROM subject").fetchall()
    course_types = db.execute("SELECT * FROM course_type").fetchall()
    
    levels_teacher = db.execute("""
            SELECT level.* FROM level
            JOIN teacher_level ON level.level_id = teacher_level.level_id
            WHERE teacher_level.teacher_id = ?
        """, (teacher_id,)).fetchall()
    
    subjects_teacher = db.execute("""
            SELECT subject.* FROM subject
            JOIN teacher_subject ON subject.id = teacher_subject.subject_id
            WHERE teacher_subject.teacher_id = ?
        """, (teacher_id,)).fetchall()

    course_types = db.execute("""
            SELECT course_type.* FROM course_type
            JOIN teacher_course_type ON course_type.course_type_id = teacher_course_type.course_type_id
            WHERE teacher_course_type.teacher_id = ?
        """, (teacher_id,)).fetchall()



    return render_template('user/profile.html', teachers=teachers, levels_teacher=levels_teacher, subjects_teacher=subjects_teacher,course_types=course_types )

@user_bp.route('/count_teacher', methods=['GET', 'POST'])
def count_teacher():
    
    teacher_id = request.args.get('teacher_id')

    
    db = get_db()

    teacher = db.execute("SELECT * FROM users WHERE id = ?", (teacher_id,)).fetchone()
    
    levels = db.execute("SELECT * FROM level").fetchall() 
    subjects = db.execute("SELECT * FROM subject").fetchall()
    course_types = db.execute("SELECT * FROM course_type").fetchall()
    
    levels_teacher = db.execute("""
            SELECT level.* FROM level
            JOIN teacher_level ON level.level_id = teacher_level.level_id
            WHERE teacher_level.teacher_id = ?
        """, (teacher_id,)).fetchall()
    
    subjects_teacher = db.execute("""
            SELECT subject.* FROM subject
            JOIN teacher_subject ON subject.id = teacher_subject.subject_id
            WHERE teacher_subject.teacher_id = ?
        """, (teacher_id,)).fetchall()

    course_types = db.execute("""
            SELECT course_type.* FROM course_type
            JOIN teacher_course_type ON course_type.course_type_id = teacher_course_type.course_type_id
            WHERE teacher_course_type.teacher_id = ?
        """, (teacher_id,)).fetchall()
    

    return render_template('user/count_teacher.html', teacher=teacher, levels_teacher=levels_teacher, subjects_teacher=subjects_teacher,course_types=course_types)

@user_bp.route('/count_teacher', methods=['GET', 'POST'])
def follow():   
    return render_template('user/count_teacher')

@user_bp.route('/count_teacher', methods=['GET', 'POST'])
def average_grade():
    db = get_db()

    teacher_id = request.args.get('teacher_id')
    
    print(teacher_id)
    if request.method == 'POST':
        grade = request.form['grade']
        db.execute("INSERT INTO evalue (grade, teacher_id) VALUES (?, ?)", (grade, teacher_id))
        db.commit()
    
    # Sélectionnez toutes les notes pour cet enseignant
    all_grades = db.execute("SELECT grade FROM evalue WHERE teacher_id = ?", (teacher_id,)).fetchall()
    
    print(all_grades)
    total = 0
    if all_grades:
        # Convertir les données en une liste de notes
        grades = [grade[0] for grade in all_grades]
        # Calculer la somme des notes
        total = sum(grades)
        # Calculer la moyenne des notes
        total /= len(grades)
        print(total)
    
    return render_template('user/count_teacher.html', total=total)