from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *
from app.db.db import get_db
from random import randint


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

        teachers = db.execute("""
            SELECT DISTINCT users.id, users.username FROM users
            JOIN teacher_level ON  teacher_level.teacher_id = users.id
            JOIN teacher_subject ON teacher_subject.teacher_id = users.id 
            JOIN teacher_course_type ON teacher_course_type.teacher_id = users.id 
            WHERE role_id = 1 AND teacher_level.level_id = ?  AND teacher_subject.subject_id = ? AND teacher_course_type.course_type_id = ?
        """, (level, subject, course_type)).fetchall()

        list_teachers=[]

        for teacher in teachers:

            levels_teacher = db.execute("""
                SELECT level.* FROM level
                JOIN teacher_level ON level.level_id = teacher_level.level_id
                WHERE teacher_level.teacher_id = ?
            """, (teacher[0],)).fetchall()
            
            subjects_teacher = db.execute("""
                SELECT subject.* FROM subject
                JOIN teacher_subject ON subject.id = teacher_subject.subject_id
                WHERE teacher_subject.teacher_id = ?
            """, (teacher[0],)).fetchall()

            course_types = db.execute("""
                SELECT course_type.* FROM course_type
                JOIN teacher_course_type ON course_type.course_type_id = teacher_course_type.course_type_id
                WHERE teacher_course_type.teacher_id = ?
            """, (teacher[0],)).fetchall()

            tarif_teacher_row = db.execute("SELECT tarif FROM users WHERE id = ?", (teacher[0],)).fetchone()

            tarif_teacher = tarif_teacher_row[0] if tarif_teacher_row is not None else None

            teacher_photo = db.execute("SELECT photo FROM users WHERE id = ?", (teacher[0],)).fetchone()

            teacher_photo_profile = teacher_photo[0] if teacher_photo is not None else None

            list_teachers.append([teacher]+[levels_teacher]+[subjects_teacher]+[course_types]+[tarif_teacher]+[teacher_photo_profile])
    
    return render_template('search/list_teacher.html',  list_teachers=list_teachers)