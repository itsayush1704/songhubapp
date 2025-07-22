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

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)  # Enable CORS for all routes

# Initialize YouTube Music API
ytmusic = YTMusic()

# In-memory storage for playlists (in a real app, use a database)
playlists = {}
# In-memory storage for recently played songs with timestamps
recently_played = []
# User profiles for personalized recommendations
user_profiles = {}
# Song features for ML-based recommendations
song_features = {}
# User listening history for collaborative filtering
user_listening_history = defaultdict(list)
# Genre preferences
user_genre_preferences = defaultdict(Counter)
# Artist preferences
user_artist_preferences = defaultdict(Counter)

# Load saved data if exists
def load_saved_data():
    global playlists, recently_played, user_profiles, song_features, user_listening_history, user_genre_preferences, user_artist_preferences
    try:
        if os.path.exists('playlists.pkl'):
            with open('playlists.pkl', 'rb') as f:
                playlists = pickle.load(f)
        if os.path.exists('recently_played.pkl'):
            with open('recently_played.pkl', 'rb') as f:
                recently_played = pickle.load(f)
        if os.path.exists('user_profiles.pkl'):
            with open('user_profiles.pkl', 'rb') as f:
                user_profiles = pickle.load(f)
        if os.path.exists('song_features.pkl'):
            with open('song_features.pkl', 'rb') as f:
                song_features = pickle.load(f)
        if os.path.exists('user_listening_history.pkl'):
            with open('user_listening_history.pkl', 'rb') as f:
                user_listening_history = pickle.load(f)
        if os.path.exists('user_genre_preferences.pkl'):
            with open('user_genre_preferences.pkl', 'rb') as f:
                user_genre_preferences = pickle.load(f)
        if os.path.exists('user_artist_preferences.pkl'):
            with open('user_artist_preferences.pkl', 'rb') as f:
                user_artist_preferences = pickle.load(f)
    except Exception as e:
        print(f"Error loading saved data: {e}")
    
    # Load search history
    load_search_history()

# Save data to files
def save_data():
    try:
        with open('playlists.pkl', 'wb') as f:
            pickle.dump(playlists, f)
        with open('recently_played.pkl', 'wb') as f:
            pickle.dump(recently_played, f)
        with open('user_profiles.pkl', 'wb') as f:
            pickle.dump(user_profiles, f)
        with open('song_features.pkl', 'wb') as f:
            pickle.dump(song_features, f)
        with open('user_listening_history.pkl', 'wb') as f:
            pickle.dump(dict(user_listening_history), f)
        with open('user_genre_preferences.pkl', 'wb') as f:
            pickle.dump(dict(user_genre_preferences), f)
        with open('user_artist_preferences.pkl', 'wb') as f:
            pickle.dump(dict(user_artist_preferences), f)
    except Exception as e:
        print(f"Error saving data: {e}")

# Helper functions for recommendation system
def get_user_id():
    """Generate or get user ID from session"""
    if 'user_id' not in session:
        session['user_id'] = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    return session['user_id']

def extract_song_features(song):
    """Extract features from a song for ML recommendations"""
    # Safely extract artist name
    artist_name = ''
    if song.get('artists') and len(song['artists']) > 0:
        first_artist = song['artists'][0]
        if isinstance(first_artist, dict):
            artist_name = first_artist.get('name', '')
    
    features = {
        'title': song.get('title', ''),
        'artist': artist_name,
        'duration': song.get('duration_seconds', 0),
        'year': song.get('year', 0)
    }
    return features

def update_user_preferences(user_id, song):
    """Update user preferences based on played song"""
    # Safely extract artist name
    artist_name = ''
    if song.get('artists') and len(song['artists']) > 0:
        first_artist = song['artists'][0]
        if isinstance(first_artist, dict):
            artist_name = first_artist.get('name', '')
            user_artist_preferences[user_id][artist_name] += 1
    
    # Add to listening history
    user_listening_history[user_id].append({
        'videoId': song.get('videoId'),
        'title': song.get('title'),
        'artist': artist_name,
        'timestamp': datetime.now().isoformat()
    })
    
    # Keep only last 100 songs in history
    user_listening_history[user_id] = user_listening_history[user_id][-100:]

def get_content_based_recommendations(user_id, limit=10):
    """Get recommendations based on content similarity"""
    if user_id not in user_listening_history or not user_listening_history[user_id]:
        return []
    
    # Get user's recent songs
    recent_songs = user_listening_history[user_id][-10:]
    
    # Create feature vectors for content-based filtering
    user_artists = [song['artist'] for song in recent_songs if song.get('artist')]
    
    try:
        # Get similar songs from YouTube Music
        recommendations = []
        for artist in set(user_artists[-3:]):  # Use last 3 unique artists
            try:
                search_results = ytmusic.search(f"artist:{artist}", filter='songs', limit=5)
                for song in search_results:
                    if song.get('videoId') not in [s['videoId'] for s in recent_songs]:
                        recommendations.append(song)
            except:
                continue
        
        return recommendations[:limit]
    except Exception as e:
        print(f"Error in content-based recommendations: {e}")
        return []

