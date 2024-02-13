from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *
from app.db.db import get_db


messaging_bp = Blueprint('messaging', __name__, url_prefix='/messaging')


