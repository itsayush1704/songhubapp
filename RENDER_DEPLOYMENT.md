# SongHub - Render Deployment Guide

🚀 Deploy your SongHub music streaming application to Render.com for free!

## Why Render for SongHub?

✅ **Perfect for Flask Apps**: Native Python support with easy configuration <mcreference link="https://render.com/docs/deploy-flask" index="1">1</mcreference>  
✅ **Persistent Storage**: Your playlist data (pickle files) will be preserved  
✅ **Free Tier**: 750 hours/month, automatic HTTPS, custom domains  
✅ **Auto-Deploy**: Automatic deployments from GitHub  
✅ **ML Libraries**: Supports scikit-learn and numpy for recommendations  

## Prerequisites

- [Render.com account](https://render.com) (free)
- GitHub repository with your SongHub code
- Updated `requirements.txt` with gunicorn

## Step 1: Prepare Your Repository

### 1.1 Update Requirements (✅ Already Done)
Your `requirements.txt` now includes:
```
Flask==2.3.3
ytmusicapi==1.3.2
python-dotenv==1.0.0
yt-dlp==2023.10.13
requests==2.31.0
numpy==1.24.3
scikit-learn==1.3.0
gunicorn==21.2.0
flask-cors==4.0.0
```

### 1.2 Render Configuration (✅ Already Created)
The `render.yaml` file is configured for optimal deployment.

### 1.3 Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Step 2: Deploy to Render

### 2.1 Create Web Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository
4. Click **"Connect"** next to your SongHub repository

### 2.2 Configure Deployment Settings <mcreference link="https://medium.com/@acharyaaarush879/deploy-your-flask-app-on-render-c452a7406fb2" index="2">2</mcreference>

**Basic Settings:**
- **Name**: `songhub-music-app` (or your preferred name)
- **Language**: `Python 3`
- **Branch**: `main` (or your default branch)
- **Region**: Choose closest to your location

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT` <mcreference link="https://docs.render.com/deploy-flask" index="3">3</mcreference>

**Instance Type:**
- Select **"Free"** for testing (750 hours/month)
- Upgrade to **"Starter"** for production ($7/month)

### 2.3 Environment Variables <mcreference link="https://blog.teclado.com/how-to-deploy-flask-and-mongodb-to-render/" index="4">4</mcreference>
Add these in the **"Environment Variables"** section:

| Key | Value | Description |
|-----|-------|-------------|
| `PYTHON_VERSION` | `3.10.12` | Python version |
| `SECRET_KEY` | `[Generate Random]` | Flask secret key |
| `FLASK_ENV` | `production` | Environment mode |

### 2.4 Advanced Settings
- **Health Check Path**: `/health`
- **Auto-Deploy**: `Yes` (deploys on every push)

## Step 3: Deploy!

1. Click **"Create Web Service"**
2. Wait for build to complete (5-10 minutes)
3. Your app will be live at: `https://your-app-name.onrender.com`

## Step 4: Verify Deployment

### 4.1 Test Core Functionality
- ✅ Visit your app URL
- ✅ Test search: Try searching for "Taylor Swift"
- ✅ Test playback: Click play on any song
- ✅ Test playlists: Create and manage playlists
- ✅ Health check: Visit `/health` endpoint

### 4.2 Performance Check
```bash
# Test health endpoint
curl https://your-app-name.onrender.com/health

# Test search API
curl "https://your-app-name.onrender.com/search?q=test"
```

## Step 5: Production Optimizations

### 5.1 Enable Persistent Storage
Render automatically provides persistent storage for your pickle files:
- `playlists.pkl`
- `recently_played.pkl`
- `user_profiles.pkl`
- And other data files

### 5.2 Performance Tuning <mcreference link="https://medium.com/@hengkysandi/how-to-host-a-python-flask-app-on-render-for-free-0bfdfedd8ce7" index="5">5</mcreference>
For better performance, add these environment variables:

| Key | Value | Description |
|-----|-------|-------------|
| `WEB_CONCURRENCY` | `2` | Number of worker processes |
| `GUNICORN_WORKERS` | `2` | Gunicorn worker count |

### 5.3 Custom Domain (Optional)
1. Go to **Settings** → **Custom Domains**
2. Add your domain
3. Configure DNS records as shown

## Monitoring & Maintenance

### Health Monitoring
- **Health Check**: Automatic monitoring via `/health`
- **Logs**: View real-time logs in Render dashboard
- **Metrics**: Monitor CPU, memory, and response times

### Automatic Updates
- **Auto-Deploy**: Enabled by default
- **Zero-Downtime**: Render handles deployments gracefully
- **Rollback**: Easy rollback to previous versions

## Troubleshooting

### Common Issues

**Build Failures:**
```bash
# Check logs in Render dashboard
# Ensure all dependencies are in requirements.txt
# Verify Python version compatibility
```

**App Won't Start:**
```bash
# Verify start command: gunicorn app:app --bind 0.0.0.0:$PORT
# Check for import errors in logs
# Ensure Flask app is named 'app' in app.py
```

**Performance Issues:**
- Monitor memory usage (512MB limit on free tier)
- Check for infinite loops or blocking operations
- Consider upgrading to paid plan for more resources

**File Persistence Issues:**
- Render provides persistent storage automatically
- Check file paths are relative to app directory
- Verify pickle files are being created/loaded correctly

### Getting Help
- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Community**: [community.render.com](https://community.render.com)
- **Support**: Available for paid plans

## Free Tier Limitations

- **Memory**: 512MB RAM
- **CPU**: Shared CPU
- **Sleep**: Apps sleep after 15 minutes of inactivity
- **Build Time**: 10 minutes max
- **Bandwidth**: Generous but not unlimited

## Upgrade Benefits

**Starter Plan ($7/month):**
- 1GB RAM
- Dedicated CPU
- No sleep
- Priority support
- Custom domains with SSL

## Security Best Practices

✅ **HTTPS**: Automatic SSL certificates  
✅ **Environment Variables**: Secure secret storage  
✅ **No Hardcoded Secrets**: All sensitive data in env vars  
✅ **Regular Updates**: Keep dependencies updated  

## Next Steps

1. **Custom Domain**: Add your own domain
2. **Database**: Consider PostgreSQL for better data management
3. **Caching**: Add Redis for improved performance
4. **Monitoring**: Set up error tracking and analytics
5. **CI/CD**: Implement automated testing

---

🎵 **Your SongHub app is now live on Render!**

Share your music streaming app with the world and enjoy the seamless deployment experience that Render provides.

**Live URL**: `https://your-app-name.onrender.com`