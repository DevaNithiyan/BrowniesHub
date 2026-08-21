"""
Vercel Serverless Entry Point for Brownies Hub
----------------------------------------------
Exposes the Flask app instance for Vercel Python Serverless Runtime
and safely restores the original request path from rewrites.
"""

import sys
import os
import urllib.parse

# Add parent directory to path so imports work seamlessly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class VercelPathMiddleware:
    """
    WSGI middleware that fixes PATH_INFO on Vercel deployments.
    Restores the original request path from __path query parameter or REQUEST_URI.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        qs = environ.get('QUERY_STRING', '')
        params = urllib.parse.parse_qs(qs)
        
        # 1. Check __path query parameter injected by vercel.json rewrite
        if '__path' in params and params['__path']:
            path = params['__path'][0]
            if path and not path.startswith('/api/index'):
                if not path.startswith('/'):
                    path = '/' + path
                environ['PATH_INFO'] = path
                clean_params = {k: v for k, v in params.items() if k != '__path'}
                environ['QUERY_STRING'] = urllib.parse.urlencode(clean_params, doseq=True)
                return self.wsgi_app(environ, start_response)
                
        # 2. Check if PATH_INFO is missing or pointing to the script name
        current_path = environ.get('PATH_INFO', '')
        if current_path in ('/api/index.py', '/api/index', '/api', '', None):
            raw_uri = environ.get('REQUEST_URI') or environ.get('RAW_URI') or environ.get('HTTP_X_VERCEL_PATH') or '/'
            path = raw_uri.split('?')[0]
            if path and not path.startswith('/api/index'):
                environ['PATH_INFO'] = path

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
