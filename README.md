# Django PC Webshop API - Local Development

> ⚠️ **Note:** This project’s active development is in the `deployment` branch.  
> The `main` branch is outdated and kept only for legacy reference because it is ready to be deployed on Render. 

A RESTful API for a PC Components Webshop, developed with Django REST Framework and a React Frontend. This version is optimized for local development.

## 🚀 Features

- RESTful API with Django REST Framework
- React Frontend with modern UI
- AI-powered PC Configuration Recommendations
- JWT Authentication
- SQLite Database (for local development)
- Swagger/OpenAPI Documentation
- CORS Support
- Automatic API Documentation with drf-spectacular
- Hot-Reload for fast development

## 📋 Prerequisites

- Python 3.12 or higher
- Node.js 18.x or higher
- npm (Node Package Manager)
- pip (Python Package Manager)
- Git (optional, for version control)

## 🛠️ Installation

1. **Clone Repository** (if using Git)
```bash
git checkout deployment
git clone https://github.com/IhrUsername/django_pc_webshop_api.git
cd django_pc_webshop_api
```

2. **Backend Setup**

a) **Create and Activate Virtual Environment**
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

b) **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

c) **Set Up Environment Variables**
Create a `.env` file in the root directory:
```env
DATABASE_ADMIN_PASSWORD_LOCAL="YourLocalPassword"
PYTHONPATH=D:\Python Projects\django_pc_webshop_api
OPENAI_API_KEY="Your-OpenAI-API-Key"  # For PC recommendations
```

d) **Run Database Migrations**
```bash
python app/manage.py migrate
```

e) **Create Superuser**
```bash
python app/manage.py createsuperuser
```

f) **Collect Static Files**
```bash
python app/manage.py collectstatic --noinput
```

3. **Frontend Setup**

a) **Navigate to Frontend Directory**
```bash
cd frontend
```

b) **Install Node Dependencies**
```bash
npm install
```

c) **Build Frontend**
```bash
npm run build
```

## 🚀 Start Development Server

1. **Start Backend Server**
```bash
# In root directory
python app/manage.py runserver
```
The backend server will be available at `http://127.0.0.1:8000`.

2. **Start Frontend Development Server**
```bash
# In frontend directory
npm start
```
The frontend server will be available at `http://localhost:3000`.

## 📚 API Documentation

The API documentation is available at the following URLs:
- Swagger UI: `http://127.0.0.1:8000/swagger/`
- ReDoc: `http://127.0.0.1:8000/redoc/`

## 🏗️ Project Structure

```
django_pc_webshop_api/
├── app/               # Django project configuration
├── users/             # User management
├── pc_components/     # PC components
├── pc_recommendations/# AI-powered PC recommendations
├── orders/           # Orders
└── static/           # Static files
├── frontend/              # React Frontend
│   ├── src/              # Source code
│   ├── public/           # Public files
│   └── build/            # Built frontend files
├── venv/                  # Virtual environment
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── .gitignore            # Git ignore file
```

## 🔧 Development Configuration

### Database
- SQLite is used as local database
- Database file: `db.sqlite3`
- Create migrations: `python app/manage.py makemigrations`
- Apply: `python app/manage.py migrate`

### Debug Mode
- Debug is enabled by default
- Detailed error messages
- Hot-Reload for code changes

### Static Files
- Local development: `python app/manage.py collectstatic`
- Static files are stored in `app/staticfiles`

## 🔒 Security

### Local Development
- JWT Authentication for API endpoints
- CORS configuration for local development
- Secure password handling
- Environment variables for sensitive data

### API Tests
```bash
# Run all tests
python app/manage.py test

# Test specific app
python app/manage.py test users
python app/manage.py test pc_components
python app/manage.py test pc_recommendations
python app/manage.py test orders
```

## 🛠️ Useful Commands

```bash
# Reset database
python app/manage.py flush

# Create new superuser
python app/manage.py createsuperuser

# Open shell
python app/manage.py shell

# Reset migrations
python app/manage.py migrate --fake zero
python app/manage.py migrate

# Rebuild frontend
cd frontend
npm run build
```

## ✅ Continuous Integration (CI)

This project uses GitHub Actions to run tests on every push and pull request.

- ✅ Runs on Ubuntu with PostgreSQL 14
- ✅ Installs dependencies from `requirements.txt`
- ✅ Runs migrations (`python manage.py migrate`)
- ✅ Executes `pytest` for all apps

**Workflow config:** `.github/workflows/tests.yml`

### ▶️ Run tests locally

```bash
# All tests
pytest

# Specific app
pytest users/tests
pytest orders/tests
pytest pc_components/tests
pytest pc_recommendations/tests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Nico Wittemann** - [https://github.com/Darkchanze/django_pc_webshop_api](https://github.com/Darkchanze/django_pc_webshop_api)

