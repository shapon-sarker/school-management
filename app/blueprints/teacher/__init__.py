from flask import Blueprint

teacher_bp = Blueprint('teacher', __name__)

from app.blueprints.teacher import routes 