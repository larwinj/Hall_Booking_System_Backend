# Hall Booking System – API Documentation

**Version:** 1.0.0

**Base URL:** `https://api.hallbooking.com/api/v1/`

**Framework:** FastAPI

**Last Updated:** November 15, 2025

**Authentication:** JWT Bearer Token (`Authorization: Bearer <access_token>`)

**Content Type:** `application/json`

---

## 📋 Overview

The **Hall Booking System** is a comprehensive FastAPI backend that enables users to search, book, and manage hall reservations. It provides role-based access for **Admin**, **Moderator/Vendor**, **Customer**, and **Guest** users with secure JWT authentication and integrated payment processing.

---

## 👥 Roles & Permissions

| Role | Capabilities |
|------|--------------|
| **Guest** | Browse halls, view availability, search (read-only) |
| **Customer** | Book halls, manage bookings, leave reviews, wallet management |
| **Moderator/Vendor** | Manage venues & rooms, approve bookings, view analytics |
| **Admin** | Full system access, user management, backup & recovery, reports |

---

## 🔐 Authentication Endpoints

### 1️⃣ **User Registration (Sign Up)**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/auth/signup` | ❌ | Register new customer account |

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass@123",
  "full_name": "John Doe",
  "phone": "+91-9876543210"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Registration successful",
  "user_id": 42,
  "email": "user@example.com"
}
```

---

### 2️⃣ **User Login**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/auth/login` | ❌ | Authenticate user and issue tokens |

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass@123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 42,
    "email": "user@example.com",
    "role": "customer"
  }
}
```

---

### 3️⃣ **Refresh Access Token**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/auth/refresh` | ✅ | Generate new access token |

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (new)",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### 4️⃣ **Logout**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/auth/logout` | ✅ | Revoke tokens and logout |

**Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### 5️⃣ **Forgot Password**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/auth/forgot-password` | ❌ | Request password reset |

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Reset link sent to email"
}
```

---

## 🏛️ Hall & Venue Endpoints

### 1️⃣ **Get All Venues (Browse)**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `GET` | `/venues` | ❌ | List all available venues |

**Query Parameters:**
- `skip=0` - Offset for pagination
- `limit=10` - Number of records
- `city=Metropolis` - Filter by city

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Grand Ballroom",
      "city": "Metropolis",
      "address": "123 Main St, Metropolis",
      "rating": 4.8,
      "rooms_count": 5,
      "amenities": ["WiFi", "Parking", "Catering"]
    }
  ],
  "total": 45,
  "page": 1
}
```

---

### 2️⃣ **Get Venue Details**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `GET` | `/venues/{venue_id}` | ❌ | Get specific venue details |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Grand Ballroom",
    "description": "Premium event space with modern facilities",
    "address": "123 Main St, Metropolis",
    "phone": "+91-9876543210",
    "email": "contact@ballroom.com",
    "rooms": [
      {
        "id": 10,
        "name": "Banquet Hall",
        "capacity": 100,
        "rate": 50.0,
        "amenities": ["Projector", "Sound System", "WiFi"]
      }
    ]
  }
}
```

---

### 3️⃣ **Get Rooms by Category**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `GET` | `/rooms` | ❌ | Get all rooms with filters |

**Query Parameters:**
- `category=Small` - Category filter (Small, Medium, Large)
- `capacity=40` - Minimum capacity
- `price_min=100` - Minimum price
- `price_max=500` - Maximum price

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 10,
      "name": "Banquet Hall A",
      "category": "Large",
      "capacity": 100,
      "rate": 50.0,
      "venue_id": 1,
      "amenities": ["Projector", "WiFi", "AC"],
      "photo_url": "https://..."
    }
  ],
  "total": 28
}
```

---

### 4️⃣ **Search Halls (Intelligent Search)**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `GET` | `/search/rooms` | ❌ | Advanced search with filters |

**Query Parameters:**
- `city=Metropolis`
- `capacity=40`
- `amenities=wifi&amenities=projector`
- `date=2030-02-01`
- `price_range=100-500`

