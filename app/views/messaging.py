from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *
from datetime import datetime
from app.db.db import get_db


messaging_bp = Blueprint('messaging', __name__, url_prefix='/messaging')


@messaging_bp.route('/messaging', methods=('GET', 'POST'))
def messaging():

     if request.method == 'POST':
          content = request.form['content']
          to_user = request.form['to_user']
          from_user = g.user['id']
          date_message = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

          db = get_db()
          db.execute(
          'INSERT INTO message (content, from_user, to_user, date_message) VALUES (?, ?, ?, ?)',
          (content, from_user, to_user, date_message)
          )
          db.commit()
     
     to_user =  request.args.get('user_id')
     if to_user == None : 
          to_user = request.form['to_user']
     from_user = g.user['id']
     print(to_user)
     print(from_user)

     db = get_db()

     messages = db.execute("""
          SELECT m.content, f.username as from_user, t.username as to_user, m.date_message FROM message m, users f, users t 
          WHERE m.from_user = f.id 
          AND m.to_user = t.id 
          AND ((m.from_user=? and m.to_user =?) or (m.from_user=? and m.to_user =?))
          order by m.date_message 
     """, (from_user, to_user, to_user, from_user)).fetchall()
     
     return render_template('messaging/messaging.html', messages=messages, to_user=to_user)

