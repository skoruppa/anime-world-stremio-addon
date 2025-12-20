import re
import requests
from flask import Blueprint, Response, request, abort
from config import Config

proxy_bp = Blueprint('proxy', __name__)

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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
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
        
        return Response(content, mimetype='application/vnd.apple.mpegurl')
    except Exception as e:
        print(f"Error proxying HLS: {e}")
        abort(502)
