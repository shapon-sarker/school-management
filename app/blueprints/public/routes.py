from flask import render_template, jsonify
from app.blueprints.public import public_bp
from datetime import datetime
import json
from flask import flash
from app.models.website_content import WebsiteContent

@public_bp.route('/')
def index():
    # Sample notices
    notices = [
        {
            'title': 'New Academic Year Registration',
            'date': '2024-03-15',
            'content': 'Registration for the new academic year 2024-25 is now open. Early bird discounts available until April 15th.'
        },
        {
            'title': 'Annual Sports Day',
            'date': '2024-03-20',
            'content': 'Annual Sports Day will be held on March 20th, 2024. All students are encouraged to participate.'
        },
        {
            'title': 'Parent-Teacher Meeting',
            'date': '2024-03-25',
            'content': 'Parent-Teacher Meeting scheduled for all classes. Please check the schedule for your ward\'s timing.'
        }
    ]
    
    # Sample news items
    news = [
        {
            'title': 'Outstanding Board Exam Results',
            'date': '2024-02-28',
            'image': 'news1.jpg',
            'summary': 'Our students achieved exceptional results in board examinations with 95% scoring distinction.'
        },
        {
            'title': 'Science Fair Winners',
            'date': '2024-02-15',
            'image': 'news2.jpg',
            'summary': 'Our students won first prize in the National Science Fair for their innovative project on renewable energy.'
        },
        {
            'title': 'New Computer Lab',
            'date': '2024-02-01',
            'image': 'news3.jpg',
            'summary': 'State-of-the-art computer lab with 50 workstations inaugurated to enhance digital learning.'
        }
    ]
    
    # Sample gallery images
    gallery_images = [
        {'src': 'campus1.jpg', 'title': 'Modern Campus Building'},
        {'src': 'lab1.jpg', 'title': 'Science Laboratory'},
        {'src': 'library1.jpg', 'title': 'Digital Library'},
        {'src': 'sports1.jpg', 'title': 'Sports Ground'},
        {'src': 'classroom1.jpg', 'title': 'Smart Classroom'},
        {'src': 'auditorium1.jpg', 'title': 'Modern Auditorium'}
    ]
    
    return render_template('public/index.html', 
                         title='Welcome to School Management System',
                         notices=notices,
                         news=news,
                         gallery_images=gallery_images)

@public_bp.route('/about')
def about():
    return render_template('public/about.html', title='About Us')

@public_bp.route('/academics')
def academics():
    current_year = datetime.now().year
    next_year = current_year + 1

    departments = [
        {
            'name': 'Science',
            'description': 'Offering Physics, Chemistry, and Biology with well-equipped laboratories',
            'icon': 'bi-flask'
        },
        {
            'name': 'Mathematics',
            'description': 'Advanced Mathematics and Statistics with focus on practical applications',
            'icon': 'bi-calculator'
        },
        {
            'name': 'Computer Science',
            'description': 'Modern programming languages and information technology courses',
            'icon': 'bi-laptop'
        },
        {
            'name': 'Languages',
            'description': 'English, French, and Spanish with native language instructors',
            'icon': 'bi-translate'
        },
        {
            'name': 'Arts & Humanities',
            'description': 'Literature, History, and Social Sciences with creative learning approach',
            'icon': 'bi-book'
        },
        {
            'name': 'Physical Education',
            'description': 'Sports, fitness training, and health education programs',
            'icon': 'bi-trophy'
        }
    ]
    return render_template('public/academics.html', 
                         title='Academics',
                         departments=departments,
                         current_year=current_year,
                         next_year=next_year)

@public_bp.route('/admissions')
def admissions():
    return render_template('public/admissions.html', title='Admissions')

@public_bp.route('/notice-board')
def notice_board():
    notices = [
        {
            'title': 'New Academic Year Registration',
            'date': '2024-03-15',
            'content': 'Registration for the new academic year 2024-25 is now open.',
            'category': 'Academic'
        },
        {
            'title': 'Annual Sports Day',
            'date': '2024-03-20',
            'content': 'Annual Sports Day will be held on March 20th, 2024.',
            'category': 'Sports'
        },
        {
            'title': 'Parent-Teacher Meeting',
            'date': '2024-03-25',
            'content': 'Parent-Teacher Meeting scheduled for all classes.',
            'category': 'Event'
        },
        {
            'title': 'Summer Camp Registration',
            'date': '2024-04-01',
            'content': 'Summer camp registration starts from April 1st, 2024.',
            'category': 'Activity'
        }
    ]
    return render_template('public/notice_board.html', 
                         title='Notice Board',
                         notices=notices)

@public_bp.route('/contact')
def contact():
    # Get contact page content
    contact_content = WebsiteContent.query.filter_by(page='contact', section='main').first()
    contact_data = {}
    
    if contact_content:
        try:
            contact_data = json.loads(contact_content.content)
        except:
            flash('Error loading contact page content.', 'warning')
    
    return render_template('public/contact.html', 
                         title='Contact Us',
                         contact=contact_data)

@public_bp.route('/gallery')
def gallery():
    images = [
        {'src': 'campus1.jpg', 'title': 'Modern Campus Building'},
        {'src': 'lab1.jpg', 'title': 'Science Laboratory'},
        {'src': 'library1.jpg', 'title': 'Digital Library'},
        {'src': 'sports1.jpg', 'title': 'Sports Ground'},
        {'src': 'classroom1.jpg', 'title': 'Smart Classroom'},
        {'src': 'auditorium1.jpg', 'title': 'Modern Auditorium'},
        {'src': 'cafeteria1.jpg', 'title': 'Student Cafeteria'},
        {'src': 'event1.jpg', 'title': 'Annual Day Celebration'},
        {'src': 'sports2.jpg', 'title': 'Indoor Sports Complex'}
    ]
    return render_template('public/gallery.html', 
                         title='Gallery',
                         images=images)

@public_bp.route('/calendar')
def calendar():
    current_year = datetime.now().year
    next_year = current_year + 1
    
    # Sample calendar events
    calendar_events = [
        {
            'term': 'First Term',
            'events': [
                {'date': f'September 1, {current_year}', 'event': 'First Term Begins'},
                {'date': f'October 15, {current_year}', 'event': 'Mid-Term Exams'},
                {'date': f'December 15, {current_year}', 'event': 'First Term Ends'}
            ]
        },
        {
            'term': 'Second Term',
            'events': [
                {'date': f'January 5, {next_year}', 'event': 'Second Term Begins'},
                {'date': f'February 15, {next_year}', 'event': 'Mid-Term Exams'},
                {'date': f'March 25, {next_year}', 'event': 'Second Term Ends'}
            ]
        },
        {
            'term': 'Third Term',
            'events': [
                {'date': f'April 5, {next_year}', 'event': 'Third Term Begins'},
                {'date': f'May 15, {next_year}', 'event': 'Mid-Term Exams'},
                {'date': f'June 30, {next_year}', 'event': 'Third Term Ends'}
            ]
        }
    ]
    
    return render_template('public/calendar.html', 
                         title='Academic Calendar',
                         calendar_events=calendar_events,
                         current_year=current_year,
                         next_year=next_year)

@public_bp.route('/result-search')
def result_search():
    return render_template('public/result_search.html', title='Search Results') 