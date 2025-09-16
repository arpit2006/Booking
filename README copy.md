# BookingMVP - Hotel Booking Platform

A comprehensive hotel booking platform built with Django, featuring modern UI/UX, secure payment processing, and complete booking management system.

## 🚀 Features

### Core Features
- **Advanced Hotel Search**: Search by location, dates, price range, amenities, and ratings
- **Real-time Booking**: Instant booking confirmation with email notifications
- **User Authentication**: Secure login/registration with role-based access
- **Payment Integration**: Secure payment processing with mock payment gateway
- **Review System**: User reviews and ratings for hotels
- **Admin Dashboard**: Comprehensive management panel for hotel owners
- **Email Notifications**: Automated booking confirmations and reminders
- **Responsive Design**: Mobile-first responsive design for all devices

### Technical Features
- **REST API**: Comprehensive API endpoints for mobile/web integration
- **Security**: Production-ready security features and HTTPS support
- **Performance**: Optimized queries and caching for fast response times
- **Scalability**: Modular architecture for easy scaling
- **Monitoring**: Comprehensive logging and error tracking

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.2.6
- **Database**: SQLite (development) / PostgreSQL (production)
- **API**: Django REST Framework
- **Authentication**: Django built-in auth + Token authentication
- **Email**: SMTP with HTML templates
- **Storage**: Local storage (development) / AWS S3 (production)

### Frontend
- **CSS Framework**: Bootstrap 5
- **JavaScript**: Vanilla JS with modern ES6+ features
- **Icons**: Font Awesome
- **Forms**: Crispy Forms with Bootstrap 5
- **Responsive**: Mobile-first design

### DevOps & Deployment
- **Environment**: django-environ for configuration
- **Static Files**: Django static files with compression
- **Security**: HTTPS, HSTS, CSRF protection, rate limiting
- **Monitoring**: Django logging with file and console handlers

## 📁 Project Structure

```
booking-mvp/
├── backend/                 # Django project settings
│   ├── settings.py         # Main settings file
│   ├── urls.py             # Root URL configuration
│   └── wsgi.py             # WSGI application
├── hotels/                 # Hotels app
│   ├── models.py           # Hotel, Booking, City models
│   ├── views.py            # Web and API views
│   ├── serializers.py      # DRF serializers
│   ├── urls.py             # Hotel URL patterns
│   ├── emails.py           # Email notification functions
│   └── admin.py            # Admin configurations
├── accounts/               # User accounts app
│   ├── models.py           # Custom User model
│   ├── views.py            # Auth views
│   ├── urls.py             # Account URL patterns
│   └── forms.py            # Authentication forms
├── core/                   # Core utilities app
│   ├── middleware.py       # Security middleware
│   ├── context_processors.py # Template context
│   └── views.py            # Utility views
├── reviews/                # Reviews app
│   ├── models.py           # Review model
│   └── admin.py            # Review admin
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── home.html           # Homepage
│   ├── hotels/             # Hotel templates
│   ├── accounts/           # Auth templates
│   └── emails/             # Email templates
├── static/                 # Static files
│   ├── css/                # Custom CSS
│   ├── js/                 # Custom JavaScript
│   └── images/             # Images
├── media/                  # User uploaded files
├── requirements.txt        # Python dependencies
├── manage.py               # Django management script
└── .env.example            # Environment variables template
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd booking-mvp
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env file with your configurations
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load sample data** (optional)
   ```bash
   python manage.py loaddata fixtures/sample_data.json
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Website: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/
   - API: http://127.0.0.1:8000/api/

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Basic Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (Production)
DB_NAME=booking_mvp
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=BookingMVP <noreply@bookingmvp.com>

