import re
import requests
from app.routes.utils import get_random_agent
from config import Config

async def get_video_from_zephyrflick_player(player_url: str):
    """
    Extract video URL and subtitles from Zephyrflick player
    :param player_url: Zephyrflick player URL
    :return: tuple (video_url, quality, headers, subtitles)
    """
    try:
        # Extract video ID from URL
        match = re.search(r'/video/([a-f0-9]+)', player_url)
        if not match:
            return None, None, None, []
        
        video_id = match.group(1)
        
        api_headers = {
            'User-Agent': get_random_agent(),
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': player_url
        }
        
        # Make POST request to get video source
        api_url = f"https://play.zephyrflick.top/player/index.php"
        params = {
            'data': video_id,
            'do': 'getVideo'
        }
        
        resp = requests.post(api_url, params=params, headers=api_headers, timeout=30)
        resp.raise_for_status()
        
        data = resp.json()
        video_url = data.get('videoSource')
        
        if not video_url:
            return None, None, None, []
        
        # Rewrite URL to use our proxy
        video_url = video_url.replace('https://play.zephyrflick.top', f'{Config.PROTOCOL}://{Config.REDIRECT_URL}')

        stream_headers = None
        
        # Get subtitles from player page
        subtitles = []
        try:
            page_resp = requests.get(player_url, headers=api_headers, timeout=30)
            page_resp.raise_for_status()
            
            # Find playerjsSubtitle variable
            subtitle_match = re.search(r'var playerjsSubtitle = "([^"]+)"', page_resp.text)
            if subtitle_match:
                subtitle_data = subtitle_match.group(1)
                # Parse subtitle entries: [Language]url
                for line in subtitle_data.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    sub_match = re.match(r'\[([^\]]+)\](.+)', line)
                    if sub_match:
                        lang_name = sub_match.group(1)
                        sub_url = sub_match.group(2)
                        
                        # Convert language name to ISO code
                        lang_code = 'eng' if 'english' in lang_name.lower() else lang_name.lower()[:3]
                        
                        # Determine file extension from original URL
                        file_ext = '.srt' if sub_url.endswith('.srt') else '.vtt'
                        subtitle_id = f"{video_id}_{lang_code}{file_ext}"
                        
                        # Store mapping for proxy route
                        from app.routes.proxy import subtitle_mappings
                        subtitle_mappings[subtitle_id] = sub_url
                        
                        # Proxy subtitle URL through our server
                        proxied_sub_url = f"{Config.PROTOCOL}://{Config.REDIRECT_URL}/subtitles/{subtitle_id}"
                        
                        subtitles.append({
                            'id': f"{video_id}_{lang_code}",
                            'url': proxied_sub_url,
                            'lang': lang_code
                        })
        except:
            pass
        
        return video_url, 'auto', stream_headers, subtitles
        
    except Exception as e:
        print(f"Error extracting Zephyrflick video: {e}")
        return None, None, None, []
