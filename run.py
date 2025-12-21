import logging

from flask import Flask, render_template, url_for, redirect
from flask_compress import Compress
from app.routes.catalog import catalog_bp
from app.routes.manifest import manifest_blueprint
from app.routes.meta import meta_bp
from app.routes.stream import stream_bp
from app.routes.proxy import proxy_bp
from app.routes.utils import cache
from config import Config

app = Flask(__name__, template_folder='./templates', static_folder='./static')
app.config.from_object('config.Config')
app.register_blueprint(manifest_blueprint)
app.register_blueprint(catalog_bp)
app.register_blueprint(meta_bp)
app.register_blueprint(stream_bp)
app.register_blueprint(proxy_bp)

Compress(app)
cache.init_app(app)

logging.basicConfig(format='%(asctime)s %(message)s')


@app.route('/')
@app.route('/configure')
def index():
    """
    Render the index page
    """
    from flask import make_response
    from app.routes.manifest import MANIFEST
    import hashlib
    
    manifest_url = f'{Config.PROTOCOL}://{Config.REDIRECT_URL}/manifest.json'
    manifest_magnet = f'stremio://{Config.REDIRECT_URL}/manifest.json'
    
    html = render_template('index.html',
                          manifest_url=manifest_url, 
                          manifest_magnet=manifest_magnet,
                          version=MANIFEST['version'])
    
    response = make_response(html)
    
    # Generate ETag based on version for 304 support
    etag = hashlib.md5(MANIFEST['version'].encode()).hexdigest()
    response.set_etag(etag)
    response.cache_control.max_age = 3600  # 1 hour
    response.cache_control.public = True
    
    # Check if client has valid cache
    if response.get_etag()[0] == request.headers.get('If-None-Match'):
        return make_response('', 304)
    
    return response


@app.route('/favicon.ico')
def favicon():
    """
    Render the favicon for the app
    """
    return app.send_static_file('favicon.ico')


@app.route('/callback')
def callback():
    """
    Callback URL from MyAnimeList
    :return: A webpage response with the manifest URL and Magnet URL
    """
    return redirect(url_for('index'))


if __name__ == '__main__':
    # For development only - use gunicorn in production
    app.run(host='0.0.0.0', port=5000, debug=False)
