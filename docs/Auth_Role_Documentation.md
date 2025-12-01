# 🔐 Authentication & Role-Based Access Control

**Project:** Hall Booking System Backend  
**Version:** 1.0.0  
**Last Updated:** November 15, 2025

---

## 📖 Overview

This document details the authentication mechanism and role-based access control (RBAC) implementation using **FastAPI JWT tokens** and permission-based middleware.

---

## 🔄 Authentication Flow

| Step | Action | Details |
|------|--------|---------|
| **1. Register** | User signup | Email + password registration with optional role selection |
| **2. Login** | Verify credentials | Email/password validation against hashed password |
| **3. Issue Tokens** | JWT generation | Access token (30 min) + Refresh token (7 days) |
| **4. Access Token** | Request authentication | Short-lived JWT for API requests |
| **5. Token Expired** | Refresh flow | Use refresh token to get new access token |
| **6. Logout** | Token revocation | Increment user token_version to invalidate all tokens |
| **7. Protected Routes** | Middleware check | Validate token signature, expiration, and version |

---

## 🎟️ JWT Token Structure

```json
{
  "sub": "42",                    // User ID
  "iat": 1731398000,              // Issued at (Unix timestamp)
  "exp": 1731401600,              // Expiration (30 mins from issue)
  "type": "access",               // Token type: access or refresh
  "ver": 1                        // Version (incremented on logout)
}
```

**Token Validation Checks:**
- ✅ Signature verification (HS256)
- ✅ Expiration time check
- ✅ Token version match (prevents reuse after logout)
- ✅ User still exists in database

---

## 🔓 Authentication Endpoints

| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|:----:|:----------:|
| POST | `/auth/signup` | User registration | ❌ | 5/hour |
| POST | `/auth/login` | Login & get tokens | ❌ | 10/hour |
| POST | `/auth/refresh` | Refresh access token | ✅ Refresh Token | 30/hour |
| POST | `/auth/logout` | Invalidate tokens | ✅ | 10/hour |
| POST | `/auth/forgot-password` | Request password reset | ❌ | 3/hour |
| POST | `/auth/reset-password` | Reset with OTP token | ❌ | 5/hour |

---

## 👥 User Roles & Hierarchy

```
┌─────────────────────────────────┐
│ ADMIN (Superuser)               │
│ - Full system access            │
│ - User management               │
│ - System configuration          │
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│ MODERATOR/VENDOR (Level 2)      │
│ - Manage own venues             │
│ - Room management               │
│ - Booking management (own)      │
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│ CUSTOMER (Level 3)              │
│ - Browse & search               │
│ - Create & manage bookings      │
│ - Leave reviews                 │
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│ GUEST (Level 4)                 │
│ - Read-only access              │
│ - Browse halls only             │
└─────────────────────────────────┘
```

---

## 📋 Role Permissions Matrix

| Resource | Action | Admin | Vendor | Customer | Guest |
|----------|--------|:-----:|:------:|:--------:|:-----:|
| **Venues** | Create | ✅ | ✅ | ❌ | ❌ |
| | Read | ✅ | ✅ | ✅ | ✅ |
| | Update | ✅ | Own | ❌ | ❌ |
| | Delete | ✅ | Own | ❌ | ❌ |
| **Rooms** | Create | ✅ | ✅ | ❌ | ❌ |
| | Read | ✅ | ✅ | ✅ | ✅ |
| | Update | ✅ | Own | ❌ | ❌ |
| | Delete | ✅ | ❌ | ❌ | ❌ |
| **Bookings** | Create | ✅ | ✅ | ✅ | ❌ |
| | Read | ✅ | ✅ | Own | ❌ |
| | Update | ✅ | ✅ | Own | ❌ |
| | Cancel | ✅ | ✅ | ✅ | ❌ |
| **Reviews** | Create | ❌ | ❌ | ✅ | ❌ |
| | Read | ✅ | ✅ | ✅ | ✅ |
| | Delete | ✅ | ❌ | Own | ❌ |
| **Reports** | Generate | ✅ | Own | Limited | ❌ |
| | Export | ✅ | Own | ❌ | ❌ |
| **Users** | Manage | ✅ | ❌ | Profile Only | ❌ |

---

## 🔗 Token Flow Examples

### Login & Get Tokens

