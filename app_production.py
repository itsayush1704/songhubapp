from flask import Flask, render_template, request, jsonify, session, send_file
from flask_cors import CORS
from ytmusicapi import YTMusic
import os
from dotenv import load_dotenv
import yt_dlp
import json
from datetime import datetime
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict, Counter
import hashlib
import time
import logging

# Load environment variables
load_dotenv()

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Production configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['DEBUG'] = False  # Set to False for production
app.config['TESTING'] = False

# Configure CORS for production
CORS(app, origins=['https://chatgptnci.pythonanywhere.com'])  # Replace with your domain

# Initialize YouTube Music API with error handling
try:
    ytmusic = YTMusic()
    logger.info("YouTube Music API initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize YouTube Music API: {e}")
    ytmusic = None

# Data storage - same as original app.py
playlists = {}
recently_played = []
user_profiles = {}
song_features = {}
user_listening_history = defaultdict(list)
user_genre_preferences = defaultdict(Counter)
user_artist_preferences = defaultdict(Counter)

# Data persistence functions with better error handling
def load_saved_data():
    """Load saved data with improved error handling for production"""
    global playlists, recently_played, user_profiles, song_features
    global user_listening_history, user_genre_preferences, user_artist_preferences
    
    data_files = {
        'playlists.pkl': 'playlists',
        'recently_played.pkl': 'recently_played',
        'user_profiles.pkl': 'user_profiles',
        'song_features.pkl': 'song_features',
        'user_listening_history.pkl': 'user_listening_history',
        'user_genre_preferences.pkl': 'user_genre_preferences',
        'user_artist_preferences.pkl': 'user_artist_preferences'
    }
    
    for filename, var_name in data_files.items():
        try:
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    data = pickle.load(f)
                    globals()[var_name] = data
                logger.info(f"Loaded {filename} successfully")
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            # Initialize with default values if loading fails
            if var_name in ['user_listening_history', 'user_genre_preferences', 'user_artist_preferences']:
                globals()[var_name] = defaultdict(list if var_name == 'user_listening_history' else Counter)
            else:
                globals()[var_name] = {} if var_name != 'recently_played' else []

def save_data():
    """Save data with improved error handling for production"""
    data_to_save = {
        'playlists.pkl': playlists,
        'recently_played.pkl': recently_played,
        'user_profiles.pkl': user_profiles,
        'song_features.pkl': song_features,
        'user_listening_history.pkl': dict(user_listening_history),
        'user_genre_preferences.pkl': dict(user_genre_preferences),
        'user_artist_preferences.pkl': dict(user_artist_preferences)
    }
    
    for filename, data in data_to_save.items():
        try:
            with open(filename, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"Saved {filename} successfully")
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")

# Error handler for production
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error. Please try again later.'
    }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Resource not found'
    }), 404

# Health check endpoint for monitoring
@app.route('/health')
def health_check():
    """Enhanced health check for production monitoring"""
    try:
        # Test YouTube Music API
        api_status = 'healthy' if ytmusic else 'unavailable'
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'api_status': api_status,
            'environment': 'production'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# Main route
@app.route('/')
def index():
    """Main application route"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return "Application temporarily unavailable", 500

# API endpoint with rate limiting consideration
@app.route('/search')
def search():
    """Search endpoint with enhanced error handling"""
    if not ytmusic:
        return jsonify({
            'status': 'error',
            'message': 'Music service temporarily unavailable'
        }), 503
    
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({
            'status': 'error',
            'message': 'Query parameter is required'
        }), 400
    
    try:
        # Implement basic rate limiting
        user_id = session.get('user_id', 'anonymous')
        current_time = time.time()
        
        # Simple in-memory rate limiting (consider Redis for production)
        if not hasattr(app, 'rate_limit_store'):
            app.rate_limit_store = {}
        
        if user_id in app.rate_limit_store:
            last_request = app.rate_limit_store[user_id]
            if current_time - last_request < 1:  # 1 second between requests
                return jsonify({
                    'status': 'error',
                    'message': 'Rate limit exceeded. Please wait before making another request.'
                }), 429
        
        app.rate_limit_store[user_id] = current_time
        
        # Perform search
        results = ytmusic.search(query, limit=20)
        
        # Process results
        processed_results = {
            'songs': [],
            'albums': [],
            'artists': [],
            'playlists': []
        }
        
        for item in results:
            result_type = item.get('resultType', '').lower()
            if result_type == 'song':
                processed_results['songs'].append(item)
            elif result_type == 'album':
                processed_results['albums'].append(item)
            elif result_type == 'artist':
                processed_results['artists'].append(item)
            elif result_type == 'playlist':
                processed_results['playlists'].append(item)
        
        return jsonify({
            'status': 'success',
            'results': processed_results,
            'query': query
        })
        
    except Exception as e:
        logger.error(f"Search error for query '{query}': {e}")
        return jsonify({
            'status': 'error',
            'message': 'Search service temporarily unavailable'
        }), 503

# Initialize data on startup
try:
    load_saved_data()
    logger.info("Application initialized successfully")
except Exception as e:
    logger.error(f"Error during initialization: {e}")

# Production WSGI application
if __name__ == '__main__':
    # This should not run in production, but kept for local testing
    app.run(debug=False, host='0.0.0.0', port=8009)
else:
    # Production configuration
    logger.info("Starting SongHub in production mode")