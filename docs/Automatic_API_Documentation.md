# 🚀 Automatically Export FastAPI's Swagger (OpenAPI)

Generate beautifully formatted API documentation directly from your FastAPI application with one command.

---

## 📋 Overview

This process **automatically exports FastAPI's OpenAPI specification** and converts it into a professional `API_Documentation.md` file, keeping it always in sync with your code.

**What you get:**
- ✅ Auto-generated from live FastAPI code
- ✅ Always up-to-date with API changes
- ✅ Professional Markdown formatting
- ✅ Organized by endpoint tags
- ✅ Complete parameter & response documentation
- ✅ Mergeable with manual notes

---

## 🔧 Step-by-Step Process

### Step 1: Ensure FastAPI Server is Running

```bash
cd backend
uvicorn app.main:app --reload
```

The OpenAPI schema is available at:
```
http://127.0.0.1:8000/openapi.json
```

### Step 2: Export OpenAPI Schema

Create a `docs` directory and export the schema:

```bash
# Create docs directory
mkdir -p docs

# Export OpenAPI JSON
curl http://127.0.0.1:8000/openapi.json -o docs/openapi.json

# Verify
ls -la docs/openapi.json
```

**Output:**
```
-rw-r--r-- docs/openapi.json  (250+ KB)
```

### Step 3: Run Documentation Generator

```bash
# Option 1: Using the provided script
python scripts/generate_api_docs.py

# Option 2: Automated (add to CI/CD)
python scripts/generate_api_docs.py && git add docs/
```

**Output:**
```
============================================================
🚀 FastAPI OpenAPI → Markdown Documentation Generator
============================================================

✓ Loaded OpenAPI schema from docs/openapi.json
⚙️  Converting OpenAPI to Markdown...
✓ Documentation saved to docs/API_Documentation.md

============================================================
✅ Documentation generated successfully!
📄 Output: docs/API_Documentation.md

📖 Next steps:
   - Open the generated Markdown file
   - Review and customize as needed
   - Add to your documentation repository
============================================================
```

### Step 4: Review Generated Documentation

```bash
# View the generated file
cat docs/API_Documentation.md

# Or open in your editor
code docs/API_Documentation.md
```

**Sample Output Structure:**
```markdown
# Hall Booking System API Documentation
**Version:** 1.0.0
**Generated:** 2025-11-15 14:30:00
**Base URL:** `/api/v1`

---

## 📋 Table of Contents

- **Authentication** (3 endpoints)
- **Users** (5 endpoints)
- **Bookings** (7 endpoints)
- **Venues** (4 endpoints)
...

---

## Authentication

### `POST` /auth/login
**User login with email and password**

🔒 **Requires Authentication**: JWT Bearer Token

**Parameters:**

- 📌 `email` (string, in *body*) — User email address
- 📌 `password` (string, in *body*) — User password

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Responses:**

- `200` — Login successful, returns access token
- `401` — Invalid credentials
- `422` — Validation error

---
```

---

## 🎯 Generated Documentation Structure

### Header Section
```markdown
# Hall Booking System API Documentation
**Version:** 1.0.0
**Generated:** 2025-11-15 14:30:00
**Base URL:** `/api/v1`
```

### Table of Contents
```markdown
## 📋 Table of Contents

- **Authentication** (3 endpoints)
- **Bookings** (7 endpoints)
- **Venues** (4 endpoints)
```

### Endpoints (Organized by Tags)

Each endpoint includes:
- ✅ HTTP Method + Path
- ✅ Summary & Description
- ✅ Authentication requirements
- ✅ Request parameters
- ✅ Request body with examples
- ✅ Response codes & descriptions

---

## 📝 Optional: Add Manual Notes

Create a `docs/manual_notes.md` file for additional documentation that won't be auto-generated:

