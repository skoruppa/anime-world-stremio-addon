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

def reorder_audio_tracks(m3u8_content: str, preferred_lang: str) -> str:
    """
    Reorder audio tracks in m3u8 to set preferred language as DEFAULT=YES and first
    """
    lines = m3u8_content.split('\n')
    audio_tracks = []
    other_lines = []
    preferred_track = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('#EXT-X-MEDIA:TYPE=AUDIO'):
            # Extract language from track
            lang_match = re.search(r'LANGUAGE="([^"]+)"', line)
            if lang_match:
                track_lang = lang_match.group(1)
                if track_lang == preferred_lang:
                    # Set as DEFAULT=YES
                    line = re.sub(r'DEFAULT=(YES|NO)', 'DEFAULT=YES', line)
                    preferred_track = line
                else:
                    # Set as DEFAULT=NO
                    line = re.sub(r'DEFAULT=(YES|NO)', 'DEFAULT=NO', line)
                    audio_tracks.append(line)
            else:
                audio_tracks.append(line)
        else:
            other_lines.append((i, line))
        i += 1
    
    # Rebuild m3u8 with preferred track first
    result = []
    audio_inserted = False
    
    for idx, line in other_lines:
        result.append(line)
        # Insert audio tracks after #EXT-X-VERSION line
        if line.startswith('#EXT-X-VERSION') and not audio_inserted:
            if preferred_track:
                result.append(preferred_track)
            result.extend(audio_tracks)
            audio_inserted = True
    
    return '\n'.join(result)

@proxy_bp.route('/cdn/hls/<path:path>')
@proxy_bp.route('/<lang>/cdn/hls/<path:path>')
def proxy_hls(path, lang=None):
    """
    Proxy HLS playlist and rewrite URLs to point to original server
    Optionally reorder audio tracks to set preferred language as default
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
        
        # Reorder audio tracks if language specified
        if lang:
            content = reorder_audio_tracks(content, lang)
        
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
