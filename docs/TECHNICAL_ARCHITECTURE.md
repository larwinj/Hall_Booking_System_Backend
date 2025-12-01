# 🎨 Hall Booking System - Technical Architecture Deep Dive

## Visual System Diagrams & Implementation Flows

---

## 1. Complete Request/Response Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT REQUEST                             │
│                   (Browser, Mobile, or API Client)                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
         ┌───────────────────────────────────────┐
         │   Request Validation & Parsing        │
         │  • Parse JSON body                    │
         │  • Validate content-type              │
         │  • Check request size                 │
         └────────────────┬──────────────────────┘
                          │
                          ▼
         ┌───────────────────────────────────────┐
         │    Middleware Stack (Sequential)      │
         │                                       │
         │  1. TrustedHosts Middleware           │
         │     ↓ Validate Host header            │
         │                                       │
         │  2. CORS Middleware                   │
         │     ↓ Check origin & headers          │
         │                                       │
         │  3. Rate Limiting Middleware          │
         │     ↓ Check request quota             │
         │                                       │
         │  4. JSON Logging Middleware           │
         │     ↓ Start request logging           │
         │                                       │
         │  5. Router Matching                   │
         │     ↓ Find appropriate handler        │
         └────────────────┬──────────────────────┘
                          │
                          ▼
         ┌───────────────────────────────────────┐
         │  Authentication & Authorization       │
         │  (if token required)                  │
         │                                       │
         │  • Extract token from header          │
         │  • Verify JWT signature               │
         │  • Decode payload                     │
         │  • Check expiration & version         │
         │  • Verify role permissions            │
         └────────────────┬──────────────────────┘
                          │
                ┌─────────┴──────────┐
                │                    │
        ✓ Token Valid        ✗ Token Invalid
                │                    │
                │                    ▼
                │            Return 401/403
                │
                ▼
         ┌───────────────────────────────────────┐
         │    Route Handler (Business Logic)     │
         │                                       │
         │  1. Validate input parameters         │
         │  2. Database queries (async)          │
         │  3. Business logic execution          │
         │  4. Response building                 │
         └────────────────┬──────────────────────┘
                          │
         ┌────────────────┴─────────────────┐
         │                                  │
    Operation             Business Rule    Database
    Success               Violated         Error
         │                    │                │
         ▼                    ▼                ▼
      Continue         Return Error          Retry
                       (4xx/5xx)         or Fail
         │                    │                │
         └────────────────┬───┴────────────┬──┘
                          │
                          ▼
         ┌───────────────────────────────────────┐
         │    Response Formatting                │
         │  • Serialize objects to JSON          │
         │  • Add response headers               │
         │  • Set status code                    │
         └────────────────┬──────────────────────┘
                          │
                          ▼
         ┌───────────────────────────────────────┐
         │    Logging & Monitoring               │
         │  • Record request duration            │
         │  • Log response size                  │
         │  • Track metrics                      │
         │  • Store in logs/metrics DB           │
         └────────────────┬──────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  RETURN RESPONSE TO CLIENT              │
│            (with appropriate status & data)            │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Booking Creation - Complete Flow with All Services

