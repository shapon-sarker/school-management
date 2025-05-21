# School Management System

A comprehensive school management system built with Flask, featuring separate portals for administrators, teachers, and students.

## Features

### Admin Portal
- User Management (Students, Teachers, Staff)
- Academic Management (Classes, Subjects, Schedules)
- Fee Management
- Content Management
- Reports & Analytics

### Teacher Portal
- Class Management
- Attendance Tracking
- Grade Management
- Study Materials Upload
- Student Performance Tracking

### Student Portal
- Profile Management
- Class Schedule Viewing
- Assignment Submission
- Fee Payment
- Result Access
- Attendance Tracking

## Advanced Features
- PDF/Excel Export for Reports
- Live Table Search & Filter
- ID Card Generation
- SMS/Email Notifications
- Dark Mode Support
- Print-Ready Templates

## Tech Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLAlchemy with SQLite/PostgreSQL/MySQL
- **Frontend**: Bootstrap 5, DataTables.js
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Email**: Flask-Mail
- **SMS**: Twilio
- **PDF Generation**: WeasyPrint
- **Excel Export**: openpyxl

## Installation

1. Clone the repository:
```bash
git clone git remote add origin https://github.com/shapon-sarker/school-management.git

cd school-management
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create .env file:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=your-phone-number
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the application:
```bash
flask run
```

## Deployment

### Prerequisites
- Python 3.8+
- PostgreSQL/MySQL for production
- Redis (optional, for caching)

### Deployment Options

1. **Render**
   - Fork this repository
   - Create a new Web Service on Render
   - Connect your repository
   - Set environment variables
   - Deploy

2. **Heroku**
   - Install Heroku CLI
   - Create Heroku app
   - Set environment variables
   - Deploy using Git

3. **Traditional Hosting**
   - Set up a Python environment
   - Install dependencies
   - Configure web server (Nginx/Apache)
   - Set up SSL certificate
   - Configure environment variables
   - Run with Gunicorn

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| SECRET_KEY | Flask secret key | Yes |
| DATABASE_URL | Database connection URL | Yes |
| MAIL_SERVER | SMTP server address | Yes |
| MAIL_PORT | SMTP server port | Yes |
| MAIL_USERNAME | SMTP username | Yes |
| MAIL_PASSWORD | SMTP password | Yes |
| TWILIO_ACCOUNT_SID | Twilio Account SID | No |
| TWILIO_AUTH_TOKEN | Twilio Auth Token | No |
| TWILIO_PHONE_NUMBER | Twilio Phone Number | No |
| REDIS_URL | Redis connection URL | No |

## Development

1. Create a new branch:
```bash
git checkout -b feature-name
```

2. Make your changes and commit:
```bash
git add .
git commit -m "Description of changes"
```

3. Push to your fork and submit a pull request

## Testing

Run tests using:
```bash
python -m pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, email support@yourschool.com or create an issue in the GitHub repository. 