def get_collaborative_recommendations(user_id, limit=10):
    """Get recommendations based on collaborative filtering"""
    if user_id not in user_listening_history:
        return []
    
    user_songs = set(song['videoId'] for song in user_listening_history[user_id])
    
    # Find similar users
    similar_users = []
    for other_user_id, other_history in user_listening_history.items():
        if other_user_id != user_id and other_history:
            other_songs = set(song['videoId'] for song in other_history)
            # Calculate Jaccard similarity
            intersection = len(user_songs.intersection(other_songs))
            union = len(user_songs.union(other_songs))
            if union > 0:
                similarity = intersection / union
                if similarity > 0.1:  # Threshold for similarity
                    similar_users.append((other_user_id, similarity))
    
    # Get recommendations from similar users
    recommendations = []
    similar_users.sort(key=lambda x: x[1], reverse=True)
    
    for similar_user_id, _ in similar_users[:5]:  # Top 5 similar users
        for song in user_listening_history[similar_user_id][-10:]:
            if song['videoId'] not in user_songs:
                recommendations.append(song)
    
    return recommendations[:limit]

def get_trending_recommendations(limit=10):
    """Get trending songs as recommendations using alternative methods"""
    try:
        # Try to get trending songs from home page instead of charts
        home = ytmusic.get_home()
        trending_songs = []
        
        if isinstance(home, list):
            for shelf in home:
                if isinstance(shelf, dict):
                    shelf_title = shelf.get('title', '').lower()
                    # Look for trending/popular content shelves
                    if any(keyword in shelf_title for keyword in ['trending', 'popular', 'hot', 'top', 'chart']):
                        contents = shelf.get('contents', [])
                        for item in contents:
                            if isinstance(item, dict) and item.get('videoId'):
                                trending_songs.append({
                                    'videoId': item.get('videoId'),
                                    'title': item.get('title'),
                                    'artists': item.get('artists', []),
                                    'thumbnails': item.get('thumbnails', []),
                                    'album': item.get('album', {}).get('name') if item.get('album') else None,
                                    'views': item.get('views'),
                                    'duration': item.get('duration')
                                })
                                if len(trending_songs) >= limit:
                                    break
                    if len(trending_songs) >= limit:
                        break
        
        if trending_songs:
            return trending_songs[:limit]
        
        # If no trending found, try searching for popular songs
        popular_searches = ['top songs 2024', 'popular music', 'trending songs']
        for search_term in popular_searches:
            try:
                search_results = ytmusic.search(search_term, filter='songs', limit=limit)
                if search_results:
                    return search_results[:limit]
            except:
                continue
                
        # Final fallback
        raise Exception("No trending data available")
        
    except Exception as e:
        print(f"Charts API failed, using fallback trending data: {str(e)}")
        # Fallback: return some popular songs as mock trending data
        fallback_trending = [
            {
                'videoId': 'dQw4w9WgXcQ',
                'title': 'Never Gonna Give You Up',
                'artists': [{'name': 'Rick Astley'}],
                'thumbnails': [{'url': 'https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'}],
                'duration': '3:33'
            },
            {
                'videoId': 'L_jWHffIx5E',
                'title': 'Smells Like Teen Spirit',
                'artists': [{'name': 'Nirvana'}],
                'thumbnails': [{'url': 'https://i.ytimg.com/vi/L_jWHffIx5E/maxresdefault.jpg'}],
                'duration': '5:01'
            },
            {
                'videoId': 'fJ9rUzIMcZQ',
                'title': 'Bohemian Rhapsody',
                'artists': [{'name': 'Queen'}],
                'thumbnails': [{'url': 'https://i.ytimg.com/vi/fJ9rUzIMcZQ/maxresdefault.jpg'}],
                'duration': '5:55'
            },
            {
                'videoId': 'kJQP7kiw5Fk',
                'title': 'Despacito',
                'artists': [{'name': 'Luis Fonsi'}, {'name': 'Daddy Yankee'}],
                'thumbnails': [{'url': 'https://i.ytimg.com/vi/kJQP7kiw5Fk/maxresdefault.jpg'}],
                'duration': '4:42'
            },
            {
                'videoId': '9bZkp7q19f0',
                'title': 'Gangnam Style',
                'artists': [{'name': 'PSY'}],
                'thumbnails': [{'url': 'https://i.ytimg.com/vi/9bZkp7q19f0/maxresdefault.jpg'}],
                'duration': '4:12'
            }
        ]
        return fallback_trending[:limit]

def get_quick_picks(auth_file=None):
    """
    Fetches the 'Quick picks' row from YouTube Music home page using ytmusicapi.

    :param auth_file: Path to your headers_auth.json file for authenticated requests (optional).
    :return: List of quick pick items (dicts), or None if not found.
    """
    try:
        # Initialize YTMusic with or without authentication
        ytmusic_instance = YTMusic(auth_file) if auth_file else ytmusic
        home_rows = ytmusic_instance.get_home()
        for row in home_rows:
            if row.get('title', '').lower() == 'quick picks':
                return row.get('contents', [])
        return None
    except Exception as e:
        print(f"Error fetching quick picks: {e}")
        return None

