from urllib.parse import unquote
from flask import Blueprint, abort

from . import wawin_client
from .manifest import MANIFEST
from .utils import respond_with, log_error
from app.database import db
from app.mapper import imdb_to_slug_cache, failed_mappings_cache

meta_bp = Blueprint('meta', __name__)


@meta_bp.route('/meta/<meta_type>/<meta_id>.json')
def addon_meta(meta_type: str, meta_id: str):
    meta_id = unquote(meta_id)

    if meta_type not in MANIFEST['types']:
        abort(404)

    # meta_id is IMDB ID (e.g., tt13706018)
    if not meta_id.startswith('tt'):
        return respond_with({'meta': {}})

    # Check if we know this is not anime (in-memory cache)
    if meta_id in failed_mappings_cache:
        return respond_with({'meta': {}})
    
    # Check if we know this is not anime (database with TTL)
    if db.is_failed_mapping(meta_id):
        failed_mappings_cache[meta_id] = True
        return respond_with({'meta': {}})
    
    # Check cache first
    if meta_id in imdb_to_slug_cache:
        slug = imdb_to_slug_cache[meta_id]
    else:
        # Find slug from IMDB ID
        slug = db.get_slug_by_imdb(meta_id)
        if slug:
            imdb_to_slug_cache[meta_id] = slug
    
    if not slug:
        return respond_with({'meta': {}})
    
    try:
        details = wawin_client.get_anime_details(slug)
        
        if not details:
            return respond_with({'meta': {}})
        
        meta = {
            'id': meta_id,
            'type': meta_type,
            'name': details.get('title'),
            'description': details.get('description'),
            'poster': details.get('poster'),
            'genres': details.get('genres', []),
            'releaseInfo': details.get('year'),
            'runtime': details.get('runtime')
        }
        
        # Only add videos for series
        if details.get('type') == 'series':
            meta['videos'] = [
                {
                    'id': f"{meta_id}:{ep['season']}:{ep['episode']}",
                    'title': ep.get('title', f"Episode {ep['episode']}"),
                    'episode': ep['episode'],
                    'season': ep.get('season', 1),
                    'thumbnail': ep.get('thumbnail')
                }
                for ep in details.get('episodes', [])
            ]
        
        return respond_with({'meta': meta}, 86400)
    except Exception as e:
        log_error(e)
        return respond_with({'meta': {}})
