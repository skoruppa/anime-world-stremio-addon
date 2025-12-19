import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

BASE_URL = "https://watchanimeworld.in"
TIMEOUT = 30

class WatchAnimeWorldAPI:
    """
    WatchAnimeWorld scraper client
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search_anime(self, query: str):
        """
        Search for anime by name
        :param query: search query
        :return: list of anime results
        """
        url = f"{BASE_URL}/search"
        params = {'q': query}
        
        resp = self.session.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []
        
        for item in soup.select('.anime-item'):
            title = item.select_one('.anime-title')
            link = item.select_one('a')
            img = item.select_one('img')
            
            if title and link:
                results.append({
                    'title': title.text.strip(),
                    'slug': link['href'].strip('/').split('/')[-1],
                    'url': urljoin(BASE_URL, link['href']),
                    'poster': img['src'] if img else None
                })
        
        return results

    def get_anime_details(self, slug: str):
        """
        Get anime details by slug
        :param slug: anime slug
        :return: anime details dict
        """
        url = f"{BASE_URL}/anime/{slug}"
        
        resp = self.session.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        title = soup.select_one('.anime-title')
        description = soup.select_one('.anime-description')
        poster = soup.select_one('.anime-poster img')
        
        episodes = []
        for ep in soup.select('.episode-item'):
            ep_link = ep.select_one('a')
            if ep_link:
                ep_num = ep.select_one('.episode-number')
                episodes.append({
                    'number': int(ep_num.text.strip()) if ep_num else len(episodes) + 1,
                    'url': urljoin(BASE_URL, ep_link['href'])
                })
        
        return {
            'title': title.text.strip() if title else None,
            'slug': slug,
            'description': description.text.strip() if description else None,
            'poster': poster['src'] if poster else None,
            'episodes': episodes
        }

    def get_episode_streams(self, slug: str, episode: int):
        """
        Get stream URLs for an episode
        :param slug: anime slug
        :param episode: episode number
        :return: list of stream sources
        """
        url = f"{BASE_URL}/watch/{slug}/{episode}"
        
        resp = self.session.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        streams = []
        
        # Find Zephyrflick player
        zephyr_iframe = soup.select_one('iframe[src*="zephyrflick"]')
        if zephyr_iframe:
            streams.append({
                'player': 'zephyrflick',
                'url': zephyr_iframe['src']
            })
        
        # Find subtitle tracks
        subtitles = []
        for track in soup.select('track[kind="subtitles"]'):
            subtitles.append({
                'url': urljoin(BASE_URL, track.get('src', '')),
                'lang': track.get('srclang', 'en'),
                'label': track.get('label', 'English')
            })
        
        return {
            'streams': streams,
            'subtitles': subtitles
        }

    def get_trending_anime(self, limit=20):
        """
        Get trending anime list
        :param limit: number of results
        :return: list of anime
        """
        url = f"{BASE_URL}/trending"
        
        resp = self.session.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []
        
        for item in soup.select('.anime-item')[:limit]:
            title = item.select_one('.anime-title')
            link = item.select_one('a')
            img = item.select_one('img')
            
            if title and link:
                results.append({
                    'title': title.text.strip(),
                    'slug': link['href'].strip('/').split('/')[-1],
                    'poster': img['src'] if img else None
                })
        
        return results

    def get_recent_episodes(self, limit=20):
        """
        Get recently added episodes
        :param limit: number of results
        :return: list of recent episodes
        """
        url = f"{BASE_URL}/recent"
        
        resp = self.session.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []
        
        for item in soup.select('.episode-item')[:limit]:
            title = item.select_one('.anime-title')
            link = item.select_one('a')
            ep_num = item.select_one('.episode-number')
            
            if title and link:
                results.append({
                    'title': title.text.strip(),
                    'slug': link['href'].strip('/').split('/')[-2],
                    'episode': int(ep_num.text.strip()) if ep_num else 1
                })
        
        return results
