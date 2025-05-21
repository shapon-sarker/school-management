from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.blueprints.admin import admin_bp
from app.models.admin import *
from app.models.user import User
from app import db
from datetime import datetime, date, timedelta
from functools import wraps
from collections import Counter, defaultdict
import json

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/profile')
@login_required
@admin_required
def profile():
    return render_template('admin/profile.html', user=current_user)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get active academic year
    academic_year = AcademicYear.query.filter_by(is_active=True).first()
    
    # Get statistics
    stats = {
        'total_students': User.query.filter_by(role='student').count(),
        'total_teachers': User.query.filter_by(role='teacher').count(),
        'fee_collection': FeePayment.query.with_entities(db.func.sum(FeePayment.amount_paid)).scalar() or 0,
        'attendance_percentage': calculate_today_attendance()
    }
    
    # Get class distribution data
    classes = Class.query.all()
    class_labels = [c.name for c in classes]
    class_data = [
        User.query.filter_by(role='student', class_id=c.id).count()
        for c in classes
    ]
    
    # Get fee collection data
    total_fee = Fee.query.with_entities(db.func.sum(Fee.amount)).scalar() or 0
    collected = FeePayment.query.with_entities(db.func.sum(FeePayment.amount_paid)).scalar() or 0
    pending = total_fee - collected
    overdue = calculate_overdue_fees()
    fee_data = [collected, pending - overdue, overdue]
    
    # Get recent activities
    recent_activities = get_recent_activities()
    
    # Get notifications
    notifications = get_notifications()
    
    return render_template('admin/dashboard.html',
                         academic_year=academic_year,
                         stats=stats,
                         class_labels=class_labels,
                         class_data=class_data,
                         fee_data=fee_data,
                         recent_activities=recent_activities,
                         notifications=notifications)

def calculate_today_attendance():
    today = date.today()
    total_students = User.query.filter_by(role='student').count()
    if total_students == 0:
        return 0
    
    present_students = Attendance.query.filter_by(
        date=today,
        status='present'
    ).count()
    
    return round((present_students / total_students) * 100, 2)

def calculate_overdue_fees():
    today = date.today()
    overdue = Fee.query.filter(Fee.due_date < today).with_entities(db.func.sum(Fee.amount)).scalar() or 0
    paid_overdue = FeePayment.query.join(Fee).filter(Fee.due_date < today).with_entities(db.func.sum(FeePayment.amount_paid)).scalar() or 0
    return overdue - paid_overdue

def get_recent_activities():
    activities = []
    
    # Get recent admissions
    recent_students = User.query.filter_by(role='student').order_by(User.created_at.desc()).limit(5)
    for student in recent_students:
        activities.append({
            'icon': 'bi-person-plus',
            'time': student.created_at.strftime('%Y-%m-%d %H:%M'),
            'description': f'New student {student.name} was admitted'
        })
    
    # Get recent fee payments
    recent_payments = FeePayment.query.order_by(FeePayment.created_at.desc()).limit(5)
    for payment in recent_payments:
        student = User.query.get(payment.student_id)
        activities.append({
            'icon': 'bi-cash',
            'time': payment.created_at.strftime('%Y-%m-%d %H:%M'),
            'description': f'Fee payment of ${payment.amount_paid} received from {student.name}'
        })
    
    # Get recent notices
    recent_notices = Notice.query.order_by(Notice.created_at.desc()).limit(5)
    for notice in recent_notices:
        activities.append({
            'icon': 'bi-megaphone',
            'time': notice.created_at.strftime('%Y-%m-%d %H:%M'),
            'description': f'New notice published: {notice.title}'
        })
    
    # Sort activities by time
    activities.sort(key=lambda x: datetime.strptime(x['time'], '%Y-%m-%d %H:%M'), reverse=True)
    return activities[:10]