# Search history storage
search_history = []

def save_search_history(query):
    """Save search query to history"""
    global search_history
    if query and query not in search_history:
        search_history.insert(0, query)
        # Keep only last 50 searches
        search_history = search_history[:50]
        # Save to file
        try:
            with open('search_history.pkl', 'wb') as f:
                pickle.dump(search_history, f)
        except Exception as e:
            print(f"Error saving search history: {e}")

def load_search_history():
    """Load search history from file"""
    global search_history
    try:
        if os.path.exists('search_history.pkl'):
            with open('search_history.pkl', 'rb') as f:
                search_history = pickle.load(f)
    except Exception as e:
        print(f"Error loading search history: {e}")
        search_history = []

# Load saved data on startup
load_saved_data()

@app.route('/')
def index():
    return render_template('index.html')

def search_songs(query, limit=20):
    """Search for songs only"""
    try:
        results = ytmusic.search(query, filter='songs', limit=limit)
        return parse_song_results(results)
    except Exception as e:
        print(f"Error searching songs: {e}")
        return []

def search_albums(query, limit=20):
    """Search for albums only"""
    try:
        results = ytmusic.search(query, filter='albums', limit=limit)
        return parse_album_results(results)
    except Exception as e:
        print(f"Error searching albums: {e}")
        return []

def search_artists(query, limit=20):
    """Search for artists only"""
    try:
        results = ytmusic.search(query, filter='artists', limit=limit)
        return parse_artist_results(results)
    except Exception as e:
        print(f"Error searching artists: {e}")
        return []

def search_playlists(query, limit=20):
    """Search for playlists only"""
    try:
        results = ytmusic.search(query, filter='playlists', limit=limit)
        return parse_playlist_results(results)
    except Exception as e:
        print(f"Error searching playlists: {e}")
        return []

def search_videos(query, limit=20):
    """Search for videos only"""
    try:
        results = ytmusic.search(query, filter='videos', limit=limit)
        return parse_video_results(results)
    except Exception as e:
        print(f"Error searching videos: {e}")
        return []

def search_all(query, limit=10):
    """Search all content types"""
    try:
        songs = search_songs(query, limit)
        albums = search_albums(query, limit)
        artists = search_artists(query, limit)
        playlists = search_playlists(query, limit)
        videos = search_videos(query, limit)
        
        return {
            'songs': songs,
            'albums': albums,
            'artists': artists,
            'playlists': playlists,
            'videos': videos
        }
    except Exception as e:
        print(f"Error in search_all: {e}")
        return {
            'songs': [],
            'albums': [],
            'artists': [],
            'playlists': [],
            'videos': []
        }

def parse_song_results(results):
    """Parse song search results into consistent format"""
    parsed = []
    for item in results:
        parsed.append({
            'type': 'song',
            'videoId': item.get('videoId'),
            'title': item.get('title'),
            'artists': item.get('artists', []),
            'album': item.get('album', {}).get('name') if item.get('album') else None,
            'duration': item.get('duration'),
            'thumbnails': item.get('thumbnails', []),
            'isExplicit': item.get('isExplicit', False),
            'year': item.get('year')
        })
    return parsed

def parse_album_results(results):
    """Parse album search results into consistent format"""
    parsed = []
    for item in results:
        parsed.append({
            'type': 'album',
            'browseId': item.get('browseId'),
            'title': item.get('title'),
            'artists': item.get('artists', []),
            'year': item.get('year'),
            'thumbnails': item.get('thumbnails', []),
            'isExplicit': item.get('isExplicit', False)
        })
    return parsed

def parse_artist_results(results):
    """Parse artist search results into consistent format"""
    parsed = []
    for item in results:
        parsed.append({
            'type': 'artist',
            'browseId': item.get('browseId'),
            'artist': item.get('artist'),
            'thumbnails': item.get('thumbnails', []),
            'subscribers': item.get('subscribers')
        })
    return parsed

def parse_playlist_results(results):
    """Parse playlist search results into consistent format"""
    parsed = []
    for item in results:
        parsed.append({
            'type': 'playlist',
            'browseId': item.get('browseId'),
            'title': item.get('title'),
            'author': item.get('author'),
            'itemCount': item.get('itemCount'),
            'thumbnails': item.get('thumbnails', [])
        })
    return parsed

