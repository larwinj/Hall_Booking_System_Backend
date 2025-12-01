# 🎭 Hall Booking System - Backend API

> **A modern, scalable, and feature-rich backend system for seamless hall booking management with real-time availability, secure payments, and comprehensive analytics.**


## 🎯 Project Overview

The **Hall Booking System** is a comprehensive backend solution designed to revolutionize the hall booking experience. It eliminates the friction of traditional booking processes by providing:

- **Unified Availability Management**: Real-time visibility across all venues and time slots
- **Transparent Pricing**: Clear cost breakdown with add-ons and instant quotes
- **Instant Confirmations**: Immediate booking confirmation with digital receipts
- **Self-Service Flexibility**: Easy rescheduling, add-ons management, and cancellations
- **Role-Based Management**: Separate interfaces for admins, vendors, customers, and guests
- **Advanced Analytics**: Comprehensive reporting and insights for business decisions

### Problem it Solves

Traditional hall booking is:
- ❌ Time-consuming and fragmented
- ❌ Prone to double-bookings and miscommunication
- ❌ Lacking transparency in pricing
- ❌ Difficult to reschedule or modify

This system provides:
- ✅ Instant online search and booking
- ✅ Real-time availability verification
- ✅ Secure digital transactions
- ✅ Seamless booking management and modifications

---

## ⚡ Features

### Core Booking Features
- 🔍 **Intelligent Search**: Multi-criteria search with intelligent fallback filters
- 📅 **Real-time Availability**: Live availability checking with conflict prevention
- 💰 **Dynamic Pricing**: Room rates, add-on pricing, and cost calculations
- 🎫 **Instant Confirmations**: Automatic confirmation with PDF generation
- 📧 **Email Notifications**: Booking confirmations, cancellations, and updates
- 🔄 **Flexible Rescheduling**: Easy booking modifications with time-slot management
- ❌ **Smart Cancellations**: Refund policy enforcement with wallet credit
- 📊 **Booking Analytics**: Comprehensive reports and metrics

### User Management
- 👤 **User Registration & Login**: Secure authentication with JWT tokens
- 🔐 **Role-Based Access Control**: Granular permissions for different user types
- 📝 **Profile Management**: User details, preferences, and account settings
- 💳 **Wallet System**: Digital wallet for bookings, refunds, and credits
- ⭐ **Favorites**: Save preferred halls for quick booking
- 📝 **Reviews & Ratings**: User feedback and hall ratings

### Admin & Vendor Features
- 🏢 **Venue Management**: Create and manage multiple venues
- 🏛️ **Room Management**: Configure rooms, capacity, amenities, and pricing
- 🛍️ **Add-ons Management**: Define services and items for booking
- 📈 **Analytics & Reporting**: Detailed business intelligence and metrics
- 👥 **User Management**: Customer and vendor account management
- 🔧 **System Configuration**: CMS and system settings management
- 📞 **Query Management**: Track and respond to customer inquiries

### Advanced Features
- 🎥 **Virtual Meetings**: Integrated gRPC-based meeting service
- 💾 **Backup & Recovery**: Automated backup management
- 🔐 **Data Security**: Password hashing, JWT authentication, CORS protection
- ⏱️ **Rate Limiting**: API rate limiting for DOS protection
- 📋 **Audit Logging**: Comprehensive JSON logging for all operations
- 🔍 **Search Analytics**: Track and analyze user search patterns
- 💳 **Wallet Transactions**: Track all financial transactions

---

## 🛠️ Technology Stack

### Backend Framework
- **FastAPI** `v0.115.0` - Modern Python async web framework
- **Uvicorn** `v0.32.0` - ASGI server for FastAPI
- **Pydantic** `v2.9.2` - Data validation and settings management

### Databases
- **PostgreSQL** - Primary relational database
  - **SQLAlchemy** `v2.0.36` (async) - ORM and database abstraction
  - **asyncpg** `v0.29.0` - Async PostgreSQL driver
  - **Alembic** - Database migration tool
  
- **MongoDB** - NoSQL database for flexible schemas
  - **PyMongo** `v4.6.0` - MongoDB driver
  - **Motor** `v3.3.1` - Async MongoDB driver

