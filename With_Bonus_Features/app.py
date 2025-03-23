from flask import Flask
from config import Config
from extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize the database with the app
    db.init_app(app)

    # Default route to help guide users
    @app.route('/')
    def index():
        return "Welcome to the URL Shortener API. Use the /shorten endpoint to create a short URL."

    # Register the blueprint containing your API endpoints
    from routes.urls import urls_bp
    app.register_blueprint(urls_bp)

    # Create database tables if they do not exist
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(app.config.get("PORT", 5000))
    app.run(debug=True, port=port)
