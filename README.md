# Coderr Backend Project

A comprehensive Django REST Framework (DRF) backend application for a freelance marketplace platform, connecting business service providers with customers. The platform enables users to create profiles, post service offers, place orders, and leave reviews.

## 🚀 Key Features

- **User Authentication & Authorization**
  - Token-based authentication (DRF Token Auth)
  - User registration and login endpoints
  - Role-based user types (Business/Customer)

- **Profile Management**
  - Distinct profiles for business users and customers
  - Profile customization with images, location, contact details, and descriptions
  - Separate endpoints for business and customer profile listings

- **Offer System**
  - Create and manage service offers
  - Multi-tier pricing (Basic, Standard, Premium)
  - Customizable offer details including delivery time, revisions, and features
  - Image uploads for offers
  - Automatic price and delivery time calculations

- **Order Management**
  - Place orders on specific offer tiers
  - Order status tracking (In Progress, Completed, Canceled)
  - Separate views for customer and business orders

- **Review System**
  - Rate and review business users
  - Star-based rating system
  - Timestamp tracking for reviews

- **Advanced Features**
  - CORS support for frontend integration
  - Django-filter integration for advanced querying
  - Media file handling for images and documents
  - Comprehensive test coverage with pytest
  - Postman environment files for API testing

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- SQLite (included with Python)
- Virtual environment tool (optional but recommended)

## 🔧 Installation Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd coderr-backend-project-DA
```

### 2. Create and Activate Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## 💡 Usage Guide

### Authentication

**Register a New User:**
```http
POST /api/registration/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123",
  "password2": "SecurePassword123"
}
```

**Login:**
```http
POST /api/login/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1
}
```

### Using Authentication Token

Include the token in the Authorization header for protected endpoints:
```http
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### Profile Management

**Get Profile Details:**
```http
GET /api/profile/{id}/
Authorization: Token <your-token>
```

**Update Profile:**
```http
PUT /api/profile/{id}/
Authorization: Token <your-token>
Content-Type: multipart/form-data

{
  "first_name": "John",
  "last_name": "Doe",
  "location": "Berlin, Germany",
  "tel": "+491234567890",
  "description": "Professional web developer",
  "type": "business"
}
```

**List Business Profiles:**
```http
GET /api/profiles/business/
```

### Offers

**Create an Offer:**
```http
POST /api/offers/
Authorization: Token <your-token>
Content-Type: multipart/form-data

{
  "title": "Professional Logo Design",
  "description": "I will create a unique logo for your brand",
  "image": <file>
}
```

**List All Offers:**
```http
GET /api/offers/
```

**Get Specific Offer:**
```http
GET /api/offers/{id}/
```

### Orders

**Create an Order:**
```http
POST /api/orders/
Authorization: Token <your-token>
Content-Type: application/json

{
  "offer_detail": 1,
  "business_user": 2
}
```

**List Orders:**
```http
GET /api/orders/
Authorization: Token <your-token>
```

### Reviews

**Create a Review:**
```http
POST /api/reviews/
Authorization: Token <your-token>
Content-Type: application/json

{
  "business_user": 2,
  "rating": 5,
  "description": "Excellent service and fast delivery!"
}
```

## ⚙️ Configuration

### REST Framework Settings

The project uses the following DRF configuration:

- **Authentication:** Token Authentication
- **Filtering:** Django-filter backend enabled
- **CORS:** All origins allowed (configure for production)

### Media Files

Media files (user uploads) are stored in the `media/` directory. Configure `MEDIA_URL` and `MEDIA_ROOT` in [core/settings.py](core/settings.py) if needed.

## 🛠️ Technologies Used / Dependencies

### Core Framework
- **Django 5.2.7** - High-level Python web framework
- **Django REST Framework 3.16.1** - Powerful toolkit for building Web APIs

### Extensions & Utilities
- **django-cors-headers 4.9.0** - Handle Cross-Origin Resource Sharing (CORS)
- **django-filter 25.2** - Dynamic QuerySet filtering
- **djangorestframework-authtoken** - Token-based authentication

### Security & Utilities
- **python-dotenv 1.2.1** - Environment variable management
- **cryptography 46.0.2** - Cryptographic recipes and primitives
- **bcrypt 5.0.0** - Password hashing

### Testing & Development
- **pytest 9.0.2** - Testing framework
- **pytest-django 4.11.1** - Django plugin for pytest
- **pytest-cov 7.0.0** - Coverage plugin for pytest
- **coverage 7.13.0** - Code coverage measurement

