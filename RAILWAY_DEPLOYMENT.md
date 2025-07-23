# SongHub - Railway Deployment Guide

This guide will help you deploy your SongHub application to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **Railway CLI** (optional): Install with `npm install -g @railway/cli`

## Deployment Methods

### Method 1: Deploy via Railway Dashboard (Recommended)

1. **Connect GitHub Repository**:
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `songhub1` repository

2. **Configure Project Settings**:
   - Railway will automatically detect it's a Python project
   - It will use the `requirements.txt` for dependencies
   - The `Procfile` will define the start command

3. **Environment Variables** (if needed):
   - Go to your project dashboard
   - Click on "Variables" tab
   - Add any environment variables:
     - `SECRET_KEY`: Generate a secure secret key
     - Any API keys if required

4. **Deploy**:
   - Railway will automatically build and deploy your app
   - You'll get a public URL like `https://your-app.railway.app`

### Method 2: Deploy via Railway CLI

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize and Deploy**:
   ```bash
   cd /path/to/songhub1
   railway init
   railway up
   ```

## Project Configuration Files

### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python app.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Procfile
```
web: python app.py
```

### Updated app.py
- Now uses `PORT` environment variable
- Binds to `0.0.0.0` for Railway compatibility
- Disabled debug mode for production

## Railway Features

✅ **Automatic Deployments**: Every push to main branch triggers deployment
✅ **Custom Domains**: Add your own domain
✅ **HTTPS**: Automatic SSL certificates
✅ **Persistent Storage**: 1GB included in free tier
✅ **Environment Variables**: Secure configuration management
✅ **Logs**: Real-time application logs
✅ **Metrics**: CPU, memory, and network monitoring

## Free Tier Limits

- **Execution Time**: 500 hours per month
- **Memory**: 512MB RAM
- **Storage**: 1GB persistent disk
- **Bandwidth**: Fair use policy
- **Custom Domains**: 1 custom domain

## Post-Deployment

1. **Test Your App**:
   - Visit the provided Railway URL
   - Test all endpoints: search, streaming, playlists
   - Check browser console for any errors

2. **Monitor Performance**:
   - Use Railway's built-in metrics
   - Monitor memory and CPU usage
   - Check application logs for errors

3. **Custom Domain** (optional):
   - Go to project settings
   - Add your custom domain
   - Configure DNS settings

## Persistent Storage

Railway provides persistent storage, which means:
- Your pickle files (playlists.pkl, recently_played.pkl, etc.) will be preserved
- Data persists across deployments
- No need to migrate to a database immediately

## Environment Variables

Recommended environment variables:
```
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
PORT=8009  # Railway will override this
```

## Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Check the build logs in Railway dashboard
   - Ensure all dependencies are in `requirements.txt`
   - Verify Python version compatibility

2. **App Not Starting**:
   - Check if PORT environment variable is properly handled
   - Verify the Procfile syntax
   - Check application logs for startup errors

3. **Import Errors**:
   - Ensure all packages are listed in `requirements.txt`
   - Check for version conflicts

4. **Performance Issues**:
   - Monitor memory usage in Railway dashboard
   - Optimize heavy operations
   - Consider upgrading to paid plan if needed

## Advantages of Railway for SongHub

1. **Perfect for Flask Apps**: Native Python support
2. **Persistent Storage**: Your pickle files are preserved
3. **Easy ML Libraries**: scikit-learn and numpy work out of the box
4. **Generous Free Tier**: 500 hours/month is plenty for development
5. **Simple Deployment**: Git push to deploy
6. **Good Performance**: Fast cold starts and execution

## Next Steps

1. **Database Migration**: Consider migrating from pickle files to PostgreSQL
2. **Caching**: Add Redis for better performance
3. **Monitoring**: Set up error tracking
4. **Scaling**: Monitor usage and upgrade plan if needed

## Support

- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [railway.app/discord](https://railway.app/discord)
- **Railway Help**: [help.railway.app](https://help.railway.app)

---

🚀 **Your SongHub app is now ready for Railway deployment!**

Simply push your changes to GitHub and deploy via the Railway dashboard.