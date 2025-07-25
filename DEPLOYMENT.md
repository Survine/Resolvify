# Deployment Guide

## Local Development Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Quick Setup

#### Using PowerShell (Recommended for Windows):
```powershell
# Run the setup script
.\setup.ps1
```

#### Using Command Prompt:
```cmd
# Run the setup script
setup.bat
```

#### Manual Setup:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database
python setup_db.py

# 3. Start the application
uvicorn main:app --reload
```

### Access the Application
- **Main Page**: http://localhost:8000
- **Employee Dashboard**: http://localhost:8000/support
- **Customer Chat**: http://localhost:8000/customer
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

### Default Login Credentials
- **Admin**: username=`admin`, password=`admin123`
- **Manager**: username=`manager1`, password=`manager123`
- **Support Agent 1**: username=`support1`, password=`support123`
- **Support Agent 2**: username=`support2`, password=`support123`

## Production Deployment

### Environment Variables
Create a `.env` file or set these environment variables:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Database Setup
For production, use PostgreSQL:

```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Update DATABASE_URL in .env file
DATABASE_URL=postgresql://username:password@host:port/database_name
```

### Running with Gunicorn (Production WSGI Server)
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment
Create a `Dockerfile`:

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t customer-support .
docker run -p 8000:8000 customer-support
```

### Nginx Configuration (Optional)
For serving static files and SSL termination:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /chat/ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security Considerations

1. **Change Default Passwords**: Update all default passwords before production
2. **Use Strong Secret Key**: Generate a secure secret key for JWT tokens
3. **Enable HTTPS**: Use SSL/TLS certificates in production
4. **Database Security**: Use secure database credentials and connections
5. **Environment Variables**: Store sensitive data in environment variables
6. **Rate Limiting**: Implement rate limiting for API endpoints
7. **Input Validation**: All inputs are validated using Pydantic schemas

## Monitoring and Logging

### Application Logs
The application uses FastAPI's built-in logging. To configure custom logging:

```python
import logging
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Start with custom logging
uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
```

### Health Check
Monitor the application health using the `/health` endpoint:
```bash
curl http://localhost:8000/health
```

## Backup and Recovery

### Database Backup
For SQLite (development):
```bash
cp customer_support.db customer_support_backup.db
```

For PostgreSQL (production):
```bash
pg_dump -h localhost -U username -d database_name > backup.sql
```

### Database Restore
For PostgreSQL:
```bash
psql -h localhost -U username -d database_name < backup.sql
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Find process using port 8000
   netstat -ano | findstr :8000
   # Kill the process
   taskkill /F /PID <process_id>
   ```

2. **Database Connection Error**:
   - Check database URL in `.env` file
   - Ensure database server is running
   - Verify credentials

3. **WebSocket Connection Issues**:
   - Check firewall settings
   - Verify WebSocket endpoints are accessible
   - Check browser console for errors

4. **Permission Denied Errors**:
   - Ensure user has proper role assignments
   - Check permission system setup
   - Verify JWT token is valid

### Getting Help
- Check the API documentation at `/docs`
- Review application logs
- Verify environment configuration
- Test with default credentials first
