# SongHub - Learn CI/CD Through Music Streaming

🎵 A Flask-based music streaming application designed to teach CI/CD concepts through hands-on implementation.

SongHub uses YouTube Music as its backend and provides a clean, modern interface for searching and playing music from YouTube Music's vast library.

<img width="692" height="1366" alt="image" src="https://github.com/user-attachments/assets/0c78da63-c907-4956-b65c-bacee620da16" />

## 🎯 Learning Objectives

This project demonstrates:
- **Continuous Integration (CI)**: Automated testing, linting, and security checks
- **Continuous Deployment (CD)**: Automated deployment to staging and production
- **Docker Containerization**: Application packaging and deployment
- **Testing Strategies**: Unit, integration, and performance testing
- **Security Best Practices**: Code scanning and vulnerability detection
- **Monitoring & Health Checks**: Application monitoring and alerting

## 🎵 Features

- 🔍 Search for songs from YouTube Music
- ▶️ Stream music directly in the browser
- 🎨 Modern, responsive UI with dark theme
- 🎵 Full playback controls
- 📱 Mobile-friendly design
- 🎧 AI-powered music recommendations
- 📋 Custom playlist management
- 🔄 Real-time loading indicators

## 🚀 CI/CD Pipeline

Our GitHub Actions pipeline includes:

### 🧪 Testing Stage
- **Code Quality**: flake8, black, isort
- **Security**: bandit, safety
- **Unit Tests**: pytest with coverage reporting
- **Integration Tests**: End-to-end workflow testing

### 🐳 Build Stage
- **Docker Image**: Multi-stage build optimization
- **Security Scanning**: Trivy vulnerability scanning
- **Image Registry**: Push to container registry

### 🚢 Deploy Stage
- **Staging Environment**: Automated deployment with smoke tests
- **Production Environment**: Manual approval with health checks
- **Performance Testing**: Locust load testing

## 📋 Prerequisites

- Python 3.10+
- Docker
- Git
- GitHub account (for CI/CD)

## 🛠️ Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/itsayush1704/songhub1.git
   cd songhub1
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open http://localhost:8002 in your browser

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Types
```bash
# Unit tests only
pytest tests/test_app.py -m unit

# Integration tests only
pytest tests/test_integration.py -m integration

# With coverage report
pytest --cov=app --cov-report=html
```

### Performance Testing
```bash
# Install locust
pip install locust

# Run performance tests
locust -f tests/performance/locustfile.py --host=http://localhost:8002
```

## 🐳 Docker Usage

### Build Image
```bash
docker build -t songhub:latest .
```

### Run Container
```bash
docker run -p 8002:8002 songhub:latest
```

### Health Check
```bash
curl http://localhost:8002/health
```

## 🔄 CI/CD Workflow Explanation

### 1. Code Quality & Security (CI)
```yaml
# Triggered on: push, pull_request
steps:
  - Lint code (flake8, black, isort)
  - Security scan (bandit, safety)
  - Run unit tests
  - Generate coverage report
```

### 2. Build & Test (CI)
```yaml
# Triggered on: successful tests
steps:
  - Build Docker image
  - Scan image for vulnerabilities
  - Run integration tests
  - Push image to registry
```

### 3. Deploy to Staging (CD)
```yaml
# Triggered on: main branch push
steps:
  - Deploy to staging environment
  - Run smoke tests
  - Performance testing
  - Security validation
```

### 4. Deploy to Production (CD)
```yaml
# Triggered on: manual approval
steps:
  - Deploy to production
  - Health checks
  - Monitoring setup
  - Rollback capability
```

## 📊 Monitoring & Observability

### Health Endpoints
- `/health` - Application health status
- `/metrics` - Application metrics (if implemented)

### Logging
- Application logs in JSON format
- Error tracking and alerting
- Performance monitoring

## 🔒 Security Features

### Code Security
- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability scanner
- **Trivy**: Container image scanner

### Runtime Security
- Non-root container user
- Minimal base image
- Environment variable protection

## 📈 Learning Exercises

### Beginner Level
1. **Fork the repository** and set up GitHub Actions
2. **Make a code change** and observe the CI pipeline
3. **Break a test** and see how CI catches it
4. **Fix the test** and watch the pipeline succeed

### Intermediate Level
1. **Add a new feature** with corresponding tests
2. **Implement a new endpoint** with proper error handling
3. **Add environment-specific configurations**
4. **Set up branch protection rules**

### Advanced Level
1. **Implement blue-green deployment**
2. **Add database migrations to the pipeline**
3. **Set up monitoring and alerting**
4. **Implement automated rollback strategies**

## 🎓 CI/CD Best Practices Demonstrated

### ✅ Continuous Integration
- **Fast Feedback**: Quick test execution
- **Fail Fast**: Early error detection
- **Consistent Environment**: Docker containers
- **Automated Quality Gates**: Code coverage thresholds

### ✅ Continuous Deployment
- **Environment Promotion**: Staging → Production
- **Automated Testing**: Smoke tests and health checks
- **Rollback Strategy**: Quick revert capability
- **Manual Approvals**: Production deployment gates

### ✅ Security Integration
- **Shift Left Security**: Early vulnerability detection
- **Dependency Scanning**: Known vulnerability checks
- **Container Security**: Image vulnerability scanning
- **Secret Management**: Secure credential handling

## 🐛 Troubleshooting

### Common Issues

1. **Tests Failing Locally**
   ```bash
   # Check Python version
   python --version
   
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

2. **Docker Build Issues**
   ```bash
   # Clean Docker cache
   docker system prune -a
   
   # Rebuild without cache
   docker build --no-cache -t songhub:latest .
   ```

3. **CI Pipeline Failures**
   - Check GitHub Actions logs
   - Verify environment variables
   - Ensure all required secrets are set

## 📚 Additional Resources

### CI/CD Learning
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Testing Strategies](https://martinfowler.com/articles/practical-test-pyramid.html)

### Flask & Python
- [Flask Documentation](https://flask.palletsprojects.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Python Security Best Practices](https://python.org/dev/security/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 🏗️ Technology Stack

- **Backend**: Flask (Python)
- **YouTube Music API**: ytmusicapi
- **Frontend**: HTML, JavaScript, TailwindCSS
- **Icons**: Font Awesome
- **Testing**: pytest, locust
- **CI/CD**: GitHub Actions
- **Containerization**: Docker
- **Security**: bandit, safety, trivy

## 📄 License

MIT License

## 📝 Note

This application is for educational purposes only. Please ensure you comply with YouTube's terms of service when using this application.

---

**Happy Learning! 🚀**

This project is designed to be your hands-on playground for mastering CI/CD concepts. Start with the basics and gradually work your way up to advanced deployment strategies!