```
START: Create Booking Request
  ├─ POST /bookings
  ├─ Authorization: Bearer token
  └─ Body: {room_id, start_time, end_time, addons}
            │
            ▼
    ┌──────────────────────────┐
    │ Step 1: Validate Input   │
    │                          │
    │ • Room exists? ✓         │
    │ • Times valid? ✓         │
    │ • User authenticated? ✓  │
    │ • Addons exist? ✓        │
    └────────┬─────────────────┘
             │
    ✓ All Valid
             │
             ▼
    ┌──────────────────────────────────────┐
    │ Step 2: Check Availability           │
    │                                      │
    │ Query: SELECT * FROM bookings WHERE  │
    │   room_id = 5 AND                    │
    │   status != 'cancelled' AND          │
    │   start_time < req.end_time AND      │
    │   end_time > req.start_time          │
    │                                      │
    │ If conflicts found:                  │
    │   → Return 409 Conflict              │
    └────────┬─────────────────────────────┘
             │
    ✓ No Conflicts
             │
             ▼
    ┌──────────────────────────────────────┐
    │ Step 3: Calculate Total Cost         │
    │                                      │
    │ room_rate = 50.0 /hour               │
    │ duration_hours = 2.5                 │
    │ base_cost = 50 * 2.5 = 125.0         │
    │                                      │
    │ For each addon:                      │
    │  addon_1: price=50, qty=2            │
    │  subtotal_1 = 50 * 2 = 100.0         │
    │                                      │
    │  addon_2: price=25, qty=1            │
    │  subtotal_2 = 25 * 1 = 25.0          │
    │                                      │
    │ addons_total = 100 + 25 = 125.0      │
    │                                      │
    │ TOTAL = 125.0 + 125.0 = 250.0        │
    └────────┬─────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────────┐
    │ Step 4: Create Booking Record        │
    │                                      │
    │ INSERT INTO bookings (                │
    │   room_id=5,                         │
    │   start_time='2030-01-15T10:00Z',    │
    │   end_time='2030-01-15T12:30Z',      │
    │   status='pending',                  │
    │   total_cost=250.0,                  │
    │   created_at=now()                   │
    │ )                                    │
    │                                      │
    │ booking_id = 42 (auto-generated)     │
    └────────┬─────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────────┐
    │ Step 5: Link Customers to Booking    │
    │                                      │
    │ INSERT INTO booking_customer (       │
    │   booking_id=42,                     │
    │   user_id=10,  (from token)          │
    │   role='primary_customer'            │
    │ )                                    │
    └────────┬─────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────────┐
    │ Step 6: Create Addon Records         │
    │                                      │
    │ INSERT INTO booking_addon VALUES     │
    │ (booking_id=42, addon_id=1,          │
    │  quantity=2, subtotal=100.0),        │
    │ (booking_id=42, addon_id=2,          │
    │  quantity=1, subtotal=25.0)          │
    │                                      │
    │ Audit Trail Created ✓                │
    └────────┬─────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────────┐
    │ Step 7: Generate PDF                 │
    │                                      │
    │ • Create professional booking doc    │
    │ • Include confirmation details       │
    │ • Add cost breakdown                 │
    │ • Upload to storage (Vercel Blob)    │
    │ • Get download URL                   │
    └────────┬─────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────────┐
    │ Step 8: Send Email Notification      │
    │                                      │
    │ • Render email template              │
    │ • Include booking details            │
    │ • Attach PDF                         │
    │ • Send via SMTP                      │
    │ • Log email sent                     │
    └────────┬─────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────────┐
    │ Step 9: Create gRPC Meeting          │
    │                                      │
    │ • Call gRPC meeting service          │
    │ • Create meeting session             │
    │ • Generate access credentials       │
    │ • Link to booking                    │
    └────────┬─────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────────┐
    │ Step 10: Build Response              │
    │                                      │
    │ {                                    │
    │   "booking_id": 42,                  │
    │   "room_id": 5,                      │
    │   "start_time": "2030-01-15T10:00Z", │
    │   "end_time": "2030-01-15T12:30Z",   │
    │   "status": "pending",               │
    │   "total_cost": 250.0,               │
    │   "addons": [...],                   │
    │   "pdf_url": "https://...",          │
    │   "meeting_access": {...},           │
    │   "created_at": "2025-11-12T..."     │
    │ }                                    │
    └────────┬─────────────────────────────┘
             │
             ▼
    RETURN: 201 Created ✓
    └─ With full booking details
       & confirmation PDF
```

---

## 3. Cancellation & Refund Flow

