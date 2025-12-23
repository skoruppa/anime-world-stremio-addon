import urllib.parse
from flask import Blueprint, abort
from .manifest import MANIFEST

from app.routes import wawin_client
from app.routes.utils import respond_with
from app.database import db
from app.mapper import get_or_create_slug_mapping

stream_bp = Blueprint('stream', __name__)


def process_stream_sync(stream_data):
    """Process a single stream source"""
    from app.players.zephyrflick import get_video_from_zephyrflick_player
    import asyncio
    
    player = stream_data.get('player')
    url = stream_data.get('url')
    
    if player == 'zephyrflick':
        try:
            # Get or create event loop (gevent compatible)
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running (gevent), create new one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    video_url, quality, headers, subtitles = loop.run_until_complete(
                        get_video_from_zephyrflick_player(url)
                    )
                    loop.close()
                else:
                    video_url, quality, headers, subtitles = loop.run_until_complete(
                        get_video_from_zephyrflick_player(url)
                    )
            except RuntimeError:
                # No event loop, create new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                video_url, quality, headers, subtitles = loop.run_until_complete(
                    get_video_from_zephyrflick_player(url)
                )
                loop.close()
        except Exception as e:
            print(f"Error processing stream: {e}")
            return None
    else:
        return None
    
    if not video_url:
        return None
    
    stream_obj = {
        'title': f'[{player}][{quality}]',
        'url': video_url
    }
    
    if headers:
        stream_obj['behaviorHints'] = {'proxyHeaders': headers}
    
    if subtitles:
        stream_obj['subtitles'] = [
            {'id': sub.get('id', sub['url']), 'url': sub['url'], 'lang': sub['lang']}
            for sub in subtitles
        ]
    
    return stream_obj


@stream_bp.route('/stream/<content_type>/<content_id>.json')
def addon_stream(content_type: str, content_id: str):
    """
    Provide stream URLs
    :param content_type: The type of content
    :param content_id: The id of the content (tt13706018:3:2 for series or tt13706018 for movies)
    :return: JSON response
    """
    content_id = urllib.parse.unquote(content_id)
    parts = content_id.split(":")

    if content_type not in MANIFEST['types']:
        abort(404)

    if len(parts) < 1 or not parts[0].startswith('tt'):
        return respond_with({'streams': []}, use_etag=False)

    imdb_id = parts[0]
    
    # Find or create slug mapping from IMDB ID
    slug = get_or_create_slug_mapping(imdb_id)
    if not slug:
        return respond_with({'streams': []}, use_etag=False)
    
    # For series: tt13706018:3:2, for movies: tt13706018
    if len(parts) == 3:
        season = int(parts[1])
        episode = int(parts[2])
    else:
        # Movies don't have season/episode
        season = None
        episode = None

    try:
        data = wawin_client.get_episode_streams(slug, season, episode)
        streams = []
        
        for stream_data in data.get('streams', []):
            stream = process_stream_sync(stream_data)
            if stream:
                streams.append(stream)
        
        return respond_with({'streams': streams}, use_etag=False)
    except Exception as e:
        print(f"Error getting streams: {e}")
        return respond_with({'streams': []}, use_etag=False)