```markdown
# Authentication Flow

## Token Lifecycle

1. **Login** → Get access & refresh tokens
2. **Use** → Include access token in Authorization header
3. **Expires** → Access token valid for 30 minutes
4. **Refresh** → Use refresh token to get new access token
5. **Logout** → Tokens invalidated server-side

## Token Structure

```json
{
  "sub": "user_id",
  "iat": 1731398000,
  "exp": 1731401600,
  "type": "access",
  "ver": 1
}
```

---

# Error Responses

All endpoints return consistent error format:

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

# Rate Limiting

- **Limit:** 100 requests per minute per IP
- **Header:** `X-RateLimit-Remaining`
- **When exceeded:** `429 Too Many Requests`
```

These notes will be **automatically merged** into the final documentation.

---

## ⚙️ How It Works

```
┌─────────────────────────────────────────────┐
│ 1. FastAPI Server Running                   │
│    - Routes defined in code                 │
│    - OpenAPI schema auto-generated          │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ 2. Export OpenAPI JSON                      │
│    curl http://localhost:8000/openapi.json  │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ 3. Run Documentation Generator              │
│    python scripts/generate_api_docs.py      │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ 4. Parse & Convert OpenAPI to Markdown      │
│    - Group by tags                          │
│    - Format endpoints                       │
│    - Extract parameters & responses         │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ 5. Merge Manual Notes (Optional)            │
│    docs/manual_notes.md                     │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ 6. Save as Markdown                         │
│    docs/API_Documentation.md                │
└─────────────────────────────────────────────┘
```

---

## 🚀 Automation in CI/CD

### GitHub Actions Example

Create `.github/workflows/generate-docs.yml`:

```yaml
name: Generate API Documentation

on:
  push:
    branches: [main, develop]
    paths:
      - 'backend/app/api/**'
      - 'backend/app/main.py'

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
      
      - name: Start FastAPI server
        run: |
          cd backend
          uvicorn app.main:app &
          sleep 5
      
      - name: Export OpenAPI schema
        run: |
          mkdir -p docs
          curl http://127.0.0.1:8000/openapi.json -o docs/openapi.json
      
      - name: Generate documentation
        run: |
          cd backend
          python scripts/generate_api_docs.py
      
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add docs/API_Documentation.md
          git commit -m "docs: auto-generated API documentation"
          git push
```

---

## 📋 File Structure

```
backend/
├── scripts/
│   └── generate_api_docs.py    # Documentation generator
├── docs/
│   ├── openapi.json            # Exported OpenAPI schema
│   ├── API_Documentation.md    # Generated documentation
│   └── manual_notes.md         # Optional manual additions
└── README.md
```

---

## ✅ Complete Workflow

```bash
# 1. Start server
cd backend
uvicorn app.main:app --reload &

# 2. Export OpenAPI
mkdir -p docs
curl http://127.0.0.1:8000/openapi.json -o docs/openapi.json

# 3. Generate documentation
python scripts/generate_api_docs.py

# 4. View result
cat docs/API_Documentation.md

# 5. Commit to repository
git add docs/
git commit -m "docs: update API documentation"
git push
```

---

## 🎁 Benefits

| Benefit | Details |
|---------|---------|
| **Always Updated** | Changes in code = automatic doc updates |
| **Single Source** | No duplicate documentation to maintain |
| **Professional** | Beautifully formatted Markdown |
| **Mergeable** | Combine auto-generated + manual docs |
| **CI/CD Ready** | Integrate into deployment pipeline |
| **Zero Effort** | One command to update everything |

---

## 🐛 Troubleshooting

**Problem:** `openapi.json` not found
```bash
# Solution: Start server and export schema
uvicorn app.main:app --reload &
curl http://127.0.0.1:8000/openapi.json -o docs/openapi.json
```

**Problem:** Script can't parse JSON
```bash
# Solution: Verify JSON is valid
python -m json.tool docs/openapi.json
```

**Problem:** Documentation looks wrong
```bash
# Solution: Regenerate from fresh schema
rm docs/openapi.json
curl http://127.0.0.1:8000/openapi.json -o docs/openapi.json
python scripts/generate_api_docs.py
```

---

## 📖 Next Steps

1. **Review** the generated `API_Documentation.md`
2. **Customize** with manual notes if needed
3. **Commit** to version control
4. **Share** with team/stakeholders
5. **Automate** in CI/CD for continuous updates

---

**Last Updated:** November 15, 2025  
**Status:** ✅ Ready to Use