```
START: User Cancels Booking
  ├─ POST /bookings/42/cancel
  ├─ Body: {reason: "Change of plans"}
  └─ Authorization: Bearer token
            │
            ▼
    ┌────────────────────────────┐
    │ Verify Booking Exists      │
    │ & User Authorization       │
    │                            │
    │ SELECT * FROM bookings     │
    │ WHERE id = 42              │
    │ Status: confirmed? ✓       │
    │ Owner match? ✓             │
    └────────┬───────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 1: Calculate Refund Amount        │
    │                                        │
    │ cancellation_time = now() (UTC)        │
    │ booking.start_time = 2030-01-15 10:00 │
    │ time_until = 95 hours (> 48h)          │
    │                                        │
    │ Policy Applied: > 48 hours             │
    │ • Refund %: 75%                        │
    │ • Cancellation Fee %: 25%              │
    │                                        │
    │ original_amount = 250.0                │
    │ refund_amount = 250.0 * 0.75 = 187.50 │
    │ cancellation_fee = 250.0 * 0.25 = 62.50│
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 2: Get/Create User Wallet         │
    │                                        │
    │ SELECT * FROM wallet                   │
    │ WHERE user_id = 10                     │
    │                                        │
    │ If not exists:                         │
    │   INSERT INTO wallet (                 │
    │     user_id=10, balance=0              │
    │   )                                    │
    │                                        │
    │ Current balance: 0.0                   │
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 3: Create Refund Transaction      │
    │                                        │
    │ INSERT INTO wallet_transaction (       │
    │   wallet_id=1,                         │
    │   type='REFUND',                       │
    │   amount=187.50,                       │
    │   status='COMPLETED',                  │
    │   reference_id=42,  (booking_id)       │
    │   description='Booking #42 cancelled'  │
    │ )                                      │
    │                                        │
    │ Transaction ID: 1001                   │
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 4: Update Wallet Balance          │
    │                                        │
    │ new_balance = 0.0 + 187.50 = 187.50    │
    │                                        │
    │ UPDATE wallet SET                      │
    │   balance = 187.50                     │
    │ WHERE id = 1                           │
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 5: Update Booking Status          │
    │                                        │
    │ UPDATE bookings SET                    │
    │   status='cancelled',                  │
    │   cancellation_reason='Change of plans'│
    │ WHERE id = 42                          │
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 6: Archive Booking Addons         │
    │ (Restore original prices for audit)    │
    │                                        │
    │ These are already in DB, just linked   │
    │ No action needed                       │
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 7: Send Cancellation Email        │
    │                                        │
    │ • Template: cancellation_notice.html   │
    │ • Context:                             │
    │   - booking_id                         │
    │   - original_amount                    │
    │   - cancellation_fee                   │
    │   - refund_amount                      │
    │   - policy_description                 │
    │   - refund_method                      │
    │ • Send to user email                   │
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 8: Notify Venue Moderator         │
    │                                        │
    │ • Send cancellation alert to moderator │
    │ • Include booking & refund details     │
    │ • Room now available for booking       │
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 9: Update Availability Cache      │
    │                                        │
    │ • Invalidate room availability cache   │
    │ • Next availability check will requery │
    │ • Real-time availability restored      │
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 10: Build Response                │
    │                                        │
    │ {                                      │
    │   "booking_id": 42,                    │
    │   "status": "cancelled",               │
    │   "refund_amount": 187.50,             │
    │   "cancellation_fee": 62.50,           │
    │   "policy": "Cancelled > 48h: 75%",    │
    │   "wallet_credited": true,             │
    │   "cancelled_at": "2025-11-12T...",    │
    │   "estimated_refund_time": "3-5 days" │
    │ }                                      │
    └────────┬───────────────────────────────┘
             │
             ▼
    RETURN: 200 OK ✓
```

---

## 4. Search Algorithm - Intelligent Fallback

