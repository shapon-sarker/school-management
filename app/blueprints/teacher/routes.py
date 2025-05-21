from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.blueprints.teacher import teacher_bp
from app.models.admin import *
from app.models.teacher import *
from app.models.user import User
from app import db
from datetime import datetime, date, timedelta
from functools import wraps
import os

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'teacher':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@teacher_bp.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    # Get active academic year
    academic_year = AcademicYear.query.filter_by(is_active=True).first()
    
    # Get statistics
    stats = {
        'total_classes': Subject.query.filter_by(teacher_id=current_user.id).count(),
        'total_students': get_total_students(),
        'attendance_percentage': calculate_today_attendance(),
        'pending_tasks': get_pending_tasks()
    }
    
    # Get today's timetable
    today_timetable = get_today_timetable()
    
    # Get recent activities
    recent_activities = get_recent_activities()
    
    # Get recent notices
    recent_notices = TeacherNotice.query.filter_by(teacher_id=current_user.id).order_by(TeacherNotice.created_at.desc()).limit(5).all()
    
    return render_template('teacher/dashboard.html',
                         academic_year=academic_year,
                         stats=stats,
                         today_timetable=today_timetable,
                         recent_activities=recent_activities,
                         recent_notices=recent_notices)

def get_total_students():
    # Get all classes taught by the teacher
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    class_ids = [subject.class_id for subject in subjects]
    
    # Count unique students in these classes
    return User.query.filter(User.role == 'student', User.class_id.in_(class_ids)).distinct().count()

def calculate_today_attendance():
    today = date.today()
    total_students = get_total_students()
    if total_students == 0:
        return 0
    
    # Get all classes taught by the teacher
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    class_ids = [subject.class_id for subject in subjects]
    
    present_students = Attendance.query.filter(
        Attendance.date == today,
        Attendance.status == 'present',
        Attendance.class_id.in_(class_ids)
    ).count()
    
    return round((present_students / total_students) * 100, 2)

def get_pending_tasks():
    # Count unmarked exams
    pending_marks = ExamResult.query.join(Subject).filter(
        Subject.teacher_id == current_user.id,
        ExamResult.marks_obtained == None
    ).count()
    
    return pending_marks

def get_today_timetable():
    today = date.today()
    day_name = today.strftime('%A').lower()
    
    timetable = TimeTable.query.filter(
        TimeTable.teacher_id == current_user.id,
        TimeTable.day_of_week == day_name
    ).order_by(TimeTable.period_number).all()
    
    formatted_timetable = []
    for period in timetable:
        class_name = Class.query.get(period.class_id).name
        section_name = Section.query.get(period.section_id).name
        subject_name = Subject.query.get(period.subject_id).name
        
        formatted_timetable.append({
            'period_number': period.period_number,
            'start_time': period.start_time,
            'end_time': period.end_time,
            'class_name': class_name,
            'section_name': section_name,
            'subject_name': subject_name
        })
    
    return formatted_timetable

def get_recent_activities():
    activities = []
    
    # Get recent attendance records
    recent_attendance = Attendance.query.join(Subject).filter(
        Subject.teacher_id == current_user.id
    ).order_by(Attendance.created_at.desc()).limit(5)
    
    for attendance in recent_attendance:
        student = User.query.get(attendance.student_id)
        activities.append({
            'icon': 'bi-calendar-check',
            'time': attendance.created_at.strftime('%Y-%m-%d %H:%M'),
            'description': f'Marked {student.name} as {attendance.status}'
        })
    
    # Get recent exam results
    recent_results = ExamResult.query.join(Subject).filter(
        Subject.teacher_id == current_user.id
    ).order_by(ExamResult.created_at.desc()).limit(5)
    
    for result in recent_results:
        student = User.query.get(result.student_id)
        subject = Subject.query.get(result.subject_id)
        activities.append({
            'icon': 'bi-file-text',
            'time': result.created_at.strftime('%Y-%m-%d %H:%M'),
            'description': f'Added marks for {student.name} in {subject.name}'
        })
    
    # Get recent study materials
    recent_materials = StudyMaterial.query.filter_by(
        teacher_id=current_user.id
    ).order_by(StudyMaterial.uploaded_at.desc()).limit(5)
    
    for material in recent_materials:
        subject = Subject.query.get(material.subject_id)
        activities.append({
            'icon': 'bi-file-earmark-text',
            'time': material.uploaded_at.strftime('%Y-%m-%d %H:%M'),
            'description': f'Uploaded {material.title} for {subject.name}'
        })
    
    # Sort activities by time
    activities.sort(key=lambda x: datetime.strptime(x['time'], '%Y-%m-%d %H:%M'), reverse=True)
    return activities[:10]

# Class Management Routes
@teacher_bp.route('/classes')
@login_required
@teacher_required
def view_classes():
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher/classes.html', subjects=subjects)

