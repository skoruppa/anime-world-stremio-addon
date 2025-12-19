import re
import requests
from bs4 import BeautifulSoup

async def get_video_from_zephyrflick_player(player_url: str):
    """
    Extract video URL from Zephyrflick player
    :param player_url: Zephyrflick player URL
    :return: tuple (video_url, quality, headers)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': player_url
        }
        
        resp = requests.get(player_url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        # Look for m3u8 playlist URL in the page
        m3u8_match = re.search(r'(https?://[^"\']+\.m3u8[^"\']*)', resp.text)
        
        if m3u8_match:
            video_url = m3u8_match.group(1)
            return video_url, 'auto', headers
        
        return None, None, None
    except Exception as e:
        print(f"Error extracting Zephyrflick video: {e}")
        return None, None, None
