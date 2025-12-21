from flask import Blueprint, abort

from .utils import respond_with

manifest_blueprint = Blueprint('manifest', __name__)

MANIFEST = {
    'id': 'com.skoruppa.watchanimeworld-stremio-addon',
    'version': '0.0.2',
    'name': 'Anime World India Addon',
    'logo': 'https://watchanimeworld.in/wp-content/uploads/AWI-SiteTitle-1.png',
    'description': 'Watch anime in Hindi, Tamil, Telugu & English from WatchAnimeWorld.in',
    'types': ['anime', 'series', 'movie'],
    'idPrefixes': ['tt'],
    'contactEmail': 'skoruppa@gmail.com',
    'catalogs': [
        {'type': 'Anime World India', 'id': 'newest_drops', 'name': 'Newest Drops'},
        {'type': 'Anime World India', 'id': 'most_watched_shows', 'name': 'Most-Watched Shows'},
        {'type': 'Anime World India', 'id': 'new_arrivals', 'name': 'New Anime Arrivals'},
        {'type': 'Anime World India', 'id': 'most_watched_films', 'name': 'Most-Watched Films'},
        {'type': 'Anime World India', 'id': 'latest_movies', 'name': 'Latest Anime Movies'},
        {
            'type': 'Anime World India',
            'id': 'search',
            'name': 'Search',
            'extra': [{'name': 'search', 'isRequired': True}]
        }
    ],
    'behaviorHints': {'configurable': False},
    'resources': ['catalog', 'meta', 'stream'],
    'stremioAddonsConfig': {
        'issuer': 'https://stremio-addons.net',
        'signature': 'eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..7gV3q1MNizIqKIMz8e4qvw.DSKuF6iQaPJp9VOPWuafWVaMhN6a32S8fGxUXYcNqS7yaqP48Ys2__2p5On7XU14e6IOE5qy56xaZCqDi61J-hEThy76L6YtS0F6tyc140pdd65-7Mw_uiXin2gq9NV4.hjecT9eBaBcBrEy5MdVnCQ'
    }
}


@manifest_blueprint.route('/manifest.json')
def addon_manifest():
    """
    Provides the manifest for the addon after the user has authenticated with MyAnimeList
    :return: JSON response
    """
    return respond_with(MANIFEST, 7200)