```
START: Search Request
  ├─ GET /search/rooms
  ├─ ?city=Metropolis&capacity=40&amenities=wifi&amenities=projector
  └─ ?date=2030-02-01
            │
            ▼
    ┌────────────────────────────────────────┐
    │ Step 1: Parse Search Criteria           │
    │                                        │
    │ city = "Metropolis"                    │
    │ date = "2030-02-01"                    │
    │ min_capacity = 40                      │
    │ amenities = ["wifi", "projector"]      │
    │ (these must ALL be present - AND logic)│
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 2: FIRST ATTEMPT - Exact Match    │
    │                                        │
    │ SELECT rooms WHERE                     │
    │   city = 'Metropolis' AND              │
    │   capacity >= 40 AND                   │
    │   amenities @> ['wifi', 'projector']   │
    │                                        │
    │ Results: 2 rooms found                 │
    │                                        │
    │ ✓ > 5 results?                         │
    │ YES → Return results                   │
    │                                        │
    │ (if NO, continue to next step)         │
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 3: SECOND ATTEMPT - Relax Filters │
    │ (if < 5 results in previous)           │
    │                                        │
    │ Change AND to OR for amenities:        │
    │                                        │
    │ SELECT rooms WHERE                     │
    │   city = 'Metropolis' AND              │
    │   capacity >= 40 AND                   │
    │   (amenities contains 'wifi' OR        │
    │    amenities contains 'projector')     │
    │                                        │
    │ Results: 8 rooms found                 │
    │                                        │
    │ ✓ > 5 results?                         │
    │ YES → Return results                   │
    │                                        │
    │ (if NO, continue to next step)         │
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 4: THIRD ATTEMPT - Remove Capacity│
    │ (if still < 5 results)                 │
    │                                        │
    │ SELECT rooms WHERE                     │
    │   city = 'Metropolis' AND              │
    │   (amenities contains 'wifi' OR        │
    │    amenities contains 'projector')     │
    │   (ignore capacity now)                │
    │                                        │
    │ Results: 12 rooms found                │
    │                                        │
    │ ✓ Have results?                        │
    │ YES → Return results (sorted by rating)│
    │                                        │
    │ (if NO, continue to next step)         │
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 5: FOURTH ATTEMPT - Expand City   │
    │ (if still < 5 results)                 │
    │                                        │
    │ SELECT rooms WHERE                     │
    │   region = 'Central' AND  (broader)    │
    │   capacity >= 30  (relaxed)            │
    │                                        │
    │ Results: 20 rooms found                │
    │                                        │
    │ Return with note: "Showing nearby"     │
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 6: For Each Room - Check Schedule │
    │                                        │
    │ For room in results:                   │
    │   SELECT bookings WHERE                │
    │   room_id = room.id AND                │
    │   status = 'confirmed' AND             │
    │   start < date.end AND                 │
    │   end > date.start                     │
    │                                        │
    │   Calculate available_slots from       │
    │   date_start to date_end minus          │
    │   confirmed booking times              │
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 7: Sort & Rank Results            │
    │                                        │
    │ Priority Ranking:                      │
    │  1. Exact match (all filters met)      │
    │  2. Rating (highest first)             │
    │  3. Price (lowest first)               │
    │  4. Availability slots (most slots)    │
    │  5. Recently viewed (favorites)        │
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Step 8: Build Response                 │
    │                                        │
    │ {                                      │
    │   "query": {                           │
    │     "criteria": {...},                 │
    │     "search_attempts": 2,              │
    │     "expansion_applied": false         │
    │   },                                   │
    │   "results": [                         │
    │     {                                  │
    │       "room_id": 5,                    │
    │       "name": "Grand Ballroom",        │
    │       "capacity": 100,                 │
    │       "rate": 50.0,                    │
    │       "available_slots": [             │
    │         {"start": "09:00", "end": ...} │
    │       ],                               │
    │       "amenities": [...],              │
    │       "rating": 4.8                    │
    │     },                                 │
    │     ...                                │
    │   ],                                   │
    │   "count": 12                          │
    │ }                                      │
    └────────┬───────────────────────────────┘
             │
             ▼
    RETURN: 200 OK with results ✓
```

---

## 5. Authentication Token Flow