**Response (200):**
```json
{
  "success": true,
  "query": {
    "criteria": {
      "city": "Metropolis",
      "capacity": 40,
      "amenities": ["wifi", "projector"]
    },
    "search_attempts": 2
  },
  "results": [
    {
      "room_id": 10,
      "name": "Banquet Hall",
      "capacity": 100,
      "available_slots": [
        {"start": "09:00", "end": "11:00"},
        {"start": "14:00", "end": "18:00"}
      ],
      "rating": 4.8
    }
  ],
  "count": 12
}
```

---

## 📅 Booking Endpoints

### 1️⃣ **Check Availability**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `GET` | `/rooms/{room_id}/availability` | ❌ | Check slot availability |

**Query Parameters:**
- `date=2030-02-01` - Required

**Response (200):**
```json
{
  "success": true,
  "date": "2030-02-01",
  "room_id": 10,
  "slots": [
    {"start": "08:00", "end": "09:00", "available": true},
    {"start": "09:00", "end": "10:00", "available": false},
    {"start": "10:00", "end": "11:00", "available": true},
    {"start": "14:00", "end": "18:00", "available": true}
  ]
}
```

---

### 2️⃣ **Create Booking**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/bookings` | ✅ | Create new booking |

**Request Body:**
```json
{
  "room_id": 10,
  "start_time": "2030-02-01T14:00:00Z",
  "end_time": "2030-02-01T18:00:00Z",
  "purpose": "Corporate Meeting",
  "attendees_count": 50,
  "special_requests": "Need vegetarian catering",
  "addons": [
    {"addon_id": 5, "quantity": 2},
    {"addon_id": 8, "quantity": 1}
  ]
}
```

**Response (201):**
```json
{
  "success": true,
  "booking_id": 42,
  "room_id": 10,
  "start_time": "2030-02-01T14:00:00Z",
  "end_time": "2030-02-01T18:00:00Z",
  "status": "pending",
  "total_cost": 250.0,
  "pdf_url": "https://storage.blob/invoice-42.pdf",
  "message": "Booking created successfully"
}
```

---

### 3️⃣ **Get My Bookings**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `GET` | `/bookings/my-bookings` | ✅ | Get user's bookings |

**Query Parameters:**
- `status=confirmed` - Filter by status
- `skip=0` - Pagination

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "booking_id": 42,
      "room_name": "Banquet Hall",
      "venue_name": "Grand Ballroom",
      "date": "2030-02-01",
      "start_time": "14:00",
      "end_time": "18:00",
      "status": "confirmed",
      "total_cost": 250.0,
      "created_at": "2025-11-15T10:30:00Z"
    }
  ],
  "total": 5
}
```

---

### 4️⃣ **Cancel Booking**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/bookings/{booking_id}/cancel` | ✅ | Cancel existing booking |

**Request Body:**
```json
{
  "reason": "Plans changed"
}
```

**Response (200):**
```json
{
  "success": true,
  "booking_id": 42,
  "status": "cancelled",
  "refund_amount": 187.50,
  "cancellation_fee": 62.50,
  "policy": "Cancelled > 48h: 75% refund",
  "wallet_credited": true,
  "message": "Booking cancelled successfully"
}
```

---

### 5️⃣ **Reschedule Booking**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/bookings/{booking_id}/reschedule` | ✅ | Reschedule booking date/time |

**Request Body:**
```json
{
  "new_start_time": "2030-02-15T10:00:00Z",
  "new_end_time": "2030-02-15T12:00:00Z"
}
```

**Response (200):**
```json
{
  "success": true,
  "booking_id": 42,
  "new_date": "2030-02-15",
  "new_time": "10:00 - 12:00",
  "cost_difference": 0,
  "message": "Booking rescheduled successfully"
}
```

---

## 💳 Payment Endpoints

### 1️⃣ **Initiate Payment (Razorpay)**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/payments/initiate` | ✅ | Start Razorpay payment |

**Request Body:**
```json
{
  "booking_id": 42
}
```

**Response (200):**
```json
{
  "success": true,
  "razorpay_order_id": "order_1A2b3C4d5E6f",
  "amount": 28674,
  "currency": "INR",
  "customer": {
    "name": "John Doe",
    "email": "user@example.com",
    "contact": "+91-9876543210"
  }
}
```

---

### 2️⃣ **Verify Payment**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/payments/verify` | ✅ | Verify Razorpay payment |

