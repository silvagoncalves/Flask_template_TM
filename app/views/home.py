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
    return render_template('home/list_teacher.html')

# Gestionnaire d'erreur 404 pour toutes les routes inconnues
@home_bp.route('/<path:text>', methods=['GET', 'POST'])
def not_found_error(text):
    return render_template('home/404.html'), 404