```
┌─────────────────────────────────────────────────────┐
│                SIGNUP / LOGIN                       │
│                                                     │
│  1. User provides: email + password                 │
│     (HTTPS only - no unencrypted transmission)      │
│                                                     │
│  2. Validate email format (RFC 5321)                │
│     ✓ Format OK? Continue                           │
│     ✗ Invalid? Return 400                           │
│                                                     │
│  3. Hash password with bcrypt:                      │
│     password_hash = bcrypt.hash(password, 12)       │
│     (12 rounds = ~100ms processing time)            │
│                                                     │
│  4. Store in database:                              │
│     CREATE USER                                     │
│     INSERT INTO users (email, hashed_password)      │
│                                                     │
│  5. Generate tokens with JWT:                       │
│                                                     │
│     Access Token:                                   │
│     ├─ sub: user_id (42)                            │
│     ├─ iat: issued_at (1731398000)                  │
│     ├─ exp: 1731401600 (30 mins later)              │
│     ├─ type: "access"                               │
│     ├─ ver: 1 (token_version)                       │
│     └─ Signed with: JWT_SECRET (HS256)              │
│                                                     │
│     Refresh Token:                                  │
│     ├─ sub: user_id (42)                            │
│     ├─ iat: issued_at (1731398000)                  │
│     ├─ exp: 1732089600 (7 days later)               │
│     ├─ type: "refresh"                              │
│     ├─ ver: 1 (token_version)                       │
│     └─ Signed with: JWT_REFRESH_SECRET (HS256)      │
│                                                     │
│  6. Return to client:                               │
│     {                                               │
│       "access_token": "eyJ0eX...",                   │
│       "refresh_token": "eyJ0eX...",                  │
│       "token_type": "bearer",                       │
│       "expires_in": 1800  (30 mins in seconds)      │
│     }                                               │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│            SUBSEQUENT API REQUESTS                  │
│                                                     │
│  1. Client includes token in header:                │
│     Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc... │
│                                                     │
│  2. Server extracts token from header               │
│                                                     │
│  3. Verify JWT signature:                           │
│     header.payload = decode(token, JWT_SECRET)      │
│     ✓ Signature valid? Continue                     │
│     ✗ Invalid sig? Return 401 Unauthorized          │
│                                                     │
│  4. Check token expiration:                         │
│     if now > token.exp:                             │
│       Return 401 Token Expired                      │
│                                                     │
│  5. Extract user info from token:                   │
│     user_id = token.sub                             │
│     token_version = token.ver                       │
│                                                     │
│  6. Verify token version matches user record:       │
│     SELECT user.token_version WHERE id = user_id    │
│     if token.ver != user.token_version:             │
│       Return 401 Token Invalidated                  │
│       (User logged out, old version)                │
│                                                     │
│  7. Attach user context to request:                 │
│     request.user_id = 42                            │
│     request.token_version = 1                       │
│                                                     │
│  8. Process request with authenticated context      │
│                                                     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│           TOKEN REFRESH (Before Expiry)             │
│                                                     │
│  1. Client detects access token near expiry         │
│                                                     │
│  2. Send refresh token:                             │
│     POST /auth/refresh                              │
│     Authorization: Bearer {refresh_token}           │
│                                                     │
│  3. Validate refresh token (same as access token):  │
│     ✓ Signature valid?                              │
│     ✓ Not expired?                                  │
│     ✓ Version matches?                              │
│                                                     │
│  4. Generate NEW access token (same user_id):       │
│     new_access_token = create_token(               │
│       subject=user_id,                              │
│       expires_delta=30_mins,                        │
│       token_type="access"                           │
│     )                                               │
│                                                     │
│  5. Return new access token:                        │
│     {                                               │
│       "access_token": "eyJ0eX... (new)",             │
│       "token_type": "bearer"                        │
│     }                                               │
│                                                     │
│  6. Client stores new token, discards old one       │
│                                                     │
│  7. Session continues seamlessly                    │
│                                                     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│               LOGOUT                                │
│                                                     │
│  1. Client requests:                                │
│     POST /auth/logout                               │
│     Authorization: Bearer {access_token}            │
│                                                     │
│  2. Server verifies token (standard validation)     │
│                                                     │
│  3. Increment user's token_version:                 │
│     UPDATE users SET                                │
│     token_version = token_version + 1               │
│     WHERE id = user_id                              │
│     (e.g., 1 → 2)                                   │
│                                                     │
│  4. All old tokens with version 1 now invalid:      │
│     On next request with old token:                 │
│     token.ver (1) != user.token_version (2)         │
│     → Return 401 Unauthorized                       │
│                                                     │
│  5. No database blacklist needed                    │
│     (Version check is instant)                      │
│                                                     │
│  6. Return success:                                 │
│     {                                               │
│       "success": true,                              │
│       "message": "Logged out successfully"          │
│     }                                               │
│                                                     │
│  7. Client discards all tokens locally              │
│                                                     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│         TOKEN SECURITY PRINCIPLES                   │
│                                                     │
│  Stored Securely:                                   │
│    ✓ Client: httpOnly cookie (XSS safe)             │
│    ✓ Or: localStorage (with care)                   │
│    ✓ Server: JWT_SECRET in env (never in code)      │
│                                                     │
│  Transmitted Securely:                              │
│    ✓ HTTPS/TLS encryption only                      │
│    ✓ Never in URLs or query params                  │
│    ✓ Always in Authorization header                 │
│                                                     │
│  Validated Strictly:                                │
│    ✓ Signature verification (HS256)                 │
│    ✓ Expiration checking                            │
│    ✓ Version matching (logout safety)               │
│    ✓ Token type verification (access vs refresh)    │
│                                                     │
│  Rotated Periodically:                              │
│    ✓ Access token: 30 minutes (short-lived)         │
│    ✓ Refresh token: 7 days (long-lived)             │
│    ✓ Force logout: Increment version                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 6. Database Connection Lifecycle

```
Application Startup
        │
        ▼
┌──────────────────────────────────┐
│ FastAPI Lifespan Event           │
│ (async context manager)          │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Initialize PostgreSQL Connection │
│                                  │
│ 1. Load POSTGRES_URL from env    │
│    postgresql+asyncpg://...      │
│                                  │
│ 2. Create async engine:          │
│    engine = create_async_engine( │
│      url=POSTGRES_URL,           │
│      echo=False,  # SQL logging  │
│      pool_size=20,               │
│      max_overflow=10             │
│    )                             │
│                                  │
│ 3. Create connection pool        │
│    (20 active + 10 overflow)     │
│                                  │
│ 4. Initialize SQLAlchemy tables: │
│    metadata.create_all(engine)   │
│    (creates missing tables)      │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Initialize MongoDB Connection    │
│                                  │
│ 1. Load MONGO_URI from env       │
│    mongodb://mongo:27017         │
│                                  │
│ 2. Create Motor client:          │
│    client = AsyncIOMotorClient(  │
│      MONGO_URI                   │
│    )                             │
│                                  │
│ 3. Verify connection:            │
│    await client.admin.          │
│      command('ping')             │
│                                  │
│ 4. Select database:              │
│    db = client['hall_booking_..']│
│                                  │
│ 5. Store in app.state:           │
│    app.state.mongo = client      │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Application Ready                │
│ (Accepts requests)               │
└────────┬─────────────────────────┘
         │
         ▼
    Request Handling Loop
    (concurrent requests)
         │
    ┌────┴────┬─────────────┐
    │          │             │