**Request Body:**
```json
{
  "razorpay_order_id": "order_1A2b3C4d5E6f",
  "razorpay_payment_id": "pay_1A2b3C4d5E6f",
  "razorpay_signature": "9ef4dffbfd84f1318f6739..."
}
```

**Response (200):**
```json
{
  "success": true,
  "booking_id": 42,
  "status": "confirmed",
  "message": "Payment verified successfully"
}
```

---

## ⭐ Reviews & Ratings

### 1️⃣ **Leave Review**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/reviews` | ✅ | Submit review for hall |

**Request Body:**
```json
{
  "booking_id": 42,
  "rating": 5,
  "title": "Excellent venue!",
  "comment": "Great ambiance and professional staff"
}
```

**Response (201):**
```json
{
  "success": true,
  "review_id": 100,
  "message": "Review submitted successfully"
}
```

---

### 2️⃣ **Get Reviews for Hall**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `GET` | `/reviews/room/{room_id}` | ❌ | Get hall reviews |

**Response (200):**
```json
{
  "success": true,
  "room_id": 10,
  "average_rating": 4.8,
  "total_reviews": 45,
  "reviews": [
    {
      "id": 100,
      "customer": "John Doe",
      "rating": 5,
      "title": "Excellent venue!",
      "comment": "Great ambiance and professional staff",
      "date": "2025-11-15"
    }
  ]
}
```

---

## 👤 User Profile

### 1️⃣ **Get My Profile**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `GET` | `/users/me` | ✅ | Get current user profile |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 42,
    "email": "user@example.com",
    "full_name": "John Doe",
    "phone": "+91-9876543210",
    "role": "customer",
    "address": "123 Main St, City",
    "profile_picture": "https://...",
    "created_at": "2025-10-15T08:30:00Z"
  }
}
```

---

### 2️⃣ **Update Profile**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `PUT` | `/users/me` | ✅ | Update user profile |

**Request Body:**
```json
{
  "full_name": "John Doe Updated",
  "phone": "+91-9999999999",
  "address": "456 Oak Ave, City"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Profile updated successfully"
}
```

---

## 💰 Wallet Management

### 1️⃣ **Get Wallet Balance**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `GET` | `/wallet` | ✅ | View wallet balance & history |

**Response (200):**
```json
{
  "success": true,
  "wallet": {
    "balance": 187.50,
    "total_credits": 1250.0,
    "total_spent": 1062.50,
    "transactions": [
      {
        "id": 1,
        "type": "REFUND",
        "amount": 187.50,
        "description": "Booking #42 cancelled",
        "date": "2025-11-15T14:30:00Z"
      }
    ]
  }
}
```

---

## 📊 Admin Reports

### 1️⃣ **Get Booking Reports**

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `GET` | `/reports/bookings` | ✅ (Admin) | Generate booking analytics |

**Query Parameters:**
- `start_date=2025-11-01`
- `end_date=2025-11-30`
- `venue_id=1` (optional)

**Response (200):**
```json
{
  "success": true,
  "report": {
    "total_bookings": 250,
    "confirmed": 230,
    "cancelled": 20,
    "total_revenue": 12500.0,
    "average_booking": 50.0,
    "occupancy_rate": 85.5
  }
}
```

---

## ❌ Error Handling

| Status | Error | Solution |
|--------|-------|----------|
| `400` | Bad Request | Validate input format |
| `401` | Unauthorized | Login required, check token |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | Resource doesn't exist |
| `409` | Conflict | Room already booked |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Contact support |

**Error Response Format:**
```json
{
  "success": false,
  "error": {
    "code": "invalid_input",
    "message": "Validation failed"
  }
}
```

---

## 🔑 JWT Token Lifecycle

| Token | Validity | Usage |
|-------|----------|-------|
| **Access** | 30 minutes | API requests in header |
| **Refresh** | 7 days | Renew access token |
| **Revoked** | — | Invalidated on logout |

**Authorization Header:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📝 Important Notes

- All timestamps use **UTC format** (ISO 8601)
- Pagination: Default `limit=10`, max `limit=100`
- All monetary values in **INR** (₹)
- Rate limit: **100 requests per minute** per IP
- Response format: Always includes `success: true/false`
- All endpoints require `Content-Type: application/json`

---

**End of API Documentation**

**Last Updated:** November 15, 2025  
**Status:** Production Ready ✅
