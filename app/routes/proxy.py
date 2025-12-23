import re
import requests
from flask import Blueprint, Response, request, abort
from urllib.parse import unquote
from cachetools import TTLCache
from config import Config
from .utils import get_random_agent

proxy_bp = Blueprint('proxy', __name__)

# Store subtitle mappings with TTL (1 hour expiration, max 500 entries)
subtitle_mappings = TTLCache(maxsize=500, ttl=3600)

@proxy_bp.route('/cdn/hls/<path:path>')
def proxy_hls(path):
    """
    Proxy HLS playlist and rewrite URLs to point to original server
    """
    # Get original URL with query params
    query_string = request.query_string.decode('utf-8')
    original_url = f"https://play.zephyrflick.top/cdn/hls/{path}"
    if query_string:
        original_url += f"?{query_string}"
    
    try:
        headers = {
            'User-Agent': get_random_agent(),
            'Referer': 'https://play.zephyrflick.top/'
        }
        
        resp = requests.get(original_url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        content = resp.text
        
        # Rewrite relative URLs to absolute URLs pointing to original server
        content = re.sub(
            r'URI="(/hls/[^"]+)"',
            r'URI="https://play.zephyrflick.top\1"',
            content
        )
        content = re.sub(
            r'^(/hls/.+)$',
            r'https://play.zephyrflick.top\1',
            content,
            flags=re.MULTILINE
        )
        
        response = Response(content, mimetype='application/vnd.apple.mpegurl')
        # Add CORS headers for Stremio Web
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
    except Exception as e:
        print(f"Error proxying HLS: {e}")
        abort(502)

@proxy_bp.route('/subtitles/<subtitle_id>')
def proxy_subtitle(subtitle_id):
    """
    Proxy subtitle files with correct content-type
    """
    original_url = subtitle_mappings.get(subtitle_id)
    if not original_url:
        abort(404)
    
    try:
        headers = {
            'User-Agent': get_random_agent(),
            'Referer': 'https://play.zephyrflick.top/'
        }
        
        resp = requests.get(original_url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        # Determine content type based on file extension
        if subtitle_id.endswith('.srt'):
            content_type = 'application/x-subrip'
        else:
            content_type = 'text/vtt'
        
        response = Response(resp.content, mimetype=content_type)
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
    except Exception as e:
        print(f"Error proxying subtitle: {e}")
        abort(502)
