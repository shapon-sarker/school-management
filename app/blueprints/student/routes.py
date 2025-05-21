from flask import render_template
from flask_login import login_required
from app.blueprints.student import student_bp
from app.utils.decorators import student_required

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    return render_template('student/dashboard.html', title='Student Dashboard')

# Student routes will be added here 