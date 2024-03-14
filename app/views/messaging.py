from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *
from datetime import datetime
from app.db.db import get_db
from random import randint

messaging_bp = Blueprint('messaging', __name__, url_prefix='/messaging')

@messaging_bp.route('/messaging', methods=('GET', 'POST'))
def messaging():
    if request.method == 'POST':
        content = request.form['content']
        to_user = request.form['to_user']
        from_user = g.user['id']
        date_message = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        db = get_db()
        if not content.strip():
            flash("Vous ne pouvez pas envoyer un message vide.", "error")
        else:
            db.execute(
                'INSERT INTO message (content, from_user, to_user, date_message) VALUES (?, ?, ?, ?)',
                (content, from_user, to_user, date_message)
            )
            db.commit()
   
    db = get_db()
    
    to_user = request.args.get('user_id')
    if to_user is None:
        to_user = request.form['to_user']
    from_user = g.user['id']

    messages = db.execute("""
        SELECT m.content, f.username as from_user, t.username as to_user, m.date_message FROM message m, users f, users t
        WHERE m.from_user = f.id 
        AND m.to_user = t.id 
        AND ((m.from_user=? and m.to_user =?) or (m.from_user=? and m.to_user =?))
        ORDER BY m.date_message 
    """, (from_user, to_user, to_user, from_user)).fetchall()

    to_user_name = db.execute("SELECT username FROM users WHERE id = ?", (to_user,)).fetchone()[0]
    while True: 
        red = randint(0, 255)
        green = randint(0, 255)
        blue = randint(0, 255)
        color_hex = '#{:02x}{:02x}{:02x}'.format(red, green, blue)
        if (red, green, blue) != (255, 255, 255):
            break 
        color_hex = '#{:02x}{:02x}{:02x}'.format(red, green, blue)



    return render_template('messaging/messaging.html', color_hex=color_hex,  messages=messages, to_user=to_user, to_user_name=to_user_name)

