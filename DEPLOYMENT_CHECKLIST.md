# SongHub PythonAnywhere Deployment Checklist

## Pre-Deployment Preparation

### 1. Account Setup
- [ ] Create PythonAnywhere account (free or paid)
- [ ] Note your username for configuration files
- [ ] Verify account type and limitations

### 2. File Preparation
- [ ] Review `requirements.txt` for all dependencies
- [ ] Update `wsgi.py` with your PythonAnywhere username
- [ ] Consider using `app_production.py` for better error handling
- [ ] Ensure all sensitive data is in environment variables

### 3. Code Review
- [ ] Remove any hardcoded secrets or API keys
- [ ] Verify all file paths are relative or configurable
- [ ] Test application locally before deployment
- [ ] Ensure CORS settings are appropriate for production

## Deployment Steps

### 1. Upload Files
**Option A: Git (Recommended)**
- [ ] Push code to GitHub/GitLab
- [ ] Clone repository in PythonAnywhere console:
  ```bash
  git clone https://github.com/yourusername/songhub.git
  cd songhub
  ```

**Option B: Direct Upload**
- [ ] Upload files via PythonAnywhere file manager
- [ ] Ensure proper directory structure

### 2. Virtual Environment Setup
- [ ] Open PythonAnywhere Bash console
- [ ] Create virtual environment:
  ```bash
  cd ~/songhub
  python3.10 -m venv venv
  source venv/bin/activate
  ```
- [ ] Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### 3. Web App Configuration
- [ ] Go to PythonAnywhere Web tab
- [ ] Click "Add a new web app"
- [ ] Choose "Manual configuration"
- [ ] Select Python 3.10
- [ ] Set source code directory: `/home/yourusername/songhub`
- [ ] Set working directory: `/home/yourusername/songhub`
- [ ] Update WSGI configuration file path: `/home/yourusername/songhub/wsgi.py`

### 4. WSGI Configuration
- [ ] Edit the WSGI file in PythonAnywhere web interface
- [ ] Replace content with your `wsgi.py` file
- [ ] Update all instances of 'yourusername' with your actual username
- [ ] Save the file

### 5. Static Files Setup
- [ ] In Web tab, add static files mapping:
  - URL: `/static/`
  - Directory: `/home/yourusername/songhub/static/`
- [ ] Ensure all CSS, JS, and image files are in the static directory

### 6. Environment Variables
- [ ] In Web tab, go to "Environment variables" section
- [ ] Add any required environment variables:
  - `SECRET_KEY`: Generate a secure secret key
  - Any API keys or configuration values

### 7. Database/Data Files (if applicable)
- [ ] Ensure data persistence files have proper permissions
- [ ] Test data loading and saving functionality
- [ ] Consider using PythonAnywhere's database services for larger applications

## Post-Deployment Testing

### 1. Basic Functionality
- [ ] Visit your app URL: `https://yourusername.pythonanywhere.com`
- [ ] Test main page loads correctly
- [ ] Check browser console for JavaScript errors
- [ ] Test search functionality
- [ ] Verify artist page navigation

### 2. API Endpoints
- [ ] Test `/health` endpoint
- [ ] Test search API: `/search?q=test`
- [ ] Verify all AJAX calls work correctly
- [ ] Check response times and performance

### 3. Error Handling
- [ ] Test invalid URLs (should show 404)
- [ ] Test API with invalid parameters
- [ ] Check error logs in PythonAnywhere
- [ ] Verify graceful error handling

## Monitoring and Maintenance

### 1. Logging
- [ ] Check error logs regularly in PythonAnywhere
- [ ] Monitor application performance
- [ ] Set up log rotation if needed

### 2. Updates
- [ ] Plan for code updates (Git pull or file upload)
- [ ] Test updates in development first
- [ ] Have rollback plan ready

### 3. Backup
- [ ] Regular backup of data files
- [ ] Keep copy of working configuration
- [ ] Document any custom configurations

## Troubleshooting Common Issues

### Import Errors
- [ ] Verify all dependencies in `requirements.txt`
- [ ] Check virtual environment activation
- [ ] Ensure Python version compatibility

### Static Files Not Loading
- [ ] Verify static files mapping in Web tab
- [ ] Check file permissions
- [ ] Ensure correct directory structure

### Application Not Starting
- [ ] Check WSGI configuration
- [ ] Review error logs
- [ ] Verify file paths in configuration

### Performance Issues
- [ ] Check for infinite loops or blocking operations
- [ ] Monitor CPU and memory usage
- [ ] Consider upgrading PythonAnywhere plan if needed

## Security Considerations

- [ ] Use HTTPS (automatic on PythonAnywhere)
- [ ] Secure secret key and environment variables
- [ ] Implement rate limiting for API endpoints
- [ ] Regular security updates for dependencies
- [ ] Monitor for suspicious activity

## Final Verification

- [ ] Application loads without errors
- [ ] All features work as expected
- [ ] Performance is acceptable
- [ ] Error handling works correctly
- [ ] Logs are being generated properly
- [ ] Backup and update procedures tested

---

**Note**: Replace 'yourusername' with your actual PythonAnywhere username throughout all configuration files.

**Support**: If you encounter issues, check PythonAnywhere's help documentation or contact their support team.