Request_1   Request_2   Request_N
    │          │             │
    ▼          ▼             ▼
    
Get connection from pool
    ↓
Execute query (async/await)
    ↓
Return connection to pool
    ↓
Return response
    
         │
         ▼
┌──────────────────────────────────┐
│ Application Shutdown             │
│ (graceful shutdown)              │
│                                  │
│ 1. Stop accepting new requests   │
│                                  │
│ 2. Wait for in-flight requests   │
│    (up to timeout)               │
│                                  │
│ 3. Close PostgreSQL connections: │
│    await engine.dispose()        │
│                                  │
│ 4. Close MongoDB connections:    │
│    client.close()                │
│                                  │
│ 5. Release all resources         │
│                                  │
│ 6. Exit cleanly                  │
└──────────────────────────────────┘
```

---

## 7. Async Request Processing Model

```
FastAPI Async Processing (Non-blocking, Concurrent)

┌─────────────────────────────────────────────────────┐
│           INCOMING REQUESTS STREAM                  │
│                                                     │
│ Request_1 ──┐                                       │
│ Request_2 ──┼─► Uvicorn Event Loop                  │
│ Request_3 ──┼─► (uses asyncio)                      │
│ Request_4 ──┤                                       │
│ Request_5 ──┤                                       │
│             │                                       │
└─────────────┼─────────────────────────────────────┘
              │
              ▼
    ┌──────────────────────────────┐
    │    Async Event Loop          │
    │   (Task Scheduler)           │
    │                              │
    │ while True:                  │
    │   for task in ready_tasks:   │
    │     execute(task)            │
    │     if blocked: sleep()      │
    │   switch_to_next()           │
    └──────────────────────────────┘
    
        │         │         │         │
        │         │         │         └──► Request_5 starts
        │         │         │              ↓
        │         │         └──► Request_4 → Query DB (awaits)
        │         │              (blocked, can switch)
        │         └──► Request_3 → Network call (awaits)
        │              (blocked, can switch)
        └──► Request_1 → Compute (CPU bound)
             → Return response (complete)
        
Key Benefit: While Request_1 is computing (quick operation),
Event loop can switch to other requests that are waiting for I/O.

Timeline Comparison:
┌──────────────────────────────────────────────┐
│ SYNC (Blocking): Process one at a time       │
│                                              │
│ Req_1: ████████ (1 sec)                      │
│ Req_2:         ████████ (1 sec)              │
│ Req_3:                 ████████ (1 sec)      │
│ Total: ══════════════════════════            │
│        3 seconds (serial)                    │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ ASYNC (Concurrent): Process multiple         │
│                                              │
│ Req_1: ████ (waiting for DB)                 │
│ Req_2:    ████ (waiting for network)         │
│ Req_3:       ████ (waiting for DB)           │
│ Total: ═════════ (1.5 seconds - concurrent)  │
│        75% faster!                           │
└──────────────────────────────────────────────┘
```

---

## 8. Analytics Report Generation & Caching

```
First Request for Report (Cache Miss)