def get_notifications():
    notifications = []
    today = date.today()
    
    # Check for overdue fees
    overdue_amount = calculate_overdue_fees()
    if overdue_amount > 0:
        notifications.append({
            'message': f'Overdue fees: ${overdue_amount}'
        })
    
    # Check for low book inventory
    low_stock_books = Book.query.filter(Book.available < 5).all()
    if low_stock_books:
        notifications.append({
            'message': f'{len(low_stock_books)} books are running low on stock'
        })
    
    # Check for upcoming exams
    upcoming_exams = Exam.query.filter(
        Exam.start_date > today,
        Exam.start_date <= today + timedelta(days=7)
    ).all()
    if upcoming_exams:
        notifications.append({
            'message': f'{len(upcoming_exams)} exams scheduled in the next 7 days'
        })
    
    return notifications

# User Management Routes
@admin_bp.route('/teachers')
@login_required
@admin_required
def teachers():
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('admin/teachers.html', teachers=teachers)

@admin_bp.route('/students')
@login_required
@admin_required
def students():
    students = User.query.filter_by(role='student').all()
    return render_template('admin/students.html', students=students)

# Academic Management Routes
@admin_bp.route('/classes')
@login_required
@admin_required
def classes():
    classes = Class.query.all()
    return render_template('admin/classes.html', classes=classes)

@admin_bp.route('/sections')
@login_required
@admin_required
def sections():
    sections = Section.query.all()
    return render_template('admin/sections.html', sections=sections)

@admin_bp.route('/subjects')
@login_required
@admin_required
def subjects():
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)

# Other Routes
@admin_bp.route('/attendance')
@login_required
@admin_required
def attendance():
    return render_template('admin/attendance.html')

@admin_bp.route('/exams')
@login_required
@admin_required
def exams():
    exams = Exam.query.all()
    return render_template('admin/exams.html', exams=exams)

@admin_bp.route('/results')
@login_required
@admin_required
def results():
    results = ExamResult.query.all()
    return render_template('admin/results.html', results=results)

@admin_bp.route('/fee-types')
@login_required
@admin_required
def fee_types():
    fees = Fee.query.all()
    return render_template('admin/fee_types.html', fees=fees)

@admin_bp.route('/fee-collection')
@login_required
@admin_required
def fee_collection():
    payments = FeePayment.query.all()
    return render_template('admin/fee_collection.html', payments=payments)

@admin_bp.route('/books')
@login_required
@admin_required
def books():
    books = Book.query.all()
    return render_template('admin/books.html', books=books)

@admin_bp.route('/issue-return')
@login_required
@admin_required
def issue_return():
    issues = BookIssue.query.all()
    return render_template('admin/issue_return.html', issues=issues)

@admin_bp.route('/vehicles')
@login_required
@admin_required
def vehicles():
    vehicles = Vehicle.query.all()
    return render_template('admin/vehicles.html', vehicles=vehicles)

@admin_bp.route('/routes')
@login_required
@admin_required
def routes():
    routes = TransportRoute.query.all()
    return render_template('admin/routes.html', routes=routes)

@admin_bp.route('/notices')
@login_required
@admin_required
def notices():
    notices = Notice.query.all()
    return render_template('admin/notices.html', notices=notices)

@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    return render_template('admin/settings.html')