def parse_video_results(results):
    """Parse video search results into consistent format"""
    parsed = []
    for item in results:
        parsed.append({
            'type': 'video',
            'videoId': item.get('videoId'),
            'title': item.get('title'),
            'artists': item.get('artists', []),
            'duration': item.get('duration'),
            'thumbnails': item.get('thumbnails', []),
            'views': item.get('views')
        })
    return parsed

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Enhanced search endpoint with multiple search types"""
    if request.method == 'GET':
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'all')
    else:
        data = request.get_json() or {}
        query = data.get('query', '')
        search_type = data.get('type', 'all')
    
    print(f"Search query received: {query}, type: {search_type}")
    
    if not query:
        return jsonify({
            'status': 'error',
            'message': 'Query parameter is required'
        }), 400
    
    # Save to search history
    save_search_history(query)
    
    try:
        # Dispatch to appropriate search function
        if search_type == 'songs':
            results = search_songs(query)
        elif search_type == 'albums':
            results = search_albums(query)
        elif search_type == 'artists':
            results = search_artists(query)
        elif search_type == 'playlists':
            results = search_playlists(query)
        elif search_type == 'videos':
            results = search_videos(query)
        else:
            results = search_all(query)
        
        print(f"Search results count: {len(results) if isinstance(results, list) else sum(len(v) for v in results.values())}")
        
        return jsonify({
            'status': 'success',
            'results': results,
            'query': query,
            'search_type': search_type
        })
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/search/history', methods=['GET'])
def get_search_history():
    """Get search history"""
    return jsonify({
        'status': 'success',
        'history': search_history
    })

@app.route('/search/suggestions', methods=['GET'])
def get_search_suggestions():
    """Get search suggestions based on query"""
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify({
            'status': 'success',
            'suggestions': []
        })
    
    try:
        # Get suggestions from YouTube Music
        suggestions = ytmusic.get_search_suggestions(query)
        return jsonify({
            'status': 'success',
            'suggestions': suggestions[:10]  # Limit to 10 suggestions
        })
    except Exception as e:
        print(f"Error getting search suggestions: {e}")
        # Fallback to search history
        history_suggestions = [h for h in search_history if query.lower() in h.lower()][:5]
        return jsonify({
            'status': 'success',
            'suggestions': history_suggestions
        })

def get_youtube_stream_url(video_id, audio_only=True, preferred_quality='bestaudio'):
    """
    Get streaming URL for a YouTube video using yt-dlp
    """
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestaudio[ext=m4a]/bestaudio' if audio_only else 'best[ext=mp4]/best'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info and 'url' in info:
                return {
                    'status': 'success',
                    'stream_url': info['url'],
                    'format_info': {
                        'format_id': info.get('format_id', 'unknown'),
                        'ext': info.get('ext', 'unknown'),
                        'acodec': info.get('acodec', 'unknown'),
                        'abr': info.get('abr', 0),
                        'asr': info.get('asr', 0),
                        'filesize': info.get('filesize'),
                        'quality': info.get('quality', 'unknown')
                    },
                    'video_info': {
                        'title': info.get('title', 'Unknown'),
                        'duration': info.get('duration', 0),
                        'uploader': info.get('uploader', 'Unknown'),
                        'view_count': info.get('view_count', 0)
                    }
                }
            
            # Try formats if direct URL not available
            formats = info.get('formats', []) if info else []
            for fmt in formats:
                if 'url' in fmt:
                    return {
                        'status': 'success',
                        'stream_url': fmt['url'],
                        'format_info': {
                            'format_id': fmt.get('format_id', 'unknown'),
                            'ext': fmt.get('ext', 'unknown'),
                            'acodec': fmt.get('acodec', 'unknown'),
                            'abr': fmt.get('abr', 0),
                            'asr': fmt.get('asr', 0),
                            'filesize': fmt.get('filesize'),
                            'quality': fmt.get('quality', 'unknown')
                        },
                        'video_info': {
                            'title': info.get('title', 'Unknown') if info else 'Unknown',
                            'duration': info.get('duration', 0) if info else 0,
                            'uploader': info.get('uploader', 'Unknown') if info else 'Unknown',
                            'view_count': info.get('view_count', 0) if info else 0
                        }
                    }
            
            return {'status': 'error', 'message': 'No stream URL found'}
            
    except Exception as e:
        return {'status': 'error', 'message': f'Error: {str(e)}'}

@app.route('/get_stream_url/<video_id>')
def get_stream_url(video_id):
    """API endpoint to get stream URL for a video"""
    try:
        audio_only = request.args.get('audio_only', 'true').lower() == 'true'
        
        # Use the working yt-dlp implementation
        result = get_youtube_stream_url(video_id, audio_only)
        
        if result['status'] == 'success':
            return jsonify(result)
        else:
            # If yt-dlp fails, fallback to direct YouTube URL
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            return jsonify({
                'status': 'success',
                'stream_url': youtube_url,
                'video_info': {
                    'title': 'YouTube Video',
                    'duration': 0,
                    'uploader': 'YouTube',
                    'view_count': 0
                },
                'note': 'Fallback to direct YouTube URL',
                'original_error': result.get('message', 'Unknown error')
            })
        
    except Exception as e:
        # Final fallback
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        return jsonify({
            'status': 'success',
            'stream_url': youtube_url,
            'video_info': {
                'title': 'YouTube Video',
                'duration': 0,
                'uploader': 'YouTube',
                'view_count': 0
            },
            'note': 'Emergency fallback to direct YouTube URL',
            'server_error': str(e)
        })

@app.route('/get_formats/<video_id>')
def get_available_formats(video_id):
    """Get all available formats for a YouTube video (similar to SimpMusic format selection)"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'extract_flat': False,
            'youtube_include_dash_manifest': True,
            'youtube_include_hls_manifest': True,
        }
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({'status': 'error', 'message': 'No video information found'}), 404
            
            formats = info.get('formats', [])
            
            # Categorize formats
            audio_formats = []
            video_formats = []
            combined_formats = []
            
            for fmt in formats:
                format_info = {
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'url': fmt.get('url'),
                    'filesize': fmt.get('filesize'),
                    'quality': fmt.get('quality'),
                    'tbr': fmt.get('tbr'),
                    'protocol': fmt.get('protocol')
                }
                
                # Audio-only formats
                if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                    format_info.update({
                        'acodec': fmt.get('acodec'),
                        'abr': fmt.get('abr'),
                        'asr': fmt.get('asr')
                    })
                    audio_formats.append(format_info)
                
                # Video-only formats
                elif fmt.get('vcodec') != 'none' and fmt.get('acodec') == 'none':
                    format_info.update({
                        'vcodec': fmt.get('vcodec'),
                        'width': fmt.get('width'),
                        'height': fmt.get('height'),
                        'fps': fmt.get('fps'),
                        'vbr': fmt.get('vbr')
                    })
                    video_formats.append(format_info)
                
                # Combined audio+video formats
                elif fmt.get('acodec') != 'none' and fmt.get('vcodec') != 'none':
                    format_info.update({
                        'acodec': fmt.get('acodec'),
                        'vcodec': fmt.get('vcodec'),
                        'abr': fmt.get('abr'),
                        'vbr': fmt.get('vbr'),
                        'width': fmt.get('width'),
                        'height': fmt.get('height'),
                        'fps': fmt.get('fps'),
                        'asr': fmt.get('asr')
                    })
                    combined_formats.append(format_info)
            
            # Sort formats by quality
            audio_formats.sort(key=lambda x: x.get('abr', 0) or x.get('tbr', 0) or 0, reverse=True)
            video_formats.sort(key=lambda x: (x.get('height', 0), x.get('vbr', 0) or x.get('tbr', 0) or 0), reverse=True)
            combined_formats.sort(key=lambda x: (x.get('height', 0), x.get('tbr', 0) or 0), reverse=True)
            
            return jsonify({
                'status': 'success',
                'video_info': {
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'view_count': info.get('view_count'),
                    'description': info.get('description', '')[:500] + '...' if info.get('description') and len(info.get('description', '')) > 500 else info.get('description', '')
                },
                'formats': {
                    'audio_only': audio_formats,
                    'video_only': video_formats,
                    'combined': combined_formats
                },
                'recommended': {
                    'best_audio': audio_formats[0] if audio_formats else None,
                    'best_video': video_formats[0] if video_formats else None,
                    'best_combined': combined_formats[0] if combined_formats else None
                }
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error getting formats: {str(e)}'
        }), 500

