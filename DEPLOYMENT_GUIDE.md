# 🚀 Production Deployment Guide

This guide covers deployment of the User Authentication System to various platforms.

## ✅ Pre-Deployment Checklist

Before deploying, ensure:

- [x] All dependencies in `requirements.txt` are installed
- [x] `.env` file is configured with production credentials
- [x] Database (MySQL or SQLite) is accessible
- [x] Port 5000 (or custom PORT) is available
- [x] Python 3.8+ is installed

## 📦 Installation

### Local Development
```bash
# Clone repository
git clone <repository-url>
cd Database

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
# Edit .env file with your database credentials

# Run development server
python app.py

# OR run production server
python run_production.py
```

### Production Deployment

#### Option 1: Waitress WSGI Server (Recommended for Windows/Linux)
```bash
cd backend
python run_production.py
```

The application will start on `http://localhost:5000` or the port specified in `PORT` environment variable.

#### Option 2: Gunicorn (Linux/Mac)
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Option 3: Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/

WORKDIR /app/backend

EXPOSE 5000

CMD ["python", "run_production.py"]
```

Build and run:
```bash
docker build -t auth-app .
docker run -p 5000:5000 -v $(pwd)/backend/.env:/app/backend/.env auth-app
```

## 🔧 Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# MySQL Configuration (Optional - will fallback to SQLite if not provided)
DB_HOST=mysql-32205804-bennesangeeta-2dc6.h.aivencloud.com
DB_USER=avnadmin
DB_PASSWORD=your_secure_password
DB_NAME=defaultdb
DB_PORT=25502

# Optional: Custom port for production
PORT=5000
```

## 🗄️ Database Setup

### MySQL (Production)
1. Set up a MySQL instance (local or cloud like Aiven Cloud)
2. Update `.env` with your credentials
3. The application will automatically create the database and tables on first run

### SQLite (Development/Fallback)
- No configuration needed
- Database file (`users_local.db`) is created automatically
- Suitable for development and small deployments

## 🔒 Security Considerations

1. **Never commit `.env` files** - Already in `.gitignore`
2. **Use strong passwords** - Minimum 8 characters recommended
3. **Enable HTTPS** - Use reverse proxy (nginx) in production
4. **Change admin password** - Update `DB_PASSWORD` in production
5. **Regular backups** - Backup your database regularly

## 🌐 Reverse Proxy Configuration (Optional)

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Enable HTTPS with Let's Encrypt
```bash
sudo certbot --nginx -d your-domain.com
```

## 📊 Monitoring & Logging

### Application Logs
The application logs to stdout. To save logs to a file:

```bash
# Linux/Mac
python run_production.py > app.log 2>&1

# Windows
python run_production.py > app.log
```

### Health Check Endpoint
Access `http://localhost:5000/` to verify the application is running.

## 🔄 Updates & Maintenance

### Updating the Application
```bash
# Pull latest changes
git pull origin main

# Install any new dependencies
cd backend
pip install -r requirements.txt --upgrade

# Restart the application
# Stop current process and run again
python run_production.py
```

### Database Migrations
The application automatically handles schema migrations. New columns are added automatically.

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in .env
PORT=8080

# Or set environment variable
export PORT=8080  # Linux/Mac
set PORT=8080     # Windows
```

### Database Connection Failed
- Check database credentials in `.env`
- Verify database server is running
- Check firewall settings
- Application will automatically fall back to SQLite

### Permission Denied (Linux/Mac)
```bash
# Install dependencies with --user flag
pip install -r requirements.txt --user

# Or use sudo (not recommended)
sudo pip install -r requirements.txt
```

## 📱 Platform-Specific Deployments

### Heroku
1. Create `Procfile`:
```
web: cd backend && python run_production.py
```

2. Deploy:
```bash
heroku create
git push heroku main
heroku config:set DB_HOST=... DB_USER=... DB_PASSWORD=...
```

### AWS EC2
1. Launch EC2 instance
2. Install Python, Git
3. Clone repository
4. Configure security groups (port 5000)
5. Run: `python run_production.py`

### DigitalOcean App Platform
1. Connect GitHub repository
2. Configure build command: `pip install -r backend/requirements.txt`
3. Configure run command: `cd backend && python run_production.py`
4. Add environment variables

### Vercel
Note: Vercel is designed for serverless functions. For optimal Vercel deployment, consider restructuring as serverless functions.

## ✅ Post-Deployment Validation

After deployment, verify:

1. ✅ Application loads at the deployed URL
2. ✅ User registration works
3. ✅ Login functionality works
4. ✅ Password reset works
5. ✅ Admin features accessible with correct password
6. ✅ Database persists data correctly

Run the validation script:
```bash
python deployment_test.py
```

## 📞 Support

For issues or questions:
- Check existing documentation
- Review error logs
- Verify environment variables
- Test database connectivity

---

**Last Updated:** March 2026  
**Version:** 1.0.0
