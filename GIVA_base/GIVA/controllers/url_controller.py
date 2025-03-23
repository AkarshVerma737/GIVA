from models.url import URL
from extensions import db
from flask import current_app
from nanoid import generate
import validators

def shorten_url(long_url, custom_alias=None):
    # Validate the long URL
    if not validators.url(long_url):
        return {"error": "Invalid URL"}, 400

    # Check if the URL already exists in the DB
    existing = URL.query.filter_by(long_url=long_url).first()
    if existing:
        return {"short_url": f"{current_app.config['BASE_URL']}/{existing.short_code}"}, 200

    # If a custom alias is provided, check for its uniqueness
    if custom_alias:
        if URL.query.filter_by(short_code=custom_alias).first():
            return {"error": "Custom alias already exists"}, 409
        short_code = custom_alias
    else:
        # Generate a unique short code using nanoid
        short_code = generate(size=7)
        while URL.query.filter_by(short_code=short_code).first():
            short_code = generate(size=7)

    base_url = current_app.config["BASE_URL"]
    new_url = URL(long_url=long_url, short_code=short_code)
    db.session.add(new_url)
    db.session.commit()

    return {"short_url": f"{base_url}/{short_code}"}, 201

def redirect_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first()
    if url:
        url.clicks += 1
        db.session.commit()
        return url.long_url, 302
    return None, 404