@app.route('/stream/<video_id>/<format_id>')
def get_specific_format_stream(video_id, format_id):
    """Get stream URL for a specific format ID"""
    try:
        ydl_opts = {
            'format': format_id,
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'extract_flat': False,
        }
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({'status': 'error', 'message': 'No video information found'}), 404
            
            return jsonify({
                'status': 'success',
                'stream_url': info.get('url'),
                'format_info': {
                    'format_id': info.get('format_id'),
                    'ext': info.get('ext'),
                    'filesize': info.get('filesize'),
                    'quality': info.get('quality')
                }
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error getting specific format: {str(e)}'
        }), 500

@app.route('/play_event', methods=['POST'])
def play_event():
    song = request.json
    user_id = get_user_id()
    
    # Add timestamp to the song data
    song['timestamp'] = datetime.now().isoformat()
    
    # Update user preferences for ML recommendations
    update_user_preferences(user_id, song)
    
    # Avoid duplicates, keep only last 20
    global recently_played
    recently_played = [s for s in recently_played if s.get('videoId') != song.get('videoId')]
    recently_played.insert(0, song)
    recently_played = recently_played[:20]
    
    # Save data after updating
    save_data()
    return jsonify({'status': 'success'})

@app.route('/recently_played')
def get_recently_played():
    # Sort by timestamp if available
    sorted_recent = sorted(recently_played, 
                         key=lambda x: x.get('timestamp', ''), 
                         reverse=True)
    return jsonify({'status': 'success', 'recently_played': sorted_recent})