```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}

Response (200):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Use Access Token

```bash
GET /bookings/my-bookings
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

Response (200): [bookings list]
```

### Refresh Expired Token

```bash
POST /auth/refresh
Authorization: Bearer {refresh_token}

Response (200):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc... (new)",
  "token_type": "bearer"
}
```

### Logout & Revoke

```bash
POST /auth/logout
Authorization: Bearer {access_token}

Response (200):
{
  "message": "Successfully logged out",
  "success": true
}
```

---

## 🛡️ Middleware & Token Validation

**Dependency Injection Pattern:**

```python
from fastapi import Depends
from app.api.deps import get_current_user

@router.get("/users/me")
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
```

**Validation Steps:**
1. Extract token from `Authorization: Bearer {token}`
2. Decode JWT signature using `JWT_SECRET`
3. Check token expiration (`exp` claim)
4. Verify token version matches user record
5. Attach user context to request

---

## 🔐 Role-Based Route Protection

**Example: Admin-only endpoint**

```python
from app.api.deps import get_current_user, role_required

@router.post("/users", dependencies=[Depends(role_required("admin"))])
async def create_user(user: UserCreate, current_user: User = Depends(get_current_user)):
    # Only admins can reach here
    return {"user_created": True}
```

**Example: Owner or Admin**

```python
@router.put("/venues/{venue_id}")
async def update_venue(
    venue_id: int, 
    data: VenueUpdate,
    current_user: User = Depends(get_current_user)
):
    # Check ownership or admin role
    if current_user.role != "admin" and venue.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"updated": True}
```

---

## ⏱️ Token Lifecycle

| Token | Lifetime | When Used | When Expired |
|-------|----------|-----------|--------------|
| **Access** | 30 minutes | Every API request | Use refresh token |
| **Refresh** | 7 days | When access expires | Re-login required |

**Token Rotation Strategy:**
- Access token is short-lived for security
- Refresh token is long-lived for convenience
- Both validated on every protected request
- Old tokens invalidated immediately on logout

---

## 🔒 Security Features

| Feature | Implementation |
|---------|-----------------|
| **Password Hashing** | bcrypt with 12 rounds (~100ms) |
| **Token Signing** | HS256 (HMAC SHA-256) |
| **Token Storage** | httpOnly cookies (XSS safe) |
| **Transmission** | HTTPS only in production |
| **Session Management** | Stateless JWT (no server sessions) |
| **Logout** | Token version increment (instant invalidation) |
| **Rate Limiting** | Per-IP request throttling |

---

## 📝 Frontend Integration Checklist

- ✅ Store tokens in httpOnly cookies or secure storage
- ✅ Attach token in `Authorization: Bearer {token}` header
- ✅ Handle 401 responses by triggering refresh flow
- ✅ Handle 403 responses (permission denied)
- ✅ Implement auto-logout on token expiration
- ✅ Clear tokens on logout
- ✅ Validate user role before showing UI elements

---

## 🚨 Error Handling

| Status | Error | Solution |
|--------|-------|----------|
| **401** | Unauthorized (invalid/missing token) | Login again |
| **401** | Token expired | Use refresh endpoint |
| **403** | Forbidden (insufficient permissions) | Access denied for this role |
| **422** | Validation error | Check request format |

---

## 🔄 Complete Login → Access → Logout Flow

```
1. User Login
   └─> POST /auth/login
       └─> Returns: access_token + refresh_token

2. Make API Requests
   ├─> GET /bookings (with access_token)
   ├─> POST /reviews (with access_token)
   └─> PUT /profile (with access_token)

3. Access Token Expires (after 30 min)
   └─> POST /auth/refresh (with refresh_token)
       └─> Returns: new access_token

4. Continue Requests
   └─> GET /reports (with new access_token)

5. User Logout
   └─> POST /auth/logout
       └─> All tokens invalidated
       └─> Must login again for new tokens
```

---

## 🎯 Best Practices

- ✅ Use HTTPS in production only
- ✅ Store JWT_SECRET as environment variable
- ✅ Use strong, random secret keys (32+ characters)
- ✅ Rotate secrets periodically
- ✅ Monitor failed login attempts
- ✅ Implement rate limiting on auth endpoints
- ✅ Validate all inputs server-side
- ✅ Never expose sensitive data in responses

---

**End of Authentication & Role Documentation**