### Deployment & DevOps
- **invoke 2.2.0** - Task execution tool
- **paramiko 4.0.0** - SSH2 protocol implementation

### Database
- **SQLite** (default) - Lightweight disk-based database

## 📁 Project Structure Overview

```
coderr-backend-project-DA/
│
├── core/                          # Main project configuration
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Root URL configuration
│   └── wsgi.py                   # WSGI configuration
│
├── auth_app/                      # User authentication
│   ├── api/
│   │   ├── views.py              # Registration and login views
│   │   └── urls.py               # Auth endpoints
│   └── models.py
│
├── profile_app/                   # User profile management
│   ├── api/
│   │   ├── views.py              # Profile CRUD operations
│   │   ├── serializers.py
│   │   └── urls.py
│   └── models.py                 # Profile model (Business/Customer)
│
├── offer_app/                     # Service offers
│   ├── api/
│   │   ├── views.py              # Offer and OfferDetail views
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── offer_filter.py       # Custom filters
│   └── models.py                 # Offer and OfferDetail models
│
├── order_app/                     # Order management
│   ├── api/
│   │   ├── views.py              # Order CRUD operations
│   │   ├── serializers.py
│   │   └── urls.py
│   └── models.py                 # Order model
│
├── review_app/                    # Review system
│   ├── api/
│   │   ├── views.py              # Review operations
│   │   ├── serializers.py
│   │   └── urls.py
│   └── models.py                 # Review model
│
├── baseinfo_app/                  # Base information/utilities
│   └── api/
│
├── media/                         # User-uploaded files
├── htmlcov/                       # Test coverage reports
│
├── manage.py                      # Django management script
├── db.sqlite3                     # SQLite database
├── requirements.txt               # Python dependencies
├── pytest.ini                     # Pytest configuration
├── .env                          # Environment variables (create this)
└── postman_env_*.json            # Postman test environments
```

## 🧪 Running Tests

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov
```

### Generate HTML Coverage Report
```bash
pytest --cov --cov-report=html
```

The coverage report will be available in the `htmlcov/` directory. Open `htmlcov/index.html` in your browser.

### Run Specific Test Module
```bash
pytest auth_app/tests/
pytest profile_app/tests/test_profile.py
```

## 📊 Database Schema

### Main Models

- **User** (Django built-in)
- **Profile** - Extended user information (OneToOne with User)
- **Offer** - Service offerings by business users
- **OfferDetail** - Pricing tiers for offers (Basic/Standard/Premium)
- **Order** - Customer orders for specific offer details
- **Review** - Customer reviews for business users

### Key Relationships

- User → Profile (One-to-One)
- User → Offers (One-to-Many)
- Offer → OfferDetails (One-to-Many)
- OfferDetail → Orders (One-to-Many)
- User → Orders (One-to-Many, as both customer and business)
- User → Reviews (One-to-Many, as both reviewer and business)

## 🔒 API Documentation

### Base URL
```
http://127.0.0.1:8000/api/
```

### Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/registration/` | Register new user | No |
| POST | `/login/` | User login | No |
| GET/PUT | `/profile/{id}/` | Profile details | Yes |
| GET | `/profiles/business/` | List business profiles | No |
| GET | `/profiles/customer/` | List customer profiles | No |
| GET/POST | `/offers/` | List/create offers | Yes (POST) |
| GET/PUT/DELETE | `/offers/{id}/` | Offer details | Yes (modify) |
| GET | `/offerdetails/{id}/` | Offer detail info | No |
| GET/POST | `/orders/` | List/create orders | Yes |
| GET/POST | `/reviews/` | List/create reviews | Yes |

**Note:** Use Postman collection files included in the repository for detailed API testing.

## 🔐 Security Considerations

- Configure `ALLOWED_HOSTS` properly for production deployment
- Implement proper CORS settings for production (avoid `CORS_ALLOW_ALL_ORIGINS = True`)
- Use HTTPS in production environments
- Regularly update dependencies to patch security vulnerabilities
- Use environment variables for sensitive configuration in production

## 🤝 Contribution Guidelines

### Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit: `git commit -m "Add your feature"`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Create a Pull Request

### Code Standards

- Follow PEP 8 style guidelines for Python code
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

### Running Code Quality Checks

```bash
# Run tests
pytest

# Check test coverage
pytest --cov --cov-report=term-missing
```

### Reporting Issues

- Use the issue tracker to report bugs
- Include detailed steps to reproduce the issue
- Provide environment information (OS, Python version, etc.)
- Attach relevant logs or screenshots


