from urllib.parse import unquote
from flask import Blueprint, abort

from . import WAWIN_ID_PREFIX, wawin_client
from .manifest import MANIFEST
from .utils import respond_with, log_error

meta_bp = Blueprint('meta', __name__)


@meta_bp.route('/meta/<meta_type>/<meta_id>.json')
def addon_meta(meta_type: str, meta_id: str):
    meta_id = unquote(meta_id)

    if meta_type not in MANIFEST['types']:
        abort(404)

    if not meta_id.startswith(WAWIN_ID_PREFIX):
        return respond_with({'meta': {}}), 404

    slug = meta_id.replace(f"{WAWIN_ID_PREFIX}:", '')

    try:
        details = wawin_client.get_anime_details(slug)
        
        if not details:
            return respond_with({'meta': {}}), 404
        
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
                    'id': f"{WAWIN_ID_PREFIX}:{slug}:{ep['season']}:{ep['episode']}",
                    'title': ep.get('title', f"Episode {ep['episode']}"),
                    'episode': ep['episode'],
                    'season': ep.get('season', 1)
                }
                for ep in details.get('episodes', [])
            ]
        
        return respond_with({'meta': meta}, 86400)
    except Exception as e:
        log_error(e)
        return respond_with({'meta': {}}), 404