@teacher_bp.route('/timetable')
@login_required
@teacher_required
def class_timetable():
    timetable = TimeTable.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher/timetable.html', timetable=timetable)

# Attendance Routes
@teacher_bp.route('/attendance/take', methods=['GET', 'POST'])
@login_required
@teacher_required
def take_attendance():
    if request.method == 'POST':
        class_id = request.form.get('class_id')
        section_id = request.form.get('section_id')
        date_str = request.form.get('date')
        attendance_data = request.form.getlist('attendance[]')
        student_ids = request.form.getlist('student_id[]')
        
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        for student_id, status in zip(student_ids, attendance_data):
            attendance = Attendance(
                student_id=student_id,
                class_id=class_id,
                section_id=section_id,
                date=date_obj,
                status=status
            )
            db.session.add(attendance)
        
        db.session.commit()
        flash('Attendance has been recorded successfully.', 'success')
        return redirect(url_for('teacher.view_attendance'))
    
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher/take_attendance.html', subjects=subjects)

@teacher_bp.route('/attendance/view')
@login_required
@teacher_required
def view_attendance():
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    class_ids = [subject.class_id for subject in subjects]
    attendance_records = Attendance.query.filter(Attendance.class_id.in_(class_ids)).all()
    return render_template('teacher/view_attendance.html', attendance_records=attendance_records)

# Examination Routes
@teacher_bp.route('/marks/enter', methods=['GET', 'POST'])
@login_required
@teacher_required
def enter_marks():
    if request.method == 'POST':
        exam_id = request.form.get('exam_id')
        subject_id = request.form.get('subject_id')
        marks_data = request.form.getlist('marks[]')
        student_ids = request.form.getlist('student_id[]')
        remarks = request.form.getlist('remarks[]')
        
        for student_id, marks, remark in zip(student_ids, marks_data, remarks):
            result = ExamResult(
                exam_id=exam_id,
                student_id=student_id,
                subject_id=subject_id,
                marks_obtained=float(marks),
                remarks=remark,
                created_by=current_user.id
            )
            db.session.add(result)
        
        db.session.commit()
        flash('Marks have been recorded successfully.', 'success')
        return redirect(url_for('teacher.view_results'))
    
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    exams = Exam.query.all()
    return render_template('teacher/enter_marks.html', subjects=subjects, exams=exams)

@teacher_bp.route('/results/view')
@login_required
@teacher_required
def view_results():
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    subject_ids = [subject.id for subject in subjects]
    results = ExamResult.query.filter(ExamResult.subject_id.in_(subject_ids)).all()
    return render_template('teacher/view_results.html', results=results)

# Student Performance Routes
@teacher_bp.route('/students')
@login_required
@teacher_required
def view_students():
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    class_ids = [subject.class_id for subject in subjects]
    students = User.query.filter(User.role == 'student', User.class_id.in_(class_ids)).all()
    return render_template('teacher/students.html', students=students)

@teacher_bp.route('/students/performance')
@login_required
@teacher_required
def student_performance():
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    subject_ids = [subject.id for subject in subjects]
    performances = StudentPerformance.query.filter(StudentPerformance.subject_id.in_(subject_ids)).all()
    return render_template('teacher/student_performance.html', performances=performances)

# Study Materials Routes
@teacher_bp.route('/materials/upload', methods=['GET', 'POST'])
@login_required
@teacher_required
def upload_material():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        subject_id = request.form.get('subject_id')
        file = request.files['material_file']
        
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', 'materials', filename)
            file.save(os.path.join(current_app.root_path, 'static', file_path))
            
            material = StudyMaterial(
                title=title,
                description=description,
                file_path=file_path,
                subject_id=subject_id,
                teacher_id=current_user.id
            )
            db.session.add(material)
            db.session.commit()
            
            flash('Study material has been uploaded successfully.', 'success')
            return redirect(url_for('teacher.view_materials'))
    
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher/upload_material.html', subjects=subjects)

@teacher_bp.route('/materials/view')
@login_required
@teacher_required
def view_materials():
    materials = StudyMaterial.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher/view_materials.html', materials=materials)

# Notice Routes
@teacher_bp.route('/notices/post', methods=['GET', 'POST'])
@login_required
@teacher_required
def post_notice():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        class_id = request.form.get('class_id')
        
        notice = TeacherNotice(
            title=title,
            content=content,
            teacher_id=current_user.id,
            class_id=class_id
        )
        db.session.add(notice)
        db.session.commit()
        
        flash('Notice has been posted successfully.', 'success')
        return redirect(url_for('teacher.view_notices'))
    
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    class_ids = list(set([subject.class_id for subject in subjects]))
    classes = Class.query.filter(Class.id.in_(class_ids)).all()
    return render_template('teacher/post_notice.html', classes=classes)

@teacher_bp.route('/notices/view')
@login_required
@teacher_required
def view_notices():
    notices = TeacherNotice.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher/view_notices.html', notices=notices)

# Teacher routes will be added here 