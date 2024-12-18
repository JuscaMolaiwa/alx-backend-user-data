#!/usr/bin/env python3
"""
Route module for the API
"""
from os import getenv
from api.v1.views import app_views
from flask import Flask, jsonify, abort, request
from flask_cors import (CORS, cross_origin)
import os
from api.v1.auth.auth import Auth
from api.v1.auth.session_auth import SessionAuth
from api.v1.auth.basic_auth import BasicAuth


app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
auth = None
auth_type = getenv('AUTH_TYPE', 'auth')
if auth_type == 'auth':
    auth = Auth()
if auth_type == 'basic_auth':
    auth = BasicAuth()
if auth_type == 'session_auth':
    auth = SessionAuth()


@app.errorhandler(401)
def unauthorized(error) -> str:
    """Unauthorized handler.
    """
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error) -> str:
    """Forbidden handler.
    """
    return jsonify({"error": "Forbidden"}), 403


@app.errorhandler(404)
def not_found(error) -> str:
    """ Not found handler
    """
    return jsonify({"error": "Not found"}), 404


@app.route('/api/v1/unauthorized', methods=['GET'])
def unauthorized_route():
    """Route to trigger the 401 Unauthorized error."""
    abort(401)


@app.route('/api/v1/forbidden', methods=['GET'])
def forbidden_route():
    """Route to trigger the 403 Forbidden error."""
    abort(403)


@app.before_request
def before_request():
    """Filter every request before it gets to the endpoint"""
    from api.v1.auth.auth import Auth
    auth = Auth()
    if auth is None:
        return
    allowed_paths = [
            '/api/v1/status/',
            '/api/v1/unauthorized/',
            '/api/v1/forbidden/'
            ]
    if not auth.require_auth(request.path, allowed_paths):
        return
    if not auth.authorization_header(request):
        abort(401)
    if not auth.current_user(request):
        abort(403)
    request.current_user = auth.current_user(request)


if __name__ == "__main__":
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=port)