# AWS S3 (Production)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Security (Production)
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Site Configuration
SITE_NAME=BookingMVP
BASE_URL=https://yourdomain.com
SUPPORT_EMAIL=support@yourdomain.com
ADMIN_URL=secure-admin-panel/
```

## 📚 API Documentation

### Authentication

All API endpoints support both Token and Session authentication.

**Get Token:**
```bash
POST /api-auth/token/
{
    "username": "your_username",
    "password": "your_password"
}
```

**Use Token:**
```bash
Authorization: Token your_token_here
```

### Endpoints

#### Hotels
- `GET /api/hotels/` - List all hotels
- `GET /api/hotels/{id}/` - Get hotel details
- `GET /api/hotels/featured/` - Get featured hotels
- `GET /api/hotels/search/` - Advanced hotel search

#### Bookings
- `GET /api/bookings/` - List user bookings
- `POST /api/bookings/` - Create new booking
- `GET /api/bookings/{id}/` - Get booking details
- `POST /api/bookings/{id}/cancel/` - Cancel booking
- `GET /api/bookings/upcoming/` - Get upcoming bookings
- `GET /api/bookings/history/` - Get booking history

#### Cities & Amenities
- `GET /api/cities/` - List all cities
- `GET /api/amenities/` - List all amenities

### API Examples

**Search Hotels:**
```bash
GET /api/hotels/search/?location=New York&check_in=2024-01-15&check_out=2024-01-20&guests=2
```

**Create Booking:**
```bash
POST /api/bookings/
{
    "hotel": 1,
    "check_in": "2024-01-15",
    "check_out": "2024-01-20",
    "guests": 2
}
```

## 🎨 Frontend Features

### User Interface
- **Modern Design**: Clean, professional design with consistent branding
- **Responsive Layout**: Mobile-first responsive design
- **Interactive Elements**: Smooth animations and transitions
- **Form Validation**: Client-side validation with user feedback
- **Loading States**: Loading indicators for better UX

### Key Pages
1. **Homepage**: Hero section, search form, featured hotels
2. **Hotel Search**: Advanced filters, sorting, pagination
3. **Hotel Details**: Image gallery, amenities, booking form
4. **User Dashboard**: Booking management, profile settings
5. **Hotel Owner Dashboard**: Property management, analytics

### JavaScript Features
- **AJAX Forms**: Form submissions without page reload
- **Dynamic Content**: Real-time price calculations
- **Interactive Maps**: Hotel location display (placeholder)
- **Image Galleries**: Hotel photo galleries with lightbox
- **Date Pickers**: User-friendly date selection

## 🔒 Security Features

### Authentication & Authorization
- **Secure Password Hashing**: bcrypt password hashing
- **Session Security**: Secure session configuration
- **CSRF Protection**: CSRF tokens on all forms
- **Rate Limiting**: API and login rate limiting
- **User Permissions**: Role-based access control

### Production Security
- **HTTPS Enforcement**: Automatic HTTPS redirect
- **Security Headers**: Comprehensive security headers
- **Content Security Policy**: CSP headers for XSS protection
- **HSTS**: HTTP Strict Transport Security
- **Secure Cookies**: Secure and HttpOnly cookie flags

### Monitoring & Logging
- **Security Logging**: Failed login attempts and suspicious activity
- **Error Tracking**: Comprehensive error logging
- **Access Logs**: Request logging for sensitive endpoints
- **Performance Monitoring**: Database query optimization

## 📧 Email System

### Email Templates
- **Booking Confirmation**: Detailed booking information
- **Welcome Email**: New user onboarding
- **Cancellation Notice**: Booking cancellation confirmation
- **Reminders**: Check-in/check-out reminders

### Email Features
- **HTML Templates**: Beautiful responsive email templates
- **Automatic Sending**: Triggered by user actions
- **Error Handling**: Graceful fallback for email failures
- **SMTP Support**: Compatible with all major email providers

## 🏗️ Development

### Adding New Features

1. **Create Models** in appropriate app
2. **Run Migrations** to update database
3. **Create Serializers** for API endpoints
4. **Implement Views** for web and API
5. **Add URL Patterns** to route requests
6. **Create Templates** for web interface
7. **Write Tests** for functionality
8. **Update Documentation**

### Code Style
- **PEP 8**: Follow Python style guidelines
- **Django Conventions**: Use Django best practices
- **Documentation**: Comment complex logic
- **Testing**: Write tests for new features

### Database Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Configure production database
- [ ] Set up email service (SMTP)
- [ ] Configure static file serving
- [ ] Set up media file storage (AWS S3)
- [ ] Configure domain and HTTPS
- [ ] Set security environment variables
- [ ] Run security checks
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

### Deployment Steps

1. **Server Setup**
   ```bash
   # Install dependencies
   sudo apt update
   sudo apt install python3 python3-pip nginx postgresql
   ```

2. **Database Setup**
   ```bash
   # Create PostgreSQL database
   sudo -u postgres createdb booking_mvp
   sudo -u postgres createuser --interactive
   ```

3. **Application Deployment**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd booking-mvp
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env with production values
   
   # Run migrations
   python manage.py migrate
   python manage.py collectstatic
   ```

4. **Web Server Configuration**
   ```nginx
   # Nginx configuration
   server {
       listen 80;
       server_name yourdomain.com;
       
       location /static/ {
           alias /path/to/booking-mvp/staticfiles/;
       }
       
       location /media/ {
           alias /path/to/booking-mvp/media/;
       }
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Monitoring

- **Application Logs**: Check Django logs regularly
- **Database Performance**: Monitor query performance
- **Server Resources**: Monitor CPU, memory, disk usage
- **User Activity**: Track user engagement metrics
- **Error Rates**: Monitor application error rates

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test hotels

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Types
- **Unit Tests**: Individual function testing
- **Integration Tests**: Feature workflow testing
- **API Tests**: Endpoint functionality testing
- **Frontend Tests**: User interface testing

## 📞 Support

### Getting Help
- **Documentation**: Check this README and code comments
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions
- **Email**: Contact support@bookingmvp.com

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request
5. Follow code review process

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap team for the responsive CSS framework
- Font Awesome for the beautiful icons
- All contributors and testers

---

**BookingMVP** - Building the future of hotel booking platforms! 🏨✨