### Authentication & Security
- **python-jose** `v3.3.0` - JWT (JSON Web Token) implementation
- **passlib[bcrypt]** `v1.7.4` - Password hashing with bcrypt
- **email-validator** `v2.2.0` - Email validation
- **bleach** `v6.1.0` - HTML sanitization

### API & Communication
- **httpx** `v0.27.2` - Async HTTP client
- **websockets** `v12.0` - WebSocket support
- **grpcio** `v1.59.0` - gRPC framework
- **grpcio-tools** `v1.59.0` - gRPC code generation

### Data Processing & Reporting
- **reportlab** `v4.0.7` - PDF generation
- **Jinja2** `v3.1.2` - Template engine
- **python-json-logger** `v2.0.7` - JSON logging
- **python-multipart** `v0.0.6` - Multipart form data handling

### Testing & Development
- **pytest** `v8.3.3` - Testing framework
- **pytest-asyncio** `v0.24.0` - Async test support
- **requests** `v2.31.0` - HTTP library for testing

### External Services
- **emails** `v0.6` - Email sending library
- **Vercel Blob Storage** - Cloud file storage

---

## 📦 Prerequisites

Before starting, ensure you have the following installed:

### System Requirements
- **Python**: 3.10 or higher
- **PostgreSQL**: 12 or higher (with asyncio support)
- **MongoDB**: 4.4 or higher (optional but recommended)
- **Git**: For version control

### Software Requirements
- **pip**: Python package manager (comes with Python)
- **Virtual Environment Tool**: `venv` (comes with Python) or `conda`
- **PostgreSQL Client**: `psql` (for database management)

### Accounts/Credentials (Optional)
- SMTP credentials for email functionality
- Vercel account for blob storage
- MongoDB Atlas (cloud MongoDB)

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/larwinj/Hall_Booking_System_Backend.git
cd hall-booking-backend
cd backend
```

### Step 2: Create Virtual Environment

**Using Python venv:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Using conda:**
```bash
conda create -n hall-booking-env python=3.10
conda activate hall-booking-env
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**Output example:**
```
Successfully installed fastapi-0.115.0 uvicorn-0.32.0 sqlalchemy-2.0.36 ...
```

### Step 4: Setup Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration (see [Environment Configuration](#environment-configuration))

### Step 5: Initialize Database

```bash
# Create PostgreSQL database
createdb hall_booking
```

### Step 6: Verify Installation

```bash
# Run tests to verify everything is working
pytest

# Check database connection
python scripts/check_db.py
```

---

## 🔧 Environment Configuration

Create a `.env` file in the `backend/` directory with the following variables:

### Database Configuration

```env
# PostgreSQL Configuration
POSTGRES_URL=postgresql+asyncpg://postgres:password@localhost:5432/hallbooking
POSTGRES_DB=hall_booking
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# MongoDB Configuration (for analytics and CMS)
MONGO_URI=mongodb://localhost:27017
MONGODB_DB_NAME=hall_booking_analytics
```

**Example with Docker Compose:**
```env
POSTGRES_URL=postgresql+asyncpg://postgres:LN24@postgres:5432/hallbooking
MONGO_URI=mongodb://mongo:27017
```

### Authentication & Security

```env
# JWT Configuration
JWT_SECRET=your_secret_key_here_min_32_characters
JWT_REFRESH_SECRET=your_refresh_secret_key_min_32_characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Guidelines:**
- Use strong, random keys (minimum 32 characters)
- Use different secrets for access and refresh tokens
- Never commit `.env` to version control
- Rotate secrets periodically in production

### CORS Configuration

```env
# CORS Origins (allow specific domains or use wildcard)
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]
# For development only (insecure in production)
BACKEND_CORS_ORIGINS=*
```

### Optional: Email Configuration

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=noreply@hallbooking.com
```

### Optional: Storage Configuration

```env
BLOB_READ_WRITE_TOKEN=your_vercel_blob_token
```

### Complete `.env.example`

