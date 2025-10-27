# Dropbox Clone API

A production-ready RESTful API for file storage and management, similar to Dropbox. Built with FastAPI, featuring JWT authentication, secure file handling, and organized storage.

## About The Project

This is a complete file storage API that allows users to:
- **Register and authenticate** securely with JWT tokens
- **Upload files** of any type with automatic organization
- **List all their files** with pagination support
- **Download files** with proper streaming
- **Delete files** they own

The API is built with modern Python technologies and follows REST best practices. All user data and files are isolated, ensuring privacy and security.

### Tech Stack

- **Framework**: FastAPI (high-performance async API framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens) with refresh token rotation
- **Password Security**: Bcrypt hashing with salt
- **Package Manager**: uv (fast Python package manager)
- **Python Version**: 3.12+

### Server Details

- **Host**: localhost
- **Port**: 8080
- **API Documentation**: Available at `/docs` (Swagger UI) and `/redoc`
- **Database**: SQLite file (`dropbox.db`) created automatically
- **File Storage**: Local filesystem in `uploads/` directory

## Features

- **JWT Authentication**: Short-lived access tokens (15 min) and refresh tokens (7 days)
- **Token Rotation**: New refresh tokens on each refresh to prevent replay attacks
- **Password Security**: Bcrypt password hashing with automatic salting
- **File Upload**: Multipart form-data support for any file type
- **File Organization**: User-specific directories with UUID filenames
- **File Management**: List (with pagination), download, and delete operations
- **Access Control**: Users can only access their own files
- **Error Handling**: Proper HTTP status codes and descriptive error messages
- **Auto-Documentation**: Interactive API docs with Swagger UI

## Database Schema

### Tables

1. **User**
   - `id` (Primary Key)
   - `displayName` (String)
   - `userName` (String, Unique)
   - `password` (String, Hashed)
   - `created` (DateTime)
   - `modified` (DateTime)

2. **File**
   - `id` (Primary Key)
   - `fileName` (String)
   - `fileType` (String)
   - `fileSize` (Integer)
   - `filePath` (String)
   - `created` (DateTime)
   - `modified` (DateTime)

3. **UserToFileAssociation**
   - `id` (Primary Key)
   - `userId` (Foreign Key → User.id)
   - `fileId` (Foreign Key → File.id, Unique)

## Getting Started

### Prerequisites

Before running the project, ensure you have:

