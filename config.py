import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Configuration class
    """
    FLASK_HOST = os.getenv('FLASK_RUN_HOST', "localhost")
    FLASK_PORT = os.getenv('FLASK_RUN_PORT', "5000")
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 600
    KITSU_STREMIO_API_URL = os.getenv('KITSU_STREMIO_API_URL', "https://anime-kitsu.strem.fun/meta")

    DEBUG = os.getenv('FLASK_DEBUG', False)
    DATABASE = "/tmp/database.json"

    # Env dependent configs
    if DEBUG in ["1", True, "False"]:  # Local development
        PROTOCOL = "http"
        REDIRECT_URL = f"{FLASK_HOST}:{FLASK_PORT}"
    else:  # Production environment
        PROTOCOL = "https"
        REDIRECT_URL = f"{FLASK_HOST}"