```env
# Database
POSTGRES_URL=postgresql+asyncpg://postgres:LN24@localhost:5432/hallbooking
POSTGRES_DB=hall_booking
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
MONGO_URI=mongodb://mongo:27017

# Authentication
JWT_SECRET=please_change_me_to_a_strong_secret_key_32_chars_minimum
JWT_REFRESH_SECRET=please_change_me_refresh_to_strong_secret_key_32_chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

# CORS
BACKEND_CORS_ORIGINS=*

# MongoDB
MONGODB_DB_NAME=hall_booking_analytics

# Optional
BLOB_READ_WRITE_TOKEN=
```

---
---

## ▶️ Running the Application

### Development Mode

**Basic Startup:**
```bash
# Run with Uvicorn
uvicorn app.main:app --reload
```

**With Custom Port and Host:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**With Debug Logging:**
```bash
uvicorn app.main:app --reload --log-level debug
```

### Production Mode

**Basic Startup (Single Worker):**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000

```
---

## 📚 API Documentation

Once the application is running, access the interactive API documentation:

### Swagger UI (ReDoc Alternative)
- **URL**: `http://localhost:8000/docs`
- **Features**:
  - Interactive endpoint testing
  - Request/response schemas
  - Authentication token input
  - Real-time validation

### ReDoc (Alternative Documentation)
- **URL**: `http://localhost:8000/redoc`
- **Features**:
  - Beautiful documentation
  - Better for printing/sharing
  - Cleaner schema organization

### OpenAPI Schema
- **URL**: `http://localhost:8000/openapi.json`
- **Use**: For IDE integration, code generation

### Base URL
```
Development: http://localhost:8000
Production: https://api.yourdomain.com
```

### Authentication
All protected endpoints require JWT token in the header:

