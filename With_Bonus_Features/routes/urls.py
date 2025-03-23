from flask import Blueprint, request, redirect, jsonify
from controllers.url_controller import shorten_url, redirect_url

urls_bp = Blueprint('urls_bp', __name__)

@urls_bp.route('/shorten', methods=['POST'])
def shorten():
    data = request.get_json()
    if not data or 'long_url' not in data:
        return jsonify({"error": "long_url is required"}), 400

    long_url = data['long_url']
    custom_alias = request.args.get('alias')  
    ttl = request.args.get('ttl')             
    ttl = int(ttl) if ttl and ttl.isdigit() else None

    result, status = shorten_url(long_url, custom_alias, ttl)
    return jsonify(result), status

@urls_bp.route('/<string:short_code>', methods=['GET'])
def go_to_url(short_code):
    long_url, status = redirect_url(short_code)
    if status == 302:
        return redirect(long_url)
    elif status == 410:
        return jsonify({"error": "This link has expired"}), 410
    else:
        return jsonify({"error": "URL not found"}), 404
