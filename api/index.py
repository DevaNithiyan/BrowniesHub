"""
Vercel Serverless Entry Point for Brownies Hub
----------------------------------------------
Exposes the Flask app instance for Vercel Python Serverless Runtime
and ensures PATH_INFO is correctly restored from Vercel edge headers.
"""

import sys
import os

# Add parent directory to path so imports work seamlessly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class VercelPathMiddleware:
    """
    WSGI middleware that fixes PATH_INFO on Vercel deployments.
    When Vercel rewrites routes to /api/index.py, this middleware restores
    the original request path from HTTP_X_MATCHED_PATH or REQUEST_URI.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        matched_path = environ.get('HTTP_X_MATCHED_PATH')
        if matched_path and matched_path != '/404' and not matched_path.startswith('/api/index'):
            path = matched_path.split('?')[0]
            environ['PATH_INFO'] = path
        elif environ.get('PATH_INFO') in ('/api/index.py', '/api/index', '/api', '', None):
            raw_uri = environ.get('REQUEST_URI') or environ.get('RAW_URI') or environ.get('HTTP_X_VERCEL_PATH') or '/'
            path = raw_uri.split('?')[0]
            if path and not path.startswith('/api/index'):
                environ['PATH_INFO'] = path

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
