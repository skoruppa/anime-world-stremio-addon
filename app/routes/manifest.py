from flask import Blueprint, abort

from . import WAWIN_ID_PREFIX
from .utils import respond_with

manifest_blueprint = Blueprint('manifest', __name__)

MANIFEST = {
    'id': 'com.skoruppa.watchanimeworld-stremio-addon',
    'version': '0.0.1',
    'name': 'WatchAnimeWorld Addon',
    'logo': 'https://watchanimeworld.in/wp-content/uploads/AWI-SiteTitle-1.png',
    'description': 'Stream anime from WatchAnimeWorld.in',
    'types': ['anime', 'series'],
    'contactEmail': 'skoruppa@gmail.com',
    'catalogs': [
        {'type': 'anime', 'id': 'trending', 'name': 'Trending'},
        {'type': 'anime', 'id': 'recent', 'name': 'Recent Episodes'},
        {
            'type': 'anime',
            'id': 'search',
            'name': 'Search',
            'extra': [{'name': 'search', 'isRequired': True}]
        }
    ],
    'behaviorHints': {'configurable': False},
    'resources': ['catalog', 'meta', 'stream'],
    'idPrefixes': [WAWIN_ID_PREFIX]
}


@manifest_blueprint.route('/manifest.json')
def addon_manifest():
    """
    Provides the manifest for the addon after the user has authenticated with MyAnimeList
    :return: JSON response
    """
    return respond_with(MANIFEST, 7200)