User: GET /reports/bookings?start=2025-01-01&end=2025-11-12
        │
        ▼
    ┌─────────────────────────────────┐
    │ Step 1: Check MongoDB Cache     │
    │                                 │
    │ SELECT * FROM reports_cache     │
    │ WHERE query_hash = hash(params) │
    │ AND expires_at > now()          │
    │                                 │
    │ Result: NO MATCH (cache miss)   │
    └────────┬────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────┐
    │ Step 2: Query PostgreSQL        │
    │                                 │
    │ SELECT COUNT(*), SUM(total_cost)│
    │   GROUP BY status               │
    │ FROM bookings                   │
    │ WHERE created_at BETWEEN ...    │
    │                                 │
    │ (Complex multi-query aggregation)
    │ Takes: ~500ms                   │
    │                                 │
    │ Results:                        │
    │ • total_bookings: 250           │
    │ • confirmed: 230                │
    │ • cancelled: 20                 │
    │ • total_revenue: 12500.0        │
    └────────┬────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────┐
    │ Step 3: Store in MongoDB Cache  │
    │                                 │
    │ INSERT INTO reports_cache {     │
    │   query_hash: "abc123",         │
    │   query_params: {...},          │
    │   results: {...},               │
    │   created_at: now(),            │
    │   expires_at: now() + 1_hour    │
    │ }                               │
    │                                 │
    │ TTL Index: automatically delete  │
    │ after expires_at                │
    └────────┬────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────┐
    │ Step 4: Return Response         │
    │                                 │
    │ {                               │
    │   "report": {...},              │
    │   "from_cache": false,          │
    │   "generated_at": now()         │
    │ }                               │
    │                                 │
    │ Total Response Time: 500ms      │
    └─────────────────────────────────┘

────────────────────────────────────────

Subsequent Requests (Cache Hit - Within 1 Hour)

User: GET /reports/bookings?start=2025-01-01&end=2025-11-12
        │
        ▼
    ┌─────────────────────────────────┐
    │ Step 1: Check MongoDB Cache     │
    │                                 │
    │ SELECT * FROM reports_cache     │
    │ WHERE query_hash = hash(params) │
    │ AND expires_at > now()          │
    │                                 │
    │ Result: MATCH FOUND!            │
    │ (cache hit)                     │
    └────────┬────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────┐
    │ Step 2: Return Cached Results   │
    │                                 │
    │ {                               │
    │   "report": {...},  (cached)    │
    │   "from_cache": true,           │
    │   "generated_at": "2 mins ago"  │
    │   "expires_in": "58 mins"       │
    │ }                               │
    │                                 │
    │ Total Response Time: 10ms       │
    │ (50x faster!)                   │
    └─────────────────────────────────┘

Cache Invalidation Scenarios:
├─ Expiration: TTL reached (1 hour)
├─ New Booking: Invalidate affected date range
├─ Cancellation: Invalidate affected venue
├─ Manual Refresh: Admin triggers cache clear
└─ Scheduled: Nightly cache refresh
```

---

## 9. Middleware Execution Order

```
Request arrives at FastAPI application
    │
    ▼
┌────────────────────────────────────────┐
│ 1. Trusted Hosts Middleware            │
│                                        │
│ Check: request.headers['Host']         │
│ Validate against whitelist             │
│                                        │
│ ✓ Valid: Continue                      │
│ ✗ Invalid: Return 400 Bad Request      │
│   (prevents Host header injection)     │
└────────┬───────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ 2. CORS Middleware                     │
│                                        │
│ Check: request.headers['Origin']       │
│ Validate against CORS_ORIGINS          │
│                                        │
│ ✓ Valid: Add CORS headers              │
│   Access-Control-Allow-Origin: *       │
│ ✗ Invalid: Return 403 Forbidden        │
│   (prevents cross-origin abuse)        │
└────────┬───────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ 3. Rate Limiting Middleware            │
│                                        │
│ Check: request.client.host IP          │
│ Lookup: current request count          │
│                                        │
│ Redis/Memory counter:                  │
│ ip:10.0.0.1 = 45 requests/min          │
│ limit = 50 requests/min                │
│                                        │
│ ✓ Within limit: Continue               │
│ ✗ Exceeded: Return 429 Too Many Req    │
│   (prevents DOS attacks)               │
└────────┬───────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ 4. JSON Logging Middleware             │
│                                        │
│ Start: record start_time               │
│ Log: method, path, headers             │
│                                        │
│ Generate: request_id (UUID)            │
│ Attach: request_id to request          │
│                                        │
│ Will log response after completion     │
└────────┬───────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ 5. Router Matching                     │
│                                        │
│ Match: request path to route           │
│ Example: POST /bookings                │
│                                        │
│ ✓ Match found: Continue to handler     │
│ ✗ No match: Return 404 Not Found       │
└────────┬───────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ 6. Authentication (Dependency)         │
│                                        │
│ Extract: token from Authorization hdr │
│ Verify: JWT signature                  │
│ Check: expiration & version            │
│                                        │
│ ✓ Valid: Attach user to request        │
│ ✗ Invalid: Return 401 Unauthorized     │
└────────┬───────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ 7. Authorization (Route Handler)       │
│                                        │
│ Check: user.role permissions           │
│ Example: POST /bookings (customer)     │
│                                        │
│ ✓ Role allowed: Continue               │
│ ✗ Role denied: Return 403 Forbidden    │
└────────┬───────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ 8. Route Handler (Business Logic)      │
│                                        │
│ Execute: core business logic           │
│ Database: read/write operations        │
│ External: API calls, emails            │
│                                        │
│ ✓ Success: Build response              │
│ ✗ Error: Raise exception               │
└────────┬───────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ 9. Response Serialization              │
│                                        │
│ Convert: Python objects to JSON        │
│ Add: Response headers                  │
│ Set: Status code                       │
└────────┬───────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ 10. Global Exception Handler           │
│                                        │
│ If exception raised anywhere:          │
│                                        │
│ Catch: All unhandled exceptions        │
│ Log: Full stack trace                  │
│ Return: 500 Internal Server Error      │
│ Message: "Internal server error"       │
│                                        │
│ Prevents info disclosure               │
└────────┬───────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ 11. JSON Logging (Response)            │
│                                        │
│ Record: end_time                       │
│ Calculate: duration_ms                 │
│ Log: status_code, response_size        │
│                                        │
│ JSON Entry (logs/app.jsonl):           │
│ {                                      │
│   "timestamp": "2025-11-12T10:30Z",    │
│   "request_id": "550e8400-e29b-41d4",  │
│   "method": "POST",                    │
│   "endpoint": "/bookings",             │
│   "status": 201,                       │
│   "duration_ms": 234,                  │
│   "user_id": 42                        │
│ }                                      │
└────────┬───────────────────────────────┘
         │
         ▼
    Response returned to client
