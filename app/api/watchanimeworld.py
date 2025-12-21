import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import re
from cachetools import TTLCache, cached
import time

BASE_URL = "https://watchanimeworld.in"
TIMEOUT = 30

# TTL cache with 15 minutes expiration
catalog_cache = TTLCache(maxsize=64, ttl=900)
search_cache = TTLCache(maxsize=128, ttl=900)
details_cache = TTLCache(maxsize=128, ttl=900)

class WatchAnimeWorldAPI:
    """
    WatchAnimeWorld scraper client
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _parse_section(self, soup, section_title):
        """Parse a section from homepage by title"""
        results = []
        
        # Check widget_list_episodes sections
        for section in soup.find_all('section', class_='widget_list_episodes'):
            title_elem = section.find('h3', class_='section-title')
            if title_elem and section_title.lower() in title_elem.text.lower():
                for slide in section.select('.swiper-slide'):
                    article = slide.find('article')
                    if not article:
                        continue
                    
                    link = article.find('a', class_='lnk-blk')
                    img = article.find('img')
                    title = article.find('h2', class_='entry-title')
                    
                    if link and title:
                        href = link.get('href', '')
                        slug = href.rstrip('/').split('/')[-1]
                        content_type = 'movie' if '/movies/' in href else 'series'
                        
                        results.append({
                            'title': title.text.strip(),
                            'slug': slug,
                            'poster': img.get('src', '').replace('//', 'https://') if img else None,
                            'type': content_type
                        })
        
        # Check widget_list_movies_series sections
        for section in soup.find_all('section', class_='widget_list_movies_series'):
            title_elem = section.find('h3', class_='section-title')
            if title_elem and section_title.lower() in title_elem.text.lower():
                for slide in section.select('.swiper-slide'):
                    article = slide.find('article')
                    if not article:
                        continue
                    
                    link = article.find('a', class_='lnk-blk')
                    img = article.find('img')
                    title = article.find('h2', class_='entry-title')
                    
                    if link and title:
                        href = link.get('href', '')
                        slug = href.rstrip('/').split('/')[-1]
                        content_type = 'movie' if '/movies/' in href else 'series'
                        
                        results.append({
                            'title': title.text.strip(),
                            'slug': slug,
                            'poster': img.get('src', '').replace('//', 'https://') if img else None,
                            'type': content_type
                        })
        
        # Check widget_top sections (Most-Watched)
        for section in soup.find_all('section', class_='widget_top'):
            title_elem = section.find('h3', class_='widget-title')
            if title_elem and section_title.lower() in title_elem.text.lower():
                for item in section.select('.top-picks__item'):
                    link = item.find('a', class_='lnk-blk')
                    img = item.find('img')
                    
                    if link and img:
                        href = link.get('href', '')
                        parts = href.rstrip('/').split('/')
                        slug = parts[-1] if parts else ''
                        alt_text = img.get('alt', '').replace('Image ', '')
                        content_type = 'movie' if '/movies/' in href else 'series'
                        
                        results.append({
                            'title': alt_text.strip(),
                            'slug': slug,
                            'poster': img.get('src', '').replace('//', 'https://') if img else None,
                            'type': content_type
                        })
        
        return results

    def _get_episodes_from_html(self, soup):
        """Extract episodes from HTML"""
        episodes = []
        # Try both selectors - page has #episode_by_temp, AJAX response doesn't
        for li in soup.select('#episode_by_temp li, li'):
            article = li.find('article', class_='episodes')
            if not article:
                continue
            
            link = article.find('a', class_='lnk-blk')
            num_epi = article.find('span', class_='num-epi')
            title_elem = article.find('h2', class_='entry-title')
            img = article.find('img')
            
            if link and num_epi:
                href = link.get('href', '')
                match = re.match(r'(\d+)x(\d+)', num_epi.text.strip())
                if match:
                    season = int(match.group(1))
                    episode = int(match.group(2))
                    ep_data = {
                        'season': season,
                        'episode': episode,
                        'title': title_elem.text.strip() if title_elem else f"Episode {episode}",
                        'url': href
                    }
                    if img:
                        thumbnail = img.get('src', '')
                        if thumbnail:
                            if thumbnail.startswith('//'):
                                thumbnail = 'https:' + thumbnail
                            elif not thumbnail.startswith('http'):
                                thumbnail = 'https://' + thumbnail
                            ep_data['thumbnail'] = thumbnail
                    episodes.append(ep_data)
        return episodes

    def _get_season_episodes(self, post_id: str, season: int):
        """Get episodes for a specific season"""
        url = f"{BASE_URL}/wp-admin/admin-ajax.php"
        params = {
            'action': 'action_select_season',
            'season': season,
            'post': post_id
        }
        
        resp = self.session.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        return self._get_episodes_from_html(soup)

    @cached(catalog_cache, key=lambda self: 'newest_drops')
    def get_newest_drops(self):
        """Get Newest Drops section"""
        try:
            resp = self.session.get(BASE_URL, timeout=TIMEOUT)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            return self._parse_section(soup, 'Newest Drops')
        except RecursionError:
            logging.error("RecursionError in get_newest_drops")
            return []
        except Exception as e:
            logging.error(f"Error in get_newest_drops: {e}")
            return []

    @cached(catalog_cache, key=lambda self: 'most_watched_shows')
    def get_most_watched_shows(self):
        """Get Most-Watched Shows section"""
        try:
            resp = self.session.get(BASE_URL, timeout=TIMEOUT)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            return self._parse_section(soup, 'Most-Watched Shows')
        except RecursionError:
            logging.error("RecursionError in get_most_watched_shows")
            return []
        except Exception as e:
            logging.error(f"Error in get_most_watched_shows: {e}")
            return []

    @cached(catalog_cache, key=lambda self: 'new_anime_arrivals')
    def get_new_anime_arrivals(self):
        """Get New Anime Arrivals section"""
        try:
            resp = self.session.get(BASE_URL, timeout=TIMEOUT)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            return self._parse_section(soup, 'New Anime Arrivals')
        except RecursionError:
            logging.error("RecursionError in get_new_anime_arrivals")
            return []
        except Exception as e:
            logging.error(f"Error in get_new_anime_arrivals: {e}")
            return []

    @cached(catalog_cache, key=lambda self: 'most_watched_films')
    def get_most_watched_films(self):
        """Get Most-Watched Films section"""
        try:
            resp = self.session.get(BASE_URL, timeout=TIMEOUT)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            return self._parse_section(soup, 'Most-Watched Films')
        except RecursionError:
            logging.error("RecursionError in get_most_watched_films")
            return []
        except Exception as e:
            logging.error(f"Error in get_most_watched_films: {e}")
            return []

    @cached(catalog_cache, key=lambda self: 'latest_anime_movies')
    def get_latest_anime_movies(self):
        """Get Latest Anime Movies section"""
        try:
            resp = self.session.get(BASE_URL, timeout=TIMEOUT)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            return self._parse_section(soup, 'Latest Anime Movies')
        except RecursionError:
            logging.error("RecursionError in get_latest_anime_movies")
            return []
        except Exception as e:
            logging.error(f"Error in get_latest_anime_movies: {e}")
            return []

    @cached(search_cache)
    def search_anime(self, query: str):
        """Search for anime"""
        try:
            url = f"{BASE_URL}/"
            params = {'s': query}
            
            resp = self.session.get(url, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = []
            
            # Search results are in #aa-movies section
            search_section = soup.select_one('#aa-movies')
            if search_section:
                for li in search_section.select('ul.post-lst > li'):
                    article = li.find('article')
                    if not article:
                        continue
                    
                    link = article.find('a', class_='lnk-blk')
                    img = article.find('img')
                    title = article.find('h2', class_='entry-title')
                    
                    if link and title:
                        href = link.get('href', '')
                        slug = href.rstrip('/').split('/')[-1]
                        content_type = 'movie' if '/movies/' in href else 'series'
                        
                        results.append({
                            'title': title.text.strip(),
                            'slug': slug,
                            'poster': img.get('src', '').replace('//', 'https://') if img else None,
                            'type': content_type
                        })
            
            return results
        except RecursionError:
            logging.error(f"RecursionError in search_anime for query: {query}")
            return []
        except Exception as e:
            logging.error(f"Error in search_anime: {e}")
            return []

    @cached(details_cache)
    def get_anime_details(self, slug: str):
        """Get anime details by slug"""
        for content_type in ['series', 'movies']:
            url = f"{BASE_URL}/{content_type}/{slug}"
            
            try:
                resp = self.session.get(url, timeout=TIMEOUT)
                resp.raise_for_status()
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                title = soup.select_one('.entry-title, h1.entry-title')
                description = soup.select_one('.description p')
                poster = soup.select_one('article.post img')
                
                genres = [g.text.strip() for g in soup.select('.genres a')]
                
                year = None
                year_elem = soup.select_one('.year .overviewCss')
                if year_elem:
                    year = year_elem.text.strip()
                
                runtime = None
                duration_elem = soup.select_one('.duration .overviewCss')
                if duration_elem:
                    runtime = duration_elem.text.strip()
                
                episodes = []
                if content_type == 'series':
                    episodes = self._get_episodes_from_html(soup)
                    
                    season_links = soup.select('.choose-season .sel-temp a')
                    if len(season_links) > 1:
                        post_id = season_links[0].get('data-post')
                        if post_id:
                            current_season = int(soup.select_one('.n_s').text.strip()) if soup.select_one('.n_s') else 1
                            for link in season_links:
                                season_num = int(link.get('data-season', 0))
                                if season_num != current_season:
                                    season_eps = self._get_season_episodes(post_id, season_num)
                                    episodes.extend(season_eps)
                    
                    episodes.sort(key=lambda x: (x['season'], x['episode']))
                else:
                    episodes.append({
                        'season': 1,
                        'episode': 1,
                        'title': title.text.strip() if title else 'Movie',
                        'url': url
                    })
                
                return {
                    'title': title.text.strip() if title else None,
                    'slug': slug,
                    'description': description.text.strip() if description else None,
                    'poster': poster.get('src', '').replace('//', 'https://') if poster else None,
                    'genres': genres,
                    'year': year,
                    'runtime': runtime,
                    'episodes': episodes,
                    'type': 'movie' if content_type == 'movies' else 'series'
                }
            except:
                continue
        
        return None

    def get_episode_streams(self, slug: str, season: int = None, episode: int = None):
        """Get stream URLs for an episode or movie"""
        # For movies, season and episode are None
        if season is not None and episode is not None:
            url = f"{BASE_URL}/episode/{slug}-{season}x{episode}/"
        else:
            url = f"{BASE_URL}/movies/{slug}"
        
        try:
            resp = self.session.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            streams = []
            
            for iframe in soup.find_all('iframe'):
                src = iframe.get('src', '') or iframe.get('data-src', '')
                if 'zephyrflick' in src.lower():
                    streams.append({
                        'player': 'zephyrflick',
                        'url': src if src.startswith('http') else urljoin(BASE_URL, src)
                    })
            
            if streams:
                return {'streams': streams}
        except:
            pass
        
        return {'streams': []}
