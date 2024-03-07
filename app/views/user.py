from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *
from app.db.db import get_db



user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile', methods=('GET', 'POST'))
@login_required 
def show_profile():

    db = get_db()
    
    user_id = g.user['id']

    teachers = db.execute("SELECT DISTINCT users.* FROM users WHERE role_id = 1 AND id = ?", (user_id ,)).fetchall()
    
    levels_teacher = db.execute("""
            SELECT level.* FROM level
            JOIN teacher_level ON level.level_id = teacher_level.level_id
            WHERE teacher_level.teacher_id = ?
        """, (user_id,)).fetchall()
    
    subjects_teacher = db.execute("""
            SELECT subject.* FROM subject
            JOIN teacher_subject ON subject.id = teacher_subject.subject_id
            WHERE teacher_subject.teacher_id = ?
        """, (user_id,)).fetchall()

    course_types = db.execute("""
            SELECT course_type.* FROM course_type
            JOIN teacher_course_type ON course_type.course_type_id = teacher_course_type.course_type_id
            WHERE teacher_course_type.teacher_id = ?
        """, (user_id,)).fetchall()
    
    followed = db.execute("""SELECT users.* FROM users
            JOIN follow ON users.id = follow.student_id
            WHERE teacher_id = ?
        """, (user_id,)).fetchall()
    
    following = db.execute("""SELECT users.* FROM users
            JOIN follow ON users.id = follow.teacher_id
            WHERE student_id = ?
        """, (user_id,)).fetchall()

    return render_template('user/profile.html', following=following, teachers=teachers, followed=followed, levels_teacher=levels_teacher, subjects_teacher=subjects_teacher,course_types=course_types )


@user_bp.route('/count_teacher', methods=['GET', 'POST'])
def count_teacher():

    db = get_db()

    teacher_id = request.args.get('teacher_id')

    teacher = db.execute("SELECT * FROM users WHERE id = ?", (teacher_id,)).fetchone()

    teachers = db.execute("SELECT DISTINCT users.* FROM users WHERE role_id = 1 AND id = ?", (g.user['id'] ,)).fetchall()

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
    
    tarif_teacher_row = db.execute("SELECT tarif FROM users WHERE id = ?", (teacher_id,)).fetchone()

    tarif_teacher = tarif_teacher_row[0] if tarif_teacher_row is not None else None
    
    if request.method == 'POST':
        try:
            if 'follow' in request.form:
                db.execute("INSERT INTO follow (student_id, teacher_id) VALUES (?, ?)", (g.user['id'], teacher_id))
            elif 'unfollow' in request.form:
                db.execute("DELETE FROM follow WHERE student_id = ? AND teacher_id = ?", (g.user['id'], teacher_id))
            elif 'grade' in request.form:
                grade = int(request.form['grade'])
                if 1 <= grade <= 5:
                    db.execute("INSERT INTO evalue (grade, teacher_id) VALUES (?, ?)", (grade, teacher_id))
                else:
                    flash ("La note doit être entre 1 et 5.")
        except ValueError:
            flash ("La note doit être un nombre entier.")
        finally:
            db.commit()

    all_grades = db.execute("SELECT grade FROM evalue WHERE teacher_id = ?", (teacher_id,)).fetchall()
    total_nb = 0
    if all_grades:
        grades = [grade[0] for grade in all_grades]
        total_nb = sum(grades) // len(grades)

    follow = db.execute("SELECT * FROM follow WHERE student_id = ? AND teacher_id = ?", (g.user['id'], teacher_id)).fetchone()

    db.close()
    return render_template('user/count_teacher.html', total_nb=total_nb, teachers=teachers, follow=follow, teacher=teacher, tarif_teacher=tarif_teacher, levels_teacher=levels_teacher, subjects_teacher=subjects_teacher, course_types=course_types)