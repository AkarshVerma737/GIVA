from models.url import URL
from extensions import db
from flask import current_app, jsonify
from nanoid import generate
import validators
from datetime import datetime, timedelta
from redis import Redis

redis_client = Redis(host='localhost', port=6379, db=0)

def shorten_url(long_url, custom_alias=None, ttl=None):
    if not validators.url(long_url):
        return {"error": "Invalid URL"}, 400

    existing = URL.query.filter_by(long_url=long_url).first()
    if existing:
        return {"short_url": f"{current_app.config['BASE_URL']}/{existing.short_code}"}, 200

    if custom_alias:
        if URL.query.filter_by(short_code=custom_alias).first():
            return {"error": "Custom alias already exists"}, 409
        short_code = custom_alias
    else:
        short_code = generate(size=7)
        while URL.query.filter_by(short_code=short_code).first():
            short_code = generate(size=7)

    expires_at = None
    if ttl:
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)

    new_url = URL(long_url=long_url, short_code=short_code, expires_at=expires_at)
    db.session.add(new_url)
    db.session.commit()
    
    return {"short_url": f"{current_app.config['BASE_URL']}/{short_code}"}, 201

def redirect_url(short_code):
    # Try cache
    cached_url = redis_client.get(short_code)
    if cached_url:
        return cached_url.decode('utf-8'), 302

    url = URL.query.filter_by(short_code=short_code).first()
    if url:
        if url.expires_at and datetime.utcnow() > url.expires_at:
            return None, 410
        # Cache the result for 1 hour
        redis_client.set(short_code, url.long_url, ex=3600)
        url.clicks += 1
        db.session.commit()
        return url.long_url, 302
    return None, 404
