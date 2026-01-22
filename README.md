# Staff Hub Backend API

Django REST API backend for Staff Hub Lite - A modern HR Management System.

## Features

- 🔐 JWT-based authentication (login, signup, logout)
- 👥 Employee management (CRUD operations)
- 📅 Attendance tracking and management
- 📊 Dashboard statistics
- 🔍 Advanced filtering and search
- 🌐 CORS enabled for frontend integration
- 📱 RESTful API design

## Tech Stack

- **Django 5.0** - Web framework
- **Django REST Framework** - API toolkit
- **Simple JWT** - JWT authentication
- **SQLite** - Database (easily switchable to PostgreSQL/MySQL)
- **django-cors-headers** - CORS middleware

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

### 1. Clone and Navigate to Server Directory

```bash
cd server
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Setup

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your settings (optional for development)
```

### 5. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create a superuser (admin account)
python manage.py createsuperuser
```

### 6. Load Demo Data (Optional)

```bash
# Create demo admin user
python manage.py shell
```

Then in the Python shell:
```python
from api.models import User
User.objects.create_user(
    email='admin@hrms.com',
    password='admin123',
    name='Admin User',
    role='Administrator',
    department='Management'
)
exit()
```

### 7. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/signup/` | Register new user | No |
| POST | `/api/auth/login/` | Login user | No |
| POST | `/api/auth/logout/` | Logout user | Yes |
| GET | `/api/auth/profile/` | Get user profile | Yes |
| PUT | `/api/auth/profile/` | Update user profile | Yes |
| POST | `/api/auth/token/refresh/` | Refresh access token | Yes |

### Employees

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/employees/` | List all employees | Yes |
| POST | `/api/employees/` | Create new employee | Yes |
| GET | `/api/employees/{id}/` | Get employee details | Yes |
| PUT | `/api/employees/{id}/` | Update employee | Yes |
| DELETE | `/api/employees/{id}/` | Delete employee | Yes |
| GET | `/api/employees/check_unique/` | Check if employee_id or email is unique | Yes |

### Attendance

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/attendance/` | List attendance records | Yes |
| POST | `/api/attendance/mark/` | Mark attendance | Yes |
| GET | `/api/attendance/today_stats/` | Get today's statistics | Yes |
| GET | `/api/attendance/by_employee/` | Get attendance by employee | Yes |
| GET | `/api/attendance/by_date/` | Get attendance by date | Yes |

### Dashboard

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/dashboard/stats/` | Get dashboard statistics | Yes |

## API Request/Response Examples

### Login

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@hrms.com",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "user": {
    "id": "uuid-here",
    "email": "admin@hrms.com",
    "name": "Admin User",
    "role": "Administrator",
    "department": "Management",
    "joinedAt": "2024-01-01T00:00:00Z"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Create Employee

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/employees/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "employee_id": "EMP001",
    "full_name": "John Doe",
    "email": "john@example.com",
    "department": "Engineering"
  }'
```

**Response:**
```json
{
  "id": "uuid-here",
  "employee_id": "EMP001",
  "full_name": "John Doe",
  "email": "john@example.com",
  "department": "Engineering",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Mark Attendance

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/attendance/mark/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "employee_id": "uuid-of-employee",
    "date": "2024-01-15",
    "status": "present"
  }'
```

## Query Parameters

### Employees List
- `department` - Filter by department
- `search` - Search by name, employee_id, or email

Example: `/api/employees/?department=Engineering&search=john`

### Attendance List
- `employee_id` - Filter by employee
- `date` - Filter by specific date
- `start_date` & `end_date` - Filter by date range

Example: `/api/attendance/?employee_id=uuid&start_date=2024-01-01&end_date=2024-01-31`

## Admin Panel

Access the Django admin panel at `http://127.0.0.1:8000/admin/`

Use the superuser credentials you created during setup.
