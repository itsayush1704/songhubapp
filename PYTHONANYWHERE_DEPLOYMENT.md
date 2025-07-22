# SongHub - PythonAnywhere Deployment Guide

This guide will help you deploy your SongHub application to PythonAnywhere.

## Prerequisites

1. A PythonAnywhere account (free or paid)
2. Your SongHub application files
3. Basic knowledge of Python and Flask

## Step 1: Upload Your Files

### Option A: Using Git (Recommended)
1. Push your code to a Git repository (GitHub, GitLab, etc.)
2. In PythonAnywhere console, clone your repository:
   ```bash
   git clone https://github.com/yourusername/songhub.git
   cd songhub
   ```

### Option B: Upload Files Directly
1. Go to the "Files" tab in your PythonAnywhere dashboard
2. Upload all your project files to `/home/yourusername/songhub/`

## Step 2: Install Dependencies

1. Open a Bash console in PythonAnywhere
2. Navigate to your project directory:
   ```bash
   cd /home/yourusername/songhub
   ```
3. Create a virtual environment:
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Step 3: Configure WSGI File

1. Go to the "Web" tab in your PythonAnywhere dashboard
2. Click "Add a new web app"
3. Choose "Manual configuration" and select Python 3.10
4. Edit the WSGI configuration file (usually at `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
5. Replace the contents with the WSGI configuration provided below

## Step 4: Set Up Static Files (if needed)

1. In the "Web" tab, scroll down to "Static files"
2. Add a static file mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/songhub/static/`

## Step 5: Environment Variables

1. In the "Web" tab, scroll down to "Environment variables"
2. Add any necessary environment variables (if your app uses them)

## Step 6: Reload and Test

1. Click "Reload" in the Web tab
2. Visit your app at `https://yourusername.pythonanywhere.com`

## Important Notes

### Free Account Limitations
- Limited CPU seconds per day
- No HTTPS for custom domains
- Apps sleep after inactivity
- Limited bandwidth

### Paid Account Benefits
- More CPU seconds
- HTTPS support
- Custom domains
- Always-on tasks
- More storage

### File Persistence
- PythonAnywhere provides persistent storage
- Your pickle files (playlists.pkl, recently_played.pkl, etc.) will be preserved
- Make sure to handle file paths correctly in production

### Performance Considerations
- YouTube Music API calls may be slower on free accounts
- Consider implementing caching for better performance
- Monitor your CPU usage in the dashboard

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed in your virtual environment
2. **File Not Found**: Check file paths are absolute or relative to the correct directory
3. **API Timeouts**: YouTube Music API may timeout on slower connections
4. **CPU Limit Exceeded**: Optimize your code or upgrade to a paid account

### Debugging

1. Check error logs in the "Web" tab
2. Use the console to test imports and functionality
3. Add logging to your application for better debugging

### Getting Help

- PythonAnywhere Help Pages: https://help.pythonanywhere.com/
- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/
- PythonAnywhere Support (paid accounts)

## Security Considerations

1. **Secret Key**: Make sure to use a secure secret key in production
2. **API Keys**: Store sensitive API keys as environment variables
3. **CORS**: Review CORS settings for production use
4. **Input Validation**: Ensure all user inputs are properly validated

## Monitoring and Maintenance

1. **Regular Updates**: Keep dependencies updated
2. **Backup Data**: Regularly backup your pickle files
3. **Monitor Usage**: Keep track of CPU and bandwidth usage
4. **Error Monitoring**: Set up logging to catch and fix issues

## Next Steps

1. Test all functionality thoroughly
2. Set up monitoring and logging
3. Consider implementing a proper database instead of pickle files
4. Optimize performance for production use
5. Set up automated backups

Your SongHub application should now be successfully deployed on PythonAnywhere!