```bash
# Example API request
curl -X GET "http://localhost:8000/bookings/my-bookings" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

---

## 📁 Project Structure

```
backend/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   │
│   ├── api/                      # API routes
│   │   ├── deps.py               # Dependency injection (auth, DB session)
│   │   └── routes/               # All API endpoints
│   │       ├── auth.py           # Authentication (login, register, refresh)
│   │       ├── users.py          # User management
│   │       ├── venues.py         # Venue management
│   │       ├── rooms.py          # Room management
│   │       ├── bookings.py       # Booking creation & management
│   │       ├── booking_reports.py# Booking-specific reports
│   │       ├── addons.py         # Add-ons management
│   │       ├── favorites.py      # User favorites
│   │       ├── reviews.py        # Hall reviews & ratings
│   │       ├── queries.py        # Customer inquiries
│   │       ├── reports.py        # Analytics & reporting
│   │       ├── search.py         # Intelligent search
│   │       ├── cms.py            # Content management
│   │       ├── analyticsreports.py # Advanced analytics
│   │       ├── backup.py         # Backup management
│   │       ├── wallet.py         # Wallet transactions
│   │       ├── meetings.py       # Virtual meetings
│   │       ├── health.py         # Health checks
│   │       └── __pycache__/
│   │
│   ├── core/                     # Application configuration
│   │   ├── config.py             # Settings & environment variables
│   │   ├── security.py           # JWT token creation & validation
│   │   ├── email_config.py       # Email configuration
│   │   ├── logging_conf.py       # Logging setup
│   │   └── __pycache__/
│   │
│   ├── db/                       # Database configuration
│   │   ├── base.py               # Base class for SQLAlchemy models
│   │   ├── base_class.py         # Base model with common columns
│   │   ├── session.py            # Database session management
│   │   ├── mongo.py              # MongoDB client
│   │   ├── mongodb.py            # MongoDB connection pool
│   │   └── __pycache__/
│   │
│   ├── middleware/               # Request/response middleware
│   │   ├── cors.py               # CORS setup
│   │   ├── json_logging.py       # JSON request/response logging
│   │   ├── rate_limiting.py      # API rate limiting
│   │   ├── trusted_hosts.py      # Trusted hosts validation
│   │   └── __pycache__/
│   │
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── user.py               # User model & authentication
│   │   ├── venue.py              # Venue model
│   │   ├── room.py               # Room model
│   │   ├── booking.py            # Booking model
│   │   ├── booking_addon.py      # Booking add-ons junction table
│   │   ├── booking_customer.py    # Booking customer relationship
│   │   ├── booking_reschedule_history.py  # Reschedule tracking
│   │   ├── addon.py              # Add-ons model
│   │   ├── review.py             # Review & rating model
│   │   ├── favorite.py           # User favorites model
│   │   ├── wallet.py             # User wallet model
│   │   ├── report.py             # Report model
│   │   ├── report_cache.py       # Report caching
│   │   ├── backup.py             # Backup records
│   │   ├── query.py              # Customer inquiries
│   │   ├── enums.py              # Enum definitions
│   │   └── __pycache__/
│   │
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── common.py             # Common response schemas
│   │   ├── user.py               # User schemas
│   │   ├── venue.py              # Venue schemas
│   │   ├── room.py               # Room schemas
│   │   ├── booking.py            # Booking schemas
│   │   ├── addon.py              # Add-on schemas
│   │   ├── review.py             # Review schemas
│   │   ├── favorite.py           # Favorite schemas
│   │   ├── wallet.py             # Wallet schemas
│   │   ├── report.py             # Report schemas
│   │   ├── search.py             # Search request/response
│   │   ├── cms.py                # CMS schemas
│   │   └── __pycache__/
│   │
│   ├── services/                 # Business logic layer
│   │   ├── booking.py            # Booking service (creation, cancellation)
│   │   ├── availability_service.py     # Room availability checking
│   │   ├── booking_data_service.py     # Booking data operations
│   │   ├── email_service.py      # Email sending
│   │   ├── notification_service.py     # Notifications
│   │   ├── pdf_service.py        # PDF generation
│   │   ├── reports.py            # Report generation
│   │   ├── venue_report_service.py     # Venue-specific reports
│   │   ├── backup_service.py     # Backup operations
│   │   ├── vercel_blob_service.py      # Cloud storage
│   │   ├── wallet_service.py     # Wallet transactions
│   │   └── __pycache__/
│   │
│   ├── utils/                    # Utility functions
│   │   ├── search.py             # Search algorithm implementation
│   │   ├── mongo_utils.py        # MongoDB utilities
│   │   ├── cms_sanitize.py       # HTML sanitization
│   │   └── __pycache__/
│   │
│   └── templates/                # Email templates
│       └── emails/               # HTML email templates
│
├── meeting_service/              # gRPC Meeting Service
│   ├── __init__.py
│   ├── main.py                   # Service entry point
│   ├── grpc_server.py            # gRPC server setup
│   ├── grpc_service.py           # gRPC service implementation
│   ├── service.py                # Business logic
│   ├── models.py                 # Data models
│   ├── proto/                    # Protocol Buffer definitions
│   │   ├── meeting.proto         # Service definition
│   │   ├── meeting_pb2.py        # Generated code
│   │   └── meeting_pb2_grpc.py   # Generated gRPC code
│   └── __pycache__/
│
├── alembic/                      # Database migrations
│   ├── env.py                    # Alembic configuration
│   ├── script.py.mako            # Migration script template
│   ├── versions/                 # Migration history
│   │   ├── 04261a04e3fc_initial.py
│   │   ├── autogen_..._add_missing_columns.py
│   │   └── e32fad9e30c6_removed_the_dob.py
│   └── __pycache__/
│
├── scripts/                      # Utility scripts
│   ├── seed.py                   # Seed sample data
│   ├── check_db.py               # Database health check
│   ├── list_tables.py            # List all tables
│   ├── autogen_and_upgrade.py    # Run migrations
│   ├── ensure_alembic_version.py # Alembic setup
│   ├── finalize_migration.py     # Migration cleanup
│   └── col_print.py              # Column printer utility
│
├── templates/                    # HTML templates
│   ├── index.html                # Landing page
│   ├── create_meeting.html       # Meeting creation form
│   └── meeting.html              # Meeting view
│
├── tests/                        # Unit & integration tests
│   ├── test_booking.py           # Booking endpoint tests
│   ├── test_rooms.py             # Room endpoint tests
│   └── __pycache__/
│
├── logs/                         # Application logs
│   ├── app.jsonl                 # JSON request/response logs
│   └── app.jsonl.* (archived)    # Log archives
│
├── .env                          # Environment variables (local)
├── .env.example                  # Environment template
├── alembic.ini                   # Alembic configuration
├── Dockerfile                    # Docker image definition
├── docker-compose.yml            # Docker Compose configuration
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── temp.py                       # Temporary dev file
```

---

## 🔌 API Endpoints (Quick Reference)

### Authentication Routes (`/auth`)
```bash
POST   /auth/signup               # User registration
POST   /auth/login                # User login
POST   /auth/refresh              # Refresh access token
POST   /auth/logout               # User logout
POST   /auth/forgot-password      # Password reset request
POST   /auth/reset-password       # Reset password with token
```

### User Management (`/users`)
```bash
GET    /users/me                  # Get current user profile
PUT    /users/me                  # Update user profile
GET    /users/:id                 # Get specific user (admin)
PUT    /users/:id                 # Update user (admin)
DELETE /users/:id                 # Delete user (admin)
GET    /users                     # List all users (admin)
```

### Venue Management (`/venues`)
```bash
GET    /venues                    # List all venues
POST   /venues                    # Create new venue (vendor/admin)
GET    /venues/:id                # Get venue details
PUT    /venues/:id                # Update venue (owner/admin)
DELETE /venues/:id                # Delete venue (owner/admin)
GET    /venues/:id/rooms          # Get venue's rooms
```

### Room Management (`/rooms`)
```bash
GET    /rooms                     # List all rooms
POST   /rooms                     # Create room (vendor/admin)
GET    /rooms/:id                 # Get room details
PUT    /rooms/:id                 # Update room (owner/admin)
DELETE /rooms/:id                 # Delete room (owner/admin)
GET    /rooms/:id/availability    # Check availability
```

### Bookings (`/bookings`)
```bash
GET    /bookings                  # List user's bookings (filtered by role)
POST   /bookings                  # Create new booking
GET    /bookings/:id              # Get booking details
PUT    /bookings/:id              # Update booking (admin/owner)
DELETE /bookings/:id              # Cancel booking
POST   /bookings/:id/cancel       # Cancel with reason
POST   /bookings/:id/reschedule   # Reschedule booking
GET    /bookings/:id/pdf          # Download booking PDF
```

### Add-ons (`/addons`)
```bash
GET    /addons                    # List all add-ons
POST   /addons                    # Create add-on (vendor/admin)
GET    /addons/:id                # Get add-on details
PUT    /addons/:id                # Update add-on (owner/admin)
DELETE /addons/:id                # Delete add-on (owner/admin)
```

### Reviews & Ratings (`/reviews`)
```bash
GET    /reviews                   # List reviews
POST   /reviews                   # Create review (customer)
GET    /reviews/:id               # Get review details
PUT    /reviews/:id               # Update review
DELETE /reviews/:id               # Delete review
GET    /reviews/room/:id          # Get room reviews
```

### Favorites (`/favorites`)
```bash
GET    /favorites                 # List favorite halls
POST   /favorites/:room_id        # Add to favorites
DELETE /favorites/:room_id        # Remove from favorites
```

### Wallet Management (`/wallet`)
```bash
GET    /wallet                    # Get wallet balance & history
POST   /wallet/add-money          # Add funds to wallet
GET    /wallet/transactions       # View transactions
POST   /wallet/refund             # Initiate refund (admin)
```

### Search (`/search`)
```bash
GET    /search/rooms              # Search rooms with filters
  ?city=Metropolis
  &capacity=40
  &amenities=wifi&amenities=projector
  &date=2030-02-01
