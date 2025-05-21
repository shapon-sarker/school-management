# Deploying to Render

This guide will help you deploy the School Management System to Render.

## Prerequisites

1. A Render account (https://render.com)
2. A GitHub repository with your project
3. A PostgreSQL database (can be created on Render)

## Steps

### 1. Create a PostgreSQL Database

1. Log in to your Render dashboard
2. Click "New +" and select "PostgreSQL"
3. Fill in the details:
   - Name: `school-management-db`
   - Database: `school_db`
   - User: `school_user`
   - Region: (choose nearest to your users)
4. Click "Create Database"
5. Note down the "External Database URL"

### 2. Create a Web Service

1. Click "New +" and select "Web Service"
2. Connect your GitHub repository
3. Fill in the details:
   - Name: `school-management`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn "app:create_app('render')" --log-file -`
   - Instance Type: Choose based on your needs (start with "Starter")

### 3. Configure Environment Variables

Add the following environment variables in your web service settings:

```
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
DATABASE_URL=your-postgres-database-url
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number
```

### 4. Deploy

1. Click "Create Web Service"
2. Wait for the build and deployment to complete
3. Your app will be available at `https://your-app-name.onrender.com`

## Post-Deployment Steps

1. Initialize the database:
   ```bash
   flask db upgrade
   ```

2. Create an admin user:
   ```bash
   flask create-admin
   ```

3. Test all functionality:
   - User registration/login
   - File uploads
   - Email notifications
   - Database operations

## Monitoring and Maintenance

1. Set up monitoring in Render dashboard
2. Configure alerts for:
   - High CPU/Memory usage
   - Error rates
   - Response times

## Troubleshooting

1. Check logs in Render dashboard
2. Common issues:
   - Database connection errors
   - Static file serving issues
   - Email configuration problems

## Scaling

1. Upgrade instance type if needed
2. Enable auto-scaling
3. Configure caching with Redis
4. Optimize database queries

## Security

1. Enable HTTPS (automatic with Render)
2. Set secure headers
3. Configure CORS if needed
4. Regular security updates

## Backup

1. Enable automatic database backups
2. Configure backup retention period
3. Test backup restoration process 