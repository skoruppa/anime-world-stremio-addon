import urllib.parse
import requests
from flask import Blueprint, abort, url_for, request

from . import wawin_client, WAWIN_ID_PREFIX
from app.routes.utils import cache
from .manifest import MANIFEST
from .utils import respond_with, log_error

catalog_bp = Blueprint('catalog', __name__)


def _is_valid_catalog(catalog_type: str, catalog_id: str):
    if catalog_type in MANIFEST['types']:
        return any(c['id'] == catalog_id for c in MANIFEST['catalogs'])
    return False


@catalog_bp.route('/catalog/<catalog_type>/<catalog_id>.json')
@catalog_bp.route('/catalog/<catalog_type>/<catalog_id>/search=<search>.json')
@cache.cached()
def addon_catalog(catalog_type: str, catalog_id: str, search: str = None):
    if not _is_valid_catalog(catalog_type, catalog_id):
        abort(404)

    try:
        metas = []
        
        if catalog_id == 'newest_drops':
            results = wawin_client.get_newest_drops()
            metas = [wawin_to_meta(item) for item in results]
        elif catalog_id == 'most_watched_shows':
            results = wawin_client.get_most_watched_shows()
            metas = [wawin_to_meta(item) for item in results]
        elif catalog_id == 'new_arrivals':
            results = wawin_client.get_new_anime_arrivals()
            metas = [wawin_to_meta(item) for item in results]
        elif catalog_id == 'most_watched_films':
            results = wawin_client.get_most_watched_films()
            metas = [wawin_to_meta(item) for item in results]
        elif catalog_id == 'latest_movies':
            results = wawin_client.get_latest_anime_movies()
            metas = [wawin_to_meta(item) for item in results]
        elif catalog_id == 'search' and search:
            search = urllib.parse.unquote(search)
            results = wawin_client.search_anime(search)
            metas = [wawin_to_meta(item) for item in results]
        
        return respond_with({'metas': metas}, 3600)
    except Exception as e:
        log_error(e)
        return respond_with({'metas': []}, 3600)


def wawin_to_meta(item: dict):
    slug = item.get('slug')
    return {
        'id': f"{WAWIN_ID_PREFIX}:{slug}",
        'name': item.get('title'),
        'type': item.get('type', 'series'),
        'poster': item.get('poster')
    }