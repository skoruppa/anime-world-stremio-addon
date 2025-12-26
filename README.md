# Anime World India Stremio Addon
![Version](https://img.shields.io/badge/version-0.0.3-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-Active-brightgreen.svg)

<div align="center">
  <img src="https://watchanimeworld.in/wp-content/uploads/AWI-SiteTitle-1.png" alt="WatchAnimeWorld Logo" width="300">
</div>

This unofficial Stremio addon allows users to access anime streams from [AnimeWorld India](https://watchanimeworld.in/) - source for anime in Hindi, Tamil, Telugu & English.

## 🎯 Supported Players
- **Zephyrflick**: Primary streaming source with subtitle support

## ✨ Features
- 🌐 Multiple language support: **Hindi, Tamil, Telugu & English**
- 📝 Subtitles in VTT/SRT format
- 📺 Multiple catalogs:
  - **Newest Drops** - Latest episode releases
  - **Most-Watched Shows** - Popular anime series
  - **New Anime Arrivals** - Recently added series
  - **Most-Watched Films** - Popular anime movies
  - **Latest Anime Movies** - Recently added movies
- 🔍 Search functionality
- 🎬 Multi-season support

## 🚀 Usage

- Browse through 5 different catalogs
- Search for your favorite anime
- Watch with subtitles in multiple languages

## 🛠️ Installation

### Quick Install

1. Visit **[https://anime-world-stremio-addon.onrender.com/](https://anime-world-stremio-addon.onrender.com/)**
2. Click **"Install In Stremio"** button 
3. In Stremio, click install, and the addon will be added and ready for use


### Manual Installation

To install the addon manually:

1. Visit [https://anime-world-stremio-addon.onrender.com/](https://anime-world-stremio-addon.onrender.com/)
2. Copy the manifest URL
3. Open Stremio and go to the addon search box
4. Paste the copied manifest URL into the addon search box and press Enter
5. In Stremio, click install, and the addon will be added and ready for use

## 🏠 Self-Hosting

### Prerequisites
- Python 3.8+
- TMDB API Key (required) - Get it from [TMDB](https://www.themoviedb.org/settings/api)
- PostgreSQL or SQLite database

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/skoruppa/anime-world-stremio-addon.git
cd anime-world-stremio-addon
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Create a `.env` file in the root directory:

```env
# Flask Configuration
FLASK_RUN_HOST=localhost
FLASK_RUN_PORT=5000
FLASK_DEBUG=False

# TMDB API Key (REQUIRED)
TMDB_API_KEY=your_tmdb_api_key_here

# Database Configuration
# For SQLite (default):
DB_TYPE=sqlite
DB_PATH=mappings.db

# For PostgreSQL:
# DB_TYPE=postgresql
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

4. **Run the addon**

**Development:**
```bash
python run.py
```

**Production (recommended):**
```bash
gunicorn -c gunicorn_config.py run:app
```

The addon will be available at `http://localhost:5000`

### Environment Variables

| Variable | Required | Default       | Description |
|----------|----------|---------------|-------------|
| `TMDB_API_KEY` | **Yes** | -             | TMDB API key for IMDB mapping |
| `DB_TYPE` | No | `sqlite`      | Database type (`sqlite` or `postgresql`) |
| `DB_PATH` | No | `mappings.db` | SQLite database file path |
| `DATABASE_URL` | No | -             | PostgreSQL connection string |
| `FLASK_RUN_HOST` | No | `localhost`   | Host to bind the server |
| `FLASK_RUN_PORT` | No | `5000`        | Port to bind the server |
| `FLASK_DEBUG` | No | `False`       | Enable debug mode |
| `GUNICORN_WORKERS` | No | `3`           | Number of gunicorn workers |

## 📝 API References

This addon is developed using:

- **Stremio Addon SDK**: [official documentation](https://github.com/Stremio/stremio-addon-sdk)
- **WatchAnimeWorld.in**: Website providing all the anime
- **TMDB API**: For IMDB ID mapping and metadata

## 🐛 Help

If you encounter any issues or have any questions regarding the addon, feel free to report them in the [issues section](https://github.com/skoruppa/anime-world-stremio-addon/issues).

## 🤝 Support

If you want to thank me for the addon, you can [buy me a coffee](https://buymeacoffee.com/skoruppa) ☕