- **Python 3.12 or higher**: [Download Python](https://www.python.org/downloads/)
- **uv package manager**: Fast Python package manager
  ```bash
  # Install uv (Windows/macOS/Linux)
  curl -LsSf https://astral.sh/uv/install.sh | sh
  
  # Or using pip
  pip install uv
  ```

### Installation & Setup

1. **Clone or download the repository**
   ```bash
   cd dropboxclone
   ```

2. **Navigate to the server directory**
   ```bash
   cd server
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```
   This will:
   - Create a virtual environment (`.venv`)
   - Install FastAPI, uvicorn, SQLAlchemy, bcrypt, PyJWT, and all dependencies
   - Lock dependencies in `uv.lock`

4. **Run the server**
   ```bash
   uv run python main.py
   ```
   
   You should see:
   ```
   INFO:     Started server process
   ✓ Uploads directory created at: /path/to/uploads
   ✓ Database initialized
   INFO:     Uvicorn running on http://localhost:8080
   ```

5. **Verify the server is running**
   
   Open your browser and visit:
   - **API Root**: http://localhost:8080/
   - **Interactive Docs**: http://localhost:8080/docs
   - **Alternative Docs**: http://localhost:8080/redoc

### Project Structure After Setup

```
dropboxclone/
├── server/
│   ├── .venv/              # Virtual environment (created by uv)
│   ├── main.py             # FastAPI application entry point
│   ├── models.py           # Database models
│   ├── schemas.py          # Pydantic schemas
│   ├── database.py         # Database configuration
│   ├── auth.py             # Authentication logic
│   ├── crud.py             # Database operations
│   ├── pyproject.toml      # Project dependencies
│   ├── uv.lock             # Dependency lock file
│   ├── dropbox.db          # SQLite database (auto-created)
│   └── uploads/            # File storage (auto-created)
│       └── {user_id}/      # User-specific directories
└── README.md
```

### Quick Test

Once the server is running, test the API:

```bash
# Test health endpoint
curl http://localhost:8080/

# Register a user
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"displayName": "Test User", "userName": "testuser", "password": "test123"}'

# Login
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"userName": "testuser", "password": "test123"}'
```

## API Endpoints

### Authentication

#### Register a New User
```http
POST /api/auth/register
Content-Type: application/json

{
  "displayName": "John Doe",
  "userName": "johndoe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "id": 1,
  "displayName": "John Doe",
  "userName": "johndoe",
  "created": "2025-10-27T10:00:00",
  "modified": "2025-10-27T10:00:00"
}
```

#### Login (Get JWT Tokens)
```http
POST /api/auth/login
Content-Type: application/json

{
  "userName": "johndoe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### Refresh Access Token
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "new-refresh-token-uuid",
  "token_type": "bearer",
  "expires_in": 900
}
```

### File Operations

All file operations require authentication using Bearer token in the Authorization header:
```
Authorization: Bearer <your-token>
```

#### Upload a File
```http
POST /api/files/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary-file-data>
```

**Response:**
```json
{
  "id": 1,
  "fileName": "document.pdf",
  "fileType": "application/pdf",
  "fileSize": 102400,
  "filePath": "uploads/1/uuid-filename.pdf",
  "message": "File uploaded successfully"
}
```

#### List Files
```http
GET /api/files/?page=1&page_size=10
Authorization: Bearer <token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Number of files per page (default: 10, max: 100)

**Response:**
```json
{
  "files": [
    {
      "id": 1,
      "fileName": "document.pdf",
      "fileType": "application/pdf",
      "fileSize": 102400,
      "created": "2025-10-27T10:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

#### Download a File
```http
GET /api/files/{file_id}/download
Authorization: Bearer <token>
```

Returns the file as a binary stream.

#### Delete a File
```http
DELETE /api/files/{file_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "File deleted successfully"
}
```

### Health Check
```http
GET /
```

Returns API status and available endpoints.

## Complete Testing Workflow

### Step 1: Register a User

```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "John Doe",
    "userName": "johndoe",
    "password": "password123"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "displayName": "John Doe",
  "userName": "johndoe",
  "created": "2025-10-27T10:00:00",
  "modified": "2025-10-27T10:00:00"
}
```

### Step 2: Login to Get JWT Tokens

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "userName": "johndoe",
    "password": "password123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Save the access_token for next steps!**

### Step 3: Upload a File

```bash
# Replace <YOUR_ACCESS_TOKEN> with the token from Step 2
curl -X POST http://localhost:8080/api/files/upload \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  -F "file=@/path/to/your/file.pdf"
```

**On Windows PowerShell:**
```powershell
curl.exe -X POST http://localhost:8080/api/files/upload `
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" `
  -F "file=@C:\path\to\your\file.pdf"
```

### Step 4: List Your Files

```bash
curl -X GET "http://localhost:8080/api/files/?page=1&page_size=10" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

### Step 5: Download a File

```bash
# Replace {file_id} with the id from the list response
curl -X GET http://localhost:8080/api/files/1/download \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  -o downloaded_file.pdf
```

### Step 6: Delete a File

```bash
curl -X DELETE http://localhost:8080/api/files/1 \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

### Step 7: Refresh Access Token (When Expired)

```bash
# Replace <YOUR_REFRESH_TOKEN> with the refresh_token from Step 2
curl -X POST http://localhost:8080/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<YOUR_REFRESH_TOKEN>"
  }'
```

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8080/docs - Test all endpoints interactively
- **ReDoc**: http://localhost:8080/redoc - Alternative documentation view

Both documentation pages are generated automatically from your code and include:
- All available endpoints
- Request/response schemas
- Authentication requirements
- Try-it-out functionality (Swagger UI only)

## Security Features

- **Password Hashing**: Passwords are hashed using bcrypt with salt before storage
- **JWT Authentication**: Short-lived access tokens (15 min) for API requests
- **Refresh Tokens**: Long-lived refresh tokens (7 days) stored securely in database
- **Token Rotation**: New refresh tokens issued on each refresh to prevent replay attacks
- **File Access Control**: Users can only access their own files
- **Unique Filenames**: UUIDs prevent filename collisions and path traversal attacks

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

All error responses include a JSON body with details:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Troubleshooting

### Port Already in Use

If you get an error that port 8080 is already in use:

```bash
# Find the process using port 8080
# On Windows:
netstat -ano | findstr :8080

# On macOS/Linux:
lsof -i :8080

# Kill the process or change the port in main.py:
# uvicorn.run(app, host="localhost", port=8081)
```

### Module Not Found Errors

If you get import errors:

```bash
# Make sure you're in the server directory
cd server

# Reinstall dependencies
uv sync

# Always run with uv run
uv run python main.py
```

### Database Locked Error

If you get "database is locked":

```bash
# Stop the server (Ctrl+C)
# Delete the database and restart
rm dropbox.db
uv run python main.py
```

### Access Token Expired

Access tokens expire after 15 minutes. Use the refresh token to get a new one:

```bash
curl -X POST http://localhost:8080/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

### File Upload Issues

For large files, you might need to increase the request size limit. Edit `main.py`:

```python
app = FastAPI(
    title="Dropbox Clone API",
    version="2.0.0",
    lifespan=lifespan,
    max_request_size=100 * 1024 * 1024  # 100MB
)
```

## Development

### Running in Development Mode

```bash
# Run with auto-reload on code changes
cd server
uvicorn main:app --reload --host localhost --port 8080
```

### Viewing Logs

The server outputs logs to the console. For detailed debugging:

```python
# In main.py, add logging configuration
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Production Deployment

For production deployment, consider:

1. **Use a production WSGI server** (e.g., Gunicorn with Uvicorn workers)
2. **Set a secure SECRET_KEY** (in `auth.py`, use environment variable)
3. **Use PostgreSQL or MySQL** instead of SQLite
4. **Store files in cloud storage** (AWS S3, Google Cloud Storage)
5. **Add rate limiting** to prevent abuse
6. **Enable HTTPS** with a reverse proxy (Nginx, Caddy)
7. **Set up CORS** if building a frontend

## License

MIT