@admin_bp.route('/fee/reports')
@login_required
@admin_required
def fee_reports():
    # Get date range from request args
    start_date = request.args.get('start_date', default=datetime.now().replace(day=1).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', default=datetime.now().strftime('%Y-%m-%d'))
    
    # Get fee type filter
    fee_type_id = request.args.get('fee_type', default=None, type=int)
    
    # Get class filter
    class_id = request.args.get('class_id', default=None, type=int)
    
    # Query fee collections with filters
    query = FeeCollection.query\
        .join(Student)\
        .join(FeeType)
    
    if fee_type_id:
        query = query.filter(FeeType.id == fee_type_id)
    if class_id:
        query = query.filter(Student.class_id == class_id)
    
    query = query.filter(
        FeeCollection.payment_date.between(start_date, end_date)
    )
    
    collections = query.all()
    
    # Calculate summary statistics
    total_collected = sum(c.amount for c in collections)
    payment_methods = Counter(c.payment_method for c in collections)
    daily_collections = defaultdict(float)
    for c in collections:
        daily_collections[c.payment_date.strftime('%Y-%m-%d')] += c.amount
    
    # Get all fee types and classes for filters
    fee_types = FeeType.query.all()
    classes = Class.query.all()
    
    return render_template('admin/fee_reports.html',
                         collections=collections,
                         total_collected=total_collected,
                         payment_methods=dict(payment_methods),
                         daily_collections=dict(daily_collections),
                         fee_types=fee_types,
                         classes=classes,
                         start_date=start_date,
                         end_date=end_date,
                         selected_fee_type=fee_type_id,
                         selected_class=class_id)

@admin_bp.route('/edit/about', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_about():
    # Get current about page content
    about_content = AboutPage.query.first()
    
    if request.method == 'POST':
        # Update about page content
        title = request.form.get('title')
        content = request.form.get('content')
        mission = request.form.get('mission')
        vision = request.form.get('vision')
        
        if about_content:
            about_content.title = title
            about_content.content = content
            about_content.mission = mission
            about_content.vision = vision
        else:
            about_content = AboutPage(
                title=title,
                content=content,
                mission=mission,
                vision=vision
            )
            db.session.add(about_content)
        
        try:
            db.session.commit()
            flash('About page updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating about page. Please try again.', 'danger')
        
        return redirect(url_for('admin.edit_about'))
    
    return render_template('admin/edit_about.html', about=about_content)

@admin_bp.route('/edit/contact', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_contact():
    # Get current contact page content
    contact_content = WebsiteContent.query.filter_by(page='contact').first()
    
    if request.method == 'POST':
        # Get form data
        contact_data = {
            'address': request.form.get('address'),
            'main_phone': request.form.get('main_phone'),
            'admissions_phone': request.form.get('admissions_phone'),
            'fax': request.form.get('fax'),
            'general_email': request.form.get('general_email'),
            'admissions_email': request.form.get('admissions_email'),
            'support_email': request.form.get('support_email'),
            'office_hours': request.form.get('office_hours'),
            'facebook': request.form.get('facebook'),
            'twitter': request.form.get('twitter'),
            'instagram': request.form.get('instagram'),
            'linkedin': request.form.get('linkedin'),
            'map_embed_url': request.form.get('map_embed_url'),
            'departments': request.form.getlist('departments[]')
        }
        
        if contact_content:
            # Update existing content
            contact_content.content = json.dumps(contact_data)
            contact_content.updated_by = current_user.id
        else:
            # Create new content
            contact_content = WebsiteContent(
                page='contact',
                section='main',
                content=json.dumps(contact_data),
                updated_by=current_user.id
            )
            db.session.add(contact_content)
        
        try:
            db.session.commit()
            flash('Contact page updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating contact page. Please try again.', 'danger')
        
        return redirect(url_for('admin.edit_contact'))
    
    # For GET request, prepare contact data
    contact_data = {}
    if contact_content:
        try:
            contact_data = json.loads(contact_content.content)
        except:
            flash('Error loading contact page content.', 'warning')
    
    return render_template('admin/edit_contact.html', contact=contact_data)

@admin_bp.route('/teacher/<int:teacher_id>')
@login_required
@admin_required
def get_teacher(teacher_id):
    teacher = User.query.filter_by(id=teacher_id, role='teacher').first_or_404()
    return jsonify({
        'id': teacher.id,
        'name': teacher.name,
        'email': teacher.email,
        'phone': teacher.phone,
        'subjects': [s.id for s in teacher.subjects]
    })

@admin_bp.route('/teacher/add', methods=['POST'])
@login_required
@admin_required
def add_teacher():
    data = request.form
    
    # Create new teacher user
    teacher = User(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone', ''),
        role='teacher'
    )
    teacher.set_password(data['password'])
    
    # Add subjects
    if 'subjects' in data:
        subject_ids = request.form.getlist('subjects')
        subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
        teacher.subjects = subjects
    
    db.session.add(teacher)
    db.session.commit()
    
    flash('Teacher added successfully!', 'success')
    return redirect(url_for('admin.teachers'))

@admin_bp.route('/teacher/<int:teacher_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_teacher(teacher_id):
    teacher = User.query.filter_by(id=teacher_id, role='teacher').first_or_404()
    data = request.form
    
    teacher.name = data['name']
    teacher.email = data['email']
    teacher.phone = data.get('phone', '')
    
    if 'subjects' in data:
        subject_ids = request.form.getlist('subjects')
        subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
        teacher.subjects = subjects
    
    db.session.commit()
    flash('Teacher updated successfully!', 'success')
    return redirect(url_for('admin.teachers'))

@admin_bp.route('/teacher/<int:teacher_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_teacher(teacher_id):
    teacher = User.query.filter_by(id=teacher_id, role='teacher').first_or_404()
    db.session.delete(teacher)
    db.session.commit()
    flash('Teacher deleted successfully!', 'success')
    return redirect(url_for('admin.teachers'))

@admin_bp.route('/student/<int:student_id>')
@login_required
@admin_required
def get_student(student_id):
    student = User.query.filter_by(id=student_id, role='student').first_or_404()
    return jsonify({
        'id': student.id,
        'name': student.name,
        'email': student.email,
        'class_id': student.class_id,
        'section_id': student.section_id,
        'roll_no': student.roll_no,
        'guardian_name': student.guardian_name,
        'phone': student.phone
    })

@admin_bp.route('/student/add', methods=['POST'])
@login_required
@admin_required
def add_student():
    data = request.form
    
    # Create new student user
    student = User(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone', ''),
        role='student',
        class_id=data['class_id'],
        section_id=data['section_id'],
        roll_no=data['roll_no'],
        guardian_name=data['guardian_name']
    )
    student.set_password(data['password'])
    
    db.session.add(student)
    db.session.commit()
    
    flash('Student added successfully!', 'success')
    return redirect(url_for('admin.students'))

@admin_bp.route('/student/<int:student_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_student(student_id):
    student = User.query.filter_by(id=student_id, role='student').first_or_404()
    data = request.form
    
    student.name = data['name']
    student.email = data['email']
    student.phone = data.get('phone', '')
    student.class_id = data['class_id']
    student.section_id = data['section_id']
    student.roll_no = data['roll_no']
    student.guardian_name = data['guardian_name']
    
    db.session.commit()
    flash('Student updated successfully!', 'success')
    return redirect(url_for('admin.students'))

@admin_bp.route('/student/<int:student_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_student(student_id):
    student = User.query.filter_by(id=student_id, role='student').first_or_404()
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('admin.students'))

@admin_bp.route('/class/<int:class_id>')
@login_required
@admin_required
def get_class(class_id):
    class_ = Class.query.get_or_404(class_id)
    return jsonify({
        'id': class_.id,
        'name': class_.name,
        'description': class_.description
    })

@admin_bp.route('/class/add', methods=['POST'])
@login_required
@admin_required
def add_class():
    data = request.form
    
    class_ = Class(
        name=data['name'],
        description=data.get('description', '')
    )
    
    db.session.add(class_)
    db.session.commit()
    
    flash('Class added successfully!', 'success')
    return redirect(url_for('admin.classes'))

@admin_bp.route('/class/<int:class_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_class(class_id):
    class_ = Class.query.get_or_404(class_id)
    data = request.form
    
    class_.name = data['name']
    class_.description = data.get('description', '')
    
    db.session.commit()
    flash('Class updated successfully!', 'success')
    return redirect(url_for('admin.classes'))

@admin_bp.route('/class/<int:class_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_class(class_id):
    class_ = Class.query.get_or_404(class_id)
    
    # Delete associated sections and student assignments
    for section in class_.sections:
        db.session.delete(section)
    
    # Update students to remove class assignment
    for student in class_.students:
        student.class_id = None
        student.section_id = None
    
    db.session.delete(class_)
    db.session.commit()
    flash('Class deleted successfully!', 'success')
    return redirect(url_for('admin.classes'))

@admin_bp.route('/section/<int:section_id>')
@login_required
@admin_required
def get_section(section_id):
    section = Section.query.get_or_404(section_id)
    return jsonify({
        'id': section.id,
        'name': section.name,
        'class_id': section.class_id
    })

@admin_bp.route('/section/add', methods=['POST'])
@login_required
@admin_required
def add_section():
    data = request.form
    
    section = Section(
        name=data['name'],
        class_id=data['class_id']
    )
    
    db.session.add(section)
    db.session.commit()
    
    flash('Section added successfully!', 'success')
    return redirect(url_for('admin.sections'))

@admin_bp.route('/section/<int:section_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_section(section_id):
    section = Section.query.get_or_404(section_id)
    data = request.form
    
    section.name = data['name']
    section.class_id = data['class_id']
    
    db.session.commit()
    flash('Section updated successfully!', 'success')
    return redirect(url_for('admin.sections'))

@admin_bp.route('/section/<int:section_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_section(section_id):
    section = Section.query.get_or_404(section_id)
    
    # Update students to remove section assignment
    for student in section.students:
        student.section_id = None
    
    db.session.delete(section)
    db.session.commit()
    flash('Section deleted successfully!', 'success')
    return redirect(url_for('admin.sections'))

@admin_bp.route('/subject/<int:subject_id>')
@login_required
@admin_required
def get_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return jsonify({
        'id': subject.id,
        'name': subject.name,
        'code': subject.code,
        'description': subject.description
    })

@admin_bp.route('/subject/add', methods=['POST'])
@login_required
@admin_required
def add_subject():
    data = request.form
    
    subject = Subject(
        name=data['name'],
        code=data['code'],
        description=data.get('description', '')
    )
    
    db.session.add(subject)
    db.session.commit()
    
    flash('Subject added successfully!', 'success')
    return redirect(url_for('admin.subjects'))

@admin_bp.route('/subject/<int:subject_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    data = request.form
    
    subject.name = data['name']
    subject.code = data['code']
    subject.description = data.get('description', '')
    
    db.session.commit()
    flash('Subject updated successfully!', 'success')
    return redirect(url_for('admin.subjects'))

@admin_bp.route('/subject/<int:subject_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Remove subject from teachers
    for teacher in subject.teachers:
        teacher.subjects.remove(subject)
    
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('admin.subjects'))

@admin_bp.route('/class/<int:class_id>/sections')
@login_required
@admin_required
def get_class_sections(class_id):
    sections = Section.query.filter_by(class_id=class_id).all()
    return jsonify([{'id': s.id, 'name': s.name} for s in sections])

@admin_bp.route('/attendance/students')
@login_required
@admin_required
def get_attendance_students():
    class_id = request.args.get('class_id', type=int)
    section_id = request.args.get('section_id', type=int)
    date = request.args.get('date')
    
    students = User.query.filter_by(
        role='student',
        class_id=class_id,
        section_id=section_id
    ).order_by(User.roll_no).all()
    
    # Get existing attendance records
    attendance_records = {
        a.student_id: a.status 
        for a in Attendance.query.filter_by(date=date, class_id=class_id, section_id=section_id).all()
    }
    
    return jsonify([{
        'id': s.id,
        'roll_no': s.roll_no,
        'name': s.name,
        'status': attendance_records.get(s.id, 'present')
    } for s in students])

@admin_bp.route('/attendance/save', methods=['POST'])
@login_required
@admin_required
def save_attendance():
    date = request.form.get('date')
    class_id = request.form.get('class_id', type=int)
    section_id = request.form.get('section_id', type=int)
    
    # Delete existing attendance records for this date and class/section
    Attendance.query.filter_by(
        date=date,
        class_id=class_id,
        section_id=section_id
    ).delete()
    
    # Get all students in this class/section
    students = User.query.filter_by(
        role='student',
        class_id=class_id,
        section_id=section_id
    ).all()
    
    # Create new attendance records
    for student in students:
        status = request.form.get(f'status_{student.id}', 'absent')
        remarks = request.form.get(f'remarks_{student.id}', '')
        
        attendance = Attendance(
            date=date,
            class_id=class_id,
            section_id=section_id,
            student_id=student.id,
            status=status,
            remarks=remarks
        )
        db.session.add(attendance)
    
    db.session.commit()
    flash('Attendance saved successfully!', 'success')
    return redirect(url_for('admin.attendance'))

@admin_bp.route('/attendance/report')
@login_required
@admin_required
def attendance_report():
    class_id = request.args.get('class_id', type=int)
    section_id = request.args.get('section_id', type=int)
    month = request.args.get('month')  # Format: YYYY-MM
    
    if not all([class_id, section_id, month]):
        return jsonify([])
    
    year, month = map(int, month.split('-'))
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    # Get all students in this class/section
    students = User.query.filter_by(
        role='student',
        class_id=class_id,
        section_id=section_id
    ).order_by(User.roll_no).all()
    
    # Get attendance records for the month
    attendance_records = Attendance.query.filter(
        Attendance.class_id == class_id,
        Attendance.section_id == section_id,
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).all()
    
    # Calculate attendance statistics
    stats = defaultdict(lambda: {'present': 0, 'absent': 0})
    for record in attendance_records:
        if record.status == 'present':
            stats[record.student_id]['present'] += 1
        else:
            stats[record.student_id]['absent'] += 1
    
    # Calculate working days
    working_days = len(set(r.date for r in attendance_records))
    
    return jsonify([{
        'roll_no': student.roll_no,
        'name': student.name,
        'present_days': stats[student.id]['present'],
        'absent_days': stats[student.id]['absent'],
        'attendance_percentage': round(
            (stats[student.id]['present'] / working_days * 100)
            if working_days > 0 else 0,
            2
        )
    } for student in students])

@admin_bp.route('/exam/<int:exam_id>')
@login_required
@admin_required
def get_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    return jsonify({
        'id': exam.id,
        'name': exam.name,
        'term': exam.term,
        'class_id': exam.class_id,
        'start_date': exam.start_date.strftime('%Y-%m-%d'),
        'end_date': exam.end_date.strftime('%Y-%m-%d'),
        'is_active': exam.is_active
    })

@admin_bp.route('/exam/add', methods=['POST'])
@login_required
@admin_required
def add_exam():
    data = request.form
    
    exam = Exam(
        name=data['name'],
        term=data['term'],
        class_id=data['class_id'],
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
        is_active=bool(data.get('is_active'))
    )
    
    db.session.add(exam)
    db.session.commit()
    
    flash('Exam added successfully!', 'success')
    return redirect(url_for('admin.exams'))

@admin_bp.route('/exam/<int:exam_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    data = request.form
    
    exam.name = data['name']
    exam.term = data['term']
    exam.class_id = data['class_id']
    exam.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    exam.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    exam.is_active = bool(data.get('is_active'))
    
    db.session.commit()
    flash('Exam updated successfully!', 'success')
    return redirect(url_for('admin.exams'))

@admin_bp.route('/exam/<int:exam_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    
    # Delete all results associated with this exam
    ExamResult.query.filter_by(exam_id=exam_id).delete()
    
    db.session.delete(exam)
    db.session.commit()
    flash('Exam deleted successfully!', 'success')
    return redirect(url_for('admin.exams'))

@admin_bp.route('/exam/<int:exam_id>/subjects')
@login_required
@admin_required
def exam_subjects(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    subjects = Subject.query.filter_by(class_id=exam.class_id).all()
    return render_template('admin/exam_subjects.html', exam=exam, subjects=subjects)

@admin_bp.route('/exam/<int:exam_id>/results')
@login_required
@admin_required
def exam_results(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    return render_template('admin/results.html', exam=exam)

@admin_bp.route('/results/students')
@login_required
@admin_required
def get_results_students():
    exam_id = request.args.get('exam_id', type=int)
    class_id = request.args.get('class_id', type=int)
    section_id = request.args.get('section_id', type=int)
    
    students = User.query.filter_by(
        role='student',
        class_id=class_id,
        section_id=section_id
    ).order_by(User.roll_no).all()
    
    subjects = Subject.query.filter_by(class_id=class_id).all()
    
    # Get existing results
    results = {}
    exam_results = ExamResult.query.filter_by(
        exam_id=exam_id,
        class_id=class_id,
        section_id=section_id
    ).all()
    
    for result in exam_results:
        if result.student_id not in results:
            results[result.student_id] = {
                'remarks': result.remarks
            }
        results[result.student_id][result.subject_id] = result.marks
    
    return jsonify({
        'students': [{
            'id': s.id,
            'roll_no': s.roll_no,
            'name': s.name
        } for s in students],
        'subjects': [{
            'id': s.id,
            'name': s.name
        } for s in subjects],
        'results': results
    })

@admin_bp.route('/results/save', methods=['POST'])
@login_required
@admin_required
def save_results():
    exam_id = request.form.get('exam_id', type=int)
    class_id = request.form.get('class_id', type=int)
    section_id = request.form.get('section_id', type=int)
    
    # Delete existing results
    ExamResult.query.filter_by(
        exam_id=exam_id,
        class_id=class_id,
        section_id=section_id
    ).delete()
    
    # Get all students and subjects
    students = User.query.filter_by(
        role='student',
        class_id=class_id,
        section_id=section_id
    ).all()
    
    subjects = Subject.query.filter_by(class_id=class_id).all()
    
    # Save new results
    for student in students:
        remarks = request.form.get(f'remarks_{student.id}', '')
        
        for subject in subjects:
            marks = request.form.get(f'marks_{student.id}_{subject.id}', type=int)
            if marks is not None:
                result = ExamResult(
                    exam_id=exam_id,
                    class_id=class_id,
                    section_id=section_id,
                    student_id=student.id,
                    subject_id=subject.id,
                    marks=marks,
                    remarks=remarks
                )
                db.session.add(result)
    
    db.session.commit()
    flash('Results saved successfully!', 'success')
    return redirect(url_for('admin.exam_results', exam_id=exam_id))

@admin_bp.route('/results/report')
@login_required
@admin_required
def generate_results_report():
    exam_id = request.args.get('exam_id', type=int)
    report_type = request.args.get('report_type')
    
    exam = Exam.query.get_or_404(exam_id)
    
    if report_type == 'class':
        return generate_class_report(exam)
    elif report_type == 'student':
        return generate_student_report(exam)
    else:
        flash('Invalid report type!', 'error')
        return redirect(url_for('admin.exam_results', exam_id=exam_id))

def generate_class_report(exam):
    # Get all results for this exam
    results = ExamResult.query.filter_by(exam_id=exam.id).all()
    
    # Calculate class statistics
    stats = defaultdict(lambda: {
        'total_students': 0,
        'pass_students': 0,
        'fail_students': 0,
        'highest_marks': 0,
        'lowest_marks': 100,
        'average_marks': 0
    })
    
    for result in results:
        stats[result.subject_id]['total_students'] += 1
        if result.marks >= 50:
            stats[result.subject_id]['pass_students'] += 1
        else:
            stats[result.subject_id]['fail_students'] += 1
        stats[result.subject_id]['highest_marks'] = max(stats[result.subject_id]['highest_marks'], result.marks)
        stats[result.subject_id]['lowest_marks'] = min(stats[result.subject_id]['lowest_marks'], result.marks)
        stats[result.subject_id]['average_marks'] += result.marks
    
    # Calculate averages
    subjects = Subject.query.filter_by(class_id=exam.class_id).all()
    for subject in subjects:
        if stats[subject.id]['total_students'] > 0:
            stats[subject.id]['average_marks'] /= stats[subject.id]['total_students']
    
    return render_template('admin/reports/class_report.html',
                         exam=exam,
                         subjects=subjects,
                         stats=stats)

def generate_student_report(exam):
    # Get all results for this exam
    results = ExamResult.query.filter_by(exam_id=exam.id).all()
    
    # Organize results by student
    student_results = defaultdict(list)
    for result in results:
        student_results[result.student_id].append(result)
    
    # Calculate student statistics
    students = []
    for student_id, student_marks in student_results.items():
        student = User.query.get(student_id)
        total_marks = sum(r.marks for r in student_marks)
        average_marks = total_marks / len(student_marks)
        passed_subjects = sum(1 for r in student_marks if r.marks >= 50)
        
        students.append({
            'student': student,
            'total_marks': total_marks,
            'average_marks': average_marks,
            'passed_subjects': passed_subjects,
            'total_subjects': len(student_marks),
            'results': sorted(student_marks, key=lambda r: r.subject.name)
        })
    
    # Sort students by average marks
    students.sort(key=lambda s: s['average_marks'], reverse=True)
    
    return render_template('admin/reports/student_report.html',
                         exam=exam,
                         students=students)

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    return render_template('admin/reports.html') 