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
    print(teacher)
    
    

    return render_template('user/count_teacher.html', teacher=teacher)