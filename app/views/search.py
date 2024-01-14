from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *
from app.db.db import get_db

# Routes /user/...
search_bp = Blueprint('search', __name__, url_prefix='/search')

@search_bp.route('/research_teacher', methods=('GET', 'POST'))
def research_teacher():
    
    if 'user_id' not in session : 
        return redirect(url_for('auth.login'))
    
    db = get_db()
    levels = db.execute("SELECT * FROM level").fetchall()
    subjects = db.execute("SELECT * FROM subject").fetchall()
    course_types = db.execute("SELECT * FROM course_type").fetchall()
    
    return render_template('search/research.html', levels=levels, subjects=subjects, course_types=course_types)

@search_bp.route('/list_teacher', methods=('GET', 'POST'))
def list_teacher():
    
    if request.method == 'POST':
        level = request.form['level']
        course_type = request.form['course_type']
        subject = request.form['subject']

        db = get_db()
        #teachers = db.execute("SELECT users.* FROM users, teacher_level WHERE role_id = 1 and teacher_level.teacher_id = users.id and teacher_level.level_id = ?", (level)).fetchall()
        #teachers = db.execute("SELECT users. *FROM users, teacher_subject WHERE role_id = 1 and teacher_subject.teacher_id = users.id and teacher_subject.id = ?", (subject)).fetchall() 
        teachers = db.execute("""
            SELECT DISTINCT users.* FROM users, teacher_level, teacher_subject, teacher_course_type
            WHERE role_id = 1 
            AND teacher_level.teacher_id = users.id AND teacher_level.level_id = ? 
            AND teacher_subject.teacher_id = users.id AND teacher_subject.subject_id = ?
            AND teacher_course_type.teacher_id = users.id AND teacher_course_type.course_type_id = ?
            COLLATE NOCASE
        """, (level, subject, course_type)).fetchall()
        print(level)
        print(subject)
        print(course_type)

        #levels_teacher = db.execute("SELECT level. * FROM level, teacher_level WHERE teacher_level.teacher_id = teacher_level.level_id and teacher_level.teacher_id = ?").fetchall()
        levels_teacher = db.execute("""
            SELECT level.* FROM level
            JOIN teacher_level ON level.level_id = teacher_level.level_id
            WHERE teacher_level.teacher_id = ?
        """, (level,)).fetchall()
        
        subjects_teacher = db.execute("""
            SELECT subject.* FROM subject
            JOIN teacher_subject ON subject.id = teacher_subject.subject_id
            WHERE teacher_subject.teacher_id = ?
        """, (subject,)).fetchall()

        course_types = db.execute("""
            SELECT course_type.* FROM course_type
            JOIN teacher_course_type ON course_type.course_type_id = teacher_course_type.course_type_id
            WHERE teacher_course_type.teacher_id = ?
        """, (course_type,)).fetchall()

        tarif = db.execute("""
            SELECT DISTINCT users.tarif FROM users, teacher_level, teacher_subject, teacher_course_type
            WHERE role_id = 1 
            AND teacher_level.teacher_id = users.id AND teacher_level.level_id = ? 
            AND teacher_subject.teacher_id = users.id AND teacher_subject.subject_id = ?
            AND teacher_course_type.teacher_id = users.id AND teacher_course_type.course_type_id = ?
            COLLATE NOCASE
        """, (level, subject, course_type)).fetchone()

        print(tarif)


    return render_template('search/list_teacher.html', teachers=teachers, tarif=tarif,  levels_teacher=levels_teacher, subjects_teacher=subjects_teacher, course_types=course_types)