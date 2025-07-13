# 📚 Book Review Backend

A FastAPI backend project for managing book reviews with user authentication, role-based access, background email tasks, and relational tagging.

---

## 🚀 Features

- ✅ **JWT Authentication** (Signup/Login/Logout)
- 📚 **Book & Review Management**
- 🧾 **Tagging System**
- 📧 **Password Reset via Email** (Celery + Redis)
- 🧪 **Unit Testing** with Pytest
- 🧠 **Async SQLModel + PostgreSQL**
- 🌱 **Alembic for Migrations**

---

## 🛠 Tech Stack

| Component       | Tool         |
|----------------|--------------|
| Framework      | FastAPI      |
| ORM            | SQLModel     |
| DB             | PostgreSQL   |
| Migrations     | Alembic      |
| Auth           | JWT Tokens   |
| Background     | Celery + Redis |
| Mail Service   | SMTP (via FastAPI Mail) |
| Testing        | Pytest       |

---

## 📦 Getting Started

### 🔧 Requirements

- Python 3.11+
- PostgreSQL
- Redis

### 🔐 Environment Setup

```bash
cp .env.example .env

📥 Install Dependencies
pip install -r requirements.txt

🧬 Run Migrations
alembic upgrade head

🚀 Running the App
uvicorn source.main:app --reload

⏱ Running Celery Worker (for email sending)
celery -A source.celery_task.c_app worker --loglevel=info
🌼 Optional: Run Flower (Celery Monitor)
celery -A source.celery_task.c_app flower

🗂 Folder Structure
Revision/
│
├── migrations/              # Alembic migration files
├── source/
│   ├── auth/                # Signup/login/password reset logic
│   ├── books/               # Book-related endpoints
│   ├── reviews/             # Review endpoints
│   ├── tags/                # Tag handling
│   ├── db/                  # Database config & models
│   ├── templates/           # Jinja templates (e.g. for password reset)
│   ├── tests/               # Pytest-based test cases
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Settings loader
│   ├── celery_task.py       # Celery app/tasks
│   ├── mail.py              # Email utility
│   └── middle_ware.py       # Logging middleware
├── .env.example             # Sample environment config
├── .gitignore
├── alembic.ini
└── requirements.txt

🧑‍💻 Author
Pavan Dudam — LinkedIn - Pavan Dudam | GitHub - PavanDudam

