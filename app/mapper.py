import requests
import re
from typing import Optional
from cachetools import TTLCache
from config import Config
from app.database import db

# Cache for failed mapping attempts (1 hour TTL, max 500 entries)
failed_mappings_cache = TTLCache(maxsize=500, ttl=3600)

# Cache for successful slug->imdb mappings (1 hour TTL, max 1000 entries)
slug_to_imdb_cache = TTLCache(maxsize=1000, ttl=3600)

# Cache for successful imdb->slug lookups (1 hour TTL, max 1000 entries)
imdb_to_slug_cache = TTLCache(maxsize=1000, ttl=3600)

def get_imdb_id_from_tmdb(tmdb_id: str, content_type: str) -> Optional[str]:
    """Get IMDB ID from TMDB ID"""
    if not Config.TMDB_API_KEY:
        return None
    
    media_type = 'tv' if content_type == 'series' else 'movie'
    url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/external_ids"
    params = {'api_key': Config.TMDB_API_KEY}
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get('imdb_id')
    except:
        pass
    return None

def get_tmdb_details_from_imdb(imdb_id: str) -> Optional[dict]:
    """Get TMDB details from IMDB ID"""
    if not Config.TMDB_API_KEY:
        return None
    
    url = f"https://api.themoviedb.org/3/find/{imdb_id}"
    params = {
        'api_key': Config.TMDB_API_KEY,
        'external_source': 'imdb_id'
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get('movie_results'):
            result = data['movie_results'][0]
            result['media_type'] = 'movie'
            return result
        elif data.get('tv_results'):
            result = data['tv_results'][0]
            result['media_type'] = 'series'
            return result
    except:
        pass
    return None

def get_all_tmdb_posters(tmdb_id: str, content_type: str) -> list:
    """Get all poster paths for a TMDB item"""
    if not Config.TMDB_API_KEY:
        return []
    
    media_type = 'tv' if content_type == 'series' else 'movie'
    url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/images"
    params = {'api_key': Config.TMDB_API_KEY}
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        posters = data.get('posters', [])
        return [p['file_path'] for p in posters if p.get('file_path')]
    except:
        pass
    return []

def search_tmdb(title: str, content_type: str, poster_url: str = None, year: str = None) -> Optional[dict]:
    """Search TMDB for title and optionally match by poster"""
    if not Config.TMDB_API_KEY:
        return None
    
    media_type = 'tv' if content_type == 'series' else 'movie'
    url = f"https://api.themoviedb.org/3/search/{media_type}"
    params = {
        'api_key': Config.TMDB_API_KEY,
        'query': title
    }
    if year:
        params['year' if media_type == 'movie' else 'first_air_date_year'] = year
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = data.get('results', [])
        
        if not results:
            return None
        
        if len(results) == 1:
            return results[0]
        
        # Match by poster if provided
        if poster_url:
            # First try to match by main poster_path
            for result in results:
                poster_path = result.get('poster_path')
                if poster_path and poster_path in poster_url:
                    return result
            
            # If no match, try all posters for each result
            for result in results:
                all_posters = get_all_tmdb_posters(str(result['id']), content_type)
                for poster_path in all_posters:
                    if poster_path in poster_url:
                        return result
        
        return results[0]
    except:
        pass
    return None

def match_by_poster(tmdb_poster_path: str, search_results: list, tmdb_id: str = None, content_type: str = None) -> Optional[dict]:
    """Match WatchAnimeWorld search result by TMDB poster path"""
    if not tmdb_poster_path:
        return None
    
    # First try to match by main poster path
    for result in search_results:
        result_poster = result.get('poster', '')
        if tmdb_poster_path in result_poster:
            return result
    
    # If no match and we have tmdb_id, try all posters
    if tmdb_id and content_type:
        all_posters = get_all_tmdb_posters(tmdb_id, content_type)
        for poster_path in all_posters:
            for result in search_results:
                result_poster = result.get('poster', '')
                if poster_path in result_poster:
                    return result
    
    return None

def get_or_create_imdb_mapping(slug: str, title: str, content_type: str, poster_url: str = None, year: str = None) -> Optional[str]:
    """Get IMDB ID for slug, creating mapping if needed (slug → IMDB)"""
    # Check cache first
    if slug in slug_to_imdb_cache:
        return slug_to_imdb_cache[slug]
    
    # Check if mapping exists in DB
    mapping = db.get_mapping(slug)
    if mapping:
        imdb_id = mapping[1]
        slug_to_imdb_cache[slug] = imdb_id
        return imdb_id
    
    # Search TMDB
    result = search_tmdb(title, content_type, poster_url, year)
    if not result:
        return None
    
    tmdb_id = str(result['id'])
    imdb_id = get_imdb_id_from_tmdb(tmdb_id, content_type)
    
    if imdb_id:
        db.set_mapping(slug, tmdb_id, imdb_id)
        slug_to_imdb_cache[slug] = imdb_id
        return imdb_id
    
    return None

def get_or_create_slug_mapping(imdb_id: str) -> Optional[str]:
    """Get slug for IMDB ID, creating mapping if needed (IMDB → slug)"""
    from app.routes import wawin_client
    
    # Check if we already tried and failed (in-memory cache)
    if imdb_id in failed_mappings_cache:
        return None
    
    # Check if we already tried and failed (database with TTL)
    if db.is_failed_mapping(imdb_id):
        failed_mappings_cache[imdb_id] = True
        return None
    
    # Check cache first
    if imdb_id in imdb_to_slug_cache:
        return imdb_to_slug_cache[imdb_id]
    
    # Check if mapping exists in DB
    slug = db.get_slug_by_imdb(imdb_id)
    if slug:
        imdb_to_slug_cache[imdb_id] = slug
        return slug
    
    # Get TMDB details from IMDB ID
    tmdb_details = get_tmdb_details_from_imdb(imdb_id)
    if not tmdb_details:
        failed_mappings_cache[imdb_id] = True
        db.add_failed_mapping(imdb_id)
        return None
    
    title = tmdb_details.get('title') or tmdb_details.get('name')
    poster_path = tmdb_details.get('poster_path')
    tmdb_id = str(tmdb_details['id'])
    
    if not title:
        failed_mappings_cache[imdb_id] = True
        db.add_failed_mapping(imdb_id)
        return None
    
    # Search on WatchAnimeWorld
    search_results = wawin_client.search_anime(title)
    if not search_results:
        failed_mappings_cache[imdb_id] = True
        db.add_failed_mapping(imdb_id)
        return None
    
    # Match by poster (required)
    matched = match_by_poster(poster_path, search_results, tmdb_id, tmdb_details['media_type'])
    if not matched:
        failed_mappings_cache[imdb_id] = True
        db.add_failed_mapping(imdb_id)
        return None
    
    slug = matched.get('slug')
    if slug:
        db.set_mapping(slug, tmdb_id, imdb_id)
        imdb_to_slug_cache[imdb_id] = slug
        return slug
    
    failed_mappings_cache[imdb_id] = True
    db.add_failed_mapping(imdb_id)
    return None