@app.route('/recommendations')
def get_recommendations():
    try:
        user_id = get_user_id()
        
        # Get different types of recommendations
        content_based = get_content_based_recommendations(user_id, limit=15)
        collaborative = get_collaborative_recommendations(user_id, limit=10)
        trending = get_trending_recommendations(limit=15)
        
        # Get recommendations based on recently played songs
        recent_recommendations = []
        if recently_played and len(recently_played) > 0:
            recent_song = recently_played[0]
            if isinstance(recent_song, dict) and 'videoId' in recent_song:
                try:
                    watch_playlist = ytmusic.get_watch_playlist(recent_song['videoId'])
                    if isinstance(watch_playlist, dict) and 'tracks' in watch_playlist:
                        recent_recommendations = watch_playlist['tracks'][:5]
                except Exception as e:
                    print(f"Error getting watch playlist: {e}")

        # Get Quick Picks recommendations
        quick_picks = get_quick_picks()
        quick_picks_recommendations = []
        if quick_picks:
            for item in quick_picks[:10]:  # Limit to 10 quick picks
                if isinstance(item, dict) and item.get('videoId'):
                    quick_picks_recommendations.append(item)

        # Get recommendations from home page
        home_recommendations = []
        try:
            home = ytmusic.get_home()
            if isinstance(home, list):
                for shelf in home:
                    if isinstance(shelf, dict) and shelf.get('title') in ['Your favorites', 'Recommended for you', 'New releases']:
                        contents = shelf.get('contents', [])
                        if isinstance(contents, list):
                            for item in contents:
                                if isinstance(item, dict) and item.get('resultType') == 'song':
                                    home_recommendations.append(item)
        except Exception as e:
            print(f"Error getting home recommendations: {e}")

        # Combine and deduplicate recommendations with priority
        all_recommendations = []
        seen_video_ids = set()

        # Priority order: Quick Picks -> Content-based -> Recent -> Collaborative -> Home -> Trending
        recommendation_sources = [
            ('quick_picks', quick_picks_recommendations),
            ('content_based', content_based),
            ('recent', recent_recommendations),
            ('collaborative', collaborative),
            ('home', home_recommendations[:5]),
            ('trending', trending)
        ]

        for source_name, recommendations in recommendation_sources:
            for rec in recommendations:
                if isinstance(rec, dict) and 'videoId' in rec and rec['videoId'] not in seen_video_ids:
                    rec['recommendation_source'] = source_name
                    all_recommendations.append(rec)
                    seen_video_ids.add(rec['videoId'])
                    if len(all_recommendations) >= 40:  # Limit total recommendations
                        break
            if len(all_recommendations) >= 40:
                break

        # If we don't have enough personalized recommendations, add more trending
        if len(all_recommendations) < 30:
            try:
                additional_trending = get_trending_recommendations(limit=40)
                for rec in additional_trending:
                    if isinstance(rec, dict) and 'videoId' in rec and rec['videoId'] not in seen_video_ids:
                        rec['recommendation_source'] = 'trending_fallback'
                        all_recommendations.append(rec)
                        seen_video_ids.add(rec['videoId'])
                        if len(all_recommendations) >= 30:
                            break
            except Exception as e:
                print(f"Error getting additional trending: {e}")

        return jsonify({
            'status': 'success',
            'recommendations': all_recommendations[:20],
            'user_id': user_id,
            'personalization_level': 'high' if len(content_based) > 0 or len(collaborative) > 0 else 'low',
            'recommendation_breakdown': {
                'quick_picks': len([r for r in all_recommendations if r.get('recommendation_source') == 'quick_picks']),
                'content_based': len([r for r in all_recommendations if r.get('recommendation_source') == 'content_based']),
                'collaborative': len([r for r in all_recommendations if r.get('recommendation_source') == 'collaborative']),
                'trending': len([r for r in all_recommendations if r.get('recommendation_source') in ['trending', 'trending_fallback']]),
                'recent': len([r for r in all_recommendations if r.get('recommendation_source') == 'recent']),
                'home': len([r for r in all_recommendations if r.get('recommendation_source') == 'home'])
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/quick_picks')
def get_quick_picks_endpoint():
    """Endpoint to get Quick Picks from YouTube Music home page"""
    try:
        quick_picks = get_quick_picks()
        if quick_picks:
            # Format the data consistently
            formatted_picks = []
            for item in quick_picks:
                if isinstance(item, dict) and item.get('videoId'):
                    formatted_picks.append({
                        'videoId': item.get('videoId'),
                        'title': item.get('title'),
                        'artists': item.get('artists', []),
                        'thumbnails': item.get('thumbnails', []),
                        'album': item.get('album', {}).get('name') if item.get('album') else None,
                        'duration': item.get('duration'),
                        'views': item.get('views')
                    })
            return jsonify({
                'status': 'success',
                'quick_picks': formatted_picks
            })
        else:
            return jsonify({
                'status': 'success',
                'quick_picks': [],
                'message': 'No Quick Picks found on home page'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/top_charts')
def top_charts():
    """Get top charts from YouTube Music using alternative methods"""
    try:
        # Try to get trending content from home page instead of charts API
        home = ytmusic.get_home()
        chart_songs = []
        
        if isinstance(home, list):
            for shelf in home:
                if isinstance(shelf, dict):
                    shelf_title = shelf.get('title', '').lower()
                    # Look for trending/chart content shelves
                    if any(keyword in shelf_title for keyword in ['trending', 'popular', 'hot', 'top', 'chart']):
                        contents = shelf.get('contents', [])
                        for item in contents:
                            if isinstance(item, dict) and item.get('videoId'):
                                # Safely extract artist names
                                artists = []
                                if item.get('artists'):
                                    for artist in item.get('artists', []):
                                        if isinstance(artist, dict) and artist.get('name'):
                                            artists.append(artist['name'])
                                if not artists:
                                    artists = ['Unknown Artist']
                                
                                chart_songs.append({
                                    'title': item.get('title'),
                                    'videoId': item.get('videoId'),
                                    'artists': artists,
                                    'thumbnails': item.get('thumbnails', []),
                                    'album': item.get('album', {}).get('name') if item.get('album') else None,
                                    'views': item.get('views'),
                                    'duration': item.get('duration')
                                })
                                if len(chart_songs) >= 20:  # Limit to 20 songs
                                    break
                        if len(chart_songs) >= 20:
                            break
        
        # If we found chart songs from home page, return them
        if chart_songs:
            return jsonify({'status': 'success', 'top_charts': chart_songs})
        
        # If no chart data found, try searching for popular songs
        popular_searches = ['top songs 2024', 'popular music', 'trending songs']
        for search_term in popular_searches:
            try:
                search_results = ytmusic.search(search_term, filter='songs', limit=15)
                if search_results:
                    for item in search_results:
                        # Safely extract artist names
                        artists = []
                        if item.get('artists'):
                            for artist in item.get('artists', []):
                                if isinstance(artist, dict) and artist.get('name'):
                                    artists.append(artist['name'])
                        if not artists:
                            artists = ['Unknown Artist']
                        
                        chart_songs.append({
                            'title': item.get('title'),
                            'videoId': item.get('videoId'),
                            'artists': artists,
                            'thumbnails': item.get('thumbnails', []),
                            'album': item.get('album', {}).get('name') if item.get('album') else None,
                            'views': item.get('views'),
                            'duration': item.get('duration')
                        })
                    if chart_songs:
                        return jsonify({'status': 'success', 'top_charts': chart_songs[:20]})
            except:
                continue
                
        # Final fallback
        raise Exception("No chart data available")
        
    except Exception as e:
        print(f"Top charts API failed, using fallback data: {str(e)}")
        # Fallback: return curated trending songs
        fallback_charts = [
            {
                'title': 'Blinding Lights',
                'videoId': '4NRXx6U8ABQ',
                'artists': ['The Weeknd'],
                'thumbnails': [{'url': 'https://i.ytimg.com/vi/4NRXx6U8ABQ/maxresdefault.jpg'}],
                'album': 'After Hours',
                'views': '2.8B views',
                'duration': '3:20'
            },
            {
                'title': 'Shape of You',
                'videoId': 'JGwWNGJdvx8',
                'artists': ['Ed Sheeran'],
                'thumbnails': [{'url': 'https://i.ytimg.com/vi/JGwWNGJdvx8/maxresdefault.jpg'}],
                'album': '÷ (Divide)',
                'views': '5.7B views',
                'duration': '3:53'
            },
            {
                'title': 'Bad Habits',
                'videoId': 'orJSJGHjBLI',
                'artists': ['Ed Sheeran'],
                'thumbnails': [{'url': 'https://i.ytimg.com/vi/orJSJGHjBLI/maxresdefault.jpg'}],
                'album': '= (Equals)',
                'views': '1.2B views',
                'duration': '3:51'
            },
            {
                'title': 'As It Was',
                'videoId': 'H5v3kku4y6Q',
                'artists': ['Harry Styles'],
                'thumbnails': [{'url': 'https://i.ytimg.com/vi/H5v3kku4y6Q/maxresdefault.jpg'}],
                'album': "Harry's House",
                'views': '1.1B views',
                'duration': '2:47'
            },
            {
                'title': 'Anti-Hero',
                'videoId': 'b1kbLWvqugk',
                'artists': ['Taylor Swift'],
                'thumbnails': [{'url': 'https://i.ytimg.com/vi/b1kbLWvqugk/maxresdefault.jpg'}],
                'album': 'Midnights',
                'views': '890M views',
                'duration': '3:20'
            },
            {
                'title': 'Flowers',
                'videoId': 'G7KNmW9a75Y',
                'artists': ['Miley Cyrus'],
                'thumbnails': [{'url': 'https://i.ytimg.com/vi/G7KNmW9a75Y/maxresdefault.jpg'}],
                'album': 'Endless Summer Vacation',
                'views': '1.4B views',
                'duration': '3:20'
            },
            {
                'title': 'Unholy',
                'videoId': 'Uq9gPaIzbe8',
                'artists': ['Sam Smith', 'Kim Petras'],
                'thumbnails': [{'url': 'https://i.ytimg.com/vi/Uq9gPaIzbe8/maxresdefault.jpg'}],
                'album': 'Gloria',
                'views': '780M views',
                'duration': '2:36'
            },
            {
                'title': 'Calm Down',
                'videoId': 'WcIcVapfqXw',
                'artists': ['Rema', 'Selena Gomez'],
                'thumbnails': [{'url': 'https://i.ytimg.com/vi/WcIcVapfqXw/maxresdefault.jpg'}],
                'album': 'Rave & Roses',
                'views': '650M views',
                'duration': '3:59'
            }
        ]
        return jsonify({'status': 'success', 'top_charts': fallback_charts})

@app.route('/playlists', methods=['GET', 'POST'])
def handle_playlists():
    if request.method == 'POST':
        data = request.json
        playlist_name = data.get('name')
        playlist_id = str(len(playlists) + 1)
        playlists[playlist_id] = {
            'name': playlist_name,
            'songs': [],
            'created_at': datetime.now().isoformat()
        }
        # Save data after creating new playlist
        save_data()
        return jsonify({
            'status': 'success',
            'playlist_id': playlist_id
        })
    else:
        # Sort playlists by creation date
        sorted_playlists = dict(sorted(
            playlists.items(),
            key=lambda x: x[1].get('created_at', ''),
            reverse=True
        ))
        return jsonify({
            'status': 'success',
            'playlists': sorted_playlists
        })

@app.route('/playlists/<playlist_id>/songs', methods=['GET', 'POST', 'DELETE'])
def handle_playlist_songs(playlist_id):
    if playlist_id not in playlists:
        return jsonify({
            'status': 'error',
            'message': 'Playlist not found'
        }), 404

    if request.method == 'POST':
        song = request.json
        # Add timestamp when song is added to playlist
        song['added_at'] = datetime.now().isoformat()
        playlists[playlist_id]['songs'].append(song)
        # Save data after adding song
        save_data()
        return jsonify({
            'status': 'success',
            'message': 'Song added to playlist'
        })
    elif request.method == 'DELETE':
        song_id = request.json.get('videoId')
        playlists[playlist_id]['songs'] = [
            song for song in playlists[playlist_id]['songs']
            if song['videoId'] != song_id
        ]
        # Save data after removing song
        save_data()
        return jsonify({
            'status': 'success',
            'message': 'Song removed from playlist'
        })
    else:
        # Sort songs by when they were added
        sorted_songs = sorted(
            playlists[playlist_id]['songs'],
            key=lambda x: x.get('added_at', ''),
            reverse=True
        )
        return jsonify({
            'status': 'success',
            'songs': sorted_songs
        })

@app.route('/default_playlists')
def get_default_playlists():
    try:
        # Get YouTube Music default playlists
        library = ytmusic.get_library_playlists()
        return jsonify({
            'status': 'success',
            'playlists': library
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/album/<album_id>')
def get_album_details(album_id):
    try:
        album = ytmusic.get_album(album_id)
        return jsonify({
            'status': 'success',
            'album': album
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/album/<album_id>/songs')
def get_album_songs(album_id):
    """Get songs from an album with option to play first song"""
    try:
        album = ytmusic.get_album(album_id)
        songs = album.get('tracks', [])
        
        # Filter out songs without videoId
        playable_songs = [song for song in songs if song.get('videoId')]
        
        return jsonify({
            'status': 'success',
            'album': {
                'title': album.get('title'),
                'artist': album.get('artist'),
                'year': album.get('year'),
                'thumbnails': album.get('thumbnails', []),
                'description': album.get('description')
            },
            'songs': playable_songs,
            'total_songs': len(playable_songs)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/artist/<artist_id>')
def get_artist_details(artist_id):
    try:
        artist = ytmusic.get_artist(artist_id)
        return jsonify({
            'status': 'success',
            'artist': artist
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/playlist/<playlist_id>')
def get_playlist_details(playlist_id):
    try:
        playlist = ytmusic.get_playlist(playlist_id)
        return jsonify({
            'status': 'success',
            'playlist': playlist
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/playlist/<playlist_id>/songs')
def get_playlist_songs(playlist_id):
    """Get songs from a playlist with option to play first song"""
    try:
        playlist = ytmusic.get_playlist(playlist_id)
        songs = playlist.get('tracks', [])
        
        # Filter out songs without videoId
        playable_songs = [song for song in songs if song.get('videoId')]
        
        return jsonify({
            'status': 'success',
            'playlist': {
                'title': playlist.get('title'),
                'author': playlist.get('author'),
                'description': playlist.get('description'),
                'thumbnails': playlist.get('thumbnails', []),
                'views': playlist.get('views'),
                'duration': playlist.get('duration')
            },
            'songs': playable_songs,
            'total_songs': len(playable_songs)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring and CI/CD"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(debug=True, port=8009)