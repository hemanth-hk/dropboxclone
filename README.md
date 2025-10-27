# TypeBox - File Storage Application

A modern full-stack file storage application with secure authentication and file management capabilities.

## 📁 Project Overview

**Server** - A FastAPI backend that handles authentication, file uploads, downloads, and storage management with JWT-based security.

**Client** - A Next.js frontend providing an intuitive interface for user authentication and file management operations.

## 🛠️ Tech Stack

**Backend**
- FastAPI (Python)
- SQLite + SQLAlchemy
- JWT Authentication

**Frontend**
- Next.js 15 (TypeScript)
- React
- Tailwind CSS + Shadcn UI
- Zustand

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.11+
- Node.js 20+

### Server Setup

```bash
cd server

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-jose passlib bcrypt python-multipart

# Create .env file
echo "SECRET_KEY=your-secret-key-here" > .env
```

### Client Setup

```bash
cd client

# Install dependencies
npm install
```

### Run Server

```bash
cd server
python main.py
```
Server runs at `http://localhost:8080`

### Run Client

```bash
cd client
npm run dev
```
Client runs at `http://localhost:3000`

---

**Visit `http://localhost:3000` to start using the application**
