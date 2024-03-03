from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.db.db import get_db
# Routes /...
home_bp = Blueprint('home', __name__)



@home_bp.route('/', methods=('GET', 'POST'))
def landing_page():
    return render_template('home/index.html')

@home_bp.route('/<path:text>', methods=['GET', 'POST'])
def not_found_error(text):
    return render_template('home/404.html'), 404