```

### Reports & Analytics (`/reports`)
```bash
GET    /reports/bookings          # Booking analytics
GET    /reports/revenue           # Revenue reports
GET    /reports/venues/:id        # Venue-specific reports
GET    /reports/user-activity     # User activity analytics
GET    /analytics/dashboard       # Dashboard metrics
```

### Health & System (`/health`)
```bash
GET    /health                    # Application health status
GET    /health/ready              # Readiness probe
```

### Virtual Meetings (`/meetings`)
```bash
POST   /meetings                  # Create meeting session
GET    /meetings/:id              # Get meeting details
POST   /meetings/:id/join         # Generate access token
DELETE /meetings/:id              # End meeting
```

**Note**: Replace `:id` with actual resource IDs. Add `?skip=0&limit=10` for pagination on list endpoints.

---

## 🔐 Authentication & Authorization

### JWT Token Flow

**1. Login & Token Generation**

```bash
# Step 1: Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**2. Use Token in Requests**

```bash
# Add token to Authorization header
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**3. Refresh Token When Expired**

```bash
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Authorization: Bearer {refresh_token}"

# Response: New access token
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc... (new)",
  "token_type": "bearer"
}
```

### Token Structure

```json
{
  "sub": "42",                    // User ID
  "iat": 1731398000,              // Issued at
  "exp": 1731401600,              // Expiration (30 mins)
  "type": "access",               // Token type
  "ver": 1                        // Token version (for logout)
}
```

### Token Security

- **Access Token**: 30 minutes (short-lived)
- **Refresh Token**: 7 days (long-lived)
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Storage**: httpOnly cookie (recommended) or localStorage
- **Transmission**: HTTPS only
- **Validation**: Signature, expiration, and version check

---

## 👥 User Roles & Permissions

### Role Hierarchy

```
┌─────────────────────────────────────────────┐
│ 1. ADMIN (Superuser)                        │
│    - Full system access                     │
│    - User management                        │
│    - System configuration                   │
│    - Analytics & reports                    │
│    - Financial management                   │
└─────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────┐
│ 2. MODERATOR/VENDOR (Content Creator)       │
│    - Own venue management                   │
│    - Room management                        │
│    - Add-on management                      │
│    - Booking management (own venues)        │
│    - Vendor-specific reports                │
└─────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────┐
│ 3. CUSTOMER (End User)                      │
│    - Search & browse halls                  │
│    - Create bookings                        │
│    - Manage own bookings                    │
│    - Leave reviews & ratings                │
│    - Wallet management                      │
│    - Add to favorites                       │
└─────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────┐
│ 4. GUEST (Limited Access)                   │
│    - Browse halls (read-only)               │
│    - View availability                      │
│    - No booking/payment capability          │
│    - Must register to book                  │
└─────────────────────────────────────────────┘
```

### Permission Matrix

| Feature | Admin | Vendor | Customer | Guest |
|---------|:-----:|:------:|:--------:|:-----:|
| Browse Halls | ✅ | ✅ | ✅ | ✅ |
| Search & Filter | ✅ | ✅ | ✅ | ✅ |
| View Pricing | ✅ | ✅ | ✅ | ✅ |
| Create Booking | ✅ | ✅ | ✅ | ❌ |
| Manage Own Bookings | ✅ | ✅ | ✅ | ❌ |
| Cancel Booking | ✅ | ✅ | ✅ | ❌ |
| Leave Reviews | ✅ | ❌ | ✅ | ❌ |
| Manage Venues | ✅ | Own Only | ❌ | ❌ |
| Manage All Bookings | ✅ | Own Venue | ❌ | ❌ |
| User Management | ✅ | ❌ | ❌ | ❌ |
| System Settings | ✅ | ❌ | ❌ | ❌ |
| View Reports | ✅ | Own Venue | Limited | ❌ |

#### 5. Migration Conflicts

**Solution:**
```bash
# Show current version
alembic current

# Show migration history
alembic history

# Downgrade to specific version
alembic downgrade <version>

# Re-generate migrations
alembic revision --autogenerate -m "Fix migration"
```


**Enable Debug Logging:**

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or in .env
LOG_LEVEL=debug

# Run application
uvicorn app.main:app --reload --log-level debug
```

**View Logs:**

```bash
# Real-time logs
tail -f logs/app.jsonl

# Pretty print logs
tail -f logs/app.jsonl | python -m json.tool

# Search logs for errors
grep '"level":"ERROR"' logs/app.jsonl
```

### Testing Requirements

- Write tests for new features
- Maintain >80% code coverage
- All tests must pass: `pytest`
- No breaking changes to existing APIs