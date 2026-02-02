# Identity Verification API

A production-ready FastAPI backend service for user authentication and identity verification, featuring JWT authentication, role-based access control, and mock government ID verification.

## 🚀 Features

- **User Authentication**: Secure registration and login with JWT tokens
- **Password Security**: Bcrypt password hashing
- **Protected Endpoints**: Role-based access control (user/admin)
- **ID Verification**: Mock NIA/NHIS identity verification system
- **Database Persistence**: SQLite database with SQLAlchemy ORM
- **API Documentation**: Auto-generated interactive Swagger UI docs

## 🛠️ Tech Stack

- **Python 3.10+**
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **JWT** - JSON Web Tokens for authentication
- **Bcrypt** - Password hashing
- **Uvicorn** - ASGI server

## 📋 Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

## ⚙️ Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/isaacjohnsondev1-coder/identity-verification-api.git
cd identity-verification-api
```

2. **Create a virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the server**
```bash
uvicorn main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🔌 API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/register` | Register new user |
| POST | `/login` | Login and get JWT token |

### Protected Endpoints (Requires Authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/me` | Get current user info |
| POST | `/verify-id` | Verify government ID |
| GET | `/admin/verifications` | List all verifications (Admin only) |

## 💡 Usage Examples

### 1. Register a New User

```bash
curl -X POST "http://127.0.0.1:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```

### 2. Login

```bash
curl -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepass123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Get User Info (Protected)

```bash
curl -X GET "http://127.0.0.1:8000/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Verify ID (Protected)

```bash
curl -X POST "http://127.0.0.1:8000/verify-id" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id_type": "NIA", "id_number": "GHA-12345678"}'
```

**Verification Logic**: 
- ID numbers ending in **even digits** → `verified`
- ID numbers ending in **odd digits** → `failed`

## 🗄️ Database Schema

### Users Table
- `id` - Primary key
- `email` - Unique user email
- `hashed_password` - Bcrypt hashed password
- `is_admin` - Admin role flag

### Verifications Table
- `id` - Primary key
- `id_type` - Type of ID (NIA/NHIS)
- `id_number` - Government ID number
- `status` - Verification status
- `user_id` - Foreign key to Users

## 🔐 Security Features

- JWT token-based authentication
- Bcrypt password hashing (cost factor: 12)
- Token expiration (30 minutes)
- Protected endpoints with role validation
- SQL injection prevention via ORM

## 🚀 Deployment

This API can be deployed to:
- **Render** - [Deploy Guide](https://render.com/docs/deploy-fastapi)
- **Railway** - [Deploy Guide](https://docs.railway.app/guides/fastapi)
- **Fly.io** - [Deploy Guide](https://fly.io/docs/languages-and-frameworks/python/)
- **Heroku** - [Deploy Guide](https://devcenter.heroku.com/articles/getting-started-with-python/)

## 📝 Project Structure

```
identity-verification-api/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
├── README.md           # This file
└── app.db              # SQLite database (auto-created)
```

## 🎯 Future Enhancements

- [ ] Real NIA/NHIS API integration
- [ ] PostgreSQL database support
- [ ] Rate limiting
- [ ] Email verification
- [ ] Password reset functionality
- [ ] Audit logging
- [ ] Docker containerization

## 👨‍💻 Author

**Isaac Johnson**
- GitHub: [@isaacjohnsondev1-coder](https://github.com/isaacjohnsondev1-coder)
- Email: isaacjohnson.dev1@gmail.com

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

Built as a portfolio project to demonstrate backend development skills with FastAPI, JWT authentication, and RESTful API design.