```

---

## 10. Complete System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────┐ │
│  │   Web      │  │   Mobile   │  │  Desktop   │  │  Third-party │ │
│  │  Browser   │  │   App      │  │   App      │  │  API Client  │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────────┘ │
└────────────────────────┬──────────────────────────────────────────┘
                         │ HTTPS/TLS
                         ▼
         ┌───────────────────────────────────┐
         │   Load Balancer / Reverse Proxy   │
         │   (NGINX / HAProxy)               │
         │                                   │
         │   • SSL/TLS Termination           │
         │   • Request Routing               │
         │   • Session Stickiness            │
         └───────┬───────────────────────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
      ▼                     ▼
┌─────────────────┐  ┌─────────────────┐
│ FastAPI Server  │  │ FastAPI Server  │
│  Instance 1     │  │  Instance 2     │
└────────┬────────┘  └────────┬────────┘
         │                    │
         └──────────┬─────────┘
                    │
         ┌──────────┴──────────┬────────────┐
         │                     │            │
         ▼                     ▼            ▼
    ┌─────────────────┐  ┌──────────────┐ ┌──────────────┐
    │  PostgreSQL     │  │  MongoDB     │ │  gRPC Service│
    │  (Primary DB)   │  │  (CMS/Cache) │ │  (Meetings)  │
    │                 │  │              │ │              │
    │ • Users         │  │ • Pages      │ │ • Meeting    │
    │ • Bookings      │  │ • Config     │ │   Sessions   │
    │ • Rooms         │  │ • Cache      │ │ • Recordings │
    │ • Wallets       │  │              │ │              │
    │ • Transactions  │  │              │ │              │
    │ • Reviews       │  │              │ │              │
    │ • Reports       │  │              │ │              │
    │                 │  │              │ │              │
    │ Replicas:       │  │ Replica Set: │ │              │
    │ • Read-only 1   │  │ • Primary    │ │              │
    │ • Read-only 2   │  │ • Secondary  │ │              │
    │                 │  │ • Arbiter    │ │              │
    └────────┬────────┘  └──────┬───────┘ └──────────────┘
             │                  │
             │  Replication     │
             │  Master→Slave    │
             │                  │
    ┌────────┴──────────────────┴─────────┐
    │                                      │
    │   Backup & Storage Services         │
    │                                      │
    │   • Daily automated backups         │
    │   • Vercel Blob Storage             │
    │   • S3-compatible storage           │
    │   • 30-day retention                │
    └──────────────────────────────────────┘

External Services:
    │
    ├─► SMTP Server (Email)
    │   └─ Gmail, SendGrid, etc.
    │
    ├─► Payment Gateway (Optional)
    │   └─ Stripe, Razorpay
    │
    └─► Monitoring & Logging
        ├─ Prometheus (metrics)
        ├─ Grafana (dashboards)
        └─ ELK Stack (centralized logs)
```

---

**This technical deep dive provides visual representations of all major system flows, making it perfect for technical presentations and architecture discussions.**

